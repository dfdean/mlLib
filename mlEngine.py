################################################################################
# 
# Copyright (c) 2020-2023 Dawson Dean
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################
#
# This takes a job file and uses it to:
#   Create a neural network as specified by the job file
#   Run the neural network for both training and testing data
#   Record the results in the job object
# In a sense, this is the interpreter for the job object. It does the actual work
# of running a neural network that is described in the Job object.
#
# The job object is used to configure a neural network, but also as a means of 
# passing commands and results between processes, either two processes on a 
# single machine or else over a network from a controller machine to worker 
# compute servers.
#
################################################################################

import os
import sys
import math
import io
import random
import json

# File ops
from os.path import isfile  #, join

# Multiprocessing
from torch.multiprocessing import Process
import multiprocessing

import numpy as np

# Pytorch
import torch
import torch.nn as nn
import torch.optim as optim

# XGBoost and its dependencies
import xgboost as xgb

# This file runs in the lib directory, so it does not need any special path to find 
# any other files in the lib dir.
import xmlTools as dxml
import tdfTools as tdf
import mlJob as mlJob
import jobShow as JobShow

torch.manual_seed(1)

PARTITION_SIZE = 10 * (1024 * 1024)
USE_GPU = False
MAX_RNN_DEPTH_WITH_GPU = 700


########################################
# Network Protocol Error Codes
#
# WARNING!
# These are defined in several files: predictor.py and mlEngine.py
# Do not change in one file and not the other.
########################################
E_NO_ERROR                  = 0
E_SERVER_ERROR              = 1
E_ASSERT_ERROR              = 2
# Client Errors
E_INVALID_CLIENT_REQUEST    = 100
# Job Request Errors
E_UNRECOGNIZED_OPTIMIZER    = 200


########################################
# Network Protocol Warning Codes
#
# WARNING!
# These are defined in several files: predictor.py and mlEngine.py
# Do not change in one file and not the other.
########################################
NO_WARN                                 = 0
E_WARN_CANT_PREDICT_START_OF_DISEASE    = 1

# These are just used for debugging
DD_DEBUG = True
DD_DEBUG_TRUNCATE_PREFLIGHT         = False
DD_DEBUG_TRUNCATE_TRAINING          = False
DD_DEBUG_TRUNCATE_TESTING           = False
DD_DEBUG_TRUNCATE_NUM_PARTITIONS    = 3

RECURRENT_STATE_LINEAR_UNIT_NAME    = "ReccurentStateLinearUnit"

LSTM_SAVED_STATE_NAME               = "LSTMState"
LSTM_LINEAR_UNIT_SAVED_STATE_NAME   = "LSTMLinearUnit"

# Debugging only
#torch.autograd.set_detect_anomaly(True)
g_ChildProcessPipe = None



################################################################################
################################################################################
def MLEngine_Init_GPU():
    try:
        if ((os.environ["MLEngine_Init"]) and (os.environ["MLEngine_Init"] == "1")):
            return
    except Exception:
        pass

    if (USE_GPU):
        # The CUDA functions are non-deterministic (by design) which can affect RNN functions.
        # To avoid non-determinism 
        # On CUDA 10.1, set environment variable CUDA_LAUNCH_BLOCKING=1. This may affect performance.
        # On CUDA 10.2 or later, set environment variable (note the leading colon symbol) 
        #   CUBLAS_WORKSPACE_CONFIG=:16:8 or CUBLAS_WORKSPACE_CONFIG=:4096:2.
        os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:2"

    os.environ["MLEngine_Init"] = "1"
# End - MLEngine_Init_GPU




################################################################################
################################################################################
def ASSERT_ERROR(messageStr):
    fExitOnAsserts = True

    print("ERROR! " + messageStr)
    if (fExitOnAsserts):
        print("Exiting process...")
        if (g_ChildProcessPipe is not None):
            MLEngine_ReturnResultsFromChildProcess(g_ChildProcessPipe, None, -1, -1, 
                                                    True, -1, -1, E_ASSERT_ERROR, -1)
        sys.exit(0)
# End - ASSERT_ERROR



################################################################################
################################################################################
def ASSERT_IF(fCondition, messageStr):
    if (fCondition):
        ASSERT_ERROR(messageStr)
# End - ASSERT_IF




################################################################################
# 
# MLEngine_SingleLayerNeuralNet
# 
# This implements a single Linear unit with or without a non-linear.
# It implements Logistics and also numeric outputs.
################################################################################
class MLEngine_SingleLayerNeuralNet(nn.Module):

    #####################################################
    # [MLEngine_SingleLayerNeuralNet::__init__]
    #####################################################
    def __init__(self, job):
        super().__init__()
        #print("MLEngine_SingleLayerNeuralNet::__init__")

        self.isLogistic = job.GetIsLogisticNetwork()
        #print("__init__: self.isLogistic=" + str(self.isLogistic))

        inputNameListStr = job.GetNetworkInputVarNames()
        inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
        self.NumInputVars = len(inputNameList)
        #print("inputNameListStr=" + str(inputNameListStr))
        #print("self.NumInputVars=" + str(self.NumInputVars))

        resultValueName = job.GetNetworkOutputVarName()
        #print("resultValueName = " + resultValueName)
        if (self.isLogistic):
            # The output is a single number that is the probability.
            self.NumOutputCategories = 1
        else:
            self.NumOutputCategories = tdf.TDF_GetNumClassesForVariable(resultValueName)
        #print("MLEngine_SingleLayerNeuralNet.Constructor numOutputCategories = " + str(self.NumOutputCategories))

        # Create the matrix of weights.
        # A nn.Linear is an object that contains a matrix A and bias vector b
        # It is used to compute (x * A-transpose) + b
        #    where x is the input, which is a vector with shape (1 x self.NumInputVars)
        #    or x is alternatively described as (rows=1, colums=self.NumInputVars). 
        self.inputToOutput = nn.Linear(self.NumInputVars, self.NumOutputCategories)

        # Depending on the result value type, make a Non-linearity.
        layerSpecXML = job.GetNetworkLayerSpec("InputLayer")
        nonLinearTypeStr = dxml.XMLTools_GetChildNodeTextAsStr(layerSpecXML, "NonLinear", "ReLU")
        self.outputNonLinearLayer = MLEngine_MakePyTorchNonLinear(nonLinearTypeStr, self.isLogistic, True)
    # End - __init__



    #####################################################
    #
    # [MLEngine_SingleLayerNeuralNet.forward]
    #
    # Forward prop.
    # This will leave pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #####################################################
    def forward(self, job, fIsTraining, inputMatrix, recurrentState, expectedOutputs):
        # fIsTraining and expectedOutputs are IGNORED here. It is only used for XGBoost

        output = self.inputToOutput(inputMatrix)

        if (job.GetDebug()):
            #job.RecordDebugVal(mlJob.DEBUG_EVENT_TIMELINE_LOSS, loss.data.item())
            job.RecordMatrixAsDebugVal(mlJob.DEBUG_EVENT_OUTPUT_AVG, 
                                        output.detach().numpy(), "Avg")

        if (self.outputNonLinearLayer is not None):
            #print("MLEngine_SingleLayerNeuralNet.forward. Raw output = " + str(output))
            output = self.outputNonLinearLayer(output)
            #print("MLEngine_SingleLayerNeuralNet.forward. Non-Linear output = " + str(output))
            if (job.GetDebug()):
                #job.RecordDebugVal(mlJob.DEBUG_EVENT_TIMELINE_LOSS, loss.data.item())
                job.RecordMatrixAsDebugVal(mlJob.DEBUG_EVENT_NONLINEAR_OUTPUT_AVG, 
                                                output.detach().numpy(), "Avg")

        return output, recurrentState
    # End - forward



    #####################################################
    # [MLEngine_SingleLayerNeuralNet.SaveNeuralNetstate]
    #####################################################
    def SaveNeuralNetstate(self, job):
        MLEngine_SaveLinearUnitToJob(self.inputToOutput, job, "inputToOutput")
    # End - SaveNeuralNetstate



    #####################################################
    #
    # [MLEngine_SingleLayerNeuralNet.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        restoredTensor = MLEngine_ReadLinearUnitFromJob(job, "inputToOutput")
        if (restoredTensor is not None):
            self.inputToOutput = restoredTensor
    # End - RestoreNetState


    #####################################################
    #####################################################
    def InitRecurrentState(self, sequenceSize):
        return None

    #####################################################
    #####################################################
    def MoveRecurrentStateOnOffGPU(self, recurrentState, toGPU, gpuDevice):
        return None

    #####################################################
    #####################################################
    def GetLibraryName(self):
        return("Pytorch")

    #####################################################
    #####################################################
    def GetInputWeights(self):
        return None

# class MLEngine_SingleLayerNeuralNet(nn.Module):








