################################################################################
# 
# Copyright (c) 2020-2024 Dawson Dean
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
# In a sense, this is the interpreter for the job object. It does the actual
# work of running a neural network that is described in the Job object.
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

# Multiprocessing
from torch.multiprocessing import Process
import multiprocessing

import numpy as np

# Pytorch
import torch
import torch.nn as nn
import torch.optim as optim

# This file runs in the lib directory, so it does not need any special path to find 
# any other files in the lib dir.
import xmlTools as dxml
import tdfTools as tdf
import mlJob as mlJob
import jobShow as JobShow

torch.manual_seed(1)

DEFAULT_PARTITION_SIZE = 20 * (1024 * 1024)
USE_GPU = False

###############################
# Repairing Matrices
# Once a number gets really small, just set it to 0. Otherwise, it will shrink and shrink
# until it underflows.
REPAIR_MATRICES_DURING_VALIDATION = True
MIN_VALID_RESULT_VALUE = 1.0E-8
MAX_VALID_RESULT_VALUE = 1.0E8
MIN_VALID_MATRIX_VALUE = 1.0E-8
MAX_VALID_MATRIX_VALUE = 1.0E8
LARGE_REASONABLE_MATRIX_VALUE = 1.0E8

# We have a different checksum for saving or validating.
# The save checksum makes sure that we save/restore the neural net correctly,
# while the validate chesum ensures each forward/backward propagate does some
# useful work. To keep these two separate, we use different names for the checksums.
g_SaveChecksumPrefix = "SAVE_"

DEFAULT_MAX_SKIPPED_DAYS_IN_SAME_SEQUENCE = 4



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

NETWORK_MIXED_ANALOG_DIGITAL_ELEMENT_NAME = "MixAnalogDigital"

# RNN
RECURRENT_STATE_LINEAR_UNIT_NAME    = "ReccurentStateLinearUnit"

# LSTM
LSTM_SAVED_STATE_NAME               = "LSTMState"
LSTM_LINEAR_UNIT_SAVED_STATE_NAME   = "LSTMLinearUnit"

# Debugging only
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
    fKillProcessOnAsserts = True
    fQuitButKeepRunningOnAsserts = False

    print("ERROR! " + messageStr)
    if (fKillProcessOnAsserts):
        print("Exiting process...")
        raise Exception()
    elif (fQuitButKeepRunningOnAsserts):
        if (g_ChildProcessPipe is not None):
            MLEngine_ReturnResultsFromChildProcess(g_ChildProcessPipe, None, -1, -1, 0,
                                                    True, -1, -1, E_ASSERT_ERROR, -1)
# End - ASSERT_ERROR



################################################################################
################################################################################
def ASSERT_IF(fCondition, messageStr):
    if (fCondition):
        ASSERT_ERROR(messageStr)
# End - ASSERT_IF



################################################################################
#
# [MLEngine_SaveLinearUnitToJob]
#
################################################################################
def MLEngine_SaveLinearUnitToJob(linearUnit, job, name):
    fDebug = False
    if (fDebug):
        print("MLEngine_SaveLinearUnitToJob. name=" + name)

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
    if (fDebug):
        print("MLEngine_ReadLinearUnitFromJob. name=" + name)

    fFoundIt, weightMatrix, biasVector = job.GetLinearUnitMatrices(name)
    if (not fFoundIt):
        if (fDebug):
            print("MLEngine_ReadLinearUnitFromJob. Error! Not found")
        return None

    # WARNING!!!!
    # Leave these as float32. Changing them to 64 will cause the checksum code to
    # compute different checksums for Linear Units when they are restored by this
    # routine compare to when they are initialized.
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
# [MLEngine_SimpleCheckArray]
#
# inputArray is a numpy array, and may be 1, 2, or 3 dimensional.
################################################################################
def MLEngine_SimpleCheckArray(linearUnit, name):
    fValid = True
    fAbortOnError = False

    # Must call clone() to force the data structures to get the latest version of the data
    # The optimizer seems to play games with multiple versions
    weightMatrix = linearUnit.weight.clone().detach().numpy()
    biasVector = linearUnit.bias.clone().detach().numpy()

    if (np.isnan(weightMatrix).any()):
        print("ERROR!:\nMLEngine_SimpleCheckArray passed an Invalid Matrix")
        fValid = False

    if (np.isnan(biasVector).any()):
        print("ERROR!:\nMLEngine_SimpleCheckArray passed an Invalid Bias Vector")
        fValid = False

    if (not fValid):
        print("    name = " + str(name))
        print("    weightMatrix = " + str(weightMatrix))
        print("    biasVector = " + str(biasVector))
        if (fAbortOnError):
            print("Exiting process...")
            raise Exception()

    return fValid
# End - MLEngine_SimpleCheckArray





################################################################################
#
# [MLEngine_FullCheckLinearUnit]
#
# linearUnit is a Tensor and may be 1, 2, or 3 dimensional.
################################################################################
def MLEngine_FullCheckLinearUnit(linearUnit, unitName):
    fValid = True
    fDebug = False

    arrayDimList = linearUnit.weight.shape
    numDimensions = len(arrayDimList)
    numDataSamples = arrayDimList[0]
    if (fDebug):
        print("MLEngine_FullCheckLinearUnit")
        print("     linearUnit = " + str(linearUnit))
        print("     type(linearUnit) = " + str(type(linearUnit)))
        print("     arrayDimList = " + str(arrayDimList))
        print("     numDimensions = " + str(numDimensions))
        print("     numDataSamples = " + str(numDataSamples))

    # Must call clone() to force the data structures to get the latest version of the data
    # The optimizer seems to play games with multiple versions
    weightMatrix = linearUnit.weight.clone().detach().numpy()
    biasVector = linearUnit.bias.clone().detach().numpy()

    for inputVecNum in range(numDataSamples):
        if (numDimensions == 3):
            vec = weightMatrix[inputVecNum][0]
        else:
            vec = weightMatrix[inputVecNum]

        for valIndex, currentVal in enumerate(vec):
            if ((math.isnan(currentVal)) 
                    or (currentVal > MAX_VALID_MATRIX_VALUE)
                    or (currentVal < -MAX_VALID_MATRIX_VALUE)
                    or ((currentVal > 0) and (currentVal < MIN_VALID_MATRIX_VALUE)) 
                    or ((currentVal < 0) and (currentVal > -MIN_VALID_MATRIX_VALUE))):
                if (currentVal == tdf.TDF_INVALID_VALUE):
                    continue

                if (fDebug):
                    print("\n\n\n MLEngine_FullCheckLinearUnit in Matrix. Found bad value")
                    print("   inputVecNum = " + str(inputVecNum) + ", valIndex = " + str(valIndex))

                fValid = False
                break
        # End - for currentValEntry in vec:

        if (not fValid):
            break
    # End - for inputVecNum in range(numDataSamples):

    if (fValid):
        for valIndex, currentVal in enumerate(biasVector):
            if ((math.isnan(currentVal)) 
                    or (currentVal > MAX_VALID_MATRIX_VALUE)
                    or (currentVal < -MAX_VALID_MATRIX_VALUE)
                    or ((currentVal > 0) and (currentVal < MIN_VALID_MATRIX_VALUE)) 
                    or ((currentVal < 0) and (currentVal > -MIN_VALID_MATRIX_VALUE))):
                if (currentVal != tdf.TDF_INVALID_VALUE):
                    continue

                if (fDebug):
                    print("\n\n\n MLEngine_FullCheckLinearUnit in biasVector. Found bad value")
                    print("   biasVector = " + str(biasVector))
                    print("   valIndex = " + str(valIndex) + ", currentVal = " + str(currentVal))

                fValid = False
                break
        # End - for valIndex, currentVal in enumerate(biasVector):
    # End - if (fValid)

    return fValid, weightMatrix, biasVector, arrayDimList, numDimensions, numDataSamples
# End - MLEngine_FullCheckLinearUnit






################################################################################
#
# [MLEngine_RepairLinearUnit]
#
# linearUnit is a Tensor and may be 1, 2, or 3 dimensional.
################################################################################
def MLEngine_RepairLinearUnit(weightMatrix, biasVector, arrayDimList, numDimensions, numDataSamples):
    fDebug = False
    fRepaired = True
                    
    if (fDebug):
        print("MLEngine_RepairLinearUnit")
        print(" weightMatrix = " + str(weightMatrix))
        print(" type(weightMatrix) = " + str(type(weightMatrix)))
        print(" biasVector = " + str(biasVector))
        print(" type(biasVector) = " + str(type(biasVector)))
        print(" arrayDimList = " + str(arrayDimList))
        print(" numDimensions = " + str(numDimensions))
        print(" numDataSamples = " + str(numDataSamples))


    for inputVecNum in range(numDataSamples):
        if (numDimensions == 3):
            vec = weightMatrix[inputVecNum][0]
        else:
            vec = weightMatrix[inputVecNum]

        for valIndex, currentVal in enumerate(vec):
            if (currentVal == tdf.TDF_INVALID_VALUE):
                continue
            elif ((math.isnan(currentVal)) or (currentVal > MAX_VALID_MATRIX_VALUE)):
                if (numDimensions == 3):
                    weightMatrix[inputVecNum][0][valIndex] = LARGE_REASONABLE_MATRIX_VALUE
                else:
                    weightMatrix[inputVecNum][valIndex] = LARGE_REASONABLE_MATRIX_VALUE                    
                if (fDebug):
                    print(">>>>>>>>>>>>>>>>>> MLEngine_RepairLinearUnit. Set value to LARGE_REASONABLE_MATRIX_VALUE")
                    print("    inputVecNum = " + str(inputVecNum) + ", valIndex = " + str(valIndex))
                    print("    vec = " + str(vec))
                    print("    weightMatrix = " + str(weightMatrix))
            elif (currentVal < -MAX_VALID_MATRIX_VALUE):
                if (numDimensions == 3):
                    weightMatrix[inputVecNum][0][valIndex] = -LARGE_REASONABLE_MATRIX_VALUE
                else:
                    weightMatrix[inputVecNum][valIndex] = -LARGE_REASONABLE_MATRIX_VALUE                    
                if (fDebug):
                    print(">>>>>>>>>>>>>>>>>> MLEngine_RepairLinearUnit. Set value to -LARGE_REASONABLE_MATRIX_VALUE")
                    print("    inputVecNum = " + str(inputVecNum) + ", valIndex = " + str(valIndex))
                    print("    vec = " + str(vec))
                    print("    weightMatrix = " + str(weightMatrix))
            elif (((currentVal > 0) and (currentVal < MIN_VALID_MATRIX_VALUE)) 
                    or ((currentVal < 0) and (currentVal > -MIN_VALID_MATRIX_VALUE))):
                if (numDimensions == 3):
                    weightMatrix[inputVecNum][0][valIndex] = 0.0
                else:
                    weightMatrix[inputVecNum][valIndex] = 0.0
                if (fDebug):
                    print(">>>>>>>>>>>>>>>>>> MLEngine_RepairLinearUnit. Set value to 0.0")
                    print("    inputVecNum = " + str(inputVecNum) + ", valIndex = " + str(valIndex))
                    print("    vec = " + str(vec))
                    print("    weightMatrix = " + str(weightMatrix))
        # End - for currentValEntry in vec:
    # End - for inputVecNum in range(numDataSamples):

    for valIndex, currentVal in enumerate(biasVector):
        if (currentVal != tdf.TDF_INVALID_VALUE):
            continue
        elif ((math.isnan(currentVal)) or (currentVal > MAX_VALID_MATRIX_VALUE)):
            biasVector[valIndex] = LARGE_REASONABLE_MATRIX_VALUE
            if (fDebug):
                print(">>>>>>>>>>>>>>>>>> MLEngine_RepairLinearUnit. Set biasVector value to LARGE_REASONABLE_MATRIX_VALUE")
                print("    inputVecNum = " + str(inputVecNum) + ", valIndex = " + str(valIndex))
                print("    biasVector = " + str(biasVector))
        elif (currentVal < -MAX_VALID_MATRIX_VALUE):
            biasVector[valIndex] = -LARGE_REASONABLE_MATRIX_VALUE
            if (fDebug):
                print(">>>>>>>>>>>>>>>>>> MLEngine_RepairLinearUnit. Set biasVector value to -LARGE_REASONABLE_MATRIX_VALUE")
                print("    inputVecNum = " + str(inputVecNum) + ", valIndex = " + str(valIndex))
                print("    biasVector = " + str(biasVector))
        elif (((currentVal > 0) and (currentVal < MIN_VALID_MATRIX_VALUE)) 
                or ((currentVal < 0) and (currentVal > -MIN_VALID_MATRIX_VALUE))):
            biasVector[valIndex] = 0.0
            if (fDebug):
                print(">>>>>>>>>>>>>>>>>> MLEngine_RepairLinearUnit. Set value biasVector to 0.0")
                print("    inputVecNum = " + str(inputVecNum) + ", valIndex = " + str(valIndex))
                print("    biasVector = " + str(biasVector))
    # End - for valIndex, currentVal in enumerate(biasVector):


    # WARNING!!!!
    # Leave these as float32. Changing them to 64 will cause the checksum code to
    # compute different checksums for Linear Units when they are restored by this
    # routine compare to when they are initialized.
    weightTensor = torch.tensor(weightMatrix, dtype=torch.float32)
    biasTensor = torch.tensor(biasVector, dtype=torch.float32)
    weightSize = weightTensor.size()
    inputSize = weightSize[1]
    outputSize = weightSize[0]

    linearUnit = nn.Linear(inputSize, outputSize)
    linearUnit.weight = torch.nn.Parameter(weightTensor)
    linearUnit.bias = torch.nn.Parameter(biasTensor)
    if (fDebug):
        print(">>>>>>>>>>>>>>>>>> MLEngine_RepairLinearUnit. Done")
        print("    linearUnit.weight = " + str(linearUnit.weight))
        print("    linearUnit.bias = " + str(linearUnit.bias))

    return fRepaired, linearUnit
# End - MLEngine_RepairLinearUnit






################################################################################
#
# [MLEngine_SetArrayChecksum]
#
# inputArray is a numpy array, and may be 1, 2, or 3 dimensional.
################################################################################
def MLEngine_SetArrayChecksum(job, linearUnit, hashName):
    fDebug = False
    if (fDebug):
        print("MLEngine_SetArrayChecksum. hashName=" + hashName)

    # Must call clone() to force the data structures to get the latest version of the data
    # The optimizer seems to play games with multiple versions
    weightMatrix = linearUnit.weight.clone().detach().numpy()
    #biasVector = linearUnit.bias.clone().detach().numpy()

    job.SetArrayChecksum(weightMatrix, hashName)
