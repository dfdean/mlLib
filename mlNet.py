################################################################################
# 
# Copyright (c) 2020 Dawson Dean
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
# In a sense, this is the interpreter for the job object. It is the actual work
# of running a neural network.
#
# The job object is used to configure a neural network, but also as a means of 
# passing commands and results between processes, either two processes on a 
# single machine or else over a network from a controller machine to worker 
# compute servers.
#
################################################################################

import os
import sys
#import shutil
#import ntpath
#import configparser
import random
import math
import string
import time
from datetime import datetime

# Pytorch
import torch
import torch.nn as nn
import torch.optim as optim

# Multiprocessing
import torch.distributed as dist
from torch.multiprocessing import Process
import multiprocessing

# This file runs in the lib directory, so it does not need any special path to find 
# any other files in the lib dir.
from xmlTools import *
from tdfTools import *
from mlJob import *

random.seed(3)



################################################################################
# 
# SimpleOneLayerNeuralNet
# 
################################################################################
class SimpleOneLayerNeuralNet(nn.Module):
    #####################################################
    # Initialize the weight matrices
    #####################################################
    def __init__(self, job):
        super(SimpleOneLayerNeuralNet, self).__init__()

        inputNameListStr = job.GetRequestValueStr("InputValues", -1)
        inputNameList = inputNameListStr.split(',')
        self.inputSize = len(inputNameList)

        resultValueName = job.GetRequestValueStr("ResultValue", "")
        #print("resultValueName = " + resultValueName)
        self.outputSize = TDF_GetNumValuesForCategoryVariable(resultValueName)

        # Create the matrix of weights.
        # A nn.Linear is an object that contains a matrix A and bias vector b
        # It is used to compute (x * A-transpose) + b
        #    where x is the input, which is a vector with shape (1 x self.inputSize)
        #    or x is alternatively described as (rows=1, colums=self.inputSize). 
        #
        self.inputToOutput = nn.Linear(self.inputSize, self.outputSize)

        # Non-linearity. Use SoftMax as the last step
        # Softmax converts a vector of real numbers into a probability distribution
        #     y[i] = e**x[i] / SUM(e**x[j])
        # So, all y[i] add up to 1.
        # Each entry is the ratio of one exponent over the sum of all exponents.
        # The exponentiation operator e**x[i] makes everything non-negative, but it
        # also converts all variable ranges to an exponential progression. So, bugger values
        # become a lot bigger.
        #
        nonLinearTypeStr = job.GetRequestValueStr("NonLinearType", "").lower()
        if (nonLinearTypeStr == "logsoftmax"):
            self.outputNonLinearLayer = nn.LogSoftmax(dim=1)
        else:
            self.outputNonLinearLayer = None
    # End - __init__



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.forward]
    #
    # Forward prop.
    # This will leavs pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #####################################################
    def forward(self, input, hidden):
        # Compute the output
        output = self.inputToOutput(input)

        if (self.outputNonLinearLayer != None):
            output = self.outputNonLinearLayer(output)

        return output, hidden
    # End - forward



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.initHidden]
    #
    # Reset the hidden state.
    # This is used each time we start a new sequence of inputs
    # Each sequence of inputs starts from an initial state.
    # One training sequence does not convey any information about 
    # another training sequence.
    # As a result, the order we train the input sequences does not matter.
    #####################################################
    def initHidden(self):
        return torch.zeros(1, 1)
    # End - initHidden



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.xxx]
    #
    #####################################################
    def ShouldBatchNetInputs(self):
        return False
    # End - ShouldBatchNetInputs



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.xxx]
    #
    #####################################################
    def MinNumDataPointsPerBatch(self):
        return 1
    # End - MinNumDataPointsPerBatch



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.xxx]
    #
    #####################################################
    def GetInputSize(self):
        return self.inputSize
    # End - GetInputSize


    #####################################################
    #
    # [SimpleOneLayerNeuralNet.SaveNeuralNetWeights]
    #
    #####################################################
    def SaveNeuralNetWeights(self, job):
        #print("SaveNeuralNetWeights")
        MLNet_SaveLinearUnitToJob(self.inputToOutput, job, "inputToOutput")
    # End - SaveNeuralNetWeights



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        #print("RestoreNetState")

        restoredTensor = MLNet_ReadLinearUnitFromJob(job, "inputToOutput")
        #print("RestoreNetState. inputToOutput-restoredTensor=" + str(restoredTensor))
        if (None != restoredTensor):
            self.inputToOutput = restoredTensor
    # End - RestoreNetState



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.CheckState]
    # 
    #####################################################
    def CheckState(self):
        self.CheckLinearUnit(self.inputToOutput, "inputToOutput")
    # End - CheckState



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.CheckLinearUnit]
    # 
    #####################################################
    def CheckLinearUnit(self, linearUnit, name):
        weightMatrix = linearUnit.weight.detach().numpy()
        biasMatrix = linearUnit.bias.detach().numpy()

        numRows = len(weightMatrix)
        for rowNum in range(numRows):
            row = weightMatrix[rowNum]
            for numVal in row:
                if (math.isnan(numVal)):
                    print("ERROR!!!!! NaN detected in " + name)
                    print("forward. weightMatrix=" + str(weightMatrix))
                    print("forward. biasMatrix=" + str(biasMatrix))
                    sys.exit(0)

        for numVal in biasMatrix:
            if (math.isnan(numVal)):
                print("ERROR!!!!! NaN detected in " + name)
                print("forward. weightMatrix=" + str(weightMatrix))
                print("forward. biasMatrix=" + str(biasMatrix))
                sys.exit(0)
    # End - CheckLinearUnit



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.PrintState]
    #
    #####################################################
    def PrintState(self):
        weightMatrix = self.inputToOutput.weight.detach().numpy()
        biasMatrix = self.inputToOutput.bias.detach().numpy()
        print("inputToOutput.weightMatrix = " + str(weightMatrix))
        print("inputToOutput.biasMatrix = " + str(biasMatrix))
    # End - PrintState
# class SimpleOneLayerNeuralNet(nn.Module):