################################################################################
# 
# MLEngine_MultiLayerNeuralNet
# 
################################################################################
class MLEngine_MultiLayerNeuralNet(nn.Module):

    #####################################################
    # Initialize the weight matrices
    #
    # Plain Python containers, such as list and dict won’t be properly registered 
    # in a module class object
    # As a result, they do not appear as Parameters, and so will not be part of the backprop
    # or gradient updates. As a result, use nn.ModuleDict instead of dict 
    # and nn.ModuleList instead of list
    #####################################################
    def __init__(self, job):
        super().__init__()
        err = E_NO_ERROR

        self.isLogistic = job.GetIsLogisticNetwork()

        inputNameListStr = job.GetNetworkInputVarNames()
        inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
        self.NumInputVars = len(inputNameList)

        resultValueName = job.GetNetworkOutputVarName()
        self.NumOutputCategories = tdf.TDF_GetNumClassesForVariable(resultValueName)
        #print(">>>>> self.NumOutputCategories = " + str(self.NumOutputCategories))

        # If the recurrent state size is 0, then this is a simple deep neural network.
        self.RecurrentStateSize = job.GetNetworkStateSize()
        self.IsRNN = (self.RecurrentStateSize > 0)
        #print("self.RecurrentStateSize = " + str(self.RecurrentStateSize))

        # Build the network
        self.NetworkLayers = []
        self.LinearUnitList = nn.ModuleList()
        layerNum = 0

        ################################
        # Create the first network layer.
        layerSpecXML = job.GetNetworkLayerSpec("InputLayer")
        if (layerSpecXML is None):
            print("Cannot find first network layer")
            raise Exception()

        inputSize = self.NumInputVars
        # If this is an RNN, then the first layer takes in a combined vector
        # made from both the inputs and the recurrent state.
        if (self.IsRNN):
            inputSize = self.RecurrentStateSize + self.NumInputVars

        err, newLayerImpl, newLinearUnit, layerOutputSize = self.MakeOneNetworkLayer(layerSpecXML, 0, inputSize, False)
        if (err != E_NO_ERROR):
            print("Error in MLEngine_MultiLayerNeuralNet::__init__")
            raise Exception()

        self.LinearUnitList.append(newLinearUnit)
        self.NetworkLayers.append(newLayerImpl)
        # Get ready to do the next layer
        layerNum += 1
        currentLayerInputSize = layerOutputSize


        ################################
        # Create each hidden layer
        layerSpecXML = job.GetNetworkLayerSpec("HiddenLayer")
        while (layerSpecXML is not None):
            err, newLayerImpl, newLinearUnit, layerOutputSize = self.MakeOneNetworkLayer(layerSpecXML, layerNum, 
                                                                        currentLayerInputSize, False)
            if (err != E_NO_ERROR):
                raise Exception()

            self.NetworkLayers.append(newLayerImpl)
            self.LinearUnitList.append(newLinearUnit)

            # Get ready to do the next layer
            layerNum += 1
            currentLayerInputSize = layerOutputSize
            layerSpecXML = dxml.XMLTools_GetPeerNode(layerSpecXML, "HiddenLayer")
        # End - while (layerSpecXML is not None):


        ################################
        # Create the last layer
        layerSpecXML = job.GetNetworkLayerSpec("OutputLayer")
        if (layerSpecXML is None):
            raise Exception()

        err, newLayerImpl, newLinearUnit, layerOutputSize = self.MakeOneNetworkLayer(layerSpecXML, layerNum, 
                                                currentLayerInputSize, True)
        if (err != E_NO_ERROR):
            raise Exception()
        self.NetworkLayers.append(newLayerImpl)
        self.LinearUnitList.append(newLinearUnit)
        self.NumLayers = layerNum + 1

        # If this is an RNN, then create the LinearUnit to compute the next state.
        # This state can be computed as a function of different kinds of inputs, 
        # such as:
        # - Previous state, current inputs
        # - Previous state, current inputs, current output
        self.rnnStateLinearUnit = None
        if (self.IsRNN):
            inputSize = self.RecurrentStateSize + self.NumInputVars + self.NumOutputCategories
            outputSize = self.RecurrentStateSize
            self.rnnStateLinearUnit = nn.Linear(inputSize, outputSize)
        # End - if (self.IsRNN)
    # End - __init__





    #####################################################
    #
    # [MakeOneNetworkLayer]
    #
    # Create 1 layer in the networ. The network will look like:
    #
    #    Inputs -> [InputToVec1] -> Vec1
    #                    -> [Vec1ToVec2] -> Vec2
    #                    -> [Vec2ToVec3] -> Vec3
    #                       .......
    #                    -> [VecNToOutput] -> outputs
    #
    #####################################################
    def MakeOneNetworkLayer(self, layerSpecXML, layerNum, currentLayerInputSize, fIsFinalLayer):
        #print("Reading network layer: " + str(layerNum))
        newLayerImpl = {'layerNum': layerNum}
        newLinearUnit = None
        newLinearUnit = None

        # Use the XML spec to create the next layer of the network
        if (fIsFinalLayer):
            if (self.isLogistic):
                # The output is a single number that is the probability.
                layerOutputSize = 1
            else:
                layerOutputSize = self.NumOutputCategories
        else:
            layerOutputSize = dxml.XMLTools_GetChildNodeTextAsInt(layerSpecXML, "layerOutputSize", -1)
        if (layerOutputSize <= 0):
            print("Invalid array size: " + str(layerOutputSize))
            return E_NO_ERROR, None, None, 0

        newLayerImpl['LayerOutputSize'] = layerOutputSize
        newLayerImpl['Name'] = "Vec" + str(layerNum) + "To" + str(layerNum + 1)
        newLayerImpl['fIsFinalLayer'] = fIsFinalLayer
        #print("MakeOneNetworkLayer. Layer " + str(layerNum) + " currentLayerInputSize=" + str(currentLayerInputSize))
        #print("MakeOneNetworkLayer. Layer " + str(layerNum) + " layerOutputSize=" + str(layerOutputSize))

        # Create the matrices of weights
        # A nn.Linear is an object that contains a matrix A and bias vector b
        # It is used to compute (x * A-transpose) + b
        #    where x is the input, which is a vector with shape (1 x self.NumInputVars)
        #    or x is alternatively described as (rows=1, colums=self.NumInputVars). 
        #
        # Plain Python containers, such as list and dict won’t be properly registered 
        # in a module class object
        # As a result, they do not appear as Parameters, and so will not be part of the backprop
        # or gradient updates. As a result, use nn.ModuleDict instead of dict 
        # and nn.ModuleList instead of list
        newLinearUnit = nn.Linear(currentLayerInputSize, layerOutputSize)

        # Make the non-linear units between linear layers
        # Depending on the result value type, make a Non-linearity
        nonLinearTypeStr = dxml.XMLTools_GetChildNodeTextAsStr(layerSpecXML, "NonLinear", "ReLU").lower()
        newLayerImpl['NonLinear'] = MLEngine_MakePyTorchNonLinear(nonLinearTypeStr, self.isLogistic, 
                                                                  fIsFinalLayer)

        return E_NO_ERROR, newLayerImpl, newLinearUnit, layerOutputSize
    # End - MakeOneNetworkLayer





    #####################################################
    #
    # [MLEngine_MultiLayerNeuralNet.forward]
    #
    # Forward prop.
    # This will leave pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #####################################################
    def forward(self, job, fIsTraining, inputMatrix, recurrentState, expectedOutputs):
        # fIsTraining and expectedOutputs are IGNORED here. It is only used for XGBoost
        vec = inputMatrix
        combinedInput = None

        # If this is an RNN, then the first layer takes in a combined vector
        # made from both the inputs and the recurrent state.
        if (self.IsRNN):
            combinedInput = torch.cat((inputMatrix, recurrentState), 1)
            vec = combinedInput
        # End - if (self.IsRNN):

        # The network will look like:
        #    Inputs -> [InputToVec1] -> Vec1
        #                    -> [Vec1ToVec2] -> Vec2
        #                    -> [Vec2ToOutput] -> outputs
        #
        # 0 is the layer that takes direct inputs, 
        # layer self.NumLayers-1 is the last layer that provides outputs
        for layerNum in range(self.NumLayers):
            layerInfo = self.NetworkLayers[layerNum]

            vec = self.LinearUnitList[layerNum](vec)
            if (layerInfo['NonLinear'] is not None):
                vec = layerInfo['NonLinear'](vec)
        # End - for layerNum in range(self.NumLayers):

        # If this is an RNN, then compute the next recurrent state
        # This state can be computed as a function of different kinds of inputs, 
        # such as:
        # - Previous state, current inputs
        # - Previous state, current inputs, current output
        if (self.IsRNN):
            combinedInput = torch.cat((combinedInput, vec), 1)
            recurrentState = self.rnnStateLinearUnit(combinedInput)
        # End - if (self.IsRNN):

        return vec, recurrentState
    # End - forward



    #####################################################
    # Reset the hidden state.
    # This is used each time we start a new sequence of inputs
    # Each sequence of inputs starts from an initial state.
    # One training sequence does not convey any information about 
    # another training sequence.
    # As a result, the order we train the input sequences does not matter.
    #####################################################
    def InitRecurrentState(self, sequenceSize):
        if (self.IsRNN):
            return torch.zeros(sequenceSize, self.RecurrentStateSize)
        else:
            return None
    # End - InitRecurrentState



    #####################################################
    #####################################################
    def MoveRecurrentStateOnOffGPU(self, recurrentState, toGPU, gpuDevice):
        if (recurrentState is not None):
            if (toGPU):
                recurrentState = recurrentState.to(gpuDevice)
            else:
                recurrentState = recurrentState.cpu()

        return recurrentState
    # End - MoveRecurrentStateOnOffGPU




    #####################################################
    #
    # [MLEngine_MultiLayerNeuralNet.SaveNeuralNetstate]
    #
    #####################################################
    def SaveNeuralNetstate(self, job):
        fDebug = False
        if (fDebug):
            print("MLEngine_MultiLayerNeuralNet.SaveNeuralNetstate")

        # Layer 0 is the layer that takes direct inputs
        # Layer self.NumLayers-1 is the last layer that provides outputs
        for layerNum in range(self.NumLayers):
            layerInfo = self.NetworkLayers[layerNum]
            if (fDebug):
                print("MLEngine_MultiLayerNeuralNet.Save Tensor for layer " + str(layerNum) + ", " + layerInfo['Name'])
            MLEngine_SaveLinearUnitToJob(self.LinearUnitList[layerNum], job, layerInfo['Name'])

        # If this is an RNN, then save the linear unit for the RecurrentVector
        if (self.IsRNN):
            MLEngine_SaveLinearUnitToJob(self.rnnStateLinearUnit, job, RECURRENT_STATE_LINEAR_UNIT_NAME)
        # End - if (self.IsRNN):
    # End - SaveNeuralNetstate




    #####################################################
    #
    # [MLEngine_MultiLayerNeuralNet.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        fDebug = False
        if (fDebug):
            print("MLEngine_MultiLayerNeuralNet.RestoreNetState")

        # Layer 0 is the layer that takes direct inputs
        # Layer self.NumLayers-1 is the last layer that provides outputs
        for layerNum in range(self.NumLayers):
            layerInfo = self.NetworkLayers[layerNum]
            restoredTensor = MLEngine_ReadLinearUnitFromJob(job, layerInfo['Name'])
            if (restoredTensor is not None):
                if (fDebug):
                    print("MLEngine_MultiLayerNeuralNet.Restore Tensor for layer " + str(layerNum) + ", " + layerInfo['Name'])
                self.LinearUnitList[layerNum] = restoredTensor

        # If this is an RNN, then restore the linear unit for the RecurrentVector
        if (self.IsRNN):
            restoredTensor = MLEngine_ReadLinearUnitFromJob(job, RECURRENT_STATE_LINEAR_UNIT_NAME)
            if (restoredTensor is not None):
                if (fDebug):
                    print("MLEngine_MultiLayerNeuralNet.Restore Tensor for RNN")
                self.rnnStateLinearUnit = restoredTensor
        # End - if (self.IsRNN):
    # End - RestoreNetState


    #####################################################
    #####################################################
    def GetLibraryName(self):
        return("Pytorch")

    #####################################################
    #####################################################
    def GetInputWeights(self):
        return None

# class MLEngine_MultiLayerNeuralNet(nn.Module):







################################################################################
# 
# MLEngine_LSTMNeuralNet
# 
################################################################################
class MLEngine_LSTMNeuralNet(nn.Module):

    #####################################################
    # 
    # [MLEngine_LSTMNeuralNet::__init__]
    #
    # Initialize the weight matrices
    #####################################################
    def __init__(self, job):
        fDebug = False

        super().__init__()

        self.isLogistic = job.GetIsLogisticNetwork()

        inputNameListStr = job.GetNetworkInputVarNames()
        inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
        self.NumInputVars = len(inputNameList)

        resultValueName = job.GetNetworkOutputVarName()
        self.NumOutputCategories = tdf.TDF_GetNumClassesForVariable(resultValueName)
        if (self.isLogistic):
            # The output is a single number that is the probability.
            self.NumOutputCategories = 1

        self.RecurrentStateSize = job.GetNetworkStateSize()
        self.NumLayers = 24

        # Build the network
        if (fDebug):
            print("self.RecurrentStateSize = " + str(self.RecurrentStateSize))
            print("MLEngine_LSTMNeuralNet::__init__  NumInputVars = " + str(self.NumInputVars))
            print("MLEngine_LSTMNeuralNet::__init__  RecurrentStateSize = " + str(self.RecurrentStateSize))
            print("MLEngine_LSTMNeuralNet::__init__  NumLayers = " + str(self.NumLayers))
        self.LSTM = nn.LSTM(input_size=self.NumInputVars, 
                            hidden_size=self.RecurrentStateSize,
                            num_layers=self.NumLayers, 
                            batch_first=True)

        # Get the output layer.
        layerSpecXML = job.GetNetworkLayerSpec("OutputLayer")
        if (layerSpecXML is None):
            raise Exception()

        # Make the linear unit that maps the final hidden state to the output domain
        self.HiddenToOutput = nn.Linear(self.RecurrentStateSize, self.NumOutputCategories)

        # Create a non-linear.
        nonLinearTypeStr = dxml.XMLTools_GetChildNodeTextAsStr(layerSpecXML, "NonLinear", "ReLU")
        self.nonLinear = MLEngine_MakePyTorchNonLinear(nonLinearTypeStr, self.isLogistic, True)
    # End - __init__




    #####################################################
    # Reset the hidden state.
    # This is used each time we start a new sequence of inputs
    # Each sequence of inputs starts from an initial state.
    # One training sequence does not convey any information about 
    # another training sequence.
    # As a result, the order we train the input sequences does not matter.
    #####################################################
    def InitRecurrentState(self, sequenceSize):
        h0 = torch.zeros(self.NumLayers, sequenceSize, self.RecurrentStateSize)
        c0 = torch.zeros(self.NumLayers, sequenceSize, self.RecurrentStateSize)

        return (h0, c0)
    # End - InitRecurrentState


    #####################################################
    #####################################################
    def MoveRecurrentStateOnOffGPU(self, recurrentState, toGPU, gpuDevice):
        if (recurrentState is None):
            return None

        h0 = recurrentState[0]
        c0 = recurrentState[1]
        if (recurrentState):
            if (toGPU):
                h0 = h0.to(gpuDevice)
                c0 = c0.to(gpuDevice)
            else:
                h0 = h0.cpu()
                c0 = c0.cpu()

        return (h0, c0)
    # End - MoveRecurrentStateOnOffGPU



    #####################################################
    #
    # [MLEngine_LSTMNeuralNet.forward]
    #
    # Forward prop.
    # This will leave pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #####################################################
    def forward(self, job, fIsTraining, inputMatrix, recurrentState, expectedOutputs):
        fDebug = False

        # fIsTraining and expectedOutputs are IGNORED here. It is only used for XGBoost
        if (fDebug):
            print("Forward(): Original inputMatrix.size()=" + str(inputMatrix.size()))

        # There is a bug, where the hidden state is modified in-place on
        # a forward(), which causes the backprop to fail because it thinks
        # the state has been changed since the last dependency graph was setup.
        # I am not sure why. Some of the LSTM examples do not pass in a hidden state
        # at all, because they process the entire sequence with a single call to
        # the lstm network. However, I try to process each prefix to the full sequence
        # as a separate trainging sequence (every prefix may have a different prediction for
        # the time until an event, so this is reasonable). Thus, I need to pass the
        # hidden state around, and so I need some way to convince Pytorch that it has 
        # not been altered. So, rebuild the state before each call to forward.
        # <> FIXME BUGBUG HACK!!!!!!!!!!!!
        recurrentState = tuple([item.data for item in recurrentState])

        # LSTM expcects a 3-dimensional tensor, with #itemsInSequence x #batches x #features
        # So, even though there is a single batch, it requires you have a dimension for 
        # the batches.
        # Sometimes, like when we slice a series of inputs into prefixes, then we pass
        # in #itemsInSequence x #features and so we have to pad this out. 
        #
        # NOTE, we always pass in a dimension for #itemsInSequence, even if this
        # may be 1 for a single data point.
        if (fDebug):
            print("LSTM forward. inputMatrix.dim()=" + str(inputMatrix.dim()))
        if (inputMatrix.dim() == 1):
            inputMatrix = inputMatrix.view(1, -1, -1)
        elif (inputMatrix.dim() == 2):
            inputMatrix = inputMatrix.view(1, 1, -1)
        if (fDebug):
            print("Forward(): Flattened inputMatrix.size()=" + str(inputMatrix.size()))
            print("Forward(): Flattened inputMatrix=" + str(inputMatrix))

        # Run the network and generate the final hidden state.
        lstmOut, recurrentState = self.LSTM(inputMatrix, recurrentState)
        if (fDebug):
            print("Forward(): lstmOut=" + str(lstmOut))
            print("Forward(): lstmOut.size()=" + str(lstmOut.size()))

        # Map the final hidden state to the output domain.
        finalOut = self.HiddenToOutput(lstmOut)
        if (fDebug):
            print("Forward(): finalOut=" + str(finalOut))
            print("Forward(): finalOut.size()=" + str(finalOut.size()))

        if (self.nonLinear is not None):
            finalOut = self.nonLinear(finalOut)
            if (fDebug):
                print("Forward(): Post-non-linear finalOut=" + str(finalOut))
                print("Forward(): Post-non-linear finalOut.size()=" + str(finalOut.size()))

        if (fDebug):
            print("Forward(): finalOut.size()=" + str(finalOut.size()))
            print("FinalOut = " + str(finalOut))

        return finalOut, recurrentState
    # End - forward



    #####################################################
    #
    # [MLEngine_LSTMNeuralNet.SaveNeuralNetstate]
    #
    #####################################################
    def SaveNeuralNetstate(self, job):
        #print("MLEngine_LSTMNeuralNet.SaveNeuralNetstate. Start")

        # Save to io.BytesIO buffer
        ioBuffer = io.BytesIO()
        torch.save(self.LSTM, ioBuffer)
        stateBytes = ioBuffer.getvalue()

        # Convert the binary data to a series of hex chars, which is a string
        # Functions like stateBytes.decode("utf-8") do not work.
        stateStr = stateBytes.hex()

        #print("MLEngine_LSTMNeuralNet.SaveNeuralNetstate. stateBytes=" + str(stateBytes))
        #print("MLEngine_LSTMNeuralNet.SaveNeuralNetstate. stateBytes.type=" + str(type(stateBytes)))
        #print("MLEngine_LSTMNeuralNet.SaveNeuralNetstate. stateBytes.len=" + str(len(stateBytes)))
        #print("MLEngine_LSTMNeuralNet.SaveNeuralNetstate. stateStr.type=" + str(type(stateStr)))
        #print("MLEngine_LSTMNeuralNet.SaveNeuralNetstate. stateStr.len=" + str(len(stateStr)))
        #print("MLEngine_LSTMNeuralNet.SaveNeuralNetstate. stateStr=" + str(stateStr))

        job.SetNamedStateAsStr(LSTM_SAVED_STATE_NAME, stateStr)
        MLEngine_SaveLinearUnitToJob(self.HiddenToOutput, job, LSTM_LINEAR_UNIT_SAVED_STATE_NAME)

        #print("MLEngine_LSTMNeuralNet.SaveNeuralNetstate. Done")
    # End - SaveNeuralNetstate





    #####################################################
    #
    # [MLEngine_LSTMNeuralNet.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        stateStr = job.GetNamedStateAsStr(LSTM_SAVED_STATE_NAME, "")
        if ((stateStr is None) or ("" == stateStr)):
            return

        #print("MLEngine_LSTMNeuralNet.RestoreNetState. stateStr=" + str(stateStr))
        #print("MLEngine_LSTMNeuralNet.RestoreNetState. stateStr.type=" + str(type(stateStr)))
        #print("MLEngine_LSTMNeuralNet.RestoreNetState. stateStr.len=" + str(len(stateStr)))

        # Convert the string of Hex characters into a byte sequence.
        stateBytes = bytearray.fromhex(stateStr)
        #print("MLEngine_LSTMNeuralNet.RestoreNetState. stateBytes=" + str(stateBytes))
        #print("MLEngine_LSTMNeuralNet.RestoreNetState. stateBytes.type=" + str(type(stateBytes)))
        #print("MLEngine_LSTMNeuralNet.RestoreNetState. stateBytes.len=" + str(len(stateBytes)))

        ioBuffer = io.BytesIO(stateBytes)
        self.LSTM = torch.load(ioBuffer)

        # Restore the linear unit for the RecurrentVector
        self.HiddenToOutput = MLEngine_ReadLinearUnitFromJob(job, LSTM_LINEAR_UNIT_SAVED_STATE_NAME)
    # End - RestoreNetState



    #####################################################
    #####################################################
    def GetLibraryName(self):
        return("Pytorch")

    #####################################################
    #####################################################
    def GetInputWeights(self):
        return None