# End - MLEngine_SetArrayChecksum




################################################################################
#
# [MLEngine_ArrayChecksumEqual]
#
################################################################################
def MLEngine_ArrayChecksumEqual(job, linearUnit, hashName, fExpectEqual):
    # Must call clone() to force the data structures to get the latest version of the data
    # The optimizer seems to play games with multiple versions
    weightMatrix = linearUnit.weight.clone().detach().numpy()
    #biasVector = linearUnit.bias.clone().detach().numpy()

    isEqual = job.CompareArrayChecksum(weightMatrix, hashName)
    if ((not isEqual) and (fExpectEqual)):
        print("MLEngine_ArrayChecksumEqual. Fail equality check when it was expected")
        print("    hashName = " + hashName)
        print("    weightMatrix = " + str(weightMatrix))
        ASSERT_ERROR("MLEngine_ArrayChecksumEqual. Fail equality check when it was expected")

    return isEqual
# End - MLEngine_ArrayChecksumEqual





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

        self.isLogistic = job.GetIsLogisticNetwork()

        inputNameListStr = job.GetNetworkInputVarNames()
        inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
        self.NumInputVars = len(inputNameList)

        resultValueName = job.GetNetworkOutputVarName()
        if (self.isLogistic):
            self.NumOutputCategories = 1
        else:
            self.NumOutputCategories = tdf.TDF_GetNumClassesForVariable(resultValueName)

        # Create the matrix of weights.
        # A nn.Linear is an object that contains a matrix A and bias vector b
        # It is used to compute (x * A-transpose) + b
        #    where x is the input, which is a vector with shape (1 x self.NumInputVars)
        #    or x is alternatively described as (rows=1, colums=self.NumInputVars). 
        #
        # The values are initialized from U(−k,k)U(−k​,k​), where k=in_features
        # The values are initialized from U(−k,k)U(−k​,k​) where k=in_features
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
    def forward(self, job, numDataSamples, inputTensor, trueResultTensor, dayNumArray, 
                fAddMinibatchDimension, maxDaysWithZeroValue):
        output = self.inputToOutput(inputTensor)
        return numDataSamples, output, trueResultTensor, None
    # End - forward



    #####################################################
    # [MLEngine_SingleLayerNeuralNet.SaveNeuralNetstate]
    #####################################################
    def SaveNeuralNetstate(self, job):
        # Save the matrix itself to the job.
        MLEngine_SaveLinearUnitToJob(self.inputToOutput, job, "inputToOutput")

        # Debug: Save a checksum of the first matrix
        if (not job.ChecksumExists("SimInMatInit")):
            MLEngine_SetArrayChecksum(job, self.inputToOutput, "SimInMatInit")
        else:
            if (MLEngine_ArrayChecksumEqual(job, self.inputToOutput, "SimInMatInit", False)):
                #ASSERT_ERROR("Save a matrix checksum that is same as initial")
                pass

        # Now save a checksum of the latest matrix.
        MLEngine_SetArrayChecksum(job, self.inputToOutput, "SimpleNetInputMatrix")
        if (not MLEngine_ArrayChecksumEqual(job, self.inputToOutput, "SimpleNetInputMatrix", True)):
            ASSERT_ERROR("Failed to save a matrix checksum")
    # End - SaveNeuralNetstate



    #####################################################
    #
    # [MLEngine_SingleLayerNeuralNet.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        fDebug = False
        if (fDebug):
            print("MLEngine_SingleLayerNeuralNet.RestoreNetState")

        # Read the matrix from the job
        restoredTensor = MLEngine_ReadLinearUnitFromJob(job, "inputToOutput")
        # We always try to restore, so will also restore even on the first time
        # we used the matrix. In that case, there is no saved state.
        if (restoredTensor is not None):
            self.inputToOutput = restoredTensor
            if (not MLEngine_ArrayChecksumEqual(job, self.inputToOutput, "SimpleNetInputMatrix", True)):
                print("MLEngine_SingleLayerNeuralNet. Fail Assert. Failed to correctly restore a neural net state")
                ASSERT_ERROR("Failed to save a matrix checksum: " + "inputToOutput")
    # End - RestoreNetState


    #####################################################
    #
    # MLEngine_SingleLayerNeuralNet.ValidateAndFixModel
    #
    # Make sure that backprop correctly updated the local network 
    #####################################################
    def ValidateAndFixModel(self, job, loss, predictionTensor, trueResultTensor):
        fValid = True

        if (REPAIR_MATRICES_DURING_VALIDATION):
            fValid, weightMatrix, biasVector, arrayDimList, numDimensions, numDataSamples = MLEngine_FullCheckLinearUnit(self.inputToOutput, 
                                                                                                                    "SimpleNetInputMatrix")
            if (not fValid):
                fValid, repairedLinearUnit = MLEngine_RepairLinearUnit(weightMatrix,
                                                  biasVector, arrayDimList, numDimensions, numDataSamples)
                if (fValid):
                    self.inputToOutput = repairedLinearUnit
                else:
                    ASSERT_ERROR("MLEngine_SingleLayerNeuralNet: Cannot repair SimpleNetInputMatrix")
                    return fValid
            # End - if (not fValid):
        else:  # if (not REPAIR_MATRICES_DURING_VALIDATION):
            MLEngine_SimpleCheckArray(self.inputToOutput, "SimpleNetInputMatrix")
        # End - if (not REPAIR_MATRICES_DURING_VALIDATION):

        # The matrix should now be different than the previous state
        if (MLEngine_ArrayChecksumEqual(job, self.inputToOutput, "SimpleNetInputMatrix", False)):
            ASSERT_ERROR("MLEngine_SingleLayerNeuralNet: Training did not update the weight matrix - Nonce=" + str(job.GetNonce()))

        # Save a checksum of the new matrix state
        MLEngine_SetArrayChecksum(job, self.inputToOutput, "SimpleNetInputMatrix")
        if (not MLEngine_ArrayChecksumEqual(job, self.inputToOutput, "SimpleNetInputMatrix", True)):
            ASSERT_ERROR("Failed to save a matrix checksum")

        return fValid
    # End - ValidateAndFixModel



    #####################################################
    #####################################################
    def GetLibraryName(self):
        return "Pytorch"

    #####################################################
    #####################################################
    def GetInputWeights(self):
        return None

    #####################################################
    # MLEngine_SingleLayerNeuralNet.CheckState
    #####################################################
    def CheckState(self, job):
        fDebug = False
        fFail = False
        errStr = ""
        if (fDebug):
            print("DebugSimpleNetJob")

        if (self.inputToOutput is None):
            print("Nonce = " + str(job.GetNonce()))
            ASSERT_ERROR("Matrix is None")

        MLEngine_SimpleCheckArray(self.inputToOutput, "SimpleNetInputMatrix")

        #<><>
        return
        #<><>
        if (job.GetNonce() <= 2):
            return

        if (job.ChecksumExists("SimInMatInit")):
            if (MLEngine_ArrayChecksumEqual(job, self.inputToOutput, "SimInMatInit", False)):
                errStr = "Save a matrix checksum that is same as initial"
                fFail = True

        if (fFail):
            print("Nonce = " + str(job.GetNonce()))
            ASSERT_ERROR(errStr)
    # End - CheckState


    #####################################################
    # MLEngine_SingleLayerNeuralNet.DebugPrint
    #####################################################
    def DebugPrint(self):
        weightMatrix = self.inputToOutput.weight.clone().detach().numpy()
        biasVector = self.inputToOutput.bias.clone().detach().numpy()

        print("Weight Matrix = " + str(weightMatrix))
        print("biasVector = " + str(biasVector))
    # End - DebugPrint

    #####################################################
    # MLEngine_SingleLayerNeuralNet.NeedTrueResultForEveryInput
    #####################################################
    def NeedTrueResultForEveryInput(self):
        return True
    # End - NeedTrueResultForEveryInput
# class MLEngine_SingleLayerNeuralNet(nn.Module):