################################################################################
# 
# CBasicOneLayerRNN
# 
# This RNN module is just 2 linear layers which operate on an input and 
# hidden state, with a LogSoftmax layer after the output
#
################################################################################
class CBasicOneLayerRNN(nn.Module):
    #####################################################
    # Initialize the weight matrices
    #####################################################
    def __init__(self, job):
        super(CBasicOneLayerRNN, self).__init__()

        inputNameListStr = job.GetRequestValueStr("InputValues", -1)
        inputNameList = inputNameListStr.split(',')
        self.inputSize = len(inputNameList)

        resultValueName = job.GetRequestValueStr("ResultValue", "")
        #print("resultValueName = " + resultValueName)
        self.outputSize = TDF_GetNumValuesForCategoryVariable(resultValueName)

        self.hiddenSize = job.GetRequestValueInt("HiddenLayerSize", 128)

        # Create the matrix of weights.
        # A nn.Linear is an object that contains a matrix A and bias vector b
        # It is used to compute (x * A-transpose) + b
        #    where x is the input, which is a vector with shape (1 x self.inputSize)
        #    or x is alternatively described as (rows=1, colums=self.inputSize). 
        #
        self.inputToHidden = nn.Linear(self.inputSize + self.hiddenSize, self.hiddenSize)
        self.inputToOutput = nn.Linear(self.inputSize + self.hiddenSize, self.outputSize)

        # Non-linearity. Use SoftMax as the last step
        # Softmax converts a vector of real numbers into a probability distribution
        #     y[i] = e**x[i] / SUM(e**x[j])
        # So, all y[i] add up to 1.
        # Each entry is the ratio of one exponent over the sum of all exponents.
        # The exponentiation operator e**x[i] makes everything non-negative, but it
        # also converts all variable ranges to an exponential progression. So, bugger values
        # become a lot bigger.
        #
        nonLinearTypeStr = job.GetRequestValueStr("NonLinearType", "").lower()
        if (nonLinearTypeStr == "logsoftmax"):
            self.outputNonLinearLayer = nn.LogSoftmax(dim=1)
        else:
            self.outputNonLinearLayer = None
    # End - __init__



    #####################################################
    #
    # [CBasicOneLayerRNN.forward]
    #
    # Forward prop.
    # This will leavs pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #####################################################
    def forward(self, input, hidden):
        #print("forward. hidden.size=" + str(hidden.size()))
        #print("forward. input.size=" + str(input.size()))

        # Combine the input and current hidden state to make a single input vector.
        combinedInput = torch.cat((input, hidden), 1)

        # Compute the next hidden state
        hidden = self.inputToHidden(combinedInput)

        #print("forward. self.inputToOutput.weight=" + str(self.inputToOutput.weight))
        #print("forward. self.inputToOutput.bias=" + str(self.inputToOutput.bias))

        # Compute the output
        output = self.inputToOutput(combinedInput)

        if (self.outputNonLinearLayer != None):
            output = self.outputNonLinearLayer(output)

        return output, hidden
    # End - forward



    #####################################################
    #
    # [CBasicOneLayerRNN.initHidden]
    #
    # Reset the hidden state.
    # This is used each time we start a new sequence of inputs
    # Each sequence of inputs starts from an initial state.
    # One training sequence does not convey any information about 
    # another training sequence.
    # As a result, the order we train the input sequences does not matter.
    #####################################################
    def initHidden(self):
        return torch.zeros(1, self.hiddenSize)
    # End - initHidden



    #####################################################
    #
    # [CBasicOneLayerRNN.xxx]
    #
    #####################################################
    def ShouldBatchNetInputs(self):
        return False
    # End - ShouldBatchNetInputs



    #####################################################
    #
    # [CBasicOneLayerRNN.xxx]
    #
    #####################################################
    def MinNumDataPointsPerBatch(self):
        return 1
    # End - MinNumDataPointsPerBatch


    #####################################################
    #
    # [CBasicOneLayerRNN.xxx]
    #
    #####################################################
    def GetInputSize(self):
        return self.inputSize
    # End - GetInputSize


    #####################################################
    #
    # [CBasicOneLayerRNN.SaveNeuralNetWeights]
    #
    #####################################################
    def SaveNeuralNetWeights(self, job):
        #print("SaveNeuralNetWeights")

        MLNet_SaveLinearUnitToJob(self.inputToHidden, job, "inputToHidden")
        MLNet_SaveLinearUnitToJob(self.inputToOutput, job, "inputToOutput")
    # End - SaveNeuralNetWeights



    #####################################################
    #
    # [CBasicOneLayerRNN.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        #print("RestoreNetState")

        restoredTensor = MLNet_ReadLinearUnitFromJob(job, "inputToHidden")
        #print("RestoreNetState. inputToHidden-restoredTensor=" + str(restoredTensor))
        if (None != restoredTensor):
            self.inputToHidden = restoredTensor

        restoredTensor = MLNet_ReadLinearUnitFromJob(job, "inputToOutput")
        #print("RestoreNetState. inputToOutput-restoredTensor=" + str(restoredTensor))
        if (None != restoredTensor):
            self.inputToOutput = restoredTensor
    # End - RestoreNetState



    #####################################################
    #
    # [CBasicOneLayerRNN.CheckState]
    # 
    #####################################################
    def CheckState(self):
        self.CheckLinearUnit(self.inputToHidden, "inputToHidden")
        self.CheckLinearUnit(self.inputToOutput, "inputToOutput")
    # End - CheckState



    #####################################################
    #
    # [CBasicOneLayerRNN.CheckLinearUnit]
    # 
    #####################################################
    def CheckLinearUnit(self, linearUnit, name):
        weightMatrix = linearUnit.weight.detach().numpy()
        biasMatrix = linearUnit.bias.detach().numpy()

        numRows = len(weightMatrix)
        for rowNum in range(numRows):
            row = weightMatrix[rowNum]
            for numVal in row:
                if (math.isnan(numVal)):
                    print("ERROR!!!!! NaN detected in " + name)
                    print("forward. weightMatrix=" + str(weightMatrix))
                    print("forward. biasMatrix=" + str(biasMatrix))
                    sys.exit(0)

        for numVal in biasMatrix:
            if (math.isnan(numVal)):
                print("ERROR!!!!! NaN detected in " + name)
                print("forward. weightMatrix=" + str(weightMatrix))
                print("forward. biasMatrix=" + str(biasMatrix))
                sys.exit(0)
    # End - CheckLinearUnit



    #####################################################
    #
    # [CBasicOneLayerRNN.PrintState]
    #
    #####################################################
    def PrintState(self):
        weightMatrix = self.inputToHidden.weight.detach().numpy()
        biasMatrix = self.inputToHidden.bias.detach().numpy()
        print("inputToHidden.weightMatrix = " + str(weightMatrix))
        print("inputToHidden.biasMatrix = " + str(biasMatrix))

        weightMatrix = self.inputToOutput.weight.detach().numpy()
        biasMatrix = self.inputToOutput.bias.detach().numpy()
        print("inputToOutput.weightMatrix = " + str(weightMatrix))
        print("inputToOutput.biasMatrix = " + str(biasMatrix))
    # End - PrintState