# class MLEngine_LSTMNeuralNet(nn.Module):






################################################################################
# 
# MLEngine_XGBoostModel
# 
# This implements a single Linear unit with or without a non-linear.
# It implements Logistics and also numeric outputs.
################################################################################
class MLEngine_XGBoostModel(nn.Module):

    #####################################################
    # Initialize the weight matrices
    #####################################################
    def __init__(self, job):
        super().__init__()

        self.BoostedTree = None

        inputNameListStr = job.GetNetworkInputVarNames()
        inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
        self.NumInputVars = len(inputNameList)

        resultValueName = job.GetNetworkOutputVarName()
        self.ResultType = tdf.TDF_GetVariableType(resultValueName)
        self.NumOutputCategories = tdf.TDF_GetNumClassesForVariable(resultValueName)

        self.isLogistic = job.GetIsLogisticNetwork()
        if (self.ResultType in (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS, tdf.TDF_DATA_TYPE_BOOL)):
            self.IsClassifier = True
        else:
            self.IsClassifier = False
        self.learningRate = float(job.GetTrainingParamStr("LearningRate", "0.1"))
        self.numEpochs = job.GetTrainingParamInt("NumEpochs", 1)


        ############################################
        # Save the booster parameters.
        # https://xgboost.readthedocs.io/en/stable/parameter.html
        # https://xgboost.readthedocs.io/en/stable/tutorials/param_tuning.html
        #
        # objective [default=reg:squarederror]
        # The Objective function. Possible options are:
        #   reg:squarederror: regression with squared loss.
        #   reg:squaredlogerror: regression with squared log loss. All input labels are 
        #           required to be greater than -1. 
        #   reg:logistic: logistic regression
        #   reg:pseudohubererror: regression with Pseudo Huber loss, a twice differentiable
        #           alternative to absolute loss.
        #   binary:logistic: logistic regression for binary classification, output probability
        #   binary:logitraw: logistic regression for binary classification, output score before
        #           logistic transformation
        #   binary:hinge: hinge loss for binary classification. This makes predictions of 0 or 1, 
        #       rather than producing probabilities.
        #   count:poisson –poisson regression for count data, output mean of Poisson distribution
        #   survival:cox: Cox regression for right censored survival time data 
        #   survival:aft: Accelerated failure time model for censored survival time data.
        #   aft_loss_distribution: Probability Density Function used by survival:aft objective 
        #       and aft-nloglik metric.
        #   multi:softmax: set XGBoost to do multiclass classification using the softmax objective, 
        #       you also need to set num_class(number of classes)
        #   multi:softprob: same as softmax, but output a vector of ndata * nclass, which can be further 
        #       reshaped to ndata * nclass matrix. The result contains predicted probability of 
        #       each data point belonging to each class.
        #   rank:pairwise: Use LambdaMART to perform pairwise ranking where the pairwise loss is minimized
        #   rank:ndcg: Use LambdaMART to perform list-wise ranking
        #   rank:map: Use LambdaMART to perform list-wise ranking
        #   reg:gamma: gamma regression with log-link. Output is a mean of gamma distribution
        #   reg:tweedie: Tweedie regression with log-link.
        #
        # Note, values that start with "reg" are designed for regression tasks.
        #   values that start with "multi" are designed for classifier tasks.
        #   values that start with "binary" are designed for boolean detector tasks.
        #
        # Do not use the job's loss string. The Pytorch loss functions do not correlate well
        # with the  objective functions. Instead, use the output data type.
        #lossTypeStr = job.GetTrainingParamStr("LossFunction", "").lower()
        if (self.isLogistic):
            self.XGBoostObjective = "binary:logistic"
        elif (self.ResultType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            self.XGBoostObjective = "reg:squarederror"
        elif (self.ResultType in (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS, tdf.TDF_DATA_TYPE_BOOL)):
            self.XGBoostObjective = "multi:softmax"

        # eta
        # Step size shrinkage used in update to prevents overfitting
        # It is a number between 0--1, defaults to 0.3
        self.XGBoostETA = float(job.GetTrainingParamStr("XGBoostETA", "0.1"))

        # max_depth
        # Maximum depth of a tree. Increasing this value will make the model more complex and 
        # more likely to overfit. Beware that XGBoost aggressively consumes memory when training a deep tree.
        self.XGBoostMaxDepth = int(job.GetTrainingParamStr("XGBoostMaxDepth", "6"))

        # lambda [default=1, alias: reg_lambda]
        # L2 regularization term on weights. Increasing this value will make model more conservative.
        self.XGBoostlambda = int(job.GetTrainingParamStr("XGBoostlambda", "1"))

        # alpha [default=0, alias: reg_alpha]
        # L1 regularization term on weights. Increasing this value will make model more conservative.
        self.XGBoostAlpha = int(job.GetTrainingParamStr("XGBoostAlpha", "0"))

        # tree_method string [default= auto]
        # Taken from https://xgboost.readthedocs.io/en/stable/treemethod.html
        #   The tree construction algorithm used in XGBoost. 
        #   updater is more primitive than tree_method as tree_method is just a pre-configuration of updater
        #   XGBoost has 4 builtin tree methods, namely exact, approx, hist and gpu_hist
        #   exact:  During each split finding procedure, it iterates over all entries of input data. 
        #       It’s more accurate (among other greedy methods) but slow in computation performance.
        #   hist: An approximation tree method used in LightGBM with slight differences in implementation
        #   gpu_hist: The gpu_hist tree method is a GPU implementation of hist
        self.XGBoostTreeMethod = job.GetTrainingParamStr("XGBoostTreeMethod", "exact")

        # updater [default= grow_colmaker,prune]
        # A comma separated string defining the sequence of tree updaters to run, providing a modular 
        # way to construct and to modify the trees. This is an advanced parameter that is 
        #   usually set automatically, depending on some other parameters. 
        #   However, it could be also set explicitly by a user. 
        # The following updaters exist:
        #    grow_colmaker: non-distributed column-based construction of trees.
        #    grow_histmaker: distributed tree construction with row-based data splitting based on 
        #       global proposal of histogram counting.
        #    grow_local_histmaker: based on local histogram counting.
        #    grow_quantile_histmaker: Grow tree using quantized histogram.
        #    grow_gpu_hist: Grow tree with GPU.
        #    sync: synchronizes trees in all distributed nodes.
        #    refresh: refreshes tree’s statistics and/or leaf values based on the current data. 
        #       Note that no random subsampling of data rows is performed.
        #    prune: prunes the splits where loss < min_split_loss (or gamma) and nodes that 
        #       have depth greater than max_depth.

        # refresh_leaf [default=1]
        # This is a parameter of the refresh updater. When this flag is 1, tree leafs as well 
        # as tree nodes’ stats are updated. When it is 0, only node stats are updated.
        #
        # min_child_weight [default=1]
        # max_delta_step [default=0] 
        # subsample [default=1]
        # sampling_method [default= uniform]
        # colsample_bytree
        # scale_pos_weight [default=1]
        #   Control the balance of positive and negative weights, useful for unbalanced classes.
        # grow_policy [default= depthwise] Controls a way new nodes are added to the tree.
        #   Currently supported only if tree_method is set to hist or gpu_hist
        # max_leaves [default=0]
        #    Maximum number of nodes to be added. Only relevant when grow_policy=lossguide is set.
        # max_bin, [default=256]
        #    Only used if tree_method is set to hist or gpu_hist.
        # predictor, [default=``auto``]
        #    The type of predictor algorithm to use. Provides the same results but allows the use
        #       of GPU or CPU.
        # num_parallel_tree, [default=1]
        #   Number of parallel trees constructed during each iteration. 
        #   This option is used to support boosted random forest.
        # monotone_constraints
        #    Constraint of variable monotonicity. See tutorial for more information.
        # interaction_constraints
        #    Constraints for interaction representing permitted interactions.

        #<> 4 is much faster
        self.numThreadsInModel = 4
    # End - __init__



    #####################################################
    #
    # [MLEngine_XGBoostModel.forward]
    #
    # Forward prop.
    # This will leave pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #####################################################
    def forward(self, job, fIsTraining, inputNumPyMatrix, recurrentState, expectedOutputs):
        fDebug = False
        fShowPredictions = False
        output = None

        if (fDebug):
            print("MLEngine_XGBoostModel.forward. self.IsClassifier=" + str(self.IsClassifier))
            print("MLEngine_XGBoostModel.forward. inputNumPyMatrix.type=" + str(type(inputNumPyMatrix)))
            print("MLEngine_XGBoostModel.forward. inputNumPyMatrix.size=" + str(inputNumPyMatrix.shape))
            #print("MLEngine_XGBoostModel.forward. inputNumPyMatrix=" + str(inputNumPyMatrix))
            if (expectedOutputs is not None):
                print("MLEngine_XGBoostModel.forward. expectedOutputs.size=" + str(expectedOutputs.shape))
                print("MLEngine_XGBoostModel.forward. expectedOutputs=" + str(expectedOutputs))

        ##############################################
        # If we are making a prediction during testing:
        if (not fIsTraining):
            # If there is no restored state, then we cannot do anything.
            ASSERT_IF((self.BoostedTree is None), "No restored tree available during testing.")

            if (self.IsClassifier):
                output = self.BoostedTree.predict(inputNumPyMatrix)
            else:
                # Create Xgboost-specific DMatrix object from the numpy arrays
                # This seems to expect a 2-dimensional matrix: Num Samples x Num Features
                inputMatrix = xgb.DMatrix(inputNumPyMatrix)
                output = self.BoostedTree.predict(inputMatrix)
        # End - if (not fIsTraining):
        ##############################################
        # Otherwise, we are training, and we have an expected result.
        else:
            if (self.isLogistic):
                params = {
                    'learning_rate': self.learningRate,
                    'max_depth': self.XGBoostMaxDepth,
                    'objective': self.XGBoostObjective,  # Loss function
                    'eta': self.XGBoostETA,  # Step size shrinkage
                    'tree_method': self.XGBoostTreeMethod
                    #'eval_metric': 'auc'
                    }
                #print("XGBoost - Logistic params = " + str(params))
            elif (self.ResultType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
                params = {
                    #'learning_rate': self.learningRate. Do not use this; it breaks things.
                    'max_depth': self.XGBoostMaxDepth,
                    'objective': self.XGBoostObjective,  # Loss function
                    'eta': 1,  # self.XGBoostETA, #Step size shrinkage
                    'tree_method': self.XGBoostTreeMethod
                    }
                #print("XGBoost - Int params = " + str(params))
            # if (self.ResultType == tdf.TDF_DATA_TYPE_BOOL or tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS)
            # These are handled by explicit params to the xgb.XGBClassifier constructor, not a params
            # dictionary

            # For int and floats, we do not use the Classifier wrapper, so create 
            # Xgboost-specific DMatrix object from the numpy arrays
            # The inputs are a 2-dimensional matrix: Num Samples x Num Features
            # The labels (the expected outputs) are a 1-dimensional matrix: Num Samples
            if (not self.IsClassifier):
                inputAndOutputMatrix = xgb.DMatrix(inputNumPyMatrix, label=expectedOutputs)

            # If there is no restored state, then create the new model.
            if (self.BoostedTree is None):
                if (self.IsClassifier):
                    # There is a bug in XGBClassifier. Do not pass num_class=2
                    # If there are at most 2 different results, then XGBClassifier uses Loss: binary:logistic and
                    # cannot handle a num_class parem, even if num_class=2
                    # num_class=self.NumOutputCategories
                    self.BoostedTree = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', num_class=2, objective="multi:softprob")
                    self.BoostedTree.fit(inputNumPyMatrix, expectedOutputs)
                else:
                    self.BoostedTree = xgb.train(params, inputAndOutputMatrix, self.numEpochs)
            # Otherwise, build the new model by extending the restored model
            else:  # if (self.BoostedTree is NOT None):
                # Process_type="Update" will only update existing trees, not create
                # new trees. This is not desireable in my case, as it will stop further learning.
                #params['verbosity'] = '0'
                previousTree = self.BoostedTree
                if (self.IsClassifier):
                    # There is a bug in XGBClassifier. Do not pass num_class=2
                    # If there are at most 2 different results, then XGBClassifier defaults to Loss: binary:logistic and
                    # cannot handle a num_class parem, even if num_class=2. So, specify an objective other than
                    # Logistic.
                    #num_class=self.NumOutputCategories
                    self.BoostedTree = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', num_class=2, objective="multi:softprob")
                    self.BoostedTree.fit(inputNumPyMatrix, expectedOutputs, xgb_model=previousTree)
                else:
                    self.BoostedTree = xgb.train(params, inputAndOutputMatrix, self.numEpochs,
                                                 xgb_model=previousTree)

            # This is only used when we want to plot the predicted results during training.
            # That is usefulf or debugging, to see that we predict different results that look plausible.
            if (fShowPredictions or fDebug):
                if (self.IsClassifier):
                    output = self.BoostedTree.predict(inputNumPyMatrix.tolist())
                else:
                    inputMatrix = xgb.DMatrix(inputNumPyMatrix)
                    output = self.BoostedTree.predict(inputMatrix)
        # End - if (expectedOutputs is NOT None):

        if ((fDebug or fShowPredictions) and (output is not None)):
            print("MLEngine_XGBoostModel.forward. output.type=" + str(type(output)))
            print("MLEngine_XGBoostModel.forward. output.size=" + str(output.shape))
            print("MLEngine_XGBoostModel.forward. output=" + str(output))
            lastOutputVal = output[len(output) - 1]
            print("MLEngine_XGBoostModel.forward. fIsTraining=" + str(fIsTraining) + ", lastOutputVal=" + str(lastOutputVal))

        return output, recurrentState
    # End - forward



    #####################################################
    # [MLEngine_XGBoostModel.SaveNeuralNetstate]
    #####################################################
    def SaveNeuralNetstate(self, job):
        fDebug = False
        if (fDebug):
            print("MLEngine_XGBoostModel.SaveNeuralNetstate")

        # Do NOT panic here.
        # This can happen when we do not call forward() on any patient in the partition.
        # That can happen if there is no patient small enough for the partition or else
        # if every patient has the same repetitious data and is skipped by data balancing.
        if (self.BoostedTree is None):
            if (fDebug):
                print("MLEngine_XGBoostModel.SaveNeuralNetstate. Bail. BoostedTree is None")
            return

        # <> TODO
        #save_raw(raw_format='deprecated')
        #Save the model to a in memory buffer representation instead of file.
        #Parameters
        #raw_format (str) – Format of output buffer. Can be json, ubj or deprecated. Right now the default is deprecated 
        #but it will be changed to ubj (univeral binary json) in the future.
        #Return type
        #An in memory buffer representation of the model

        # Dump_model makes a text file, while save_model makes a binary file.
        filePathName = job.MakeStateFilePathname("xgboost")
        if (fDebug):
            print("MLEngine_XGBoostModel.SaveNeuralNetstate - filePathName = " + str(filePathName))

        self.BoostedTree.save_model(filePathName)
        # There is also boostedTree.dump_model(fileName), which seems to make a human-readable
        # printout, not used for restoring a tree.

        job.SetNamedStateAsStr(mlJob.SAVED_STATE_TYPE_ELEMENT_NAME, "file")
        job.SetNamedStateAsStr(mlJob.SAVED_STATE_FILE_PATH_ELEMENT_NAME, filePathName)
    # End - SaveNeuralNetstate



    #####################################################
    #
    # [MLEngine_XGBoostModel.RestoreNetState]
    #
    # A model that has been trained or loaded can compute predictions
    #####################################################
    def RestoreNetState(self, job):
        fDebug = False

        saveStateType = job.GetNamedStateAsStr(mlJob.SAVED_STATE_TYPE_ELEMENT_NAME, "").lower()
        if (fDebug):
            print("MLEngine_XGBoostModel.RestoreNetState. saveStateType=" + str(saveStateType))

        ###############################
        # An empty string is not an error, it just means there is no saved state
        if (saveStateType == ""):
            pass
        ###############################
        elif (saveStateType == "file"):
            saveStateFilePathname = job.GetNamedStateAsStr(mlJob.SAVED_STATE_FILE_PATH_ELEMENT_NAME, "")
            if (fDebug):
                print("MLEngine_XGBoostModel.RestoreNetState. saveStateFilePathname=" + str(saveStateFilePathname))

            if (not os.path.exists(saveStateFilePathname)):
                saveStateFilePathname = job.MakeStateFilePathname("xgboost")
                if (fDebug):
                    print("MLEngine_XGBoostModel.RestoreNetState. Revised saveStateFilePathname=" + str(saveStateFilePathname))

            if (fDebug):
                print("MLEngine_XGBoostModel.RestoreNetState. saveStateFilePathname=" + str(saveStateFilePathname))

            if ((saveStateFilePathname is not None) and (saveStateFilePathname != "")):
                if (self.IsClassifier):
                    self.BoostedTree = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
                else:
                    self.BoostedTree = xgb.Booster()
                self.BoostedTree.load_model(saveStateFilePathname)
            else:
                print("RestoreNetState ERROR! Bogus saveStateFilePathname: " + str(saveStateFilePathname))
        # End - if (saveStateType == "file"):
        ###############################
        else:
            print("RestoreNetState ERROR! Bogus saveStateType: " + str(saveStateType))
    # End - RestoreNetState


    #####################################################
    #####################################################
    def InitRecurrentState(self, sequenceSize):
        return None

    #####################################################
    #####################################################
    def MoveRecurrentStateOnOffGPU(self, recurrentState, toGPU, gpuDevice):
        return None

    #####################################################
    #####################################################
    def GetLibraryName(self):
        return("XGBoost")

    #####################################################
    #####################################################
    def GetInputWeights(self):
        inputWtArray = self.BoostedTree.feature_importances_

        #Available importance_types = [‘weight’, ‘gain’, ‘cover’, ‘total_gain’, ‘total_cover’]
        #weight : The number of times a feature is used to split the data across all trees.
        #cover : The number of times a feature is used to split the data across all trees weighted 
        #   by the number of training data points that go through those splits.
        #gain : The average training loss reduction gained when using a feature for splitting.
        #xgb.get_booster().get_score(importance_type = 'gain')

        return inputWtArray

# class MLEngine_XGBoostModel(nn.Module):






#####################################################
#
# [MLEngine_MakePyTorchNonLinear]
#
#####################################################
def MLEngine_MakePyTorchNonLinear(nonLinearTypeStr, fIsLogistic, fIsFinalLayer):
    # Make the non-linear units between linear layers
    # Depending on the result value type, make a Non-linearity.
    #
    # Tanh is the Hyperbolic Tangent 
    # It is -1 for negative values and 1 for positive values.
    #     Tanh(x)= (exp(x)+exp(−x)) / (exp(x)−exp(−x))
    #
    # Relu is a rectifying linear unit.
    # It is 0 for negative values and the identity function for positive values.
    #    ReLU(x) = max(0,x)
    #
    # Softmax converts a vector of real numbers into a probability distribution
    #     y[i] = e**x[i] / SUM(e**x[j])
    # So, all y[i] add up to 1.
    # Each entry is the ratio of one exponent over the sum of all exponents.
    # The exponentiation operator e**x[i] makes everything non-negative, but it
    # also converts all variable ranges to an exponential progression. So, bigger
    # values become a lot bigger.
    #
    nonLinearTypeStr = nonLinearTypeStr.lower()
    #print("nonLinearTypeStr = " + nonLinearTypeStr)
    if ((fIsLogistic) and (fIsFinalLayer)):
        newNonLinear = nn.Sigmoid()
    elif (nonLinearTypeStr == "tanh"):
        newNonLinear = torch.nn.Tanh()
    elif (nonLinearTypeStr == "relu"):
        newNonLinear = torch.nn.ReLU()
    elif (nonLinearTypeStr == "logsoftmax"):
        # A typical deep network will output a 3-dimensional matrix. 
        # This is using Pytorch, so we will always add a miniBatch dimension, and so the 
        # output will be [N, B, C] where N=num Samples, B = batch, C=NumFeatures
        # The last dimension is what we want, which is the lab values.
        # So, we want the non-linear to normalize along the last dimension,
        # which is n=2 since it's 0-based.
        # This is different than LSTM which output a 3-dimensional tensor
        # so their last dimension is the third, and which is index=2. 
        softMaxDimension = 2
        newNonLinear = nn.LogSoftmax(dim=softMaxDimension)
    elif (nonLinearTypeStr == "sigmoid"):
        newNonLinear = torch.nn.Sigmoid()
    elif (nonLinearTypeStr in ("none", "")):
        newNonLinear = None
    else:
        newNonLinear = None
        print("Error! MakeOneNetworkLayer found unrecognized non-linear type: " + nonLinearTypeStr)

    return newNonLinear
# End - MLEngine_MakePyTorchNonLinear




################################################################################
#
# [MLEngine_SaveLinearUnitToJob]
#
################################################################################
def MLEngine_SaveLinearUnitToJob(linearUnit, job, name):
    fDebug = False
    if (fDebug):
        print("MLEngine_SaveLinearUnitToJob")

    # Make private copies so we do not affect future backprop.
    weightMatrix = linearUnit.weight.detach().numpy()
    biasVector = linearUnit.bias.detach().numpy()

    job.SetLinearUnitMatrices(name, weightMatrix, biasVector)
# End - MLEngine_SaveLinearUnitToJob





################################################################################
#
# [MLEngine_ReadLinearUnitFromJob]
#
################################################################################
def MLEngine_ReadLinearUnitFromJob(job, name):
    fDebug = False

    fFoundIt, weightMatrix, biasVector = job.GetLinearUnitMatrices(name)
    if (not fFoundIt):
        if (fDebug):
            print("MLEngine_ReadLinearUnitFromJob. Error! Not found")
        return None

    weightTensor = torch.tensor(weightMatrix, dtype=torch.float32)
    biasTensor = torch.tensor(biasVector, dtype=torch.float32)
    weightSize = weightTensor.size()
    inputSize = weightSize[1]
    outputSize = weightSize[0]

    linearUnit = nn.Linear(inputSize, outputSize)
    linearUnit.weight = torch.nn.Parameter(weightTensor)
    linearUnit.bias = torch.nn.Parameter(biasTensor)

    return linearUnit
# End - MLEngine_ReadLinearUnitFromJob




################################################################################
#
# [MLEngine_PreflightGroupOfDataPoints]
# 
# Batch all data for a single patient.
# Batching is more than speed - it is also the accurracy of the final result.
# We are computing the loss as a function of the current weights, and the loss includes
# the weights. So, if the weights have high variance, then the loss, and subsequentally
# the future updates will have higher variance. Once variance is high, the system 
# will oscillate and not smoothly converge.
#
# Since the batch is a single patient, then the batch size is small, usually 5-20.
# As a result, I send them all in as a single minibatch, so there is only 1 minibatch
# which is the original complete batch.
#
################################################################################
def MLEngine_PreflightGroupOfDataPoints(job, inputArray, trueResultArray, numDataSamples):
    fDebug = False
    if (fDebug):
        print("MLEngine_PreflightGroupOfDataPoints. numDataSamples=" + str(numDataSamples))
        print("     inputArray=" + str(inputArray))
        print("     trueResultArray=" + str(trueResultArray))
        print("     Job Type = " + str(job.GetNetworkType().lower()))

    # Preflight wants data in the form (NumSamples x NumFeatures)
    arrayShape = inputArray.shape
    numDimensions = len(arrayShape)
    ASSERT_IF((numDimensions != 2), "MLEngine_PreflightGroupOfDataPoints. Bad array shape: " + str(arrayShape))
    numSamples = arrayShape[0]
    #numFeatures = arrayShape[1]
    ASSERT_IF((numSamples != len(trueResultArray)), "MLEngine_PreflightGroupOfDataPoints. Bad trueResultArray len: " + str(len(trueResultArray)))

    for sampleNum in range(numSamples):
        inputVec = inputArray[sampleNum]
        resultVal = trueResultArray[sampleNum]
        job.PreflightData(inputVec, resultVal)
    # End - for sampleNum in range(numSamples):
# End - MLEngine_PreflightGroupOfDataPoints




################################################################################
#
# [MLEngine_NormalizeInputs]
#
# The normal value can be:
#
#       1. norm = (value - min) / (max - min)
#       This is always positive
#
#       2. norm = (value - avgVal) / (max - min)
#       This may be negative
#
################################################################################
def MLEngine_NormalizeInputs(job, numDataSets, inputArray, fAddMinibatchDimension):
    fDebug = False

    numInputVars, inputVarNameStemArray, inputTypeArray, preflightInputMins, preflightInputMaxs, preflightMeanInput = job.GetPreflightResults()
    if (fDebug):
        print("MLEngine_NormalizeInputs. inputArray=" + str(inputArray))
        print("     numInputVars=" + str(numInputVars))
        print("     inputVarNameStemArray=" + str(inputVarNameStemArray))
        print("     inputTypeArray=" + str(inputTypeArray))
        print("     preflightInputMins=" + str(preflightInputMins))
        print("     preflightInputMaxs=" + str(preflightInputMaxs))
        print("     preflightMeanInput=" + str(preflightMeanInput))

    for sampleNum in range(numDataSets):
        if (fAddMinibatchDimension):
            inputVec = inputArray[sampleNum][0]
        else:
            inputVec = inputArray[sampleNum]

        for inputNum in range(numInputVars):
            valueRange = preflightInputMaxs[inputNum] - preflightInputMins[inputNum]
            if (valueRange == 0):
                print("ERROR!!!! MLEngine_NormalizeInputs (valueRange == 0). inputNum=" + str(inputNum))
                print("     preflightInputMaxs[inputNum]=" + str(preflightInputMaxs[inputNum]))
                print("     preflightInputMins[inputNum]=" + str(preflightInputMins[inputNum]))
                #print("     valueRange=" + str(valueRange))
                inputNameListStr = job.GetNetworkInputVarNames()
                inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
                print("     inputName=" + str(inputNameList[inputNum]))
                normValue = 0
            else:                
                diffFromMin = (inputVec[inputNum] - preflightInputMins[inputNum])
                normValue = diffFromMin / valueRange

            if (fDebug):
                print("MLEngine_NormalizeInputs. preflightInputMins[inputNum]=" + str(preflightInputMins[inputNum]))
                print("     preflightInputMaxs[inputNum]=" + str(preflightInputMaxs[inputNum]))
                print("     preflightMeanInput[inputNum]=" + str(preflightMeanInput[inputNum]))
                print("     normValue=" + str(normValue))

            if (fAddMinibatchDimension):
                inputArray[sampleNum][0][inputNum] = normValue
            else:
                inputArray[sampleNum][inputNum] = normValue
        # End - for inputNum in range(numInputVars):
    # End - for sampleNum in range(numDataSets)

    return inputArray
# End - MLEngine_NormalizeInputs




################################################################################
#
# [MLEngine_TrainGroupOfDataPoints]
# 
# Batch all data for a single patient.
# Batching is more than speed - it is also the accurracy of the final result.
# We are computing the loss as a function of the current weights, and the loss includes
# the weights. So, if the weights have high variance, then the loss, and subsequentally
# the future updates will have higher variance. Once variance is high, the system 
# will oscillate and not smoothly converge.
#
# Since the batch is a single patient, then the batch size is small, usually 5-20.
# As a result, I send them all in as a single minibatch, so there is only 1 minibatch
# which is the original complete batch.
#
################################################################################
def MLEngine_TrainGroupOfDataPoints(job, localNeuralNet, localLossFunction, localOptimizer, 
                                    lossTypeStr, fUsePytorch, cudaIsAvailable, gpuDevice,
                                    inputArray, trueResultArray, numDataSamples, 
                                    fAddMinibatchDimension):
    fDebug = False
    if (fDebug):
        print("\n==========================================")
        print("MLEngine_TrainGroupOfDataPoints. numDataSamples=" + str(numDataSamples))
        print("trueResultArray = " + str(trueResultArray))

    recurrentState = localNeuralNet.InitRecurrentState(numDataSamples)
    if ((cudaIsAvailable) and (recurrentState is not None)):
        recurrentState = localNeuralNet.MoveRecurrentStateOnOffGPU(recurrentState, True, gpuDevice)

    if (fUsePytorch):
        inputArray = MLEngine_NormalizeInputs(job, numDataSamples, inputArray, fAddMinibatchDimension)

    if (fUsePytorch):
        # Convert numpy matrices to Pytorch Tensors
        inputTensor = torch.from_numpy(inputArray).float()
        trueResultTensor = torch.from_numpy(trueResultArray).float()
        if (cudaIsAvailable):
            inputSize = inputTensor.size()
            rnnDepth = inputSize[0]
            if (rnnDepth >= MAX_RNN_DEPTH_WITH_GPU):
                print("Error! Skip RNN data (too long for GPU), rnnDepth=" + str(rnnDepth))
                return
            inputTensor = inputTensor.to(gpuDevice)
        # End - if (cudaIsAvailable):

        output, recurrentState = localNeuralNet.forward(job, True, inputTensor, recurrentState, trueResultTensor)
    # End - if (fUsePytorch):
    else:  # if (not fUsePytorch):
        if (fAddMinibatchDimension):
            numVars = len(inputArray[0][0])
        else:
            numVars = len(inputArray[0])
        mergedArray = np.concatenate([inputArray, trueResultArray], axis=1)
        uniqueArray, _ = np.unique(mergedArray, axis=0, return_counts=True)
        if (fAddMinibatchDimension):
            slicedInput = uniqueArray[:, :, 0:numVars]
            slicedResult = uniqueArray[:, :, numVars:numVars + 1]
        else:
            slicedInput = uniqueArray[:, 0:numVars]
            slicedResult = uniqueArray[:, numVars:numVars + 1]

        output, recurrentState = localNeuralNet.forward(job, True, slicedInput, recurrentState, slicedResult)
    # End - if (not fUsePytorch):

    # Transfer the output back to the CPU so we can access the results
    if ((cudaIsAvailable) and (output is not None)):
        output = output.cpu()

    # Compare output and ground-truth target in the job.
    # This is NOT a loss function, but rather it only updates job statistics.
    for index in range(numDataSamples):
        if (fAddMinibatchDimension):
            inputVec = inputArray[index][0]
            trueResult = trueResultArray[index][0][0]
        else:
            inputVec = inputArray[index]
            trueResult = trueResultArray[index][0]
        job.RecordTrainingSample(inputVec, trueResult)
    # End - for index in range(numDataSamples):

    # Now, compare predicted outputs to the ground-truth targets and compute the 
    # Loss (or Divergence or Div). This will also backpropagate and update the weights.
    # SADLY, XGBoost does not seem to provide the computed outputs during training.
    if (fUsePytorch):
        MLEngine_ComputeTrainingLossAndUpdate(job, output, trueResultTensor, 
                                              localNeuralNet, localOptimizer,
                                              lossTypeStr, localLossFunction)
# End - MLEngine_TrainGroupOfDataPoints






################################################################################
#
# [MLEngine_ComputeTrainingLossAndUpdate]
# 
# This procedure is only called for Pytorch.
################################################################################
def MLEngine_ComputeTrainingLossAndUpdate(job, output, trueResultTensor, 
                                          localNeuralNet, localOptimizer,
                                          lossTypeStr, localLossFunction):
    fDebug = False

    if (fDebug):
        print("===================================================")
        print("MLEngine_ComputeTrainingLossAndUpdate. output.size=" + str(output.size()))
        print("     output=" + str(output))
        print("     trueResultTensor.size=" + str(trueResultTensor.size()))
        print("     trueResultTensor=" + str(trueResultTensor))

    # Compute the loss between the prediction and the actual result.
    # Initially:
    #   output is a 3-d array: [ N, miniBatch=1, C ]
    #   trueResultTensor is a 3-d array: [ N, miniBatch=1, C ]
    # Where N is sequence size and C = number of classes
    # We may have to convert this for different loss functions.

    ##################
    # nllloss takes parameters:
    #    output is (N,C) 
    #    trueResult (also called Target) which is (N)
    if (lossTypeStr == "nllloss"):
        output = output[:, -1, :]
        trueResultTensor = trueResultTensor[:, -1, -1]
        trueResultTensor = trueResultTensor.long()
        if (fDebug):
            print("MLEngine_ComputeTrainingLossAndUpdate. nllloss")
            print("MLEngine_ComputeTrainingLossAndUpdate. Modified output.size=" + str(output.size()))
            print("MLEngine_ComputeTrainingLossAndUpdate. Modified output=" + str(output))
            print("MLEngine_ComputeTrainingLossAndUpdate. Modified trueResultTensor.size=" + str(trueResultTensor.size()))
            print("MLEngine_ComputeTrainingLossAndUpdate. Modified trueResultTensor=" + str(trueResultTensor))
    # End - if (lossTypeStr == "nllloss"):
    ##################
    # bceloss takes parameters:
    #    output is (N, batch, C) 
    #    trueResult (also called Target) is the same size: (N, batch, C)
    elif (lossTypeStr == "bceloss"):
        if (fDebug):
            print("MLEngine_ComputeTrainingLossAndUpdate. bceloss")
    # End - if (lossTypeStr == "bceloss"):
    ##################
    # L2 Loss (MSELoss) takes 2 matrices of the same size.
    # output: (N,∗) where ∗*∗ means, any number of additional dimensions
    # actualResult (also called Target) (N,∗), same shape as the input
    elif (lossTypeStr == "l2loss"):
        if (fDebug):
            print("MLEngine_ComputeTrainingLossAndUpdate. l2loss")

    # The result of the LSTM forward pass has shape (sequenceSize, batchSize, vocabSize)
    # If this is not LSTM, then swap the middle and last column. This makes it 
    # (sequenceSize, batchSize, vocabSize)
    #<>output = output.transpose(1, 2)

    if (fDebug):
        print("MLEngine_ComputeTrainingLossAndUpdate. Ready for loss()")
        print("     output.size=" + str(output.size()))
        print("     output=" + str(output))
        print("     trueResultTensor.size=" + str(trueResultTensor.size()))
        print("     trueResultTensor=" + str(trueResultTensor))

    loss = localLossFunction(output, trueResultTensor)
    job.RecordDebugVal(mlJob.DEBUG_EVENT_TIMELINE_LOSS, loss.data.item())

    if (fDebug):
        print("MLEngine_ComputeTrainingLossAndUpdate. loss.size=" + str(loss.size()))
        print("     loss=" + str(loss))
        print("     loss.data=" + str(loss.data))
        print("     loss.data.item()=" + str(loss.data.item()))

    # Initialize the gradients to 0. This prevents gradients from any previous
    # data set (ie a patient) from influencing the learning for the current data set.
    if (localOptimizer is not None):
        localOptimizer.zero_grad()
        localNeuralNet.zero_grad()  # <> ????? Do I need to do both?
    else:
        localNeuralNet.zero_grad()

    # Back-propagate. 
    # This function generates the gradients.
    # This is implemented by the base class, but it uses a
    # train of dependencies that was saved when the subclass computed the forward pass.
    # We call this on the loss value, but it kept pointers to the neural network that
    # calculated it. Additionally, each variable in the neural network recorded which
    # vectors and weights were used to compute it, so we can traverse the network in 
    # reverse order, from outputs back to inputs.
    try:
        loss.backward(retain_graph=True)
    except Exception:  # cuDNN as err:
        print("!!! Error. Caught exception in backward()")
        print("MLEngine_ComputeTrainingLossAndUpdate. output=" + str(output))
        print("     output.size=" + str(output.size()))
        print("     trueResultTensor.size=" + str(trueResultTensor.size()))
        print("     loss.size=" + str(loss.size()))
        print("     loss=" + str(loss))
        print("     loss.data=" + str(loss.data))
        print("     loss.data.item()=" + str(loss.data.item()))
        ASSERT_ERROR("MLEngine_ComputeTrainingLossAndUpdate")

    if (localOptimizer is not None):
        localOptimizer.step()
    else:
        learningRate = float(job.GetTrainingParamStr("LearningRate", "0.1"))
        with torch.no_grad():
            for currentParam in localNeuralNet.parameters():
                if (currentParam.grad is not None):
                    currentParam -= (learningRate * currentParam.grad)
    # End - Update matrices

    job.RecordTrainingLoss(loss.data.item())
# End - MLEngine_ComputeTrainingLossAndUpdate






################################################################################
#
# [MLEngine_TestGroupOfDataPoints]
# 
################################################################################
def MLEngine_TestGroupOfDataPoints(job, localNeuralNet, fUsePytorch, cudaIsAvailable, gpuDevice,
                                    inputArray, trueResultArray, numDataSamples, 
                                    fAddMinibatchDimension, networkOutputDataType):
    fDebug = False
    if (fDebug):
        print("\n==========================================")
        print("MLEngine_TestGroupOfDataPoints. numDataSamples=" + str(numDataSamples))
        print("     fUsePytorch=" + str(fUsePytorch))

    if (fUsePytorch):
        inputArray = MLEngine_NormalizeInputs(job, numDataSamples, inputArray, fAddMinibatchDimension)

    # Convert numpy matrices to Pytorch Tensors
    if (fUsePytorch):
        inputGroupSequenceTensor = torch.from_numpy(inputArray)
        trueResultTensor = torch.from_numpy(trueResultArray)
        inputGroupSequenceTensor = inputGroupSequenceTensor.float()
        trueResultTensor = trueResultTensor.float()

    recurrentState = localNeuralNet.InitRecurrentState(numDataSamples)
    if ((cudaIsAvailable) and (recurrentState is not None)):
        recurrentState = localNeuralNet.MoveRecurrentStateOnOffGPU(recurrentState, True, gpuDevice)

    with torch.no_grad():
        # Transfer the input tensor to GPU. We transferred the recurrent state to the GPU
        # once before the loop began.
        if ((fUsePytorch) and (cudaIsAvailable)):
            inputGroupSequenceTensor = inputGroupSequenceTensor.to(gpuDevice)

        # We pass in a 2-dimensional tensor for the input. This eliminates the #sequenceNum
        # So, we pass in (#batches x #features)
        # This is essentially a 1-dimensional array, since the batch index is always 0.
        # For XGboost, pass None for the trueResultArray. This tells forward() that we are 
        # not training
        if (fUsePytorch):
            output, recurrentState = localNeuralNet.forward(job, False, inputGroupSequenceTensor, 
                                                            recurrentState, trueResultArray)
        else:
            output, recurrentState = localNeuralNet.forward(job, False, inputArray, recurrentState, None)
    # End - with torch.no_grad():

    # Transfer the output back to the CPU so we can access the results
    if (cudaIsAvailable):
        output = output.cpu()

    if ((fUsePytorch) and (fDebug)):
        print("MLEngine_TestGroupOfDataPoints. output.size=" + str(output.size()))
        print("     output=" + str(output))
        print("     trueResultTensor.size=" + str(trueResultTensor.size()))
        print("     trueResultTensor=" + str(trueResultTensor))

    ASSERT_IF((output is None), "MLEngine_TestGroupOfDataPoints. output is None")
    predictedResultList = MLEngine_MakeListOfResults(job, output, numDataSamples, 
                                                     fUsePytorch, networkOutputDataType)

    # Compare predicted outputs to the ground-truth targets.
    # We store the results in the Job, and include lots of statistics like what
    # the accuracy was for different groups of result. 
    for index in range(numDataSamples):
        # Pytorch uses a 3rd dimension, for minibatches
        if (fAddMinibatchDimension):
            trueResult = trueResultArray[index][0][0]
        else:
            trueResult = trueResultArray[index][0]

        job.RecordTestingResult(trueResult, predictedResultList[index])
    # End - for index in range(numDataSamples):
# End - MLEngine_TestGroupOfDataPoints






################################################################################
#
# [MLEngine_MakeListOfResults]
#
################################################################################
def MLEngine_MakeListOfResults(job, output, numDataSamples, fUsePytorch, networkOutputDataType):
    fDebug = False

    # Note, a Boolean is a category result with two categories (0 and 1). But a Boolean
    # that is also a logistic, is a single floating point value between 0 and 1.
    isLogistic = job.GetIsLogisticNetwork()

    if (fDebug):
        print("MLEngine_MakeListOfResults. fUsePytorch = " + str(fUsePytorch))
        print("     networkOutputDataType = " + str(networkOutputDataType))
        print("     isLogistic = " + str(isLogistic))
        print("     numDataSamples = " + str(numDataSamples))
        print("     output = " + str(output))
        print("     output.type = " + str(type(output)))
        if (output is not None):
            print("     output.shape = " + str(output.shape))

    # If this is a category result, and if we are using xgBoost, then we already have a
    # list of outputs.
    if ((not fUsePytorch) 
            and (networkOutputDataType in (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS, tdf.TDF_DATA_TYPE_BOOL))
            and (not isLogistic)):
        #mostProbableCategoryList = np.asarray([np.argmax(line) for line in output])
        predictedResultList = [round(value) for value in output]
        return predictedResultList
    # End - if xgBoost and Categorical

    predictedResultList = [0] * numDataSamples

    # Compare predicted outputs to the ground-truth targets.
    for index in range(numDataSamples):
        # In a logistic, we want the probability that an item is true, not the most likely.
        # Note, a Boolean is a category result with two categories (0 and 1). But a Boolean
        # that is also a logistic is a single floating point value between 0 and 1.
        if (isLogistic):
            if (fUsePytorch):
                # Output is N x 1 x 1 where minibatch dim is 1 and there is also only 1 output, 
                # which is the result of the sigmoid.
                predictedResult = output[index][0][0].item()
            else:
                # Output is vector of length N, the result of the sigmoid.
                predictedResult = output[index]
            if (fDebug):
                print("MLEngine_MakeListOfResults. Logistic Network predictedResult: " + str(predictedResult))
        # End - if (isLogistic):
        # A category output is a list of probabilities. Get the class ID with the top probability
        elif (networkOutputDataType in (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS, tdf.TDF_DATA_TYPE_BOOL)):
            if (fUsePytorch):
                topProbability, topIndexTensor = output[index][0].topk(1)
                predictedResult = topIndexTensor.item()
                if (fDebug):
                    print("MLEngine_MakeListOfResults. topProbability: " + str(topProbability))
                    print("     topIndexTensor=" + str(topIndexTensor))
                    print("     topIndexTensor.type=" + str(type(topIndexTensor)))
                    print("     topIndexTensor.size=" + str(topIndexTensor.shape))
            else:
                # <> TODO: Lift making mostProbableCategoryList out of the loop
                mostProbableCategoryList = np.asarray([np.argmax(line) for line in output])
                predictedResult = mostProbableCategoryList[index]
                if (fDebug):
                    print("MLEngine_MakeListOfResults. mostProbableCategoryList = " + str(mostProbableCategoryList))
        # End - elif (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS or tdf.TDF_DATA_TYPE_BOOL)):
        # An int or float output is just the number.
        else:  # if ((tdf.TDF_DATA_TYPE_FLOAT) or (tdf.TDF_DATA_TYPE_INT)):
            if (fUsePytorch):
                predictedResult = output[index][0][0].item()
            else:
                predictedResult = output[index]
        # End - if (tdf.TDF_DATA_TYPE_FLOAT or tdf.TDF_DATA_TYPE_INT):

        predictedResultList[index] = predictedResult
    # End - for index in range(numDataSamples):

    if (fDebug):
        print("MLEngine_MakeListOfResults - predictedResultList: " + str(predictedResultList))

    return predictedResultList
# End - MLEngine_MakeListOfResults





################################################################################
# 
#
# [MLEngine_PreflightOneFilePartitionImpl]
#
# This returns:
#   job
#   numPatientsProcessed
#   fEOF - True iff we hit the end of the file
#   startPosFirstPatientInPartition
#   stopPosLastPatientInPartition
#   patientPositionList
#
################################################################################
def MLEngine_PreflightOneFilePartitionImpl(job, currentPartitionStart, currentPartitionStop):
    tdfFilePathName = job.GetDataParam("TrainData", "")
    inputNameListStr = job.GetNetworkInputVarNames()
    resultValueName = job.GetNetworkOutputVarName()
    _, requirePropertyRelationList, requirePropertyNameList, requirePropertyValueList = job.GetFilterProperties()
    startPosFirstPatientInPartition = -1
    stopPosLastPatientInPartition = -1
    
    # Open the file in the worker process address space
    tdfReader = tdf.TDF_CreateTDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                                            requirePropertyNameList)

    # On Preflight, we will build the list of patient positions. Initialize this.
    patientPositionList = []

    # Pytorch wants data (NumSamples x NumBatches x NumFeatures)
    # XGBoost wants data (NumSamples x NumFeatures)
    # Preflight wants data (NumSamples x NumFeatures)
    fAddMinibatchDimension = False

    # Get the first patient
    startPatientPosInFile = -1
    stopPatientPosInFile = -1
    fFoundPatient, fEOF, startPatientPosInFile, stopPatientPosInFile = tdfReader.GotoFirstPatientInPartition(
                                                                                     startPatientPosInFile, stopPatientPosInFile, 
                                                                                     currentPartitionStart, currentPartitionStop)
    #######################################
    # This loop looks at each patient in the current partition
    numPatientsProcessed = 0
    while ((not fEOF) and (fFoundPatient)):
        # On Preflight, we create a list of the patient locations as well as the valid boundaries of the partition.
        # Record where we found the first patient. We will return this as the start of the first patient in the partition.
        if (startPosFirstPatientInPartition < 0):
            startPosFirstPatientInPartition = startPatientPosInFile

        # We always save the stop of the patient, always overwriting the previour iteration.
        # Eventually, on the last iteration, this will write this for the last time.
        if (stopPatientPosInFile > 0):
            stopPosLastPatientInPartition = stopPatientPosInFile
        patientInfoDict = {'a': startPatientPosInFile, 'b': stopPatientPosInFile}
        patientPositionList.append(patientInfoDict)
 
        # Get a sequence of data points for a single patient. 
        numReturnedDataSets, inputArray, resultArray = tdfReader.GetDataForCurrentPatient(requirePropertyRelationList,
                                                                            requirePropertyNameList,
                                                                            requirePropertyValueList,
                                                                            fAddMinibatchDimension,
                                                                            False)  # fNormalize inmputs
        if (numReturnedDataSets >= 1):
            MLEngine_PreflightGroupOfDataPoints(job, inputArray, resultArray, numReturnedDataSets)
            # Go to the next patient in this partition
            numPatientsProcessed += 1
        # End - if (numReturnedDataSets >= 1):

        startPatientPosInFile = -1
        stopPatientPosInFile = -1
        if (not fEOF):
            fFoundPatient, fEOF, startPatientPosInFile, stopPatientPosInFile = tdfReader.GotoNextPatientInPartition(startPatientPosInFile, 
                                                                                                        stopPatientPosInFile, 
                                                                                                        currentPartitionStop)
    # End - while ((not fEOF) and (fFoundPatient)):

    tdfReader.Shutdown()

    return job, numPatientsProcessed, fEOF, startPosFirstPatientInPartition, stopPosLastPatientInPartition, patientPositionList
# End - MLEngine_PreflightOneFilePartitionImpl






################################################################################
#
# [MLEngine_TrainOneFilePartitionImpl]
#
# This returns:
#   job
#   numPatientsProcessed
#   totalSkippedPatients
#   numDataPointsProcessed
#   fEOF - True iff we hit the end of the file
#
################################################################################
def MLEngine_TrainOneFilePartitionImpl(job, currentPartitionStart, currentPartitionStop, 
                                       localNeuralNet, localLossFunction, localOptimizer, 
                                       fUsePytorch, cudaIsAvailable, gpuDevice):
    fDebug = False
    
    tdfFilePathName = job.GetDataParam("TrainData", "")
    inputNameListStr = job.GetNetworkInputVarNames()
    resultValueName = job.GetNetworkOutputVarName()
    _, requirePropertyRelationList, requirePropertyNameList, requirePropertyValueList = job.GetFilterProperties()
    #batchSizeFromConfig = job.GetTrainingParamInt(mlJob.TRAINING_OPTION_BATCHSIZE, -1)

    if (fDebug):
        print("MLEngine_TrainOneFilePartitionImpl. currentPartitionStart = " + str(currentPartitionStart))
        print("     currentPartitionStop = " + str(currentPartitionStop))

    # Open the file in the worker process address space
    tdfReader = tdf.TDF_CreateTDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                                            requirePropertyNameList)

    # Get some properties that are used for each training.
    lossTypeStr = job.GetTrainingParamStr("LossFunction", "").lower()

    # In some cases, we add a batches dimension to all data:
    #   Pytorch wants data (NumSamples x NumBatches x NumFeatures)
    #   XGBoost wants data (NumSamples x NumFeatures)
    if (fUsePytorch):
        fAddMinibatchDimension = True
    else:
        fAddMinibatchDimension = False

  
    ##############################
    # Make a list of patients in this file partition and group them by training priority.
    # We go through the classes in round robin, so first train a patient with priority 0, then
    # a patient in priority 1, and so on, until we reach the end and then go back to the beginning.
    # We iterate only while we can find one patient from each or most priorities.
    # We may not train all patients from the lowest priorities, because we do not want that to
    # overshadow the higher priorities. So, may not train all items from the more common classes.
    job.StartPrioritizingTrainingSamplesInPartition()
    numTrainingPriorities = job.GetNumTrainingPriorities()
    # Warning! Dont use [ [] ] * PatientsForTrainingPriority
    # That makes a list containing the same sublist object numTrainingPriorities times
    PatientsForTrainingPriority = [ [] for _ in range(numTrainingPriorities) ]
    #PatientsForTrainingPriority = []
    #for index in range(numTrainingPriorities):
    #   PatientsForTrainingPriority.append([])


    # This loop looks at each patient in the current partition
    # Examine every patient and decide which result class it is in.
    # This is tricky - a single patient may have several different classes of result.
    startPatientPosInFile = -1
    stopPatientPosInFile = -1
    fFoundPatient, fEOF, startPatientPosInFile, stopPatientPosInFile = tdfReader.GotoFirstPatientInPartition(
                                                                           startPatientPosInFile, stopPatientPosInFile, 
                                                                           currentPartitionStart, currentPartitionStop)
    while ((not fEOF) and (fFoundPatient)):
        # Get a sequence of data points for a single patient. 
        numReturnedDataSets, inputArray, resultArray = tdfReader.GetDataForCurrentPatient(requirePropertyRelationList,
                                                                        requirePropertyNameList,
                                                                        requirePropertyValueList,
                                                                        False,  # fAddMinibatchDimension
                                                                        False)  # fNormalize inmputs
        #######################################
        if (numReturnedDataSets >= 1):
            numSamples = inputArray.shape[0]

            # This is tricky - a single patient may have several different classes of result.
            # We consider the patient to be in its most rare class.
            # The most rare class is class 0, then class 1 is second most rare class and so on.
            trainingPriority = -1
            for sampleNum in range(numSamples):
                currentPriority = job.GetTrainingPriority(resultArray[sampleNum].item())
                if ((trainingPriority < 0) or (currentPriority < trainingPriority)):
                    trainingPriority = currentPriority
            # End - for sampleNum in range(numSamples):

            if (trainingPriority >= 0):
                patientInfoDict = {"a": startPatientPosInFile, "b": stopPatientPosInFile}
                PatientsForTrainingPriority[trainingPriority].append(patientInfoDict)
            # if (trainingPriority >= 0):
        # End - if (numReturnedDataSets >= 1)

        # Go to the next patient
        startPatientPosInFile = -1
        stopPatientPosInFile = -1
        if (not fEOF):
            fFoundPatient, fEOF, startPatientPosInFile, stopPatientPosInFile = tdfReader.GotoNextPatientInPartition(
                                                                                                        startPatientPosInFile, 
                                                                                                        stopPatientPosInFile, 
                                                                                                        currentPartitionStop)
    # End - while ((not fEOF) and (fFoundPatient)):


    # Randomize each of the patient lists
    for index in range(numTrainingPriorities):
        patientList = PatientsForTrainingPriority[index]
        random.shuffle(patientList)
        PatientsForTrainingPriority[index] = patientList


    # Now, train one patient from each level of data priority.
    # The more rare results are higher priority
    numPatientsProcessed = 0
    numDataPointsProcessed = 0
    patientIndexAtEachPriority = 0
    tooManySkippedClasses = job.GetMaxSkippedTrainingPriorities()
    while (True):
        numSkippedClasses = 0
        for priorityLevel in range(numTrainingPriorities):
            ptList = PatientsForTrainingPriority[priorityLevel]
            if (patientIndexAtEachPriority < len(ptList)):
                patientInfo = ptList[patientIndexAtEachPriority]
                tdfReader.GotoNextPatientInPartition(patientInfo["a"], patientInfo["b"], -1)
                numReturnedDataSets, inputArray, resultArray = tdfReader.GetDataForCurrentPatient(requirePropertyRelationList,
                                                                                requirePropertyNameList,
                                                                                requirePropertyValueList,
                                                                                fAddMinibatchDimension,
                                                                                False)  # fNormalize inmputs)
                if (numReturnedDataSets >= 1):
                    MLEngine_TrainGroupOfDataPoints(job, localNeuralNet, localLossFunction, localOptimizer, 
                                                    lossTypeStr, fUsePytorch, cudaIsAvailable, gpuDevice,
                                                    inputArray, resultArray, 
                                                    numReturnedDataSets, fAddMinibatchDimension)
                    numPatientsProcessed += 1
                    numDataPointsProcessed += numReturnedDataSets
                # if (numReturnedDataSets >= 1):
            # End - if (patientIndexAtEachPriority < len(ptList)):
            else:
                numSkippedClasses += 1
        # End - for priorityLevel in range(numTrainingPriorities):

        if (numSkippedClasses >= tooManySkippedClasses):
            break
        patientIndexAtEachPriority += 1
    # End - while (True):

    tdfReader.Shutdown()


    # Just for kicks and grins, count how many patients we skipped.
    totalSkippedPatients = 0
    for priorityLevel in range(numTrainingPriorities):
        ptList = PatientsForTrainingPriority[priorityLevel]
        if (patientIndexAtEachPriority < len(ptList)):
            totalSkippedPatients += (len(ptList) - patientIndexAtEachPriority)
    # End - for priorityLevel in range(numTrainingPriorities):


    return job, numPatientsProcessed, totalSkippedPatients, numDataPointsProcessed, fEOF