################################################################################
# 
# MLEngine_DeepNeuralNet
# 
################################################################################
class MLEngine_DeepNeuralNet(nn.Module):

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
        fDebug = False

        super().__init__()
        err = E_NO_ERROR

        self.isLogistic = job.GetIsLogisticNetwork()
        inputNameListStr = job.GetNetworkInputVarNames()
        inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
        self.NumInputVars = len(inputNameList)

        resultValueName = job.GetNetworkOutputVarName()
        self.NumOutputCategories = tdf.TDF_GetNumClassesForVariable(resultValueName)

        # If the recurrent state size is 0, then this is a simple deep neural network.
        self.RecurrentStateSize = job.GetNetworkStateSize()
        self.IsRNN = (self.RecurrentStateSize > 0)
        if (fDebug):
            print("self.RecurrentStateSize = " + str(self.RecurrentStateSize))
            print("self.IsRNN = " + str(self.IsRNN))
            print("self.NumOutputCategories = " + str(self.NumOutputCategories))

        # Build the network
        self.NetworkLayers = []
        self.LinearUnitList = nn.ModuleList()
        layerNum = 0

        ################################
        # Create the first network layer. This does some things differently
        # than all other network layers
        layerSpecXML = job.GetNetworkLayerSpec("InputLayer")
        if (layerSpecXML is None):
            print("Cannot find first network layer")
            raise Exception()

        inputSize = self.NumInputVars
        # If this is an RNN, then the first layer takes in a combined vector
        # made from both the inputs and the recurrent state.
        if (self.IsRNN):
            inputSize = self.RecurrentStateSize + self.NumInputVars

        err, newLayerInfo, newLinearUnit, layerOutputSize = self.MakeOneNetworkLayer(layerSpecXML, 
                                                                       0, inputSize, False)
        if (err != E_NO_ERROR):
            print("Error in MLEngine_DeepNeuralNet::__init__")
            raise Exception()

        self.LinearUnitList.append(newLinearUnit)
        self.NetworkLayers.append(newLayerInfo)
        # Get ready to do the next layer
        layerNum += 1
        currentLayerInputSize = layerOutputSize


        ################################
        # Create each hidden layer
        layerSpecXML = job.GetNetworkLayerSpec("HiddenLayer")
        while (layerSpecXML is not None):
            err, newLayerInfo, newLinearUnit, layerOutputSize = self.MakeOneNetworkLayer(layerSpecXML, 
                                                                 layerNum, currentLayerInputSize, False)
            if (err != E_NO_ERROR):
                raise Exception()

            self.NetworkLayers.append(newLayerInfo)
            self.LinearUnitList.append(newLinearUnit)

            # Get ready to do the next layer
            layerNum += 1
            currentLayerInputSize = layerOutputSize
            layerSpecXML = dxml.XMLTools_GetPeerNode(layerSpecXML, "HiddenLayer")
        # End - while (layerSpecXML is not None):


        ################################
        # Create the last layer.
        # This may be complicated because it may take more than the previous layer's output
        # as its inputs.
        layerSpecXML = job.GetNetworkLayerSpec("OutputLayer")
        if (layerSpecXML is None):
            raise Exception()

        err, newLayerInfo, newLinearUnit, layerOutputSize = self.MakeOneNetworkLayer(layerSpecXML, 
                                                               layerNum, currentLayerInputSize, True)
        if (err != E_NO_ERROR):
            raise Exception()
        self.NetworkLayers.append(newLayerInfo)
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

        if (fDebug):
            print("MLEngine_DeepNeuralNet.__init__")
            print("   Len(self.LinearUnitList) = " + str(len(self.LinearUnitList)))
            print("   Len(self.NetworkLayers) = " + str(len(self.NetworkLayers)))
            print("   Num Params=" + str(len(list(self.parameters()))))
            #print("   Params=" + str(list(self.parameters())))
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
        fDebug = False

        newLayerInfo = {'layerNum': layerNum}
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

        newLayerInfo['LayerOutputSize'] = layerOutputSize
        newLayerInfo['Name'] = "Vec" + str(layerNum) + "To" + str(layerNum + 1)
        newLayerInfo['fIsFinalLayer'] = fIsFinalLayer
        newLayerInfo['MixAnalogDigital'] = dxml.XMLTools_GetChildNodeTextAsBool(layerSpecXML, 
                                                            NETWORK_MIXED_ANALOG_DIGITAL_ELEMENT_NAME, 
                                                            False)

        if (newLayerInfo['MixAnalogDigital']):
            origLayerInputSize = currentLayerInputSize
            currentLayerInputSize += self.NumInputVars
            if (fDebug):
                print("Found Analog Layer!")
                print("fIsFinalLayer = " + str(fIsFinalLayer))
                print("New origLayerInputSize = " + str(origLayerInputSize))
                print("New self.NumInputVars = " + str(self.NumInputVars))
                print("New currentLayerInputSize = " + str(currentLayerInputSize))
            # End - if (fDebug):
        # End - if (newLayerInfo['MixAnalogDigital']):


        # Create the matrices of weights
        # A nn.Linear is an object that contains a matrix A and bias vector b
        # It is used to compute (x * A-transpose) + b
        #    where x is the input, which is a vector with shape (1 x self.NumInputVars)
        #    or x is alternatively described as (rows=1, colums=self.NumInputVars). 
        #
        # The values are initialized from U(−k,k), where k=in_features
        #
        # Plain Python containers, such as list and dict won’t be properly registered 
        # in a module class object. As a result, they do not appear as Parameters, 
        # and so will not be part of the backprop or gradient updates. 
        # As a result, use nn.ModuleDict instead of dict and nn.ModuleList instead of list
        newLinearUnit = nn.Linear(currentLayerInputSize, layerOutputSize)

        # Be careful.
        # Consider just layer 1. Initially, after allocation, every node in layer 1 is identical.
        # Each node is a combination of all inputs so they are all the same combination of the 
        # same inputs. How do the channels ever differentiate?
        # The constructor will randomly initialize all coefficients at the beginning?

        # Make the non-linear units between linear layers
        # Depending on the result value type, make a Non-linearity
        nonLinearTypeStr = dxml.XMLTools_GetChildNodeTextAsStr(layerSpecXML, "NonLinear", "ReLU").lower()
        newLayerInfo['NonLinear'] = MLEngine_MakePyTorchNonLinear(nonLinearTypeStr, self.isLogistic, 
                                                                  fIsFinalLayer)

        # If a Linear Unit is not a direct attribute then we must make it a parameter explicitly.        
        # self.register_parameter(None, param)

        return E_NO_ERROR, newLayerInfo, newLinearUnit, layerOutputSize
    # End - MakeOneNetworkLayer





    #####################################################
    #
    # [MLEngine_DeepNeuralNet.forward]
    #
    # Forward prop.
    # This will leave pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #
    # Process each sequence in a timeline.
    # - If every input corresponds to a different output, then we can batch all inputs/results together
    #   in a single sequence. Really, each input vector is a different sequence, but for efficiency, we 
    #   combine them all into 1 sequence.
    # - If the neural network takes a series of inputs to make a single prediction, like LSTM or then we split
    #   the timeline up into sequences, where each sequence is a series of 1 or more inputs without result values,
    #   and the last entry in the sequence is a set of inputs WITH a result.
    #####################################################
    def forward(self, job, numDataSamples, inputTensor, trueResultTensor, 
                dayNumArray, fAddMinibatchDimension, maxDaysWithZeroValue):
        fDebug = False

        vec = inputTensor
        combinedInput = None

        # The network will look like:
        #    Inputs -> [InputToVec1] -> Vec1
        #                -> [Vec1ToVec2] -> Vec2
        #                -> [Vec2ToOutput] -> outputs
        # layer 0 takes direct inputs
        # layer self.NumLayers-1 is the last layer that provides outputs
        #
        # We can do this with a single matrix operation for a simple Deep Network.
        # However, if it is recurrent, then we need to generate the recurrent
        # state from eack output K to be an input to K+1. As a result, we will
        # have to do each column as a separate step.

        ###########################################################
        # Non-Recurrent Network - the simple case which does a single batch
        if (not self.IsRNN):
            for layerNum in range(self.NumLayers):
                layerInfo = self.NetworkLayers[layerNum]

                if (layerInfo['MixAnalogDigital']):
                    vec = torch.cat((vec, inputTensor), 2)
                # End - if (layerInfo['MixAnalogDigital']):

                vec = self.LinearUnitList[layerNum](vec)
                if (layerInfo['NonLinear'] is not None):
                    vec = layerInfo['NonLinear'](vec)
            # End - for layerNum in range(self.NumLayers):

            return numDataSamples, vec, trueResultTensor, None
        # End - if (not self.IsRNN)

        ###########################################################
        # Recurrent Network - the slow case which does each input sequentially
        else:   # if (not self.IsRNN):
            # Get Hyperparameters that only apply to an RNN
            maxDaysSkippedInSameSequence = job.GetTrainingParamInt(mlJob.TRAINING_MAX_SKIPPED_DAYS_IN_SAME_SEQUENCE,
                                    DEFAULT_MAX_SKIPPED_DAYS_IN_SAME_SEQUENCE)
            if (fDebug):
                print("MLEngine_DeepNeuralNet.forward. maxDaysSkippedInSameSequence=" + str(maxDaysSkippedInSameSequence))

            # Initialize the hidden state.
            # This is used each time we start a new sequence of inputs
            # Each sequence of inputs starts from an initial state.
            # One training sequence does not convey any information about 
            # another training sequence.
            # As a result, the order we train the input sequences does not matter.
            recurrentState = torch.zeros(self.RecurrentStateSize)
            #recurrentState = recurrentState.to(gpuDevice)
            #recurrentState = recurrentState.cpu()

            # Make a list of all possible results. This is likely more space than we need and we will trim it
            # down to the final size when this procedure is about to return.
            if (fAddMinibatchDimension):
                resultList = torch.zeros(numDataSamples, 1, self.NumOutputCategories)
            else:
                resultList = torch.zeros(numDataSamples, self.NumOutputCategories)
            numDaysForResult = torch.zeros(numDataSamples)
            numValidResults = 0
            prevDayNum = -1
            numInputsInCurrentSequence = 0
            for inputVecNum in range(numDataSamples):
                currentDayNum = dayNumArray[inputVecNum]
                if (fAddMinibatchDimension):
                    vec = inputTensor[inputVecNum][0]
                    trueResult = trueResultTensor[inputVecNum][0][0].item()
                else:
                    vec = inputTensor[inputVecNum]
                    trueResult = trueResultTensor[inputVecNum][0].item()
                savedInputVecForCurrentSample = vec
                if (fDebug):
                    print("MLEngine_DeepNeuralNet.forward")
                    print("     currentDayNum = " + str(currentDayNum))
                    print("     vec = " + str(vec))
                    print("     trueResult = " + str(trueResult))

                # If we skipped a few days, then this is a new sequence.
                if ((prevDayNum > 0) and ((currentDayNum - prevDayNum) > maxDaysSkippedInSameSequence)):
                    recurrentState = torch.zeros(self.RecurrentStateSize)
                    numInputsInCurrentSequence = 0
                    if (fDebug):
                        print("MLEngine_DeepNeuralNet.forward. Start a new Sequence. currentDayNum=" + str(currentDayNum) + ", prevDayNum=" + str(prevDayNum))
                # End - if ((prevDayNum > 0) and ((currentDayNum - prevDayNum) > maxDaysSkippedInSameSequence)):
                prevDayNum = currentDayNum
                numInputsInCurrentSequence += 1

                # The first layer takes in a combined vector
                # made from both the inputs and the recurrent state.
                if (fDebug):
                    print("MLEngine_DeepNeuralNet.forward. Make input vector")
                    print("     Old vec=" + str(vec))
                    print("     recurrentState=" + str(recurrentState))
                vec = torch.cat((vec, recurrentState), 0)
                if (fDebug):
                    print("     New vec=" + str(vec))

                # Pass the vector through each layer of the neural net
                for layerNum in range(self.NumLayers):
                    layerInfo = self.NetworkLayers[layerNum]

                    if (layerInfo['MixAnalogDigital']):
                        vec = torch.cat((vec, inputTensor), 2)
                    # End - if (layerInfo['MixAnalogDigital']):

                    vec = self.LinearUnitList[layerNum](vec)
                    if (layerInfo['NonLinear'] is not None):
                        vec = layerInfo['NonLinear'](vec)
                # End - for layerNum in range(self.NumLayers):

                # Compute the next recurrent state
                combinedInput = torch.cat((recurrentState, savedInputVecForCurrentSample, vec), 0)
                recurrentState = self.rnnStateLinearUnit(combinedInput)

                if (fDebug):
                    print("MLEngine_DeepNeuralNet.forward. Done with layers")
                    print("     vec=" + str(vec))
                    print("     combinedInput=" + str(combinedInput))
                    print("     New recurrentState=" + str(recurrentState))
                    print("     trueResult=" + str(trueResult) + ", tdf.TDF_INVALID_VALUE=" + str(tdf.TDF_INVALID_VALUE))
                    print("     trueResult > tdf.TDF_INVALID_VALUE=" + str(trueResult > tdf.TDF_INVALID_VALUE))

                # Save this value if it marks the end of a series
                if (trueResult > tdf.TDF_INVALID_VALUE):
                    # Save the result with its gradient. Also, compact the results that we will keep.
                    # Don't waste time on compacting inputTensor or dayNumArray, we do not return those.
                    if (fAddMinibatchDimension):
                        resultList[numValidResults][0] = vec
                        trueResultTensor[numValidResults][0][0] = trueResult
                    else:
                        resultList[numValidResults] = vec
                        trueResultTensor[numValidResults][0] = trueResult
                    numDaysForResult[numValidResults] = numInputsInCurrentSequence
                    numValidResults += 1

                    if (fDebug):
                        print("MLEngine_DeepNeuralNet.forward. Got a prediction with an associated valid result")
                        print("     numValidResults=" + str(numValidResults))
                        print("     resultList=" + str(resultList))
                        print("     trueResultTensor=" + str(trueResultTensor))
                        print("     resultList.dim()=" + str(resultList.dim()))
                        print("     trueResultTensor.dim()=" + str(trueResultTensor.dim()))
                        print("     trueResult.type=" + str(type(trueResult)))

                    # We do not have to start a new sequence. We do that above only when we see data 
                    # that is not in the same time sequence as the previous data.
                    #recurrentState = torch.zeros(self.RecurrentStateSize)
                # End - if (trueResult > tdf.TDF_INVALID_VALUE):
            # End - for inputVecNum in range(numDataSamples):

            # Truncate the result tensors to just contain valid results.
            if (fAddMinibatchDimension):
                # Don't waste time on compacting inputTensor or dayNumArray, we do not return those.
                #inputArray = inputArray[:numValidResults, :1, :self.NumInputVars]
                resultList = resultList[:numValidResults, :1, :1]
                trueResultTensor = trueResultTensor[:numValidResults, :1, :1]
            else:
                # Don't waste time on compacting inputTensor or dayNumArray, we do not return those.
                #inputArray = inputArray[:numValidResults, :self.NumInputVars]
                resultList = resultList[:numValidResults, :1]
                trueResultTensor = trueResultTensor[:numValidResults, :1]
            numDaysForResult = numDaysForResult[:numValidResults]

            if (fDebug):
                print("MLEngine_DeepNeuralNet.forward. Done")
                print("     numValidResults=" + str(numValidResults))
                print("     resultList=" + str(resultList))
                print("     trueResultTensor=" + str(trueResultTensor))
                print("     numDaysForResult=" + str(numDaysForResult))

            return numValidResults, resultList, trueResultTensor, numDaysForResult
        # if (self.IsRNN):
    # End - forward




    #####################################################
    #
    # [MLEngine_DeepNeuralNet.SaveNeuralNetstate]
    #
    #####################################################
    def SaveNeuralNetstate(self, job):
        fDebug = False
        if (fDebug):
            print("MLEngine_DeepNeuralNet.SaveNeuralNetstate start. nonceNum = " + str(job.GetNonce()))

        # Save the matrices to the job.
        # Layer 0 is the layer that takes direct inputs
        # Layer self.NumLayers-1 is the last layer that provides outputs
        for layerNum in range(self.NumLayers):
            layerInfo = self.NetworkLayers[layerNum]

            # Do the actual save
            MLEngine_SaveLinearUnitToJob(self.LinearUnitList[layerNum], job, layerInfo['Name'])

            # Save a checksum of the matrix
            checksumName = g_SaveChecksumPrefix + layerInfo['Name']
            MLEngine_SetArrayChecksum(job, self.LinearUnitList[layerNum], checksumName)
            # Make sure the save worked
            if (not MLEngine_ArrayChecksumEqual(job, self.LinearUnitList[layerNum], checksumName, True)):
                ASSERT_ERROR("MLEngine_DeepNeuralNet.SaveNeuralNetstate. Failed to save a matrix checksum: " + checksumName)
        # End - for layerNum in range(self.NumLayers):


        # If this is an RNN, then save the linear unit for the RecurrentVector
        if (self.IsRNN):
            MLEngine_SaveLinearUnitToJob(self.rnnStateLinearUnit, job, RECURRENT_STATE_LINEAR_UNIT_NAME)

            # Save the new checksum
            MLEngine_SetArrayChecksum(job, self.rnnStateLinearUnit, g_SaveChecksumPrefix + RECURRENT_STATE_LINEAR_UNIT_NAME)
            if (not MLEngine_ArrayChecksumEqual(job, self.rnnStateLinearUnit, g_SaveChecksumPrefix + RECURRENT_STATE_LINEAR_UNIT_NAME, True)):
                ASSERT_ERROR("Failed to save a matrix checksum: " + RECURRENT_STATE_LINEAR_UNIT_NAME)
        # End - if (self.IsRNN):
    # End - SaveNeuralNetstate




    #####################################################
    #
    # [MLEngine_DeepNeuralNet.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        fDebug = False
        if (fDebug):
            print("MLEngine_DeepNeuralNet.RestoreNetState start. nonceNum = " + str(job.GetNonce()))

        # Layer 0 is the layer that takes direct inputs
        # Layer self.NumLayers-1 is the last layer that provides outputs
        for layerNum in range(self.NumLayers):
            layerInfo = self.NetworkLayers[layerNum]

            restoredTensor = MLEngine_ReadLinearUnitFromJob(job, layerInfo['Name'])

            # We always try to restore, so will also restore even on the first time
            # we used the matrix. In that case, there is no saved state, but that is not an error.
            if (restoredTensor is not None):
                if (fDebug):
                    print("MLEngine_DeepNeuralNet.Restore Tensor for layer " + str(layerNum) + ", " + layerInfo['Name'])
                self.LinearUnitList[layerNum] = restoredTensor

                # Make sure the tensor we restored matches the checksum.
                checksumName = g_SaveChecksumPrefix + layerInfo['Name']
                if (not MLEngine_ArrayChecksumEqual(job, restoredTensor, checksumName, True)):
                    print("MLEngine_DeepNeuralNet.RestoreNetState. Restored matrix does not match checksum: " + checksumName)
                    print("     checksumName = " + str(checksumName))
                    print("     layerNum = " + str(layerNum))
                    ASSERT_ERROR("MLEngine_DeepNeuralNet.RestoreNetState. Restored matrix does not match checksum")
            # End - if (restoredTensor is not None):
        # End - for layerNum in range(self.NumLayers):

        # If this is an RNN, then restore the linear unit for the RecurrentVector
        if (self.IsRNN):
            restoredTensor = MLEngine_ReadLinearUnitFromJob(job, RECURRENT_STATE_LINEAR_UNIT_NAME)
            if (restoredTensor is not None):
                if (fDebug):
                    print("MLEngine_DeepNeuralNet.Restore Recurrent State Tensor for RNN is None")
                self.rnnStateLinearUnit = restoredTensor
                if (not MLEngine_ArrayChecksumEqual(job, self.rnnStateLinearUnit, g_SaveChecksumPrefix + RECURRENT_STATE_LINEAR_UNIT_NAME, True)):
                    ASSERT_ERROR("MLEngine_DeepNeuralNet.RestoreNetState. Failed to Restore RNN matrix checksum: " + RECURRENT_STATE_LINEAR_UNIT_NAME)
            # End - if (restoredTensor is not None):
        # End - if (self.IsRNN):
    # End - RestoreNetState





    #####################################################
    #
    # MLEngine_DeepNeuralNet.ValidateAndFixModel
    #
    # Make sure that backprop correctly updated the local network 
    #####################################################
    def ValidateAndFixModel(self, job, loss, predictionTensor, trueResultTensor):
        fDebug = True
        fVerbose = False
        fValid = True
        fAbortOnError = False

        ##################################################
        if (REPAIR_MATRICES_DURING_VALIDATION):
            for layerNum in range(self.NumLayers):
                layerInfo = self.NetworkLayers[layerNum]
                fValid, weightMatrix, biasVector, arrayDimList, numDimensions, numDataSamples = MLEngine_FullCheckLinearUnit(self.LinearUnitList[layerNum], 
                                                                                                                        layerInfo['Name'])
                if (not fValid):
                    fValid, repairedLinearUnit = MLEngine_RepairLinearUnit(weightMatrix,
                                                    biasVector, arrayDimList, numDimensions, numDataSamples)
                    if (fValid):
                        self.LinearUnitList[layerNum] = repairedLinearUnit
                    else:
                        print("ValidateAndFixModel: Failing. name=" + str(layerInfo['Name']))
                        if (fAbortOnError):
                            raise Exception()
                        return False
                # End - if (not fValid):
            # End - for layerNum in range(self.NumLayers):

            # If this is an RNN, then also check the linear unit for the RecurrentVector
            if (self.IsRNN):
                fValid, weightMatrix, biasVector, arrayDimList, numDimensions, numDataSamples = MLEngine_FullCheckLinearUnit(self.rnnStateLinearUnit, 
                                                                                                                    RECURRENT_STATE_LINEAR_UNIT_NAME)
                if (not fValid):
                    fValid, repairedLinearUnit = MLEngine_RepairLinearUnit(weightMatrix,
                                                    biasVector, arrayDimList, numDimensions, numDataSamples)
                    if (fValid):
                        self.rnnStateLinearUnit = repairedLinearUnit
                    else:
                        print("ValidateAndFixModel: Failing. name=" + str(RECURRENT_STATE_LINEAR_UNIT_NAME))
                        if (fAbortOnError):
                            raise Exception()
                        return False
            # End - if (self.IsRNN):
        ##################################################
        else:  # if (not REPAIR_MATRICES_DURING_VALIDATION):
            for layerNum in range(self.NumLayers):
                layerInfo = self.NetworkLayers[layerNum]

                fValid = MLEngine_SimpleCheckArray(self.LinearUnitList[layerNum], layerInfo['Name'])  # <><> Crash here
                if (not fValid):
                    print("ValidateAndFixModel: Failing. name=" + str(layerInfo['Name']))
                    if (fAbortOnError):
                        raise Exception()
                    return False
            # End - for layerNum in range(self.NumLayers):

            # If this is an RNN, then also check the linear unit for the RecurrentVector
            if (self.IsRNN):
                fValid = MLEngine_SimpleCheckArray(self.rnnStateLinearUnit, RECURRENT_STATE_LINEAR_UNIT_NAME)
                if (not fValid):
                    print("ValidateAndFixModel: Failing. name=" + str(RECURRENT_STATE_LINEAR_UNIT_NAME))
                    if (fAbortOnError):
                        raise Exception()
                    return False
            # End - if (self.IsRNN):
        # End - if (not REPAIR_MATRICES_DURING_VALIDATION):


        ##################################################
        # Each matrix should now be different than its previous state
        for layerNum in range(self.NumLayers):
            layerInfo = self.NetworkLayers[layerNum]
            if (MLEngine_ArrayChecksumEqual(job, self.LinearUnitList[layerNum], layerInfo['Name'], False)):
                paramList = list(self.parameters())
                if (fVerbose):
                    print("\n\nMLEngine_DeepNeuralNet.ValidateAndFixModel Error. Training did not update the weight matrix: " 
                    + layerInfo['Name'] + ", Nonce=" + str(job.GetNonce()))
                    print("   LayerNum=" + str(layerNum))
                    print("   Num Params=" + str(len(paramList)))
                    print("   Loss=" + str(loss))
                    print("   predictionTensor=" + str(predictionTensor))
                    print("   trueResultTensor=" + str(trueResultTensor))
                    for printLayerNum in range(self.NumLayers):
                        printLayerInfo = self.NetworkLayers[printLayerNum]
                        print("Layer Param " + printLayerInfo['Name'] + ": " + str(paramList[printLayerNum]))
                        print("Layer Param Grad " + printLayerInfo['Name'] + ": " + str(paramList[printLayerNum].grad))
                    print("\n==========\n Params:")
                    print(str(list(self.parameters())))
                    ASSERT_ERROR("Training did not update the weight matrix: " + layerInfo['Name'] + ", Nonce=" + str(job.GetNonce()))
                # End - if (fVerbose):
            # End - if (MLEngine_ArrayChecksumEqual(job, self.LinearUnitList[layerNum], layerInfo['Name'])):
        # End - for layerNum in range(self.NumLayers):

        # If this is an RNN, then also check the linear unit for the RecurrentVector
        if (self.IsRNN):
            if (MLEngine_ArrayChecksumEqual(job, self.rnnStateLinearUnit, RECURRENT_STATE_LINEAR_UNIT_NAME, False)):
                # Do not panic here. The recurrent state seems to cycle through a few states, 
                # particularly at the beginning.
                if (False):
                    #weightMatrix = self.rnnStateLinearUnit.weight.detach().numpy()
                    #biasVector = self.rnnStateLinearUnit.bias.clone().detach().numpy()
                    print("\n==========")
                    print("Fail Assert. Params=" + str(list(self.parameters())))
                    print("self.rnnStateLinearUnit=" + str(self.rnnStateLinearUnit))
                    print("self.rnnStateLinearUnit=" + str(weightMatrix))
                    print("Saved Checksum=" + str(job.GetSavedArrayChecksum(RECURRENT_STATE_LINEAR_UNIT_NAME)))
                    print("New Checksum=" + str(job.ComputeArrayChecksum(weightMatrix)))
                #print("Hmmm.... Training did not update the RNN weight matrix: " + RECURRENT_STATE_LINEAR_UNIT_NAME)
                #ASSERT_ERROR("Training did not update the RNN weight matrix: " + RECURRENT_STATE_LINEAR_UNIT_NAME)
        # End - if (self.IsRNN):

        ###############
        # Save a checksum of the new matrix state
        # Layer 0 is the layer that takes direct inputs
        # Layer self.NumLayers-1 is the last layer that provides outputs
        for layerNum in range(self.NumLayers):
            layerInfo = self.NetworkLayers[layerNum]
            MLEngine_SetArrayChecksum(job, self.LinearUnitList[layerNum], layerInfo['Name'])
            if (not MLEngine_ArrayChecksumEqual(job, self.LinearUnitList[layerNum], layerInfo['Name'], True)):
                print("\n==========\nFail Assert. Params=" + str(list(self.parameters())) + "\n==============")
                ASSERT_ERROR("Failed to save a matrix checksum: " + layerInfo['Name'])

        # If this is an RNN, then save the linear unit for the RecurrentVector
        if (self.IsRNN):
            MLEngine_SetArrayChecksum(job, self.rnnStateLinearUnit, RECURRENT_STATE_LINEAR_UNIT_NAME)
            if (not MLEngine_ArrayChecksumEqual(job, self.rnnStateLinearUnit, RECURRENT_STATE_LINEAR_UNIT_NAME, True)):
                print("\n==========\nFail Assert. Params=" + str(list(self.parameters())) + "\n==============")
                ASSERT_ERROR("Failed to save a matrix checksum: " + RECURRENT_STATE_LINEAR_UNIT_NAME)
        # End - if (self.IsRNN):

        return fValid
    # End - ValidateAndFixModel


    #####################################################
    #####################################################
    def GetLibraryName(self):
        return "Pytorch"

    #####################################################
    #####################################################
    def GetInputWeights(self):
        return None


    #####################################################
    #
    # MLEngine_DeepNeuralNet.CheckState
    #
    #####################################################
    def CheckState(self, job):
        for layerNum in range(self.NumLayers):
            layerInfo = self.NetworkLayers[layerNum]
            MLEngine_SimpleCheckArray(self.LinearUnitList[layerNum], layerInfo['Name'])
        # End - for layerNum in range(self.NumLayers):

        # If this is an RNN, then also check the linear unit for the RecurrentVector
        if (self.IsRNN):
            MLEngine_SimpleCheckArray(self.rnnStateLinearUnit, RECURRENT_STATE_LINEAR_UNIT_NAME)
        # End - if (self.IsRNN):
    # End - CheckState


    #####################################################
    # MLEngine_DeepNeuralNet.DebugPrint
    #####################################################
    def DebugPrint(self):
        return
    # End - DebugPrint


    #####################################################
    # MLEngine_DeepNeuralNet.NeedTrueResultForEveryInput
    #####################################################
    def NeedTrueResultForEveryInput(self):
        return not self.IsRNN
    # End - NeedTrueResultForEveryInput