# class CBasicOneLayerRNN(nn.Module):







#####################################################
#
# [PrintVector]
#
#####################################################
def PrintVector(message, vectorTensor):
    vectorMatrix = vectorTensor.detach().numpy()
    print(message + str(vectorMatrix))
# End - PrintVector




################################################################################
#
# [MLNet_SaveLinearUnitToJob]
#
################################################################################
def MLNet_SaveLinearUnitToJob(linearUnit, job, name):
    #print("MLNet_SaveLinearUnitToJob. name=" + str(name))
    #print("MLNet_SaveLinearUnitToJob. linearUnit=" + str(linearUnit))

    #print("MLNet_SaveLinearUnitToJob. linearUnit.weight=" + str(linearUnit.weight))
    #print("MLNet_SaveLinearUnitToJob. linearUnit.bias=" + str(linearUnit.bias))

    weightMatrix = linearUnit.weight.detach().numpy()
    biasMatrix = linearUnit.bias.detach().numpy()
    #print("MLNet_SaveLinearUnitToJob. weightMatrix=" + str(weightMatrix))
    #print("MLNet_SaveLinearUnitToJob. biasMatrix=" + str(biasMatrix))

    job.SetNeuralNetLinearUnitMatrices(name, weightMatrix, biasMatrix)
# End - MLNet_SaveLinearUnitToJob





################################################################################
#
# [MLNet_ReadLinearUnitFromJob]
#
################################################################################
def MLNet_ReadLinearUnitFromJob(job, name):
    fFoundIt, weightMatrix, biasMatrix = job.GetNeuralNetLinearUnitMatrices(name)
    if (not fFoundIt):
        return None

    weightTensor = torch.tensor(weightMatrix, dtype=torch.float32)
    biasTensor = torch.tensor(biasMatrix, dtype=torch.float32)
    weightSize = weightTensor.size()
    inputSize = weightSize[1]
    outputSize = weightSize[0]
    #print("MLNet_ConvertStringsToLinearUnit.  inputSize = " + str(inputSize))
    #print("MLNet_ConvertStringsToLinearUnit.  outputSize = " + str(outputSize))

    linearUnit = nn.Linear(inputSize, outputSize)
    linearUnit.weight = torch.nn.Parameter(weightTensor)
    linearUnit.bias = torch.nn.Parameter(biasTensor)

    return linearUnit
# End - MLNet_ConvertStringsToLinearUnit






################################################################################
#
# [DMS_TrainOneDataSequence]
# 
################################################################################
def DMS_TrainOneDataSequence(job, localNeuralNet, localLossFunction, localOptimizer,
                         inputGroupSequenceTensor, trueResultTensor, numDataSamples):
    #print("DMS_TrainOneDataSequence. numDataSamples=" + str(numDataSamples))
    #print("DMS_TrainOneDataSequence. inputGroupSequenceTensor.size=" + str(inputGroupSequenceTensor.size()))
    #print("DMS_TrainOneDataSequence. numDataSamples=" + str(numDataSamples))

    epochNum = job.GetEpochNum()
    #print("DMS_TrainOneDataSequence. EpochNum=" + str(epochNum))

    learningRate = float(job.GetRequestValueStr("LearningRate", 0.1))
    #print("DMS_TrainOneDataSequence. learningRate=" + str(learningRate))

    # Create initial hidden state. This also clears out any hidden state 
    # left over from a previous training sequence.
    hiddenState = localNeuralNet.initHidden()
    #print("DMS_TrainOneDataSequence. hiddenState.size=" + str(hiddenState.size()))

    #print("DMS_TrainOneDataSequence. Iterate samples. numDataSamples=" + str(numDataSamples))
    totalLoss = 0.0
    for index in range(numDataSamples):
        #print("=====================================")
        #print("DMS_TrainOneDataSequence. index=" + str(index))

        # Initianlize the gradients to 0
        if (localOptimizer != None):
            localOptimizer.zero_grad()
        else:
            localNeuralNet.zero_grad()

        if (epochNum == 1):
            #print("DMS_TrainOneDataSequence. index=" + str(index))
            localNeuralNet.CheckState()

        if (False and (epochNum == 1) and (index >= 172)):
            print("State before forward:")
            localNeuralNet.PrintState()
            PrintVector("Hidden State: ", hiddenState)
            PrintVector("Input: ", inputGroupSequenceTensor[index])

        # We pass in a 2-dimensional tensor for both the input and hidden state.
        # The first dimension is the batch, which is always a single value
        # The second dimension is the valueIndex, which identifies which value.
        # This is essentially a 1-dimensional array, since the batch index is always 0.
        #print("DMS_TrainOneDataSequence. Process one sample")
        #print("Input tensor=" + str(inputGroupSequenceTensor[index]))
        output, hiddenState = localNeuralNet.forward(inputGroupSequenceTensor[index], hiddenState)
        #print("DMS_TrainOneDataSequence. output=" + str(output))
        #print("DMS_TrainOneDataSequence. trueResultTensor=" + str(trueResultTensor))
        #print("DMS_TrainOneDataSequence. output.type=" + str(type(output)))
        #print("DMS_TrainOneDataSequence. output.size=" + str(output.size()))
        #print("DMS_TrainOneDataSequence. trueResultTensor.type=" + str(type(trueResultTensor)))
        #print("DMS_TrainOneDataSequence. trueResultTensor.size=" + str(trueResultTensor.size()))

        loss = localLossFunction(output, trueResultTensor[index][0])
        #print("DMS_TrainOneDataSequence. loss.type=" + str(type(loss)))
        #print("DMS_TrainOneDataSequence. loss.size=" + str(loss.size()))
        #print("DMS_TrainOneDataSequence. loss=" + str(loss))
        #print("DMS_TrainOneDataSequence. loss.data=" + str(loss.data))
        #print("DMS_TrainOneDataSequence. loss.data.item()=" + str(loss.data.item()))

        if (False and (epochNum == 1) and (index >= 172)):
            print("DMS_TrainOneDataSequence. After forward but before backprop:")
            localNeuralNet.PrintState()
            PrintVector("Hidden State: ", hiddenState)
            PrintVector("Input: ", inputGroupSequenceTensor[index])
            print("DMS_TrainOneDataSequence. predictedClass=" + str(predictedClass) + ", actualClass=" + str(actualClass))
            print("DMS_TrainOneDataSequence. loss=" + str(loss))
            print("DMS_TrainOneDataSequence. loss.data=" + str(loss.data))
            print("DMS_TrainOneDataSequence. loss.data.item()=" + str(loss.data.item()))

        # Back-propagate. 
        # This function generates the gradients.
        # This is implemented by the base class, but it uses a
        # train of dependencies that was saved when the subclass computed the forward pass.
        # We call this on the loss value, but it kept pointers to the neural network that
        # calculated it. Additionally, each variable in the neural network recorded which
        # vectors and weights were used to compute it, so we can traverse the network in 
        # reverse order, from outputs back to inputs.
        loss.backward(retain_graph=True)

        # Compare output to target. This is the loss, which will be
        # used to adjust the weights on back propagation.
        actualClass = trueResultTensor[index][0][0].data.item()
        topValue, topIndex = output.topk(1)
        #???? predictedClass = topIndex[0].item()
        predictedClass = topValue[0].item()
        #print("DMS_TrainOneDataSequence. predictedClass=" + str(predictedClass) + ", actualClass=" + str(actualClass))
        job.RecordTrainingLoss(loss.data.item())
        job.RecordTrainingForFutureEvent(actualClass, predictedClass)


        #print("Computing gradients")
        if (localOptimizer != None):
            localOptimizer.step()
        else:
            if (index >= 2):
                gradientIndex = 0
                for currentParam in localNeuralNet.parameters():
                    currentParam.data.add_(-learningRate, currentParam.grad.data)
                    # Save a copy of the gradient.
                    #currentGrad = totalGradientList[gradientIndex]
                    #currentGrad = currentGrad + currentParam.grad.data
                    #print("currentGrad=" + str(currentGrad))
                    #totalGradientList[gradientIndex] = currentGrad
                    #gradientIndex += 1


        if (False and (epochNum == 1) and (index >= 172)):
            print("State After forward:")
            localNeuralNet.PrintState()
            PrintVector("Hidden State: ", hiddenState)
    # End - for index in range(numDataSamples):

    #print("DMS_TrainOneDataSequence: job=" + str(job))
    return job