# End - MLEngine_TrainOneFilePartitionImpl







################################################################################
#
# [MLEngine_TestOneFilePartitionImpl]
#
# This returns one value: fEOF
#   fEOF - True iff we hit the end of the file
#
################################################################################
def MLEngine_TestOneFilePartitionImpl(job, currentPartitionStart, currentPartitionStop, 
                                      localNeuralNet, fUsePytorch, cudaIsAvailable, gpuDevice):
    fDebug = False

    tdfFilePathName = job.GetDataParam("TestData", "")
    inputNameListStr = job.GetNetworkInputVarNames()
    resultValueName = job.GetNetworkOutputVarName()
    _, requirePropertyRelationList, requirePropertyNameList, requirePropertyValueList = job.GetFilterProperties()
    networkOutputDataType = job.GetResultValueType()

    # Pytorch wants data (NumSamples x NumBatches x NumFeatures) while
    # XGBoost wants data (NumSamples x NumFeatures)
    if (fUsePytorch):
        fAddMinibatchDimension = True
    else:
        fAddMinibatchDimension = False

    # Open the file in the worker address space
    tdfReader = tdf.TDF_CreateTDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                                            requirePropertyNameList)

    #######################################
    # This loop looks at each patient in the current partition
    # Unlike training, the order does not matter. The arrays are not changing
    # and We compute the accuracy for every patient, no matter the order.
    numPatientsProcessed = 0
    fFoundPatient, fEOF, _, _ = tdfReader.GotoFirstPatientInPartition(-1, -1, currentPartitionStart, currentPartitionStop)
    while ((not fEOF) and (fFoundPatient)):
        # Get all data points for a single patient. 
        numReturnedDataSets, inputArray, resultArray = tdfReader.GetDataForCurrentPatient(requirePropertyRelationList,
                                                                            requirePropertyNameList,
                                                                            requirePropertyValueList,
                                                                            fAddMinibatchDimension,
                                                                            False)  # fNormalize inmputs
        if (numReturnedDataSets >= 1):
            if (fDebug):
                print("MLEngine_TestOneFilePartitionImpl. numReturnedDataSets=" + str(numReturnedDataSets))
            MLEngine_TestGroupOfDataPoints(job, localNeuralNet, fUsePytorch, cudaIsAvailable, gpuDevice,
                                           inputArray, resultArray, 
                                           numReturnedDataSets, fAddMinibatchDimension, networkOutputDataType)
        # End - if (numReturnedDataSets >= 1):

        # Go to the next patient in this partition
        numPatientsProcessed += 1
        fFoundPatient, fEOF, _, _ = tdfReader.GotoNextPatientInPartition(-1, -1, currentPartitionStop)
    # End - while ((not fEOF) and (fFoundPatient)):

    tdfReader.Shutdown()

    return job, numPatientsProcessed, fEOF