# class MLEngine_DeepNeuralNet(nn.Module):










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
        err = E_NO_ERROR
        super().__init__()

        self.isLogistic = job.GetIsLogisticNetwork()
        inputNameListStr = job.GetNetworkInputVarNames()
        inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
        self.NumInputVars = len(inputNameList)

        resultValueName = job.GetNetworkOutputVarName()
        self.NumOutputCategories = tdf.TDF_GetNumClassesForVariable(resultValueName)

        self.RecurrentStateSize = job.GetNetworkStateSize()
        self.NumLayers = 24
        if (fDebug):
            print("self.RecurrentStateSize = " + str(self.RecurrentStateSize))
            print("self.NumOutputCategories = " + str(self.NumOutputCategories))

        # Build the network
        if (fDebug):
            print("self.RecurrentStateSize = " + str(self.RecurrentStateSize))
            print("MLEngine_LSTMNeuralNet::__init__  NumInputVars = " + str(self.NumInputVars))
            print("MLEngine_LSTMNeuralNet::__init__  RecurrentStateSize = " + str(self.RecurrentStateSize))
            print("MLEngine_LSTMNeuralNet::__init__  NumLayers = " + str(self.NumLayers))
        self.LSTM = nn.LSTM(input_size=self.NumInputVars, 
                            hidden_size=self.RecurrentStateSize,
                            num_layers=self.NumLayers, 
                            batch_first=False)

        ################################
        # Get the output layer.
        layerSpecXML = job.GetNetworkLayerSpec("OutputLayer")
        if (layerSpecXML is None):
            raise Exception()

        if (self.isLogistic):
            # The output is a single number that is the probability.
            layerOutputSize = 1
        else:
            layerOutputSize = self.NumOutputCategories

        # Make the linear unit that maps the final hidden state to the output domain
        self.HiddenToOutput = nn.Linear(self.RecurrentStateSize, layerOutputSize)

        # Create a non-linear.
        nonLinearTypeStr = dxml.XMLTools_GetChildNodeTextAsStr(layerSpecXML, "NonLinear", "ReLU").lower()
        self.nonLinear = MLEngine_MakePyTorchNonLinear(nonLinearTypeStr, self.isLogistic, True)


        if (fDebug):
            print("MLEngine_LSTMNeuralNet.__init__")
            print("   Num Params=" + str(len(list(self.parameters()))))
            #print("   Params=" + str(list(self.parameters())))
    # End - __init__




    #####################################################
    #
    # [MLEngine_LSTMNeuralNet.forward]
    #
    # Forward prop.
    # This will leave pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #####################################################
    def forward(self, job, numDataSamples, inputTensor, trueResultTensor, dayNumArray, 
                fAddMinibatchDimension, maxDaysWithZeroValue):
        fDebug = False

        # Get Hyperparameters that only apply to an RNN
        maxDaysSkippedInSameSequence = job.GetTrainingParamInt(mlJob.TRAINING_MAX_SKIPPED_DAYS_IN_SAME_SEQUENCE,
                                DEFAULT_MAX_SKIPPED_DAYS_IN_SAME_SEQUENCE)
        if (fDebug):
            print("MLEngine_LSTMNeuralNet.forward. maxDaysSkippedInSameSequence=" + str(maxDaysSkippedInSameSequence))

        # LSTM expcects a 3-dimensional tensor, with #itemsInSequence x #batches x #features
        # So, even though there is a single batch, it requires you have a dimension for 
        # the batches.
        # NOTE, we always pass in a dimension for #itemsInSequence, even if this
        # may be 1 for a single data point.
        if (fDebug):
            print("MLEngine_LSTMNeuralNet.forward")
            print("    Original inputTensor.size()=" + str(inputTensor.size()))
            print("    Original inputTensor.size()=" + str(inputTensor.size()))
        if (inputTensor.dim() == 1):
            inputTensor = inputTensor.view(1, -1, -1)
        elif (inputTensor.dim() == 2):
            inputTensor = inputTensor.view(1, 1, -1)
        if (fDebug):
            print("    Fixed inputTensor.size()=" + str(inputTensor.size()))
            print("    Fixed inputTensor=" + str(inputTensor))

        # Make a list of inputs.
        currentInputSequence = torch.zeros(0, 1, self.NumInputVars)
        numInputsInCurrentSequence = 0

        # Initialize the hidden state.
        # This is used each time we start a new sequence of inputs
        # Each sequence of inputs starts from an initial state.
        # One training sequence does not convey any information about 
        # another training sequence.
        # As a result, the order we train the input sequences does not matter.
        h0 = torch.zeros(self.NumLayers, 1, self.RecurrentStateSize)
        c0 = torch.zeros(self.NumLayers, 1, self.RecurrentStateSize)
        recurrentState = (h0, c0)
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

        # Make a list of all possible results. This is likely more space than we need and we will trim it
        # down to the final size when this procedure is about to return.
        if (fAddMinibatchDimension):
            resultList = torch.zeros(numDataSamples, 1, self.NumOutputCategories)
        else:
            resultList = torch.zeros(numDataSamples, self.NumOutputCategories)
        numDaysForResult = torch.zeros(numDataSamples)
        numValidResults = 0
        prevDayNum = -1

        for inputVecNum in range(numDataSamples):
            currentDayNum = dayNumArray[inputVecNum]
            if (fAddMinibatchDimension):
                vec = inputTensor[inputVecNum][0]
                trueResult = trueResultTensor[inputVecNum][0][0].item()
            else:
                vec = inputTensor[inputVecNum]
                trueResult = trueResultTensor[inputVecNum][0].item()
            savedInputVecForCurrentSample = vec
            if ((False) and (fDebug)):
                print("MLEngine_DeepNeuralNet.forward")
                print("     currentDayNum = " + str(currentDayNum))
                print("     vec = " + str(vec))
                print("     trueResult = " + str(trueResult))

            # If we skipped a few days, then this is a new sequence.
            if ((prevDayNum > 0) and ((currentDayNum - prevDayNum) > maxDaysSkippedInSameSequence)):
                h0 = torch.zeros(self.NumLayers, 1, self.RecurrentStateSize)
                c0 = torch.zeros(self.NumLayers, 1, self.RecurrentStateSize)
                recurrentState = (h0, c0)
                recurrentState = tuple([item.data for item in recurrentState])
                currentInputSequence = torch.zeros(0, 1, self.NumInputVars)
                numInputsInCurrentSequence = 0
                if (fDebug):
                    print("MLEngine_LSTMNeuralNet.forward. Start a new Sequence. currentDayNum=" + str(currentDayNum) + ", prevDayNum=" + str(prevDayNum))
            # End - if ((prevDayNum > 0) and ((currentDayNum - prevDayNum) > maxDaysSkippedInSameSequence)):
            
            prevDayNum = currentDayNum

            # Add the current input the the sequence we are building.
            if ((False) and (fDebug)):
                print("MLEngine_LSTMNeuralNet.forward()")
                print("     Before currentInputSequence=" + str(currentInputSequence))

            tempTensor = torch.zeros(1, 1, self.NumInputVars)
            tempTensor[0][0] = vec
            currentInputSequence = torch.cat((currentInputSequence, tempTensor), 0)
            numInputsInCurrentSequence += 1
            if ((False) and (fDebug)):
                print("MLEngine_LSTMNeuralNet.forward()")
                print("     numInputsInCurrentSequence=" + str(numInputsInCurrentSequence))
                print("     After currentInputSequence=" + str(currentInputSequence))

            # Get an output if there is a value true result to compare the prediction to.
            # There may be several steps, all building up a sequence of inputs, before we
            # finally get a step that also has a true result. Don't bother making a prediction
            # unless there is a true result we can compare to.
            if (trueResult > tdf.TDF_INVALID_VALUE):
                # Run the network and generate the final hidden state.
                #<><> lstmOut, recurrentState = self.LSTM(currentInputSequence, recurrentState)
                lstmOut, recurrentState = self.LSTM(currentInputSequence, None)
                if (fDebug):
                    print("MLEngine_LSTMNeuralNet.forward()")
                    print("     numInputsInCurrentSequence=" + str(numInputsInCurrentSequence))
                    print("     lstmOut.size()=" + str(lstmOut.size()))
                    print("     lstmOut=" + str(lstmOut))
                    print("     trueResult=" + str(trueResult) + ", tdf.TDF_INVALID_VALUE=" + str(tdf.TDF_INVALID_VALUE))
                    print("     trueResult > tdf.TDF_INVALID_VALUE=" + str(trueResult > tdf.TDF_INVALID_VALUE))

                # Map the final hidden state to the output domain.
                prediction = self.HiddenToOutput(lstmOut)
                if (fDebug):
                    print("MLEngine_LSTMNeuralNet.forward() Make prediction")
                    print("    prediction.type=" + str(type(prediction)))
                    print("    prediction.size()=" + str(prediction.size()))
                    print("    prediction=" + str(prediction))
                if (self.nonLinear is not None):
                    prediction = self.nonLinear(prediction)
                    if (fDebug):
                        print("    Post-non-linear prediction=" + str(prediction))
                        print("    Post-non-linear prediction.type=" + str(type(prediction)))
                        print("    Post-non-linear prediction.size()=" + str(prediction.size()))

                # Save the result with its gradient. Also, compact the results that we will keep.
                # Don't waste time on compacting inputTensor or dayNumArray, we do not return those.
                numPredictionValues = prediction.size()[0]
                print("    numPredictionValues=" + str(numPredictionValues))
                predictionTensorWithGradient = prediction[numPredictionValues - 1][0]
                print("    predictionTensorWithGradient=" + str(predictionTensorWithGradient))
                if (fAddMinibatchDimension):
                    resultList[numValidResults][0] = predictionTensorWithGradient
                    trueResultTensor[numValidResults][0][0] = trueResult
                else:
                    resultList[numValidResults] = predictionTensorWithGradient
                    trueResultTensor[numValidResults][0] = trueResult
                numDaysForResult[numValidResults] = numInputsInCurrentSequence
                numValidResults += 1

                if (fDebug):
                    print("MLEngine_DeepNeuralNet.forward. Got a prediction with an associated valid result")
                    print("     numValidResults=" + str(numValidResults))
                    print("     resultList=" + str(resultList))
                    print("     trueResultTensor=" + str(trueResultTensor))
                    print("     resultList.dim()=" + str(resultList.dim()))
                    print("     trueResultTensor.dim()=" + str(trueResultTensor.dim()))
                    print("     trueResult.type=" + str(type(trueResult)))
                    print("     numDaysForResult=" + str(numDaysForResult))

                # We do not have to start a new sequence. We do that above only when we see data 
                # that is not in the same time sequence as the previous data.
                #recurrentState = torch.zeros(self.RecurrentStateSize)
            # End - if (trueResult > tdf.TDF_INVALID_VALUE):
        # End - for inputVecNum in range(numDataSamples):

        # Truncate the result tensors to just contain valid results.
        if (fAddMinibatchDimension):
            # Don't waste time on compacting inputTensor or dayNumArray, we do not return those.
            #inputArray = inputArray[:numValidResults, :1, :self.NumInputVars]
            resultList = resultList[:numValidResults, :1, :1]
            trueResultTensor = trueResultTensor[:numValidResults, :1, :1]
        else:
            # Don't waste time on compacting inputTensor or dayNumArray, we do not return those.
            #inputArray = inputArray[:numValidResults, :self.NumInputVars]
            resultList = resultList[:numValidResults, :1]
            trueResultTensor = trueResultTensor[:numValidResults, :1]
        numDaysForResult = numDaysForResult[:numValidResults]

        if (fDebug):
            print("MLEngine_LSTMNeuralNet.forward. Done")
            print("     numValidResults=" + str(numValidResults))
            print("     resultList=" + str(resultList))
            print("     trueResultTensor=" + str(trueResultTensor))
            print("     numDaysForResult=" + str(numDaysForResult))

        return numValidResults, resultList, trueResultTensor, numDaysForResult
    # End - forward



    #####################################################
    #
    # [MLEngine_LSTMNeuralNet.SaveNeuralNetstate]
    #
    #####################################################
    def SaveNeuralNetstate(self, job):
        # Save to io.BytesIO buffer
        ioBuffer = io.BytesIO()
        torch.save(self.LSTM, ioBuffer)
        stateBytes = ioBuffer.getvalue()

        # Convert the binary data to a series of hex chars, which is a string
        # Functions like stateBytes.decode("utf-8") do not work.
        stateStr = stateBytes.hex()

        job.SetNamedStateAsStr(LSTM_SAVED_STATE_NAME, stateStr)
        MLEngine_SaveLinearUnitToJob(self.HiddenToOutput, job, LSTM_LINEAR_UNIT_SAVED_STATE_NAME)
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
    #
    # [MLEngine_LSTMNeuralNet.CheckState
    #
    #####################################################
    def CheckState(self, job):
        return
    # End - CheckState


    #####################################################
    # Make sure that backprop correctly updated the local network 
    #####################################################
    def ValidateAndFixModel(self, job, loss, predictionTensor, trueResultTensor):
        fValid = True

        if (REPAIR_MATRICES_DURING_VALIDATION):
            fValid = True
        else:  # if (not REPAIR_MATRICES_DURING_VALIDATION):
            fValid = True
        # End - if (not REPAIR_MATRICES_DURING_VALIDATION):

        return fValid
    # End - ValidateAndFixModel


    #####################################################
    #####################################################
    def GetLibraryName(self):
        return "Pytorch"

    #####################################################
    #####################################################
    def GetInputWeights(self):
        return None

    #####################################################
    # DebugPrint
    #####################################################
    def DebugPrint(self):
        return
    # End - DebugPrint

    #####################################################
    # MLEngine_LSTMNeuralNet.NeedTrueResultForEveryInput
    #####################################################
    def NeedTrueResultForEveryInput(self):
        return False
    # End - NeedTrueResultForEveryInput