# End - DMS_TrainOneDataSequence






################################################################################
#
# [DMS_TestOneDataSequence]
#
################################################################################
def DMS_TestOneDataSequence(job, localNeuralNet, inputGroupSequenceTensor, 
                            trueResultTensor, numDataSamples):
    # Create initial hidden state. This also clears out any hidden state 
    # left over from a previous training sequence.
    hiddenState = localNeuralNet.initHidden()

    # Read each group of labs in and run the RNN on the current lab group
    # Each iteration processes the next vector in the sequence of states.
    # Each vector represents a single group of labs
    # This gerates the next hidden state, which we keep for processing the next inputs
    # Notice, we can stop after any number of states and make a best guess at that moment.
    for index in range(numDataSamples):
        # We pass in a 2-dimensional tensor for both the input and hidden state.
        # The first dimension is the batch, which is always a single value
        # The second dimension is the valueIndex, which identifies which value.
        # This is essentially a 1-dimensional array, since the batch index is always 0.
        output, hiddenState = localNeuralNet.forward(inputGroupSequenceTensor[index], hiddenState)

        #print(">>>output = " + str(output))
        #print(">>>output.len = " + str(len(output)))
        #print(">>>output.size() = " + str(output.size()))
        #print(">>>resultTensor = " + str(resultTensor))
        #print(">>>resultTensor.size() = " + str(resultTensor.size()))
        actualClass = trueResultTensor[index][0][0].data.item()
        topValue, topIndex = output.topk(1)
        predictedClass = topIndex[0].item()

        #print("actualClass: " + str(actualClass))
        #print("predictedClass: " + str(predictedClass))
        job.RecordTestingResultForFutureEvent(actualClass, predictedClass)
        # End - for index in range(numDataSamples):    
    # Look at each result

    return job
# End - DMS_TestOneDataSequence





################################################################################
#
# [TDF_DataSetListContainsInterestingValue]
#
################################################################################
def TDF_DataSetListContainsInterestingValue(resultTensor, numDataSamples, resultValueName):
    for index in range(numDataSamples):
        resultVal = resultTensor[index][0][0].data.item()
        if ((resultVal > TDF_FUTURE_EVENT_NOW_OR_PAST) and (resultVal < TDF_FUTURE_EVENT_NOT_IN_10YRS)):
            return(True)

    return(False)
# End - TDF_DataSetListContainsInterestingValue