# End - MLEngine_TestOneFilePartitionImpl






################################################################################
#
# [MLEngine_CreateNeuralNetFromJobSpec]
#
# Create the neural network in this address space.
################################################################################
def MLEngine_CreateNeuralNetFromJobSpec(job):
    valStr = job.GetNetworkType().lower()
    if (valStr == "simplenet"):
        localNeuralNet = MLEngine_SingleLayerNeuralNet(job)
    elif (valStr == "multilevelnet"):
        localNeuralNet = MLEngine_MultiLayerNeuralNet(job)
    elif (valStr == "lstm"):
        localNeuralNet = MLEngine_LSTMNeuralNet(job)
    elif (valStr == "xgboost"):
        localNeuralNet = MLEngine_XGBoostModel(job)
    else:
        return None

    # Restore the network matrices
    localNeuralNet.RestoreNetState(job)

    return localNeuralNet
# End - MLEngine_CreateNeuralNetFromJobSpec






################################################################################
#
# [MLEngine_CreateLossFunctionForJob]
#
# Create the neural network in this address space.
#
# For Regression:
#    torch.nn.L1Loss (L1 Loss - Mean Absolute Error) 
#           loss = AbsoluteVal(predict - actual) A V-shape
#
#    torch.nn.MSELoss (L2 Loss - Mean Squared Error) 
#           loss = (predict - actual)**2  An upward parabola
#
#    torch.nn.SmoothL1Loss - Smooth L1 Loss or also called Huber loss
#           loss = if Abs(actual - precict) < 1  ===>  0.5 * (predict - actual)**2
#           loss = otherwise  ===>  Abs(actual - precict) - 0.5
#
# For categorization:
#    nn.BCELoss (Binary Cross Entropy Loss, the output non-Linear of the network is nn.Sigmoid)
#           loss = -1 * SUM( actual * log(predicted) )
#           Input: (∗), where ∗ means any number of dimensions.
#           Output: scalar. If reduction is 'none', then (∗)(*)(∗), same shape as input
#
#    nn.NLLLoss (Negative Log Likelihood, the output non-Linear of the network is nn.LogSoftmax)
#           Input: (N,C) or (C), where C = number of classes
#           Output: If reduction is 'none', shape (N)(N)(N)
################################################################################
def MLEngine_CreateLossFunctionForJob(job):
    lossTypeStr = job.GetTrainingParamStr("LossFunction", "").lower()
    #print("lossTypeStr=" + lossTypeStr)

    if (lossTypeStr == "l1loss"):
        localLossFunction = nn.L1Loss()
        lossDimension = 2
    elif (lossTypeStr == "l2loss"):
        localLossFunction = nn.MSELoss()
        lossDimension = 2
    elif (lossTypeStr == "nllloss"):
        localLossFunction = nn.NLLLoss()
        lossDimension = 1
    elif (lossTypeStr == "crossentropyloss"):
        localLossFunction = torch.nn.CrossEntropyLoss()
        lossDimension = 1
    elif (lossTypeStr == "bceloss"):
        localLossFunction = nn.BCELoss()
        lossDimension = 2
    else:
        localLossFunction = None
        lossDimension = -1

    return localLossFunction, lossDimension