# class MLEngine_LSTMNeuralNet





################################################################################
################################################################################
def MLEngine_ValidatePredictedResult(testTensor):
    fDebug = False
    fIsValid = True

    arrayDimList = testTensor.shape
    numDimensions = len(arrayDimList)
    numDataSamples = arrayDimList[0]
    for inputVecNum in range(numDataSamples):
        if (numDimensions == 3):
            vec = testTensor[inputVecNum][0]
        else:
            vec = testTensor[inputVecNum]

        for currentValEntry in vec:
            currentVal = currentValEntry.item()
            #print("currentVal = " + str(currentVal))
            if (currentVal != tdf.TDF_INVALID_VALUE):
                if ((math.isnan(currentVal))
                        or ((currentVal > MAX_VALID_RESULT_VALUE) or (currentVal < -MAX_VALID_RESULT_VALUE))
                        or ((currentVal > 0) and (currentVal < MIN_VALID_RESULT_VALUE)) 
                        or ((currentVal < 0) and (currentVal > -MIN_VALID_RESULT_VALUE))):
                    fIsValid = False
                    if (fDebug):
                        print("MLEngine_ValidatePredictedResult. Invalid")
                        print("     testTensor = " + str(testTensor))
                        print("     type(testTensor) = " + str(type(testTensor)))
                        print("     arrayDimList = " + str(arrayDimList))
                        print("     numDimensions = " + str(numDimensions))
                        print("     numDataSamples = " + str(numDataSamples))
                    break
        # End - for currentValEntry in vec:
    # End - for inputVecNum in range(numDataSamples):

    if (not fIsValid):
        print("ERROR! NaN value!")
        raise Exception()

    return fIsValid
# End - MLEngine_ValidatePredictedResult



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

    numInputVars, preflightInputMins, preflightInputRanges = job.GetPreflightResults()
    if (fDebug):
        print("MLEngine_NormalizeInputs. inputArray=" + str(inputArray))
        print("     numInputVars=" + str(numInputVars))
        print("     preflightInputMins=" + str(preflightInputMins))
        print("     preflightInputRanges=" + str(preflightInputRanges))

    for sampleNum in range(numDataSets):
        if (fAddMinibatchDimension):
            inputVec = inputArray[sampleNum][0]
        else:
            inputVec = inputArray[sampleNum]

        for inputNum in range(numInputVars):
            if (preflightInputRanges[inputNum] == 0):
                # Do not freak about this....some values may always be 0.
                if (False):
                    print("ERROR!!!! MLEngine_NormalizeInputs (preflightInputRanges[inputNum] == 0). inputNum=" + str(inputNum))
                    print("     preflightInputRanges[inputNum]=" + str(preflightInputRanges[inputNum]))
                    print("     preflightInputMins[inputNum]=" + str(preflightInputMins[inputNum]))
                    inputNameListStr = job.GetNetworkInputVarNames()
                    inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
                    print("     inputName=" + str(inputNameList[inputNum]))
                # End - if (False):
                normValue = 0
            else:                
                diffFromMin = (inputVec[inputNum] - preflightInputMins[inputNum])
                normValue = diffFromMin / preflightInputRanges[inputNum]

            if (fDebug):
                print("MLEngine_NormalizeInputs. preflightInputMins[inputNum]=" + str(preflightInputMins[inputNum]))
                print("     preflightInputRanges[inputNum]=" + str(preflightInputRanges[inputNum]))
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
# Batch all data for a single timeline.
# Batching is more than speed - it is also the accurracy of the final result.
# We are computing the loss as a function of the current weights, and the loss includes
# the weights. So, if the weights have high variance, then the loss, and subsequentally
# the future updates will have higher variance. Once variance is high, the system 
# will oscillate and not smoothly converge.
#
# Since the batch is a single timeline, then the batch size is small, usually 5-20.
# As a result, I send them all in as a single minibatch, so there is only 1 minibatch
# which is the original complete batch.
#
################################################################################
def MLEngine_TrainGroupOfDataPoints(job, localNeuralNet, localLossFunction, localOptimizer, 
                                    lossTypeStr, fUsePytorch, cudaIsAvailable, gpuDevice,
                                    inputArray, trueResultArray, dayNumArray, numDataSamples, 
                                    fAddMinibatchDimension, maxDaysWithZeroValue):
    fDebug = False
    if (fDebug):
        print("\n==========================================")
        print("MLEngine_TrainGroupOfDataPoints. numDataSamples=" + str(numDataSamples))
        print("trueResultArray = " + str(trueResultArray))

    localNeuralNet.CheckState(job)
    fEveryInputMakesPrediction = localNeuralNet.NeedTrueResultForEveryInput()
    epochNum = job.GetEpochNum()

    #######################################
    # Batch the entire matrix as a single batch, but use Pytorch
    if (fUsePytorch):
        if (fDebug):
            print("MLEngine_TrainGroupOfDataPoints. Original inputArray=" + str(inputArray))

        # Normalize all inputs using the value from preflight
        inputArray = MLEngine_NormalizeInputs(job, numDataSamples, inputArray, fAddMinibatchDimension)
        if (fDebug):
            print("MLEngine_TrainGroupOfDataPoints. Normalized inputArray=" + str(inputArray))

        # Convert numpy matrices to Pytorch Tensors
        inputTensor = torch.from_numpy(inputArray).float()
        trueResultTensor = torch.from_numpy(trueResultArray).float()

        # Compare output and ground-truth target in the job.
        # This is NOT a loss function, but rather it only updates job statistics.
        if (epochNum == 0):
            for index in range(numDataSamples):
                if (fAddMinibatchDimension):
                    inputVec = inputArray[index][0]
                    trueResult = trueResultArray[index][0][0]
                else:
                    inputVec = inputArray[index]
                    trueResult = trueResultArray[index][0]
                job.RecordTrainingSample(inputVec, trueResult)
            # End - for index in range(numDataSamples):
        # End - if (epochNum):

        if (fDebug):
            print("MLEngine_TrainGroupOfDataPoints. Before forward()")
            print("   numDataSamples=" + str(numDataSamples))
            print("   inputTensor=" + str(inputTensor))
            print("   trueResultTensor=" + str(trueResultTensor))
            print("   dayNumArray=" + str(dayNumArray))

        if (cudaIsAvailable):
            inputTensor = inputTensor.to(gpuDevice)
            trueResultTensor = trueResultTensor.to(gpuDevice)
            print("Converting from CPU to GPU")
            raise Exception()
        # End - if (cudaIsAvailable):

        # NOTE!
        # forward() may only return some of the original inputs as outputs. If the neural network takes a series of inputs to 
        # make a single prediction, like LSTM or an RNN, a series of several inputs may all combine to make a 
        # single output. This means that the output vector may have fewer data entries than the original 
        # input matrix. For simplicity, forward will also return a list of truncated true values, which will
        # only contain true values that correspond to a prediction. So, it eliminates all true values that 
        # are placeholders that were associated with one of the intermetdiate inputs.
        localNeuralNet.train()
        localNeuralNet.CheckState(job)
        numDataSamples, predictionTensor, trueResultTensor, numDaysForResult = localNeuralNet.forward(job, numDataSamples, 
                                                                    inputTensor, trueResultTensor, dayNumArray, 
                                                                    fAddMinibatchDimension, maxDaysWithZeroValue)
        localNeuralNet.CheckState(job)

        # Transfer the output back to the CPU so we can access the results
        if ((cudaIsAvailable) and (predictionTensor is not None)):
            print("Converting from CPU to GPU")
            predictionTensor = predictionTensor.cpu()
            raise Exception()

        if (fDebug):
            print("MLEngine_TrainGroupOfDataPoints. After forward()")
            print("   numDataSamples=" + str(numDataSamples))
            print("   inputTensor=" + str(inputTensor))
            print("   predictionTensor=" + str(predictionTensor))
            print("   trueResultTensor=" + str(trueResultTensor))
            #print("   dayNumArray=" + str(dayNumArray))

        # <><> BUGBUG - FIXME - Remove this when the code is more stable.
        fIsValid = MLEngine_ValidatePredictedResult(predictionTensor)
        if (not fIsValid):
            print("ERROR! Bogus predictionTensor")
            print("   inputTensor = " + str(inputTensor))
            print("   predictionTensor = " + str(predictionTensor))
            print("   cudaIsAvailable = " + str(cudaIsAvailable))
            localNeuralNet.CheckState(job)
            raise Exception()
        # <><> BUGBUG - FIXME

        # Now, compare predicted outputs to the ground-truth targets and compute the 
        # Loss (or Divergence or Div). This will also backpropagate and update the weights.
        MLEngine_ComputeTrainingLossAndUpdate(job, predictionTensor, trueResultTensor, 
                                            localNeuralNet, localOptimizer,
                                            lossTypeStr, localLossFunction)
        localNeuralNet.CheckState(job)
    # End - if (fUsePytorch):