################################################################################
#
# [DMS_TrainOneFilePartition]
#
# This returns one value: fEOF
#   fEOF - True iff we hit the end of the file
#
#            # Add the gradients
#            if (totalGradientList == None):
#                totalGradientList = currentGradientList
#            else:
#                numGradients = len(currentGradientList)
#                for gradientIndex in range(numGradients):
#                    #print("gradientIndex=" + str(gradientIndex))
#                    totalGradient = totalGradientList[gradientIndex]
#                    newGradient = currentGradientList[gradientIndex]
#                    totalGradient = totalGradient + newGradient
#                    totalGradientList[gradientIndex] = totalGradient
################################################################################
def DMS_TrainOneFilePartition(job, currentPartitionStart, currentPartitionStop, 
                            clipNumPatients, localNeuralNet, localLossFunction, 
                            localOptimizer, localScheduler):
    tdfFilePathName = job.GetDataParam("TrainData")
    inputNameListStr = job.GetRequestValueStr("InputValues", -1)
    resultValueName = job.GetRequestValueStr("ResultValue", -1)
    windowStartEvent = job.GetRequestValueStr("WindowStartEvent", "")
    windowStopEvent = job.GetRequestValueStr("WindowStopEvent", "")
    resultTypeStr = job.GetRequestValueStr("ResultValueType", "")
    #print("DMS_TrainOneFilePartition. inputNameListStr=" + str(inputNameListStr))
    #print("DMS_TrainOneFilePartition. resultValueName=" + str(resultValueName))
    #print("DMS_TrainOneFilePartition. windowStartEvent=" + str(windowStartEvent))
    #print("DMS_TrainOneFilePartition. windowStopEvent=" + str(windowStopEvent))
    #print("DMS_TrainOneFilePartition. clipNumPatients=" + str(clipNumPatients))
    #print("DMS_TrainOneFilePartition. EpochNum=" + str(job.GetEpochNum()))

    tdfReader = TDF_CreateTDFFileReader(tdfFilePathName)
    #print("DMS_TrainOneFilePartition. Opened TDF file")
    fEOF = False
    numPatientsProcessed = 0

    #######################################
    # This loop looks at each patient in the current partition
    fFoundPatient, fEOF = tdfReader.GotoFirstPatientInPartition(currentPartitionStart, currentPartitionStop)
    while ((not fEOF) and (fFoundPatient)):
        #print("DMS_TrainOneFilePartition. Found Patient. fEOF=" + str(fEOF) + ", fFoundPatient=" + str(fFoundPatient))
        #job.Log("DMS_TrainOneFilePartition. Found Patient. fEOF=" + str(fEOF) + ", fFoundPatient=" + str(fFoundPatient))

        #######################################
        # This loop looks at each event window in the current patient
        fFoundWindow = tdfReader.SetFirstDataWindow(windowStartEvent, [], windowStopEvent, [])
        while (fFoundWindow):
            # Get all data points for the next window.
            # This is a sequence of data points for a single patient. 
            # We are programming a recurrent neural net, so we process all data points in a sequence.
            numReturnedDataSets, inputTensor, resultTensor = tdfReader.GetDataFromCurrentWindow(inputNameListStr, 
                                                                                    resultValueName, "NormInt0-100", 24)
            # There must be at least N values. 
            # The hidden state is initialized on the first set of values, 
            # and then the gradient of the intiial state is not available
            # until we have done at least 2 sets of data. If we only use one data set
            # then the gradients are not valid and we fail when updating the weights.
            # So....if there is only 1 data set, then pass it through the neural net twice.
            if (numReturnedDataSets < localNeuralNet.MinNumDataPointsPerBatch()):
                fFoundWindow = tdfReader.SetNextDataWindow()
                continue
            if (not TDF_DataSetListContainsInterestingValue(resultTensor, numReturnedDataSets, resultValueName)):
                fFoundWindow = tdfReader.SetNextDataWindow()
                continue

            print("DMS_TrainOneFilePartition. numReturnedDataSets=" + str(numReturnedDataSets))
            #print("!!!Valid sequence")
            #print("DMS_TrainOneFilePartition. inputTensor.size=" + str(inputTensor.size()))
            #print("DMS_TrainOneFilePartition. resultTensor.size=" + str(resultTensor.size()))
            #print("DMS_TrainOneFilePartition. inputTensor=" + str(inputTensor))
            #print("DMS_TrainOneFilePartition. resultTensor=" + str(resultTensor))

            job = DMS_TrainOneDataSequence(job, localNeuralNet, localLossFunction, localOptimizer,
                                          inputTensor, resultTensor, numReturnedDataSets)

            fFoundWindow = tdfReader.SetNextDataWindow()
            #print("DMS_TrainOneFilePartition. fFoundWindow = " + str(fFoundWindow))
        # End - while (fFoundWindow):

        # Go to the next patient in this partition
        numPatientsProcessed += 1
        if ((clipNumPatients > 0) and (numPatientsProcessed >= clipNumPatients)):
            #print("DMS_TrainOneFilePartition. Stop at clipped number patients. numPatientsProcessed=" + str(numPatientsProcessed))
            break

        fFoundPatient, fEOF = tdfReader.GotoNextPatientInPartition(currentPartitionStop)
        #print("TrainOneFilePartition. fEOF=" + str(fEOF))
    # End - while ((not fEOF) and (fFoundPatient)):

    tdfReader.Shutdown()
    return job, numPatientsProcessed, fEOF
# End - DMS_TrainOneFilePartition







################################################################################
#
# [DMS_TestOneFilePartition]
#
# This returns one value: fEOF
#   fEOF - True iff we hit the end of the file
#
################################################################################
def DMS_TestOneFilePartition(job, currentPartitionStart, currentPartitionStop, 
                             clipNumPatients, localNeuralNet):
    tdfFilePathName = job.GetDataParam("TestData")
    inputNameListStr = job.GetRequestValueStr("InputValues", -1)
    resultValueName = job.GetRequestValueStr("ResultValue", -1)
    windowStartEvent = job.GetRequestValueStr("WindowStartEvent", "")
    windowStopEvent = job.GetRequestValueStr("WindowStopEvent", "")
    resultTypeStr = job.GetRequestValueStr("ResultValueType", "")
    #print("DMS_TestOneFilePartition. inputNameListStr=" + str(inputNameListStr))
    #print("DMS_TestOneFilePartition. resultValueName=" + str(resultValueName))
    #print("DMS_TestOneFilePartition. windowStartEvent=" + str(windowStartEvent))
    #print("DMS_TestOneFilePartition. windowStopEvent=" + str(windowStopEvent))

    tdfReader = TDF_CreateTDFFileReader(tdfFilePathName)
    #print("DMS_TestOneFilePartition. Opened TDF file")
    fEOF = False
    numPatientsProcessed = 0

    #######################################
    # This loop looks at each patient in the current partition
    fFoundPatient, fEOF = tdfReader.GotoFirstPatientInPartition(currentPartitionStart, currentPartitionStop)
    while ((not fEOF) and (fFoundPatient)):
        #job.Log("Found Patient. fEOF=" + str(fEOF) + ", fFoundPatient=" + str(fFoundPatient))

        #######################################
        # This loop looks at each event window in the current patient
        fFoundWindow = tdfReader.SetFirstDataWindow(windowStartEvent, [], windowStopEvent, [])
        while (fFoundWindow):
            # Get all data points for the next prediction.
            # This is a sequence of data points for a single patient. 
            # We are programming a recurrent neural net, so we process all data points in a sequence.
            numReturnedDataSets, inputTensor, resultTensor = tdfReader.GetDataFromCurrentWindow(inputNameListStr, 
                                                                                    resultValueName, "NormInt0-100", 24)

            # There must be at least N values. 
            # The hidden state is initialized on the first set of values, 
            # and then the gradient of the intiial state is not available
            # until we have done at least 2 sets of data. If we only use one data set
            # then the gradients are not valid and we fail when updating the weights.
            # So....if there is only 1 data set, then pass it through the neural net twice.
            if (numReturnedDataSets < localNeuralNet.MinNumDataPointsPerBatch()):
                fFoundWindow = tdfReader.SetNextDataWindow()
                continue
            if (not TDF_DataSetListContainsInterestingValue(resultTensor, numReturnedDataSets, resultValueName)):
                fFoundWindow = tdfReader.SetNextDataWindow()
                continue

            #print("DMS_TestOneFilePartition. numReturnedDataSets=" + str(numReturnedDataSets))
            job = DMS_TestOneDataSequence(job, localNeuralNet, inputTensor, 
                                        resultTensor, numReturnedDataSets)

            fFoundWindow = tdfReader.SetNextDataWindow()
            #print("fFoundWindow = " + str(fFoundWindow))
        # End - while (fFoundWindow):

        # Go to the next patient in this partition
        numPatientsProcessed += 1
        if ((clipNumPatients > 0) and (numPatientsProcessed >= clipNumPatients)):
            break

        fFoundPatient, fEOF = tdfReader.GotoNextPatientInPartition(currentPartitionStop)
    # End - while ((not fEOF) and (fFoundPatient)):

    tdfReader.Shutdown()
    return job, numPatientsProcessed, fEOF