# End - MLEngine_CreateLossFunctionForJob






################################################################################
#
# [MLEngine_ReturnResultsFromChildProcess]
#
################################################################################
def MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, numPatientsProcessed, numSkippedPatients, numDataPointsProcessed,
                                            fEOF, startPosFirstPatientInPartition, stopPosLastPatientInPartition, 
                                            err,
                                            patientPositionList):
    resultDict = {'jobStr': "", 
                'numPatientsProcessed': numPatientsProcessed, 
                'numSkippedPatients': numSkippedPatients,
                'numDataPointsProcessed': numDataPointsProcessed,
                'fEOF': fEOF, 
                'startValidData': startPosFirstPatientInPartition, 
                'stopValidData': stopPosLastPatientInPartition, 
                'err': err, 
                'patientPositionList': patientPositionList}
    if (job is not None):
        resultDict['jobStr'] = job.WriteJobToString()

    sendPipeEnd.send(resultDict)

    sendPipeEnd.close()
# End - MLEngine_ReturnResultsFromChildProcess





################################################################################
#
# [MLEngine_PreflightOneFilePartitionInChildProcess]
#
# This runs in a worker process, which may be another process on the same machine
# or else a process on a remote server on the network.
# All inputs and outputs are passed as strings and integers.
# The job is serialized/deserialized as a string of XML text, so it can be passed
# as a parameter string, modified, then returned as a result string.
################################################################################
def MLEngine_PreflightOneFilePartitionInChildProcess(sendPipeEnd, jobStr, 
                                        partitionStartPosition, partitionStopPosition):
    #print("MLEngine_PreflightOneFilePartitionInChildProcess start.")
    #print("partitionStartPosition = " + str(partitionStartPosition))
    #print("partitionStopPosition = " + str(partitionStopPosition))
    global g_ChildProcessPipe
    g_ChildProcessPipe = sendPipeEnd

    # Regenerate the runtime job object from its serialized string form. 
    job = mlJob.MLJob_CreateMLJobFromString(jobStr)

    # This will overwrite patientPositionList.
    job, numPatientsProcessed, fEOF, startPosFirstPatient, stopPosLastPatient, patientPositionList = MLEngine_PreflightOneFilePartitionImpl(job, 
                                                                    partitionStartPosition, partitionStopPosition)

    # We build up a list of patient positions during preflight.
    # We reuse this list on all training epochs to quickly load patients.
    patientPositionListStr = json.dumps(patientPositionList)
    
    # Send the results back to the control process.
    MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, numPatientsProcessed, 0, 0, fEOF, 
                                           startPosFirstPatient, stopPosLastPatient,
                                           E_NO_ERROR, patientPositionListStr)
    ASSERT_IF((patientPositionListStr == ""), 
            "MLEngine_PreflightOneFilePartitionInChildProcess. BAD Patient Position List: " + str(patientPositionListStr))

    if (False):
        print("Num VancDoses Found During Parsing = " + str(tdf.TDF_GetDebugVal("ParsedVancDose")))
        print("      Num VancDoses Found Step 1 = " + str(tdf.TDF_GetDebugVal("FetchStep1VancDoses")))
        print("      Num VancDoses Found Step 2 = " + str(tdf.TDF_GetDebugVal("FetchStep2VancDoses")))
        print("      Num VancDoses Found Step 3 = " + str(tdf.TDF_GetDebugVal("FetchStep3VancDoses")))
        print("Num VancLevels Found During Parsing = " + str(tdf.TDF_GetDebugVal("ParsedVancLvl")))
        print("      Num VancLevels Found Step 1 = " + str(tdf.TDF_GetDebugVal("FetchStep1VancLvl")))
        print("      Num VancLevels Found Step 2 = " + str(tdf.TDF_GetDebugVal("FetchStep2VancLvl")))
        print("      Num VancLevels Found Step 3 = " + str(tdf.TDF_GetDebugVal("FetchStep3VancLvl")))
        print("      Num VancLevels Found Step 4 = " + str(tdf.TDF_GetDebugVal("FetchStep4VancLvl")))

    # Return and exit the process.