# End - MLEngine_TrainGroupOfDataPoints






################################################################################
#
# [MLEngine_ComputeTrainingLossAndUpdate]
# 
# This procedure is only called for Pytorch.
################################################################################
def MLEngine_ComputeTrainingLossAndUpdate(job, predictionTensor, trueResultTensor, 
                                        localNeuralNet, localOptimizer,
                                        lossTypeStr, localLossFunction):
    fDebug = False
    if (fDebug):
        print("===================================================")
        print("MLEngine_ComputeTrainingLossAndUpdate. Start. predictionTensor.size=" + str(predictionTensor.size()))
        print("     trueResultTensor.size=" + str(trueResultTensor.size()) + " predictionTensor.size=" + str(predictionTensor.size()))
        print("     trueResultTensor=" + str(trueResultTensor))
        print("     predictionTensor=" + str(predictionTensor))

    # Compute the loss between the prediction and the actual result.
    # Initially:
    #   predictionTensor is a 3-d array: [ N, miniBatch=1, C ]
    #   trueResultTensor is a 3-d array: [ N, miniBatch=1, C ]
    # Where N is sequence size and C = number of classes
    # We may have to convert this for different loss functions.

    ##################
    # nllloss takes parameters:
    #    predictionTensor is (N,C) 
    #    trueResult (also called Target) which is (N)
    if (lossTypeStr == "nllloss"):
        predictionTensor = predictionTensor[:, -1, :]
        trueResultTensor = trueResultTensor[:, -1, -1]
        trueResultTensor = trueResultTensor.long()
        if (fDebug):
            print("MLEngine_ComputeTrainingLossAndUpdate. nllloss")
    # End - if (lossTypeStr == "nllloss"):
    ##################
    # bceloss takes parameters:
    #    predictionTensor is (N, batch, C) 
    #    trueResult (also called Target) is the same size: (N, batch, C)
    ##################
    # L2 Loss (MSELoss) takes 2 matrices of the same size.
    #   predictionTensor: (N,∗) where ∗*∗ means any number of additional dimensions
    #   actualResult (also called Target) (N,∗), same shape as the input

    loss = localLossFunction(predictionTensor, trueResultTensor)
    if (fDebug):
        print("MLEngine_ComputeTrainingLossAndUpdate. loss.size=" + str(loss.size()))
        print("     loss=" + str(loss) + ",  loss.data=" + str(loss.data) + ", loss.data.item()=" + str(loss.data.item()))

    # Initialize the gradients to 0. This prevents gradients from any previous
    # data set (ie a timeline) from influencing the learning for the current data set.
    if (localOptimizer is not None):
        localOptimizer.zero_grad()
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
        print("     predictionTensor=" + str(predictionTensor))
        print("     loss=" + str(loss))
        ASSERT_ERROR("MLEngine_ComputeTrainingLossAndUpdate")

    localNeuralNet.CheckState(job)

    if (localOptimizer is not None):
        if (fDebug):
            print("Call Optimizer step")
        localOptimizer.step()
    else:
        learningRate = float(job.GetTrainingParamStr(mlJob.TRAINING_OPTION_LEARNING_RATE, "0.1"))
        if (learningRate == 0):
            print("!!! Error. 0 Learning Rate")
            ASSERT_ERROR("MLEngine_ComputeTrainingLossAndUpdate")

        if (fDebug):
            print("No Optimizer. step=" + str(learningRate))
        with torch.no_grad():
            for currentParam in localNeuralNet.parameters():
                if (currentParam.grad is not None):
                    currentParam = currentParam - (learningRate * currentParam.grad)
    # End - Update matrices

    localNeuralNet.CheckState(job)

    # Debug - make sure that backprop correctly updated the local network 
    fValid = localNeuralNet.ValidateAndFixModel(job, loss, predictionTensor, trueResultTensor)
    if (not fValid):
        print("\n\nBail in MLEngine_ComputeTrainingLossAndUpdate")
        raise Exception()
    job.IncrementNonce()

    localNeuralNet.CheckState(job)

    job.RecordTrainingLoss(loss.data.item())

    localNeuralNet.CheckState(job)
# End - MLEngine_ComputeTrainingLossAndUpdate






################################################################################
#
# [MLEngine_TestGroupOfDataPoints]
# 
################################################################################
def MLEngine_TestGroupOfDataPoints(job, localNeuralNet, fUsePytorch, cudaIsAvailable, gpuDevice,
                                   inputArray, trueResultArray, dayNumArray, numDataSamples, 
                                   fAddMinibatchDimension, networkOutputDataType,
                                   maxDaysWithZeroValue):
    fDebug = False
    if (fDebug):
        print("\n==========================================")
        print("MLEngine_TestGroupOfDataPoints. numDataSamples=" + str(numDataSamples))
        print("     fUsePytorch=" + str(fUsePytorch))

    if (not fUsePytorch):
        return

    # Normalize all inputs using the value from preflight
    inputArray = MLEngine_NormalizeInputs(job, numDataSamples, inputArray, fAddMinibatchDimension)

    # Build a number of inputs that eventually lead to each output
    fEveryInputMakesPrediction = localNeuralNet.NeedTrueResultForEveryInput()
    numSequencesForEachResult = []
    if (True):   # (fEveryInputMakesPrediction):
        numPreviousInputSequences = 0
        for index in range(numDataSamples):
            if (fAddMinibatchDimension):
                trueResult = trueResultArray[index][0][0]
            else:
                trueResult = trueResultArray[index][0]

            if (trueResult == tdf.TDF_INVALID_VALUE):
                numPreviousInputSequences += 1
            else:
                numSequencesForEachResult.append(numPreviousInputSequences + 1)
                numPreviousInputSequences = 0
        # End - for result in trueResultArray:
    # End - if (fEveryInputMakesPrediction):

    # Convert numpy matrices to Pytorch Tensors
    inputGroupSequenceTensor = torch.from_numpy(inputArray).float()
    trueResultTensor = torch.from_numpy(trueResultArray).float()

    # Transfer the input tensor to GPU. We transferred the recurrent state to the GPU
    # once before the loop began.
    if (cudaIsAvailable):
        inputGroupSequenceTensor = inputGroupSequenceTensor.to(gpuDevice)
        trueResultTensor = trueResultTensor.to(gpuDevice)

    # NOTE!
    # forward() may only return some of the outputs. If the neural network takes a series of inputs to 
    # make a single prediction, like LSTM or an RNN, a series of several inputs may all combine to make a 
    # single output. This means that the output vector may have fewer data entries than the original 
    # input matrix. For simplicity, forward will also return a list of truncated true values, which will
    # only contain true values that correspond to a prediction. So, it eliminates all true values that 
    # are placeholders that were associated with one of the intermetdiate inputs.
    with torch.no_grad():
        numDataSamples, predictionTensor, trueResultTensor, numDaysForResult = localNeuralNet.forward(job, numDataSamples, 
                                                                    inputGroupSequenceTensor, trueResultTensor, dayNumArray, 
                                                                    fAddMinibatchDimension, maxDaysWithZeroValue)
    # End - with torch.no_grad():

    # Transfer the output back to the CPU so we can access the results
    if (cudaIsAvailable):
        predictionTensor = predictionTensor.cpu()

    ASSERT_IF((predictionTensor is None), "MLEngine_TestGroupOfDataPoints. predictionTensor is None")
    predictedResultList = MLEngine_MakeListOfResults(job, predictionTensor, numDataSamples, 
                                                     fUsePytorch, networkOutputDataType)

    # Compare predicted outputs to the ground-truth targets.
    # We store the results in the Job, and include lots of statistics like what
    # the accuracy was for different groups of result. 
    for index in range(numDataSamples):
        # Pytorch uses a 3rd dimension, for minibatches
        if (fAddMinibatchDimension):
            trueResult = trueResultTensor[index][0][0].item()
        else:
            trueResult = trueResultTensor[index][0].item()

        if (trueResult == tdf.TDF_INVALID_VALUE):
            continue

        if (numDaysForResult is not None):
            subGroupNum = int(numDaysForResult[index])
        else:
            subGroupNum = -1

        job.RecordTestingResult(trueResult, predictedResultList[index], subGroupNum)
    # End - for index in range(numDataSamples):
# End - MLEngine_TestGroupOfDataPoints






################################################################################
#
# [MLEngine_MakeListOfResults]
#
################################################################################
def MLEngine_MakeListOfResults(job, predictedResultTensor, numDataSamples, fUsePytorch, networkOutputDataType):
    fDebug = False

    # Note, a Boolean is a category result with two categories (0 and 1). But a Boolean
    # that is also a logistic, is a single floating point value between 0 and 1.
    isLogistic = job.GetIsLogisticNetwork()

    if (fDebug):
        print("MLEngine_MakeListOfResults. fUsePytorch = " + str(fUsePytorch))
        print("     networkOutputDataType = " + str(networkOutputDataType))
        print("     isLogistic = " + str(isLogistic))
        print("     numDataSamples = " + str(numDataSamples))
        print("     predictedResultTensor = " + str(predictedResultTensor))
        if (predictedResultTensor is not None):
            print("     predictedResultTensor.type = " + str(type(predictedResultTensor)))
            print("     predictedResultTensor.shape = " + str(predictedResultTensor.shape))

    # If this is a category result, and if we are using xgBoost, then we already have a
    # list of outputs.
    if ((not fUsePytorch) 
            and (networkOutputDataType in (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS, tdf.TDF_DATA_TYPE_BOOL))
            and (not isLogistic)):
        #mostProbableCategoryList = np.asarray([np.argmax(line) for line in predictedResultTensor])
        predictedResultList = [round(value) for value in predictedResultTensor]
        return predictedResultList
    # End - if xgBoost and Categorical


    # Compare predicted outputs to the ground-truth targets.
    # An int or float output is just the number.
    if (networkOutputDataType in (tdf.TDF_DATA_TYPE_FLOAT, tdf.TDF_DATA_TYPE_INT)):
        if (fUsePytorch):
            predictedResultList = predictedResultTensor[:, 0, 0].tolist()
        else:
            predictedResultList = predictedResultTensor.tolist()
    # End - if (tdf.TDF_DATA_TYPE_FLOAT or tdf.TDF_DATA_TYPE_INT):
    # In a logistic, we want the probability that an item is true, not the most likely.
    # Note, a Boolean is a category result with two categories (0 and 1). But a Boolean
    # that is also a logistic is a single floating point value between 0 and 1.
    elif (isLogistic):
        if (fUsePytorch):
            # predictedResultTensor is N x 1 x 1 where minibatch dim is 1 and there is also only 1 output, 
            # which is the result of the sigmoid.
            predictedResultList = predictedResultTensor[:, 0, 0].tolist()
        else:
            # predictedResultTensor is vector of length N, the result of the sigmoid.
            predictedResultList = predictedResultTensor.tolist()
        if (fDebug):
            print("MLEngine_MakeListOfResults. Logistic Network predictedResultList: " + str(predictedResultList))
    # End - if (isLogistic):
    # A category output is a list of probabilities. Get the class ID with the top probability
    elif (networkOutputDataType in (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS, tdf.TDF_DATA_TYPE_BOOL)):
        predictedResultList = [0] * numDataSamples
        for index in range(numDataSamples):
            if (fUsePytorch):
                topProbability, topIndexTensor = predictedResultTensor[index][0].topk(1)
                predictedResult = topIndexTensor.item()
                if (fDebug):
                    print("MLEngine_MakeListOfResults. topProbability: " + str(topProbability))
                    print("     topIndexTensor=" + str(topIndexTensor))
                    print("     topIndexTensor.type=" + str(type(topIndexTensor)))
                    print("     topIndexTensor.size=" + str(topIndexTensor.shape))
            else:
                # <> TODO: Lift making mostProbableCategoryList out of the loop
                mostProbableCategoryList = np.asarray([np.argmax(line) for line in predictedResultTensor])
                predictedResult = mostProbableCategoryList[index]
                if (fDebug):
                    print("MLEngine_MakeListOfResults. mostProbableCategoryList = " + str(mostProbableCategoryList))
            predictedResultList[index] = predictedResult
        # End - for index in range(numDataSamples):
    # End - elif (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS or tdf.TDF_DATA_TYPE_BOOL)):


    if (fDebug):
        print("MLEngine_MakeListOfResults - predictedResultList: " + str(predictedResultList))

    return predictedResultList