# End - DMS_TestOneFilePartition()






################################################################################
#
# [DMS_CreateNeuralNetFromJobSpec]
#
################################################################################
def DMS_CreateNeuralNetFromJobSpec(sendPipeEnd, job, debugCmd):
    # Create the neural network in this address space.
    valStr = job.GetRequestValueStr("NetworkType", -1).lower()
    #print("NetworkType=" + valStr)
    if (valStr == "simplenet"):
        localNeuralNet = SimpleOneLayerNeuralNet(job)
    elif (valStr == "tinyrnn"):
        sys.exit(0)
        localNeuralNet = SimpleOneLayerNeuralNet(job)
        #localNeuralNet = CBasicTwoLayerRNN(job)
    elif (valStr == "lstm"):
        sys.exit(0)
        localNeuralNet = CBasicLSTMRNN(job)
    else:
        job.FinishJobExecution(False, "DMS_RunMLJob. Invalid NeuralNet type:" + valStr)
        jobStr = job.WriteJobToString(True)
        resultDict = {}
        resultDict['jobStr'] = jobStr
        resultDict['numPatientsProcessed'] = numPatientsProcessed
        resultDict['fEOF'] = fEOF
        sendPipeEnd.send(resultDict)
        sendPipeEnd.close()
        return None

    # Restore the network matrices
    localNeuralNet.RestoreNetState(job)

    return localNeuralNet
# End - DMS_CreateNeuralNetFromJobSpec






################################################################################
#
# [DMS_TrainOneFilePartitionInChildProcess]
#
# This runs in a worker process, which may be another process on the same machine
# or else a process on a remote server on the network.
# All inputs and outputs are passed as strings and integers.
# The job is serialized/deserialized as a string of XML text, so it can be passed
# as a parameter string, modified, then returned as a result string.
################################################################################
def DMS_TrainOneFilePartitionInChildProcess(sendPipeEnd, jobStr, currentPartitionStart, 
                                    currentPartitionStop, clipNumPatients, debugCmd):
    #print("DMS_TrainOneFilePartitionInChildProcess")
    #print("DMS_TrainOneFilePartitionInChildProcess. jobStr=" + jobStr)
    numPatientsProcessed = 0
    fEOF = False

    # Regenerate the runtime job object from its serialized string form. 
    job = MLJob_CreateMLJobFromString(jobStr)

    # Create the neural network in this address space.
    localNeuralNet = DMS_CreateNeuralNetFromJobSpec(sendPipeEnd, job, debugCmd)
    if (None == localNeuralNet):
        return

    # Define the loss function
    #    For categorization, use nn.NLLLoss because the last layer of the RNN is nn.LogSoftmax
    #    For the loss function, use nn.BCELoss because the last layer of the RNN is nn.Sigmoid
    lossTypeStr = job.GetRequestValueStr("LossFunction", "")
    if (lossTypeStr == "NLLLoss"):
        localLossFunction = nn.NLLLoss()
    elif (lossTypeStr == "BCELoss"):
        localLossFunction = nn.BCELoss()
    else:
        job.FinishJobExecution(False, "DMS_RunMLJob. Invalid LossFunction type:" + lossTypeStr)
        jobStr = job.WriteJobToString(True)
        resultDict = {}
        resultDict['jobStr'] = jobStr
        resultDict['numPatientsProcessed'] = numPatientsProcessed
        resultDict['fEOF'] = fEOF
        sendPipeEnd.send(resultDict)
        sendPipeEnd.close()
        return

    # Optionally, create an optimizer. If there is none, then we can
    # explicitly apply the gradients ourselves. This is nicer when using
    # multiple worker processes, because each process returns a gradient tensor.
    learningRate = float(job.GetRequestValueStr("LearningRate", 0.1))
    #print("DMS_RunMLJob. learningRate=" + str(learningRate))
    optimizerType = job.GetRequestValueStr("Optimizer", -1)
    #print("DMS_RunMLJob. optimizerType=" + optimizerType)
    if (optimizerType == "SGD"):
        print("Making SGD optimizer")
        localOptimizer = optim.SGD(localNeuralNet.parameters(), lr=learningRate)
        localScheduler = torch.optim.lr_scheduler.StepLR(localOptimizer, 1, gamma=0.9)
    elif (optimizerType == "None"):
        localOptimizer = None
        localScheduler = None
    else:
        job.FinishJobExecution(False, "DMS_RunMLJob. Invalid optimizer type:" + optimizerType)
        jobStr = job.WriteJobToString(True)
        resultDict = {}
        resultDict['jobStr'] = jobStr
        resultDict['numPatientsProcessed'] = numPatientsProcessed
        resultDict['fEOF'] = fEOF
        sendPipeEnd.send(resultDict)
        sendPipeEnd.close()
        return

    ###############################
    # DEBUG
    if ((debugCmd == "CheckSavedState") and (job.HasTestMatrix("SampleInput", "input"))):
        print("Restore debug state")
        testInputArray = job.GetTestMatrix("SampleInput", "input")
        testInput = torch.tensor(testInputArray, dtype=torch.float32)
        print("testInput=" + str(testInput))
        hiddenState = localNeuralNet.initHidden()
        localNeuralNet.zero_grad()
        output, hiddenState = localNeuralNet.forward(testInput, hiddenState)
        print("output=" + str(output))
        job.CheckTestMatrix("SampleInput", "output", output.detach().numpy())

    # Do the actual work
    job, numPatientsProcessed, fEOF = DMS_TrainOneFilePartition(job, currentPartitionStart, 
                                                            currentPartitionStop, clipNumPatients, 
                                                            localNeuralNet, localLossFunction, 
                                                            localOptimizer, localScheduler)

    # During training, we optionally save the updated weights to the job, for later use.
    #print("Saving Neural Net State")
    localNeuralNet.SaveNeuralNetWeights(job)
    #print("Finished saving Neural Net State")

    ###############################
    # DEBUG
    if (debugCmd == "CheckSavedState"):
        print("Saving debug state")
        inputSize = localNeuralNet.GetInputSize()
        testInput = torch.rand((1, inputSize), dtype=torch.float32)
        print("testInput=" + str(testInput))
        job.SetTestMatrix("SampleInput", "input", testInput.detach().numpy())
        hiddenState = localNeuralNet.initHidden()
        localNeuralNet.zero_grad()
        output, hiddenState = localNeuralNet.forward(testInput, hiddenState)
        job.SetTestMatrix("SampleInput", "output", output.detach().numpy())
        print("output=" + str(output))


    # Send the results back to the control process.
    jobStr = job.WriteJobToString(True)
    resultDict = {}
    resultDict['jobStr'] = jobStr
    resultDict['numPatientsProcessed'] = numPatientsProcessed
    resultDict['fEOF'] = fEOF
    sendPipeEnd.send(resultDict)
    sendPipeEnd.close()

    # Return and exit the process.