# End - MLEngine_PreflightOneFilePartitionInChildProcess






################################################################################
#
# [MLEngine_TrainOneFilePartitionInChildProcess]
#
# This runs in a worker process, which may be another process on the same machine
# or else a process on a remote server on the network.
# All inputs and outputs are passed as strings and integers.
# The job is serialized/deserialized as a string of XML text, so it can be passed
# as a parameter string, modified, then returned as a result string.
################################################################################
def MLEngine_TrainOneFilePartitionInChildProcess(sendPipeEnd, jobStr, epochNum,
                                                currentPartitionStart, currentPartitionStop):
    global g_ChildProcessPipe
    g_ChildProcessPipe = sendPipeEnd
    fDebug = False

    if (fDebug):
        print("MLEngine_TrainOneFilePartitionInChildProcess start.")
        print("     epochNum = " + str(epochNum))
        print("     currentPartitionStart = " + str(currentPartitionStart))
        print("     currentPartitionStop = " + str(currentPartitionStop))

    # Regenerate the runtime job object from its serialized string form. 
    job = mlJob.MLJob_CreateMLJobFromString(jobStr)

    job.RecordDebugEvent(mlJob.DEBUG_EVENT_TIMELINE_CHUNK)

    fAllowMultiplePartitions = True
    if (not job.TrainingCanPauseResume()):
        fAllowMultiplePartitions = False

    # Create the neural network in this address space.
    localNeuralNet = MLEngine_CreateNeuralNetFromJobSpec(job)
    if (localNeuralNet is None):
        if (fDebug):
            print("MLEngine_TrainOneFilePartitionInChildProcess Failed making neural net.")
        MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, 0, 0, 0, False, -1, -1, E_SERVER_ERROR, "")
        return
    elif (fDebug):
        print("MLEngine_TrainOneFilePartitionInChildProcess Made neural net.")

    # Many of the models are in Pytorch, but not all anymore, and some parts
    # of training and testing rely on the type of software used.
    fUsePytorch = False
    if (localNeuralNet.GetLibraryName() == "Pytorch"):
        fUsePytorch = True

    # Check if we can use the GPU.
    cudaIsAvailable = False
    gpuDevice = None
    if ((fUsePytorch) and (USE_GPU) and (job.OKToUseGPU())):
        cudaIsAvailable = torch.cuda.is_available()
        if (cudaIsAvailable):
            numGPUs = torch.cuda.device_count()
            if (numGPUs <= 0):
                cudaIsAvailable = False
        if (fDebug):
            print("cudaIsAvailable = " + str(cudaIsAvailable))
            print("numGPUs = " + str(numGPUs))
        if (cudaIsAvailable):
            gpuDevice = torch.device('cuda')
            if (gpuDevice is None):
                cudaIsAvailable = False
    # End - if (USE_GPU)

    if (cudaIsAvailable):
        localNeuralNet = localNeuralNet.to(gpuDevice)

    # Create the loss function in this address space.
    if (fUsePytorch):
        localLossFunction, lossDimension = MLEngine_CreateLossFunctionForJob(job)
        if ((localLossFunction is None) or (lossDimension < 0)):
            if (fDebug):
                print("MLEngine_TrainOneFilePartitionInChildProcess Error. Failed to make loss function.")
            MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, 0, 0, 0, False, -1, -1, E_SERVER_ERROR, "")
            return
    else:
        localLossFunction = None
        lossDimension = 0

    # If we are using Pytorch, create an optimizer. If there is none, then we can
    # explicitly apply the gradients ourselves. This latter approach is useful when using
    # multiple worker processes, because each process returns a gradient tensor.
    localOptimizer = None
    if (fUsePytorch):
        optimizerType = job.GetTrainingParamStr("Optimizer", "").lower()
        if (optimizerType == "sgd"):
            learningRate = float(job.GetTrainingParamStr("LearningRate", "0.1"))
            localOptimizer = optim.SGD(localNeuralNet.parameters(), lr=learningRate)
        elif (optimizerType == "adam"):
            learningRate = float(job.GetTrainingParamStr("LearningRate", "0.1"))
            weightDecay = 0
            localOptimizer = optim.Adam(localNeuralNet.parameters(), lr=learningRate, weight_decay=weightDecay)
        elif (optimizerType in ("", "none")):
            localOptimizer = None
        else:
            MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, 0, 0, 0, False, -1, -1, E_SERVER_ERROR, "")
            return
    # End - if (fUsePytorch):

    # Restore the state of the optimizer. This was saved by the
    # previous child process when it completed.
    if ((fAllowMultiplePartitions) and (localOptimizer is not None)):
        valStr = job.GetNamedStateAsStr(mlJob.RUNTIME_OPTIMIZER_STATE, "")
        if (valStr != ""):
            stateBytes = bytearray.fromhex(valStr)
            ioBuffer = io.BytesIO(stateBytes)
            stateDict = torch.load(ioBuffer)
            localOptimizer.load_state_dict(stateDict)
        # End - if (valStr != ""):
    # End - if (localOptimizer is not None):

    # Do the actual work. 
    job, numPatientsProcessed, totalSkippedPatients, numDataPointsProcessed, fEOF = MLEngine_TrainOneFilePartitionImpl(job, 
                                                                currentPartitionStart, currentPartitionStop,
                                                                localNeuralNet, localLossFunction, localOptimizer,
                                                                fUsePytorch, cudaIsAvailable, gpuDevice)

    # Save the updated weights to the job, for later use.
    if (cudaIsAvailable):
        # Map net back to the CPU device so we can save its state to the Job
        # We only do this for training, not testing, because only training will
        # read the updated network matrices and save those back to the Job.
        localNeuralNet = localNeuralNet.cpu()

    localNeuralNet.SaveNeuralNetstate(job)
    valStr = ""
    if (localOptimizer is not None):
        valDict = localOptimizer.state_dict()
        ioBuffer = io.BytesIO()
        torch.save(valDict, ioBuffer)
        bufferBytes = ioBuffer.getvalue()
        # Convert the binary data to a series of hex chars, which is a string
        # Functions like stateBytes.decode("utf-8") do not work.
        valStr = bufferBytes.hex()
    # End - if (localOptimizer is not None):
    job.SetNamedStateAsStr(mlJob.RUNTIME_OPTIMIZER_STATE, valStr)

    # Send the results back to the control process.
    MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, numPatientsProcessed, totalSkippedPatients, numDataPointsProcessed,
                                            fEOF, currentPartitionStart, currentPartitionStop,
                                            E_NO_ERROR, "")

    if (fDebug):
        print("MLEngine_TrainOneFilePartitionInChildProcess done, and exiting")

    # Return and exit the process.