# End - MLEngine_MakeListOfResults





################################################################################
# 
# [MLEngine_PreflightOneFilePartitionImpl]
#
# This returns:
#   job
#   fEOF - True iff we hit the end of the file
#   startPosFirstTimelineInPartition
#   stopPosLastTimelineInPartition
#   timelinePositionList
#
################################################################################
def MLEngine_PreflightOneFilePartitionImpl(job, currentPartitionStart, currentPartitionStop):
    fDebug = False

    tdfFilePathName = job.GetDataParam("TrainData", "")
    inputNameListStr = job.GetNetworkInputVarNames()
    resultValueName = job.GetNetworkOutputVarName()
    _, requirePropertyRelationList, requirePropertyNameList, requirePropertyValueList = job.GetFilterProperties()
    
    preflightNumMissingInputsList = job.GetPreflightNumMissingInputs()
    if (fDebug):
        print("MLEngine_PreflightOneFilePartitionImpl. preflightNumMissingInputsList=" + str(preflightNumMissingInputsList))

    # Open the file in the worker process address space
    tdfReader = tdf.TDF_CreateTDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                                            requirePropertyNameList)

    # On Preflight, we will build the list of timeline positions. Initialize this.
    timelinePositionList = []
    # Make a list of timelines in this file partition and group them by training priority.
    # We go through the classes in round robin, so first train a timeline with priority 0, then
    # a timeline in priority 1, and so on, until we reach the end and then go back to the beginning.
    # We iterate only while we can find one timeline from each or most priorities.
    # We may not train all timelines from the lowest priorities, because we do not want that to
    # overshadow the higher priorities. So, may not train all items from the more common classes.
    numTrainingPriorities = job.GetNumTrainingPriorities()
    # Warning! Dont use [ [] ] * TimelinesForTrainingPriority
    # That makes a list containing the same sublist object numTrainingPriorities times
    TimelinesForTrainingPriority = [[] for _ in range(numTrainingPriorities)]


    #######################################
    # This loop looks at each timeline in the current partition
    # Examine every timeline and decide which result class it is in.
    # This is tricky - a single timeline may have several different classes of result.
    # Get the first timeline
    startTimelinePosInFile = -1
    stopTimelinePosInFile = -1
    startPosFirstTimelineInPartition = -1
    stopPosLastTimelineInPartition = -1
    fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile = tdfReader.GotoFirstTimelineInPartition(
                                                                            startTimelinePosInFile, stopTimelinePosInFile, 
                                                                            currentPartitionStart, currentPartitionStop,
                                                                            False)  # fOnlyFindTimelineBoundaries
    while ((not fEOF) and (fFoundTimeline)):
        # On Preflight, we create a list of the timeline locations as well as the valid boundaries of the partition.
        # Record where we found the first timeline. We return this as the start of the first timeline in the partition.
        if (startPosFirstTimelineInPartition < 0):
            startPosFirstTimelineInPartition = startTimelinePosInFile
        # We always save the stop of the timeline, which will overwriting the previous iteration.
        # Eventually, on the last iteration, this will write this for the last time.
        if (stopTimelinePosInFile > 0):
            stopPosLastTimelineInPartition = stopTimelinePosInFile

        # Get a sequence of all data points for the current timeline. 
        numReturnedDataSets, inputArray, resultArray, dayNumArray = tdfReader.GetDataForCurrentTimeline(requirePropertyRelationList,
                                                                requirePropertyNameList,
                                                                requirePropertyValueList,
                                                                False,  # fAddMinibatchDimension
                                                                False,  # NeedTrueResultForEveryInput
                                                                preflightNumMissingInputsList)  # Count missing instances

        if (numReturnedDataSets >= 1):
            numSamples = inputArray.shape[0]
            for sampleNum in range(numSamples):
                job.PreflightData(inputArray[sampleNum], resultArray[sampleNum].item())
            # End - for sampleNum in range(numSamples):

            # This is tricky - a single timeline may have several different classes of result.
            # We consider the timeline to be in its most rare class.
            # The most rare class is class 0, and class 1 is second most rare class and so on.
            trainingPriority = -1
            for sampleNum in range(numSamples):
                currentResult = resultArray[sampleNum].item()
                # Be careful, results may sometimes be invalid if we are processing a
                # sequence. There may not be a result for every intermediate step, only
                # the last step.
                if (currentResult != tdf.TDF_INVALID_VALUE):
                    currentPriority = job.GetTrainingPriority(currentResult)
                    if ((trainingPriority < 0) or (currentPriority < trainingPriority)):
                        trainingPriority = currentPriority
                # End - if (currentResult != tdf.TDF_INVALID_VALUE):
            # End - for sampleNum in range(numSamples):

            if (trainingPriority >= 0):
                timelineInfoDict = {"a": startTimelinePosInFile, "b": stopTimelinePosInFile}
                TimelinesForTrainingPriority[trainingPriority].append(timelineInfoDict)
                timelinePositionList.append(timelineInfoDict)
            # if (trainingPriority >= 0):
        # End - if (numReturnedDataSets >= 1)

        # Go to the next timeline
        startTimelinePosInFile = -1
        stopTimelinePosInFile = -1
        fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile = tdfReader.GotoNextTimelineInPartition(startTimelinePosInFile, 
                                                                                                        stopTimelinePosInFile, 
                                                                                                        currentPartitionStop,
                                                                                                        False)  # fOnlyFindTimelineBoundaries
    # End - while ((not fEOF) and (fFoundTimeline)):

 
    tdfReader.Shutdown()

    job.SetPreflightNumMissingInputs(preflightNumMissingInputsList)

    return job, fEOF, startPosFirstTimelineInPartition, stopPosLastTimelineInPartition, timelinePositionList, TimelinesForTrainingPriority
# End - MLEngine_PreflightOneFilePartitionImpl






################################################################################
#
# [MLEngine_TrainOneFilePartitionImpl]
#
# This returns several results:
#   job
#   numTimelinesProcessed
#   totalSkippedTimelines
#   numDataPointsProcessed
#   fEOF - True iff we hit the end of the file
#
################################################################################
def MLEngine_TrainOneFilePartitionImpl(job, currentPartitionStart, currentPartitionStop, 
                                       localNeuralNet, localLossFunction, localOptimizer, 
                                       fUsePytorch, cudaIsAvailable, gpuDevice, TimelinesForTrainingPriority):
    fDebug = False
    
    tdfFilePathName = job.GetDataParam("TrainData", "")
    inputNameListStr = job.GetNetworkInputVarNames()
    resultValueName = job.GetNetworkOutputVarName()
    _, requirePropertyRelationList, requirePropertyNameList, requirePropertyValueList = job.GetFilterProperties()
    if (fDebug):
        print("MLEngine_TrainOneFilePartitionImpl. currentPartitionStart = " + str(currentPartitionStart))
        print("     currentPartitionStop = " + str(currentPartitionStop))

    # Open the file in the worker process address space
    tdfReader = tdf.TDF_CreateTDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                                            requirePropertyNameList)
    maxDaysWithZeroValue = tdfReader.GetMaxDaysWithZeroValue()

    # Get some properties that are used for each training.
    lossTypeStr = job.GetTrainingParamStr(mlJob.TRAINING_OPTION_LOSS_FUNCTION_ELEMENT_NAME, "").lower()
    priorityPolicy = job.GetTrainingParamStr(mlJob.TRAINING_OPTION_RESULT_PRIORITY_POLICY_ELEMENT_NAME, "").lower()

    fEveryInputMakesPrediction = localNeuralNet.NeedTrueResultForEveryInput()

    # In some cases, we add a batches dimension to all data:
    #   Pytorch wants data in the form: (NumSamples x NumBatches x NumFeatures)
    #   XGBoost wants data in the form: (NumSamples x NumFeatures)
    fAddMinibatchDimension = True
 
    # Compute the list lengths. These are the lists of timelines for each resault priority.
    # Also, randomize the order of each of the timeline lists
    numTrainingPriorities = job.GetNumTrainingPriorities()
    NumTimelinesAtEachPriority = [0] * numTrainingPriorities
    maxNumPtsAtAnyPriority = 0
    for index in range(numTrainingPriorities):
        timelineList = TimelinesForTrainingPriority[index]

        # Count
        numTimelinesAtCurrentPriority = len(timelineList)
        NumTimelinesAtEachPriority[index] = numTimelinesAtCurrentPriority
        if (numTimelinesAtCurrentPriority >= maxNumPtsAtAnyPriority):
            maxNumPtsAtAnyPriority = numTimelinesAtCurrentPriority

        # Randomize
        random.shuffle(timelineList)
        TimelinesForTrainingPriority[index] = timelineList
    # End - for index in range(numTrainingPriorities):

    if (fDebug):
        print("MLEngine_TrainOneFilePartitionImpl")
        print("    NumTimelinesAtEachPriority=" + str(NumTimelinesAtEachPriority))
        print("    TimelinesForTrainingPriority=" + str(TimelinesForTrainingPriority))

    # Now, train one timeline from each level of data priority.
    # The more rare results are higher priority which is a lower index.
    # So, priority 0 is the highest priority and most rare.
    numTimelinesProcessed = 0
    numDataPointsProcessed = 0
    for timelineIndexAtEachPriority in range(maxNumPtsAtAnyPriority):
        numPrioritiesProcessed = 0
        for priorityLevel in range(numTrainingPriorities):
            ptList = TimelinesForTrainingPriority[priorityLevel]
            if (timelineIndexAtEachPriority < NumTimelinesAtEachPriority[priorityLevel]):                
                timelineInfo = ptList[timelineIndexAtEachPriority]
                numPrioritiesProcessed += 1

                tdfReader.GotoNextTimelineInPartition(timelineInfo["a"], timelineInfo["b"], -1, False)
                numReturnedDataSets, inputArray, resultArray, dayNumArray = tdfReader.GetDataForCurrentTimeline(requirePropertyRelationList,
                                                                                    requirePropertyNameList,
                                                                                    requirePropertyValueList,
                                                                                    fAddMinibatchDimension,
                                                                                    fEveryInputMakesPrediction,
                                                                                    None)
                if (numReturnedDataSets >= 1):
                    if (fDebug):
                        print("MLEngine_TrainOneFilePartitionInChildProcess")
                        print("     maxDaysWithZeroValue=" + str(maxDaysWithZeroValue))
                        print("     fEveryInputMakesPrediction=" + str(fEveryInputMakesPrediction))
                        print("     numReturnedDataSets=" + str(numReturnedDataSets))
                        print("     inputArray=" + str(inputArray))
                        print("     resultArray=" + str(resultArray))

                    localNeuralNet.CheckState(job)
                    MLEngine_TrainGroupOfDataPoints(job, localNeuralNet, localLossFunction, localOptimizer, 
                                                    lossTypeStr, fUsePytorch, cudaIsAvailable, gpuDevice,
                                                    inputArray, resultArray, dayNumArray,
                                                    numReturnedDataSets, fAddMinibatchDimension, 
                                                    maxDaysWithZeroValue)
                    localNeuralNet.CheckState(job)

                    numTimelinesProcessed += 1
                    numDataPointsProcessed += numReturnedDataSets
                # if (numReturnedDataSets >= 1):
            # End - if (timelineIndexAtEachPriority < NumTimelinesAtEachPriority[priorityLevel]):
        # End - for priorityLevel in range(numTrainingPriorities):

        # Stop processing when one of several conditions are met
        #    Only the most common timeline is left
        #    There are no timelines left
        if (numPrioritiesProcessed <= 1):
            break
    # End - for timelineIndexAtEachPriority in range(maxNumPtsAtAnyPriority):

    tdfReader.Shutdown()
    localNeuralNet.CheckState(job)

    return job, numTimelinesProcessed, numDataPointsProcessed
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

    fEveryInputMakesPrediction = localNeuralNet.NeedTrueResultForEveryInput()

    # Open the file in the worker address space
    tdfReader = tdf.TDF_CreateTDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                                            requirePropertyNameList)
    maxDaysWithZeroValue = tdfReader.GetMaxDaysWithZeroValue()

    #######################################
    # This loop looks at each timeline in the current partition
    # Unlike training, the order does not matter. The arrays are not changing
    # and We compute the accuracy for every timeline, no matter the order.
    numTimelinesProcessed = 0
    fFoundTimeline, fEOF, _, _ = tdfReader.GotoFirstTimelineInPartition(-1, -1, currentPartitionStart, currentPartitionStop, False)
    while ((not fEOF) and (fFoundTimeline)):
        # Get all data points for a single timeline. 
        numReturnedDataSets, inputArray, resultArray, dayNumArray = tdfReader.GetDataForCurrentTimeline(requirePropertyRelationList,
                                                                            requirePropertyNameList,
                                                                            requirePropertyValueList,
                                                                            fAddMinibatchDimension,
                                                                            fEveryInputMakesPrediction,
                                                                            None)
        if (numReturnedDataSets >= 1):
            if (fDebug):
                print("MLEngine_TestOneFilePartitionImpl. numReturnedDataSets=" + str(numReturnedDataSets))
            MLEngine_TestGroupOfDataPoints(job, localNeuralNet, fUsePytorch, cudaIsAvailable, gpuDevice,
                                           inputArray, resultArray, dayNumArray,
                                           numReturnedDataSets, fAddMinibatchDimension, 
                                           networkOutputDataType, maxDaysWithZeroValue)
        # End - if (numReturnedDataSets >= 1):

        # Go to the next timeline in this partition
        numTimelinesProcessed += 1
        fFoundTimeline, fEOF, _, _ = tdfReader.GotoNextTimelineInPartition(-1, -1, currentPartitionStop, False)
    # End - while ((not fEOF) and (fFoundTimeline)):

    tdfReader.Shutdown()

    return job, numTimelinesProcessed, fEOF
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
    elif (valStr in ("deepnet", "multilevelnet")):
        localNeuralNet = MLEngine_DeepNeuralNet(job)
    elif (valStr == "lstm"):
        localNeuralNet = MLEngine_LSTMNeuralNet(job)
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
    lossTypeStr = job.GetTrainingParamStr(mlJob.TRAINING_OPTION_LOSS_FUNCTION_ELEMENT_NAME, "").lower()
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
def MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, numTimelinesProcessed, numSkippedTimelines, numDataPointsProcessed,
                                            fEOF, startPosFirstTimelineInPartition, stopPosLastTimelineInPartition, 
                                            err, timelinePositionList):
    resultDict = {'jobStr': "", 
                'numTimelinesProcessed': numTimelinesProcessed, 
                'numSkippedTimelines': numSkippedTimelines,
                'numDataPointsProcessed': numDataPointsProcessed,
                'fEOF': fEOF, 
                'startValidData': startPosFirstTimelineInPartition, 
                'stopValidData': stopPosLastTimelineInPartition, 
                'err': err, 
                'timelinePositionList': timelinePositionList}
    if (job is not None):
        resultDict['jobStr'] = job.WriteJobToString()

    sendPipeEnd.send(resultDict)

    sendPipeEnd.close()