# End - DMS_TrainOneFilePartitionInChildProcess





################################################################################
#
# [DMS_TestOneFilePartitionInChildProcess]
#
# This runs in a worker process, which may be another process on the same machine
# or else a process on a remote server on the network.
# All inputs and outputs are passed as strings and integers.
# The job is serialized/deserialized as a string of XML text, so it can be passed
# as a parameter string, modified, then returned as a result string.
################################################################################
def DMS_TestOneFilePartitionInChildProcess(sendPipeEnd, jobStr, currentPartitionStart,
                                       currentPartitionStop, clipNumPatients, debugCmd):
    #print("DMS_TestOneFilePartitionInChildProcess")
    numPatientsProcessed = 0
    fEOF = False

    # Regenerate the runtime job object from its serialized string form. 
    job = MLJob_CreateMLJobFromString(jobStr)

    # Create the neural network in this address space.
    localNeuralNet = DMS_CreateNeuralNetFromJobSpec(sendPipeEnd, job, debugCmd)
    if (None == localNeuralNet):
        return

    ###############################
    # DEBUG
    if ((debugCmd == "CheckSavedState") and (job.HasTestMatrix("SampleInput", "input"))):
        print("Restore debug state")
        testInputArray = job.GetTestMatrix("SampleInput", "input")
        testInput = torch.tensor(testInputArray, dtype=torch.float32)
        print("testInput=" + str(testInput))
        hiddenState = localNeuralNet.initHidden()
        localNeuralNet.zero_grad()
        output, hiddenState = localNeuralNet.forward(testInput, hiddenState)
        print("output=" + str(output))
        job.CheckTestMatrix("SampleInput", "output", output.detach().numpy())

    # Do the actual work
    job, numPatientsProcessed, fEOF = DMS_TestOneFilePartition(job, currentPartitionStart, 
                                                currentPartitionStop, clipNumPatients,
                                                localNeuralNet)

    # Send the results back to the control process.
    jobStr = job.WriteJobToString(True)
    resultDict = {}
    resultDict['jobStr'] = jobStr
    resultDict['numPatientsProcessed'] = numPatientsProcessed
    resultDict['fEOF'] = fEOF
    sendPipeEnd.send(resultDict)
    sendPipeEnd.close()

    # Return and exit the process.
# End - DMS_TestOneFilePartitionInChildProcess