# End - MLEngine_TrainOneFilePartitionInChildProcess







################################################################################
#
# [MLEngine_TestOneFilePartitionInChildProcess]
#
# This runs in a worker process, which may be another process on the same machine
# or else a process on a remote server on the network.
# All inputs and outputs are passed as strings and integers.
# The job is serialized/deserialized as a string of XML text, so it can be passed
# as a parameter string, modified, then returned as a result string.
################################################################################
def MLEngine_TestOneFilePartitionInChildProcess(sendPipeEnd, jobStr, currentPartitionStart,
                                                currentPartitionStop):
    global g_ChildProcessPipe
    g_ChildProcessPipe = sendPipeEnd
    numPatientsProcessed = 0
    fEOF = False

    # Regenerate the runtime job object from its serialized string form. 
    job = mlJob.MLJob_CreateMLJobFromString(jobStr)

    # Create the neural network in this address space.
    localNeuralNet = MLEngine_CreateNeuralNetFromJobSpec(job)
    if (localNeuralNet is None):
        MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, 0, 0, 0, False, -1, -1, E_SERVER_ERROR, "")
        return

    # Many of the models are in Pytorch, but not all anymore, and some parts
    # of training and testing rely on the type of software used.
    fUsePytorch = False
    if (localNeuralNet.GetLibraryName() == "Pytorch"):
        fUsePytorch = True

    # Check if we can use the GPU.
    cudaIsAvailable = False
    gpuDevice = None
    if ((fUsePytorch) and (USE_GPU) and (job.OKToUseGPU())):
        cudaIsAvailable = torch.cuda.is_available()
        if (cudaIsAvailable):
            numGPUs = torch.cuda.device_count()
            if (numGPUs <= 0):
                cudaIsAvailable = False
        if (cudaIsAvailable):
            gpuDevice = torch.device('cuda')
            if (gpuDevice is None):
                cudaIsAvailable = False
    # End - if (USE_GPU)

    if (cudaIsAvailable):
        localNeuralNet = localNeuralNet.to(gpuDevice)

    # Do the actual work
    job, numPatientsProcessed, fEOF = MLEngine_TestOneFilePartitionImpl(job, currentPartitionStart, 
                                                                        currentPartitionStop, localNeuralNet,
                                                                        fUsePytorch, cudaIsAvailable, gpuDevice)

    MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, numPatientsProcessed, 0, 0, fEOF, -1, -1, E_NO_ERROR, "")

    # Return and exit the process.
# End - MLEngine_TestOneFilePartitionInChildProcess







################################################################################
#
# [MLEngine_PreflightNeuralNet]
#
################################################################################
def MLEngine_PreflightNeuralNet(job, partitionSize):
    fDebug = False
    if (fDebug):
        print("=======================\nPreflight:")

    # Before training, do the preflight
    job.StartPreflight()

    # Get a dictionary of partitions for the file.
    # Initially, this dictionary is in order, so the nth entry in the dictionary is
    # the nth partition, and adjacent entries are adjacent in the file. We will first go
    # through the file in this sequence, but shuffle it on later epochs.
    trainTDFFilePathName = job.GetDataParam("TrainData", "")
    partitionList = tdf.CreateFilePartitionList(trainTDFFilePathName, partitionSize)

    #######################################
    # This loop looks at each partition in the file. One partition is 
    # a large chunk of data and may contain many patients.
    partitionCount = 0
    nextPartitionStartPosition = -1
    for partitionInfo in partitionList:
        # If we shifted the previous partition, then adjust the current partition
        # to start after the shifted previous partition.
        if (nextPartitionStartPosition > 0):
            partitionInfo['start'] = nextPartitionStartPosition
            partitionInfo['stop'] = nextPartitionStartPosition + partitionSize

        # Get information about the current file Partition.
        currentPartitionStart = partitionInfo['start']
        currentPartitionStop = partitionInfo['stop']

        # Make a pipe that will be used to return the results. 
        recvPipeEnd, sendPipeEnd = multiprocessing.Pipe(False)

        # Prepare the arguments to go to the worker process.
        # This may be another process on this machine or else a remote process on another server.
        jobStr = job.WriteJobToString()
        #print("MLEngine_PreflightNeuralNet jobStr=" + str(jobStr))

        # Fork the job process.
        processInfo = Process(target=MLEngine_PreflightOneFilePartitionInChildProcess, args=(sendPipeEnd, jobStr, 
                                                                     currentPartitionStart, currentPartitionStop))
        processInfo.start()

        # Get the results.
        resultDict = recvPipeEnd.recv()

        jobStr = resultDict['jobStr']
        job.ReadJobFromString(jobStr)
        stopValidData = resultDict['stopValidData']
        patientPositionListStr = resultDict['patientPositionList']
        ASSERT_IF((patientPositionListStr == ""), 
            "MLEngine_PreflightNeuralNet. BAD Patient Position List patientPositionListStr: " + str(patientPositionListStr))

        # Wait for the process to complete.
        processInfo.join()

        # Update the data to show where this ends, and where to find all patients in this partition.
        partitionInfo['stop'] = stopValidData
        partitionInfo['ptListStr'] = patientPositionListStr

        # The next position will start immediately after this one ends.
        nextPartitionStartPosition = stopValidData

        partitionCount += 1
        if ((DD_DEBUG_TRUNCATE_PREFLIGHT) and (partitionCount >= DD_DEBUG_TRUNCATE_NUM_PARTITIONS)):
            break
    # End - for partitionInfo in partitionList:

    job.FinishPreflight()

    # Return the updated job that has been changed by the child processes.
    return job, partitionList
# End - MLEngine_PreflightNeuralNet()







################################################################################
#
# [MLEngine_TrainNeuralNet]
#
################################################################################
def MLEngine_TrainNeuralNet(job, fSimulation, partitionSize):
    fDebug = False
    childProcessErr = E_NO_ERROR

    MLEngine_Init_GPU()

    # Get a dictionary of partitions for the file.
    # Initially, this dictionary is in order, so the nth entry in the dictionary is
    # the nth partition, and adjacent entries are adjacent in the file. We will first go
    # through the file in this sequence, but may shuffle it on later epochs.
    job, partitionList = MLEngine_PreflightNeuralNet(job, partitionSize)

    # Return the updated job that has been changed by the child processes.
    if (fSimulation):
        return job

    print("=======================\nTraining:")
    job.StartTraining()

    numEpochs = job.GetTrainingParamInt("NumEpochs", 1)

    #######################################
    # TRAINING - Iterate once for each Epoch
    for epochNum in range(numEpochs):
        #print("\n\n\n\n============================================================\n\n\n\n")
        job.StartTrainingEpoch()
        job.RecordDebugEvent(mlJob.DEBUG_EVENT_TIMELINE_EPOCH)
        
        #######################################
        # This loop looks at each partition in the file. One partition is 
        # a large chunk of data and may contain many patients.
        partitionCount = 0
        for partitionInfo in partitionList:
            # Get information about the current file Partition.
            # On the first epoch, this is still being updated as we find the patient boundaries in the file.
            currentPartitionStart = partitionInfo['start']
            currentPartitionStop = partitionInfo['stop']
            #patientPositionListStr = partitionInfo['ptListStr']

            # Make a pipe that will be used to return the results. 
            recvPipeEnd, sendPipeEnd = multiprocessing.Pipe(False)

            # Prepare the arguments to go to the worker process.
            # This may be another process on this machine or else a remote process on another server.
            jobStr = job.WriteJobToString()

            # Fork the job process.
            processInfo = Process(target=MLEngine_TrainOneFilePartitionInChildProcess, args=(sendPipeEnd, jobStr, 
                                                        epochNum, currentPartitionStart, currentPartitionStop))
            processInfo.start()

            # Get the results.
            resultDict = recvPipeEnd.recv()
            if (fDebug):
                print("MLEngine_TrainNeuralNet. Got result back from child process")

            numPatientsProcessed = resultDict['numPatientsProcessed']
            numSkippedPatients = resultDict['numSkippedPatients']
            numDataPointsProcessed = resultDict['numDataPointsProcessed']
            childProcessErr = resultDict['err']
            jobStr = resultDict['jobStr']
            if ((jobStr is not None) and (jobStr != "")):
                job.ReadJobFromString(jobStr)
            if (fDebug):
                print("MLEngine_TrainNeuralNet. numPatientsProcessed=" + str(numPatientsProcessed))

            # Wait for the process to complete.
            processInfo.join()
            if (fDebug):
                print("MLEngine_TrainNeuralNet. join finished")

            if (childProcessErr == E_ASSERT_ERROR):
                break

            # Update the results. These are (roughly) the same for each Epoch, so we only update
            # it once, on the first Epoch.
            if (epochNum == 0):
                job.SetNumPatientsTrainedPerEpoch(job.GetNumPatientsTrainedPerEpoch() + numPatientsProcessed)
                job.SetNumPatientsSkippedPerEpoch(job.GetNumPatientsSkippedPerEpoch() + numSkippedPatients)
                job.SetNumDataPointsPerEpoch(job.GetNumDataPointsPerEpoch() + numDataPointsProcessed)

            partitionCount += 1
            if ((DD_DEBUG_TRUNCATE_TRAINING) and (partitionCount >= DD_DEBUG_TRUNCATE_NUM_PARTITIONS)):
                print("Truncating training")
                break
        # End - for partitionInfo in partitionList:

        job.FinishTrainingEpoch()
        
        # Some models (like XGBoost) cannot train different data at different times.
        # In these cases, we can only do 1 Epoch, and we try to process all data as a single partition.
        if (not job.TrainingCanPauseResume()):
            break

        # At the end of each partition, shuffle the partition list so we will
        # train the data in a different order on the next epoch.
        if (not DD_DEBUG):
            if (not job.IsTrainingOptionSet("NoShuffle")):
                random.shuffle(partitionList)

        if ((childProcessErr == E_ASSERT_ERROR) or (DD_DEBUG_TRUNCATE_TRAINING)):
            break
    # End - for epochNum in range(numEpochs):


    # Return the updated job that has been changed by the child processes.
    return job, childProcessErr
# End - MLEngine_TrainNeuralNet()





################################################################################
#
# [MLEngine_TestNeuralNet]
#
################################################################################
def MLEngine_TestNeuralNet(job, partitionSize):
    #print("MLEngine_TestNeuralNet. Start Testing:")
    MLEngine_Init_GPU()

    job.StartTesting()

    #######################################
    # This loop looks at each partition in the file. One partition is 
    # a large chunk of data and may contain many patients.
    fEOF = False
    currentPartitionStart = 0
    currentPartitionStop = currentPartitionStart + partitionSize
    partitionCount = 0
    while (not fEOF):
        job.LogMsg("Start Partition. StartPos=" + str(currentPartitionStart))

        # Make a pipe that will be used to return the results. 
        recvPipeEnd, sendPipeEnd = multiprocessing.Pipe(False)

        # Prepare the arguments to go to the worker process.
        # This may be another process on this machine or else a remote process on another server.
        jobStr = job.WriteJobToString()
        #print("MLEngine_TestNeuralNet jobStr=" + str(jobStr))

        # Fork the job process.
        processInfo = Process(target=MLEngine_TestOneFilePartitionInChildProcess, args=(sendPipeEnd, jobStr, 
                                                    currentPartitionStart, currentPartitionStop))
        processInfo.start()

        # Get the results.
        resultDict = recvPipeEnd.recv()
        fEOF = resultDict['fEOF']
        jobStr = resultDict['jobStr']
        job.ReadJobFromString(jobStr)

        # Wait for the process to complete.
        processInfo.join()

        # Go to the next partition
        currentPartitionStart = currentPartitionStop
        currentPartitionStop = currentPartitionStart + partitionSize

        partitionCount += 1
        if ((DD_DEBUG_TRUNCATE_TESTING) and (partitionCount >= DD_DEBUG_TRUNCATE_NUM_PARTITIONS)):
            break
    # End - while (not fEOF):

    # Return the updated job that has been changed by the child processes.
    return job
# End - MLEngine_TestNeuralNet()






################################################################################
#
# [MLEngine_RunJob]
#
# Train and test a job.
################################################################################
def MLEngine_RunJob(jobFilePathName, trainedJobFilePathName, fDebug):
    err = E_NO_ERROR

    # Open the job.
    jobErr, job = mlJob.MLJob_ReadExistingMLJob(jobFilePathName)
    if (mlJob.JOB_E_NO_ERROR != jobErr):
        print("MLEngine_RunJob. Error making network")
        return

    #job.SetLogFilePathname("/home/ddean/ddRoot/logs/mlTrainTest-", True)
    job.SetDebug(fDebug)

    MLEngine_Init_GPU()

    # Initialize the engine.
    job.StartJobExecution()

    # TODO: Make this a calculated value, depending on the memory size of the machine
    partitionSize = PARTITION_SIZE

    trainTDFFilePathName = job.GetDataParam("TrainData", "")
    #print("MLEngine_Train. trainedFilePathName=" + str(trainedFilePathName))
    if (trainTDFFilePathName != ""):
        # Some models (like XGBoost) cannot train different data at different times.
        # In these cases, we can only do 1 Epoch, and we try to process all data as a single partition.
        if (not job.TrainingCanPauseResume()):
            try:
                fileInfo = os.stat(trainTDFFilePathName)
                partitionSize = fileInfo.st_size
            except Exception:
                partitionSize = PARTITION_SIZE

        job, err = MLEngine_TrainNeuralNet(job, False, partitionSize)
    # End - if (trainTDFFilePathName != ""):

    if (err == E_NO_ERROR):
        testTDFFilePathName = job.GetDataParam("TestData", "")
        if (testTDFFilePathName != ""):
            job = MLEngine_TestNeuralNet(job, PARTITION_SIZE)

    job.FinishJobExecution(err, " ")

    if ((trainedJobFilePathName is not None) 
            and (trainedJobFilePathName != "")):
        job.SaveAs(trainedJobFilePathName)

    JobShow.JobShow_WriteReport(job, JobShow.MLJOB_CONSOLE_REPORT, "")
    JobShow.JobShow_WriteReport(job, JobShow.MLJOB_LOG_REPORT, "")
    #JobShow.JobShow_WriteReport(job, MLJOB_FILE_REPORT, "/home/ddean/ddRoot/trainingResults.txt")
    #JobShow.JobShow_WriteReport(job, MLJOB_FILE_REPORT, "/home/ddean/ddRoot/trainingResults.csv")
# End - MLEngine_RunJob