# End - MLEngine_ReturnResultsFromChildProcess






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
def MLEngine_TrainOneFilePartitionInChildProcess(sendPipeEnd, jobStr,
                                            currentPartitionStart, currentPartitionStop,
                                            TimelinesForTrainingPriorityStr):
    global g_ChildProcessPipe
    g_ChildProcessPipe = sendPipeEnd
    totalSkippedTimelines = 0
    fDebug = False

    #<> Debugging Only!
    torch.autograd.set_detect_anomaly(True)

    if (fDebug):
        print("MLEngine_TrainOneFilePartitionInChildProcess start.")
        print("     currentPartitionStart = " + str(currentPartitionStart))
        print("     currentPartitionStop = " + str(currentPartitionStop))

    # Regenerate the runtime job object from its serialized string form. 
    job = mlJob.MLJob_CreateMLJobFromString(jobStr)

    # Convert other strings passed accross address spaces to a runtime data structure.
    TimelinesForTrainingPriority = json.loads(TimelinesForTrainingPriorityStr)

    # Create the neural network in this address space.
    localNeuralNet = MLEngine_CreateNeuralNetFromJobSpec(job)
    if (localNeuralNet is None):
        if (fDebug):
            print("MLEngine_TrainOneFilePartitionInChildProcess Failed making neural net.")
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
            gpuDevice = torch.device('cuda')
            if ((numGPUs <= 0) or (gpuDevice is None)):
                cudaIsAvailable = False
        # End - if (cudaIsAvailable):
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
            learningRate = float(job.GetTrainingParamStr(mlJob.TRAINING_OPTION_LEARNING_RATE, "0.1"))
            if (learningRate == 0):
                ASSERT_ERROR("MLEngine_TrainOneFilePartitionInChildProcess. 0 Learning Rate")

            localOptimizer = optim.SGD(localNeuralNet.parameters(), lr=learningRate)
        elif (optimizerType == "adam"):
            learningRate = float(job.GetTrainingParamStr(mlJob.TRAINING_OPTION_LEARNING_RATE, "0.1"))
            if (learningRate == 0):
                ASSERT_ERROR("MLEngine_TrainOneFilePartitionInChildProcess. Error. 0 Learning Rate")

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
    if (localOptimizer is not None):
        valStr = job.GetNamedStateAsStr(mlJob.RUNTIME_OPTIMIZER_STATE, "")
        if (valStr != ""):
            #print("Restore optimizer state: " + str(valStr))
            stateBytes = bytearray.fromhex(valStr)
            ioBuffer = io.BytesIO(stateBytes)
            stateDict = torch.load(ioBuffer)
            localOptimizer.load_state_dict(stateDict)
        # End - if (valStr != ""):
    # End - if (localOptimizer is not None):

    localNeuralNet.CheckState(job)


    # Do the actual work. 
    job, numTimelinesProcessed, numDataPointsProcessed = MLEngine_TrainOneFilePartitionImpl(job, 
                                                                    currentPartitionStart, currentPartitionStop,
                                                                    localNeuralNet, localLossFunction, localOptimizer,
                                                                    fUsePytorch, cudaIsAvailable, gpuDevice, 
                                                                    TimelinesForTrainingPriority)

    localNeuralNet.CheckState(job)


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
    #print("Save optimizer state: " + str(valStr))
    job.SetNamedStateAsStr(mlJob.RUNTIME_OPTIMIZER_STATE, valStr)

    # Send the results back to the control process.
    MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, numTimelinesProcessed, totalSkippedTimelines, numDataPointsProcessed,
                                            False, currentPartitionStart, currentPartitionStop,
                                            E_NO_ERROR, "")

    if (fDebug):
        print("MLEngine_TrainOneFilePartitionInChildProcess. Finished. nonceNum = " + str(job.GetNonce()))
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
    numTimelinesProcessed = 0
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
    job, numTimelinesProcessed, fEOF = MLEngine_TestOneFilePartitionImpl(job, currentPartitionStart, 
                                                                        currentPartitionStop, localNeuralNet,
                                                                        fUsePytorch, cudaIsAvailable, gpuDevice)

    MLEngine_ReturnResultsFromChildProcess(sendPipeEnd, job, numTimelinesProcessed, 0, 0, fEOF, -1, -1, E_NO_ERROR, "")

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

    job.StartPreflight()

    # Get a dictionary of partitions for the file.
    # Initially, this dictionary is in order, so the nth entry in the dictionary is
    # the nth partition, and adjacent entries are adjacent in the file. We will first go
    # through the file in this sequence, but shuffle it on later epochs.
    trainTDFFilePathName = job.GetDataParam("TrainData", "")
    partitionList = tdf.CreateFilePartitionList(trainTDFFilePathName, partitionSize)

    #######################################
    # This loop looks at each partition in the file. One partition is 
    # a large chunk of data and may contain many timelines.
    partitionCount = 0
    nextPartitionStartPosition = -1
    for partitionInfo in partitionList:
        # If we shifted the previous partition, then adjust the current partition
        # to start after the shifted previous partition.
        if (nextPartitionStartPosition > 0):
            partitionInfo['start'] = nextPartitionStartPosition
            partitionInfo['stop'] = nextPartitionStartPosition + partitionSize

        # This will overwrite timelinePositionList.
        job, _, _, stopPosLastTimeline, timelinePositionList, TimelinesForTrainingPriority = MLEngine_PreflightOneFilePartitionImpl(job, partitionInfo['start'], partitionInfo['stop'])
        if (fDebug):
            print("MLEngine_PreflightNeuralNet. timelinePositionList=" + str(timelinePositionList))
            print("MLEngine_PreflightNeuralNet. TimelinesForTrainingPriority=" + str(TimelinesForTrainingPriority))

        # We build up a list of timeline positions during preflight.
        # We reuse this list on all training epochs to quickly load timelines.
        timelinePositionListStr = json.dumps(timelinePositionList)
        TimelinesForTrainingPriorityStr = json.dumps(TimelinesForTrainingPriority)

        # Update the data to show where this ends, and where to find all timelines in this partition.
        partitionInfo['stop'] = stopPosLastTimeline
        partitionInfo['ptListStr'] = timelinePositionListStr
        partitionInfo['ptPriorityListStr'] = TimelinesForTrainingPriorityStr

        # The next position will start immediately after this one ends.
        nextPartitionStartPosition = stopPosLastTimeline

        partitionCount += 1
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
def MLEngine_TrainNeuralNet(job, partitionSize):
    fDebug = False
    childProcessErr = E_NO_ERROR

    # Get a dictionary of partitions for the file.
    # Initially, this dictionary is in order, so the nth entry in the dictionary is
    # the nth partition, and adjacent entries are adjacent in the file. We will first go
    # through the file in this sequence, but may shuffle it on later epochs.
    job, partitionList = MLEngine_PreflightNeuralNet(job, partitionSize)

    print("=================\nTraining:")
    job.StartTraining()

    numEpochs = job.GetTrainingParamInt("NumEpochs", 1)

    #######################################
    # TRAINING - Iterate once for each Epoch
    for epochNum in range(numEpochs):
        if (fDebug):
            print("\n\n\n\n ==================================\nEpoch: " 
                    + str(epochNum) + "\n\n\n")
        job.StartTrainingEpoch()
        
        #######################################
        # This loop looks at each partition in the file. One partition is 
        # a large chunk of data and may contain many timelines.
        partitionCount = 0
        for partitionInfo in partitionList:
            # Get information about the current file Partition.
            # On the first epoch, this is still being updated as we find the timeline boundaries in the file.
            currentPartitionStart = partitionInfo['start']
            currentPartitionStop = partitionInfo['stop']
            TimelinesForTrainingPriorityStr = partitionInfo['ptPriorityListStr']

            # Make a pipe that will be used to return the results. 
            recvPipeEnd, sendPipeEnd = multiprocessing.Pipe(False)

            # Prepare the arguments to go to the worker process.
            # This may be another process on this machine or else a remote process on another server.
            jobStr = job.WriteJobToString()

            # Fork the job process.
            processInfo = Process(target=MLEngine_TrainOneFilePartitionInChildProcess, args=(sendPipeEnd, 
                                                        jobStr, 
                                                        currentPartitionStart, currentPartitionStop, 
                                                        TimelinesForTrainingPriorityStr))
            processInfo.start()

            # Wait for the job process to finish and get the results.
            resultDict = recvPipeEnd.recv()
            if (fDebug):
                print("MLEngine_TrainNeuralNet. Got result back from child process")

            numTimelinesProcessed = resultDict['numTimelinesProcessed']
            numSkippedTimelines = resultDict['numSkippedTimelines']
            numDataPointsProcessed = resultDict['numDataPointsProcessed']
            childProcessErr = resultDict['err']
            jobStr = resultDict['jobStr']
            if ((jobStr is not None) and (jobStr != "")):
                job.ReadJobFromString(jobStr)
            if (fDebug):
                print("MLEngine_TrainNeuralNet. numTimelinesProcessed=" + str(numTimelinesProcessed))

            # Wait for the process to complete.
            processInfo.join()
            if (fDebug):
                print("MLEngine_TrainNeuralNet. join finished")

            if (fDebug):
                print("MLEngine_TrainNeuralNet")
                print("    numTimelinesProcessed = " + str(numTimelinesProcessed))
                print("    numDataPointsProcessed = " + str(numDataPointsProcessed))
                print("    childProcessErr = " + str(childProcessErr))


            if (childProcessErr == E_ASSERT_ERROR):
                break

            # Update the results. These are (roughly) the same for each Epoch, so we only update
            # it once, on the first Epoch.
            if (epochNum == 0):
                job.SetNumTimelinesTrainedPerEpoch(job.GetNumTimelinesTrainedPerEpoch() + numTimelinesProcessed)
                job.SetNumTimelinesSkippedPerEpoch(job.GetNumTimelinesSkippedPerEpoch() + numSkippedTimelines)
                job.SetNumDataPointsPerEpoch(job.GetNumDataPointsPerEpoch() + numDataPointsProcessed)

            partitionCount += 1
        # End - for partitionInfo in partitionList:

        job.FinishTrainingEpoch()
        
        if (childProcessErr == E_ASSERT_ERROR):
            break

        # Some models (like XGBoost) cannot train different data at different times.
        # In these cases, we can only do 1 Epoch, and we try to process all data as a single partition.
        if (not job.TrainingCanPauseResume()):
            break

        # At the end of each partition, shuffle the partition list so we will
        # train the data in a different order on the next epoch.
        random.shuffle(partitionList)
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

    job.StartTesting()

    #######################################
    # This loop looks at each partition in the file. One partition is 
    # a large chunk of data and may contain many timelines.
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
    # End - while (not fEOF):

    # Return the updated job that has been changed by the child processes.
    return job
# End - MLEngine_TestNeuralNet()






################################################################################
#
# [MLEngine_RunJob]
#
# Train and test one job, described in a Job file
################################################################################
def MLEngine_RunJob(jobFilePathName, trainedJobFilePathName, fDebug):
    err = E_NO_ERROR

    # Open the job.
    jobErr, job = mlJob.MLJob_ReadExistingMLJob(jobFilePathName)
    if (mlJob.JOB_E_NO_ERROR != jobErr):
        print("MLEngine_RunJob. Error making network for " + jobFilePathName)
        return

    job.SetDebug(fDebug)

    MLEngine_Init_GPU()

    # Initialize the engine.
    job.StartJobExecution()

    # TODO: Make this a calculated value, depending on the memory size of the machine
    partitionSize = DEFAULT_PARTITION_SIZE

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
                partitionSize = DEFAULT_PARTITION_SIZE

        job, err = MLEngine_TrainNeuralNet(job, partitionSize)
    # End - if (trainTDFFilePathName != ""):

    if (err == E_NO_ERROR):
        testTDFFilePathName = job.GetDataParam("TestData", "")
        if (testTDFFilePathName != ""):
            job = MLEngine_TestNeuralNet(job, DEFAULT_PARTITION_SIZE)

    # <><><> xxxxxxxxxxxxxx
    #print("\n\n\n\nMLEngine_RunJob - BAIL DUDE!!!!\n\n\n")
    #raise Exception()

    job.FinishJobExecution(err, " ")

    if ((trainedJobFilePathName is not None) 
            and (trainedJobFilePathName != "")):
        job.SaveAs(trainedJobFilePathName)

    JobShow.JobShow_WriteReport(job, JobShow.MLJOB_CONSOLE_REPORT, "")
    JobShow.JobShow_WriteReport(job, JobShow.MLJOB_LOG_REPORT, "")
    #JobShow.JobShow_WriteReport(job, MLJOB_FILE_REPORT, "/home/ddean/ddRoot/trainingResults.txt")
    #JobShow.JobShow_WriteReport(job, MLJOB_FILE_REPORT, "/home/ddean/ddRoot/trainingResults.csv")
# End - MLEngine_RunJob