################################################################################
#
# [DMS_TrainNeuralNet]
#
################################################################################
def DMS_TrainNeuralNet(job, partitionSize):
    print("=======================")
    print("Training:")

    job.StartTraining()

    numEpochs = job.GetRequestValueInt("NumEpochs", 1)
    clipNumPatients = job.GetRequestValueInt("ClipNumTrainPatients", -1)
    #print("DMS_TrainNeuralNet. numEpochs=" + str(numEpochs))
    #print("DMS_TrainNeuralNet. clipNumPatients=" + str(clipNumPatients))


    #######################################
    # Iterate one for each Epoch
    for epochNum in range(numEpochs):
        print("Epoch " + str(epochNum))
        job.StartTrainingEpoch()

        numRemainingPatientsInEpoch = -1
        if (clipNumPatients > 0):
            numRemainingPatientsInEpoch = clipNumPatients

        debugCmd = "CheckSavedState"

        #######################################
        # This loop looks at each partition in the file. One partition is 
        # a large chunk of data and may contain many patients.
        fEOF = False
        currentPartitionStart = 0
        currentPartitionStop = currentPartitionStart + partitionSize
        while (not fEOF):
            job.Log("Start Partition. StartPos=" + str(currentPartitionStart))

            # Make a pipe that will be used to return the results. 
            recvPipeEnd, sendPipeEnd = multiprocessing.Pipe(False)

            # Prepare the arguments to go to the worker process.
            # Thia may be another process on this machine or else a remote process on another server.
            jobStr = job.WriteJobToString(True)
            #print("DMS_TrainNeuralNet jobStr=" + str(jobStr))

            # Fork the job process.
            processInfo = Process(target=DMS_TrainOneFilePartitionInChildProcess, args=(sendPipeEnd, jobStr, 
                                                    currentPartitionStart, currentPartitionStop, 
                                                    numRemainingPatientsInEpoch, debugCmd))
            processInfo.start()

            # Get the results.
            resultDict = recvPipeEnd.recv()
            #print("DMS_TrainNeuralNet. Got result back from child process")

            jobStr = resultDict['jobStr']
            numPatientsProcessed = resultDict['numPatientsProcessed']
            fEOF = resultDict['fEOF']
            job.ReadJobFromString(jobStr)
            #print("DMS_TrainNeuralNet. jobStr=" + str(jobStr))
            #print("DMS_TrainNeuralNet. numPatientsProcessed=" + str(numPatientsProcessed))
            #print("DMS_TrainNeuralNet. fEOF=" + str(fEOF))

            # Wait for the process to complete.
            processInfo.join()

            # If we only want to process a limited number of patients, then stop if we
            # have reached the limit.
            if (clipNumPatients > 0):
                numRemainingPatientsInEpoch = numRemainingPatientsInEpoch - numPatientsProcessed
                if (numRemainingPatientsInEpoch <= 0):
                    #print("DMS_TrainNeuralNet. Stop at clipped patients. numRemainingPatientsInEpoch=" + str(numRemainingPatientsInEpoch))
                    break
            #print("DMS_TrainNeuralNet. numRemainingPatientsInEpoch=" + str(numRemainingPatientsInEpoch))
            # End - if (clipNumPatients > 0):

            # Go to the next partition
            currentPartitionStart = currentPartitionStop
            currentPartitionStop = currentPartitionStart + partitionSize
        # End - while (not fEOF):

        job.FinishTrainingEpoch()
    # End - for epochNum in range(numEpochs):

    job.FinishTraining()
    job.PrintTrainingStats()

    # Return the updated job that has been changed by the child processes.
    return job
# End - DMS_TrainNeuralNet()








################################################################################
#
# [DMS_TestNeuralNet]
#
################################################################################
def DMS_TestNeuralNet(job, partitionSize):
    #print("DMS_TestNeuralNet. Start Testing:")

    job.StartTesting()

    clipNumPatients = job.GetRequestValueInt("ClipNumTestPatients", -1)
    numRemainingPatients = -1
    if (clipNumPatients > 0):
        numRemainingPatients = clipNumPatients

    debugCmd = ""

    #######################################
    # This loop looks at each partition in the file. One partition is 
    # a large chunk of data and may contain many patients.
    fEOF = False
    currentPartitionStart = 0
    currentPartitionStop = currentPartitionStart + partitionSize
    while (not fEOF):
        job.Log("Start Partition. StartPos=" + str(currentPartitionStart))

        # Make a pipe that will be used to return the results. 
        recvPipeEnd, sendPipeEnd = multiprocessing.Pipe(False)

        # Prepare the arguments to go to the worker process.
        # This may be another process on this machine or else a remote process on another server.
        jobStr = job.WriteJobToString(True)
        #print("DMS_TestNeuralNet jobStr=" + str(jobStr))

        # Fork the job process.
        processInfo = Process(target=DMS_TestOneFilePartitionInChildProcess, args=(sendPipeEnd, jobStr, 
                                                    currentPartitionStart, currentPartitionStop,
                                                    numRemainingPatients, debugCmd))
        processInfo.start()

        # Get the results.
        resultDict = recvPipeEnd.recv()

        jobStr = resultDict['jobStr']
        numPatientsProcessed = resultDict['numPatientsProcessed']
        fEOF = resultDict['fEOF']
        job.ReadJobFromString(jobStr)
        #print("numPatientsProcessed=" + str(numPatientsProcessed))
        #print("numRemainingPatients=" + str(numRemainingPatients))
        #print("fEOF=" + str(fEOF))

        # Wait for the process to complete.
        processInfo.join()

        # If we only want to process a limited number of patients, then stop if we
        # have reached the limit.
        if (clipNumPatients > 0):
            numRemainingPatients = numRemainingPatients - numPatientsProcessed
            if (numRemainingPatients <= 0):
                break
        # End - if (clipNumPatients > 0):

        # Go to the next partition
        currentPartitionStart = currentPartitionStop
        currentPartitionStop = currentPartitionStart + partitionSize
    # End - while (not fEOF):

    job.FinishTesting()
    job.PrintTestingStats()

    # Return the updated job that has been changed by the child processes.
    return job
# End - DMS_TestNeuralNet()






################################################################################
#
# [DMS_RunMLJob]
#
################################################################################
def DMS_RunMLJob(filePathName):
    # Open the job.
    job = MLJob_ReadExistingMLJob(filePathName)

    job.SelectFirstRequestVariant()
    job.DiscardPastResults()
    job.StartNewResult()

    # Initialize the engine.
    job.StartJobExecution()

    partitionSize = 2 * (1024 * 1024)

    trainTDFFilePathName = job.GetDataParam("TrainData")
    if (trainTDFFilePathName != ""):
        job = DMS_TrainNeuralNet(job, partitionSize)

    testTDFFilePathName = job.GetDataParam("TestData")
    if (testTDFFilePathName != ""):
        job = DMS_TestNeuralNet(job, partitionSize)

    job.FinishJobExecution(True, "")
    if (not job.GetJobControlBool("SaveNetState", False)):
        job.RemoveAllSavedState()

    job.SaveAs("/home/ddean/ddRoot/tools/modifiedJob.txt")
# End - DMS_RunMLJob




################################################################################
# TEST CODE
################################################################################
def MLNet_UnitTest():
    Test_StartModuleTest("MLNet")

    Test_StartTest("Run BVTJob1")
    filePathName = "/home/ddean/ddRoot/tools/BVTJob1.txt"
    DMS_RunMLJob(filePathName)
# End - MLNet_UnitTest


#       TimeUntil_Dialysis
#       TimeUntil_CKD5
#       TimeUntil_CKD4
#       TimeUntil_CKD3
#       TimeUntil_CKD1
#       TimeUntil_CKD
#       TimeUntil_ESRD
#       TimeUntil_MELD10
#       TimeUntil_MELD20
#       TimeUntil_MELD30
#       TimeUntil_MELD40
#       TimeUntil_Cirrhosis
#       TimeUntil_ESLD
#       TimeUntil_AKIResolution
#       TimeUntil_AKI




