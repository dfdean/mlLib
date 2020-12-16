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
#import string

# Pytorch
import torch
import torch.nn as nn
import torch.optim as optim

# Multiprocessing
from torch.multiprocessing import Process
import multiprocessing

# This file runs in the lib directory, so it does not need any special path to find 
# any other files in the lib dir.
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
        self.NumInputVars = len(inputNameList)
        #print("self.NumInputVars=" + str(self.NumInputVars))

        resultValueName = job.GetRequestValueStr("ResultValue", "")
        #print("resultValueName = " + resultValueName)
        
        self.NumOutputCategories = TDF_GetNumClassesForVariable(resultValueName)
        #print("numOutputCategories = " + str(numOutputCategories))

        # Create the matrix of weights.
        # A nn.Linear is an object that contains a matrix A and bias vector b
        # It is used to compute (x * A-transpose) + b
        #    where x is the input, which is a vector with shape (1 x self.NumInputVars)
        #    or x is alternatively described as (rows=1, colums=self.NumInputVars). 
        #
        self.inputToOutput = nn.Linear(self.NumInputVars, self.NumOutputCategories)

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
        #print("nonLinearTypeStr = " + nonLinearTypeStr)
        if (nonLinearTypeStr == "logsoftmax"):
            self.outputNonLinearLayer = nn.LogSoftmax(dim=1)
        elif (nonLinearTypeStr == "none"):
            self.outputNonLinearLayer = None
        else:
            self.outputNonLinearLayer = None
            print("Error! SimpleOneLayerNeuralNet.__init__ found unrecognized non-linear type: " + nonLinearTypeStr)
            return
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
        #return torch.zeros(1, 1)
        return None
    # End - initHidden



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.ShouldBatchNetInputs]
    #
    #####################################################
    def ShouldBatchNetInputs(self):
        return False
    # End - ShouldBatchNetInputs



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.MinNumDataPointsPerBatch]
    #
    #####################################################
    def MinNumDataPointsPerBatch(self):
        return 1
    # End - MinNumDataPointsPerBatch



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.GetInputSize]
    #
    #####################################################
    def GetInputSize(self):
        return self.NumInputVars
    # End - GetInputSize


    #####################################################
    #
    # [SimpleOneLayerNeuralNet.SaveNeuralNetWeights]
    #
    #####################################################
    def SaveNeuralNetWeights(self, job):
        #print("SaveNeuralNetWeights")
        MLEngine_SaveLinearUnitToJob(self.inputToOutput, job, "inputToOutput")
    # End - SaveNeuralNetWeights



    #####################################################
    #
    # [SimpleOneLayerNeuralNet.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        #print("RestoreNetState")

        restoredTensor = MLEngine_ReadLinearUnitFromJob(job, "inputToOutput")
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
# MultiLayerNeuralNet
# 
################################################################################
class MultiLayerNeuralNet(nn.Module):
    #####################################################
    # Initialize the weight matrices
    #####################################################
    def __init__(self, job):
        super(MultiLayerNeuralNet, self).__init__()

        inputNameListStr = job.GetRequestValueStr("InputValues", -1)
        inputNameList = inputNameListStr.split(',')
        self.NumInputVars = len(inputNameList)

        resultValueName = job.GetRequestValueStr("ResultValue", "")
        #print("resultValueName = " + resultValueName)
        
        self.NumOutputCategories = TDF_GetNumClassesForVariable(resultValueName)
        #print("numOutputCategories = " + str(numOutputCategories))

        # The network will look like:
        #
        #    Inputs -> [InputToVec1] -> Vec1
        #                    -> [Vec1ToVec2] -> Vec2
        #                    -> [Vec2ToOutput] -> outputs
        #
        self.Vec1Size = self.NumInputVars * 2
        self.Vec2Size = self.NumOutputCategories * 4
        #print("MultiLayerNeuralNet.__init__: NumInputVars=" + str(self.NumInputVars))
        #print("MultiLayerNeuralNet.__init__: Vec1Size=" + str(self.Vec1Size))
        #print("MultiLayerNeuralNet.__init__: Vec2Size=" + str(self.Vec2Size))

        # Create the matrices of weights
        # A nn.Linear is an object that contains a matrix A and bias vector b
        # It is used to compute (x * A-transpose) + b
        #    where x is the input, which is a vector with shape (1 x self.NumInputVars)
        #    or x is alternatively described as (rows=1, colums=self.NumInputVars). 
        #
        self.InputToVec1 = nn.Linear(self.NumInputVars, self.Vec1Size)
        self.Vec1ToVec2 = nn.Linear(self.Vec1Size, self.Vec2Size)
        self.Vec2ToOutput = nn.Linear(self.Vec2Size, self.NumOutputCategories)

        # Make the non-linear units between linear layers
        #    ReLU(x) = max(0,x)
        self.Vec1NonLinear = torch.nn.ReLU()
        self.Vec2NonLinear = torch.nn.ReLU()

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
        #print("nonLinearTypeStr = " + nonLinearTypeStr)
        if (nonLinearTypeStr == "logsoftmax"):
            self.outputNonLinearLayer = nn.LogSoftmax(dim=1)
        elif (nonLinearTypeStr == "none"):
            self.outputNonLinearLayer = None
        else:
            self.outputNonLinearLayer = None
            print("Error! MultiLayerNeuralNet.__init__ found unrecognized non-linear type: " + nonLinearTypeStr)
            return
    # End - __init__



    #####################################################
    #
    # [MultiLayerNeuralNet.forward]
    #
    # Forward prop.
    # This will leave pointers for all of the dependencies, 
    # so backward propagation can be done by the base class.
    #####################################################
    def forward(self, input, hidden):
        # The network will look like:
        #
        #    Inputs -> [InputToVec1] -> Vec1
        #                    -> [Vec1ToVec2] -> Vec2
        #                    -> [Vec2ToOutput] -> outputs
        #
        vec1 = self.InputToVec1(input)
        vec1 = self.Vec1NonLinear(vec1)

        vec2 = self.Vec1ToVec2(vec1)
        vec2 = self.Vec2NonLinear(vec2)

        output = self.Vec2ToOutput(vec2)
        if (self.outputNonLinearLayer != None):
            output = self.outputNonLinearLayer(output)

        return output, hidden
    # End - forward



    #####################################################
    #
    # [MultiLayerNeuralNet.initHidden]
    #
    # Reset the hidden state.
    # This is used each time we start a new sequence of inputs
    # Each sequence of inputs starts from an initial state.
    # One training sequence does not convey any information about 
    # another training sequence.
    # As a result, the order we train the input sequences does not matter.
    #####################################################
    def initHidden(self):
        #return torch.zeros(1, 1)
        return None
    # End - initHidden



    #####################################################
    #
    # [MultiLayerNeuralNet.ShouldBatchNetInputs]
    #
    #####################################################
    def ShouldBatchNetInputs(self):
        return False
    # End - ShouldBatchNetInputs



    #####################################################
    #
    # [MultiLayerNeuralNet.MinNumDataPointsPerBatch]
    #
    #####################################################
    def MinNumDataPointsPerBatch(self):
        return 1
    # End - MinNumDataPointsPerBatch



    #####################################################
    #
    # [MultiLayerNeuralNet.GetInputSize]
    #
    #####################################################
    def GetInputSize(self):
        return self.NumInputVars
    # End - GetInputSize


    #####################################################
    #
    # [MultiLayerNeuralNet.SaveNeuralNetWeights]
    #
    #####################################################
    def SaveNeuralNetWeights(self, job):
        #print("SaveNeuralNetWeights")
        MLEngine_SaveLinearUnitToJob(self.InputToVec1, job, "InputToVec1")
        MLEngine_SaveLinearUnitToJob(self.Vec1ToVec2, job, "Vec1ToVec2")
        MLEngine_SaveLinearUnitToJob(self.Vec2ToOutput, job, "Vec2ToOutput")
    # End - SaveNeuralNetWeights



    #####################################################
    #
    # [MultiLayerNeuralNet.RestoreNetState]
    #
    #####################################################
    def RestoreNetState(self, job):
        #print("RestoreNetState")
        restoredTensor = MLEngine_ReadLinearUnitFromJob(job, "InputToVec1")
        if (None != restoredTensor):
            self.InputToVec1 = restoredTensor

        restoredTensor = MLEngine_ReadLinearUnitFromJob(job, "Vec1ToVec2")
        if (None != restoredTensor):
            self.Vec1ToVec2 = restoredTensor

        restoredTensor = MLEngine_ReadLinearUnitFromJob(job, "Vec2ToOutput")
        if (None != restoredTensor):
            self.Vec2ToOutput = restoredTensor
    # End - RestoreNetState



    #####################################################
    #
    # [MultiLayerNeuralNet.CheckState]
    # 
    #####################################################
    def CheckState(self):
        self.CheckLinearUnit(self.InputToVec1, "InputToVec1")
        self.CheckLinearUnit(self.Vec1ToVec2, "Vec1ToVec2")
        self.CheckLinearUnit(self.Vec2ToOutput, "Vec2ToOutput")
    # End - CheckState



    #####################################################
    #
    # [MultiLayerNeuralNet.CheckLinearUnit]
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
    # [MultiLayerNeuralNet.PrintState]
    #
    #####################################################
    def PrintState(self):
        weightMatrix = self.InputToVec1.weight.detach().numpy()
        biasMatrix = self.InputToVec1.bias.detach().numpy()
        print("InputToVec1.weightMatrix = " + str(weightMatrix))
        print("InputToVec1.biasMatrix = " + str(biasMatrix))

        weightMatrix = self.Vec1ToVec2.weight.detach().numpy()
        biasMatrix = self.Vec1ToVec2.bias.detach().numpy()
        print("Vec1ToVec2.weightMatrix = " + str(weightMatrix))
        print("Vec1ToVec2.biasMatrix = " + str(biasMatrix))

        weightMatrix = self.Vec2ToOutput.weight.detach().numpy()
        biasMatrix = self.Vec2ToOutput.bias.detach().numpy()
        print("Vec2ToOutput.weightMatrix = " + str(weightMatrix))
        print("Vec2ToOutput.biasMatrix = " + str(biasMatrix))
    # End - PrintState
# class MultiLayerNeuralNet(nn.Module):









################################################################################
#
# [MLEngine_SaveLinearUnitToJob]
#
################################################################################
def MLEngine_SaveLinearUnitToJob(linearUnit, job, name):
    #print("MLEngine_SaveLinearUnitToJob. name=" + str(name))
    #print("MLEngine_SaveLinearUnitToJob. linearUnit=" + str(linearUnit))

    #print("MLEngine_SaveLinearUnitToJob. linearUnit.weight=" + str(linearUnit.weight))
    #print("MLEngine_SaveLinearUnitToJob. linearUnit.bias=" + str(linearUnit.bias))

    weightMatrix = linearUnit.weight.detach().numpy()
    biasMatrix = linearUnit.bias.detach().numpy()
    #print("MLEngine_SaveLinearUnitToJob. weightMatrix=" + str(weightMatrix))
    #print("MLEngine_SaveLinearUnitToJob. biasMatrix=" + str(biasMatrix))

    job.SetNeuralNetLinearUnitMatrices(name, weightMatrix, biasMatrix)
# End - MLEngine_SaveLinearUnitToJob





################################################################################
#
# [MLEngine_ReadLinearUnitFromJob]
#
################################################################################
def MLEngine_ReadLinearUnitFromJob(job, name):
    fFoundIt, weightMatrix, biasMatrix = job.GetNeuralNetLinearUnitMatrices(name)
    if (not fFoundIt):
        return None

    weightTensor = torch.tensor(weightMatrix, dtype=torch.float32)
    biasTensor = torch.tensor(biasMatrix, dtype=torch.float32)
    weightSize = weightTensor.size()
    inputSize = weightSize[1]
    outputSize = weightSize[0]
    #print("MLEngine_ReadLinearUnitFromJob.  inputSize = " + str(inputSize))
    #print("MLEngine_ReadLinearUnitFromJob.  outputSize = " + str(outputSize))

    linearUnit = nn.Linear(inputSize, outputSize)
    linearUnit.weight = torch.nn.Parameter(weightTensor)
    linearUnit.bias = torch.nn.Parameter(biasTensor)

    return linearUnit
# End - MLEngine_ReadLinearUnitFromJob






################################################################################
#
# [MLEngine_TrainOneDataSequence]
# 
################################################################################
def MLEngine_TrainOneDataSequence(job, localNeuralNet, localLossFunction, lossDimension,
                                localOptimizer, inputGroupSequenceTensor, 
                                trueResultTensor, numDataSamples):
    #print("MLEngine_TrainOneDataSequence. numDataSamples=" + str(numDataSamples))
    #print("MLEngine_TrainOneDataSequence. inputGroupSequenceTensor.size=" + str(inputGroupSequenceTensor.size()))

    epochNum = job.GetEpochNum()
    #print("MLEngine_TrainOneDataSequence. EpochNum=" + str(epochNum))

    learningRate = float(job.GetRequestValueStr("LearningRate", 0.1))
    #print("MLEngine_TrainOneDataSequence. learningRate=" + str(learningRate))

    # Create initial hidden state. This also clears out any hidden state 
    # left over from a previous training sequence.
    hiddenState = localNeuralNet.initHidden()
    #print("MLEngine_TrainOneDataSequence. hiddenState.size=" + str(hiddenState.size()))

    totalLoss = 0.0
    for index in range(numDataSamples):
        #print("=====================================")
        #print("MLEngine_TrainOneDataSequence. index=" + str(index))

        # Initianlize the gradients to 0
        if (localOptimizer != None):
            localOptimizer.zero_grad()
        else:
            localNeuralNet.zero_grad()

        if (epochNum == 1):
            #print("MLEngine_TrainOneDataSequence. index=" + str(index))
            localNeuralNet.CheckState()

        # We pass in a 2-dimensional tensor for both the input and hidden state.
        # The first dimension is the batch, which is always a single value
        # The second dimension is the valueIndex, which identifies which value.
        # This is essentially a 1-dimensional array, since the batch index is always 0.
        #print("MLEngine_TrainOneDataSequence. Process one sample")
        #print("Input tensor=" + str(inputGroupSequenceTensor[index]))
        output, hiddenState = localNeuralNet.forward(inputGroupSequenceTensor[index], hiddenState)
        #print("MLEngine_TrainOneDataSequence. output=" + str(output))
        #print("MLEngine_TrainOneDataSequence. output.type=" + str(type(output)))
        #print("MLEngine_TrainOneDataSequence. output.size=" + str(output.size()))
        #print("MLEngine_TrainOneDataSequence. trueResultTensor[index]=" + str(trueResultTensor))
        #print("MLEngine_TrainOneDataSequence. trueResultTensor.type=" + str(type(trueResultTensor)))
        #print("MLEngine_TrainOneDataSequence. trueResultTensor.size=" + str(trueResultTensor[index].size()))

        if (lossDimension == 1):
            longTensor = trueResultTensor[index].long()
            #print("lossDimension=1. trueResultTensor=" + str(trueResultTensor[index]))
            #print("lossDimension=1. trueResultTensor=" + str(longTensor[0]))
            loss = localLossFunction(output, longTensor[0])
        else:
            loss = localLossFunction(output, trueResultTensor[index])
        #print("MLEngine_TrainOneDataSequence. loss.type=" + str(type(loss)))
        #print("MLEngine_TrainOneDataSequence. loss.size=" + str(loss.size()))
        #print("MLEngine_TrainOneDataSequence. loss=" + str(loss))
        #print("MLEngine_TrainOneDataSequence. loss.data=" + str(loss.data))
        #print("MLEngine_TrainOneDataSequence. loss.data.item()=" + str(loss.data.item()))

        # Back-propagate. 
        # This function generates the gradients.
        # This is implemented by the base class, but it uses a
        # train of dependencies that was saved when the subclass computed the forward pass.
        # We call this on the loss value, but it kept pointers to the neural network that
        # calculated it. Additionally, each variable in the neural network recorded which
        # vectors and weights were used to compute it, so we can traverse the network in 
        # reverse order, from outputs back to inputs.
        loss.backward(retain_graph=True)

        # Compare output to target.
        trueResult = trueResultTensor[index][0][0].data.item()
        # Use this for a category output
        if (job.GetResultValueType() == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            topProbability, topIndex = output.topk(1)
            predictedResult = topIndex[0].item()
        else:
            predictedResult = output[0].item()

        job.RecordTrainingLoss(loss.data.item())
        job.RecordTrainingResult(trueResult, predictedResult)

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
    # End - for index in range(numDataSamples):

    #print("MLEngine_TrainOneDataSequence: job=" + str(job))
    return job
# End - MLEngine_TrainOneDataSequence






################################################################################
#
# [MLEngine_TestOneDataSequence]
#
################################################################################
def MLEngine_TestOneDataSequence(job, localNeuralNet, inputGroupSequenceTensor, 
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
        with torch.no_grad():
            output, hiddenState = localNeuralNet.forward(inputGroupSequenceTensor[index], hiddenState)

        # Compare output to target.
        trueResult = trueResultTensor[index][0][0].data.item()
        # Use this for a category output
        if (job.GetResultValueType() == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            #topProbability, topValue = output.topk(1)
            #predictedResult = topValue[0].item()
            predictedResult = output.argmax(1).item()
            #print("TDF_DATA_TYPE_FUTURE_EVENT_CLASS. predictedResult = " + str(predictedResult))
        else:
            predictedResult = output[0].item()

        #print("trueResult: " + str(trueResult) + ", predictedResult: " + str(predictedResult))
        job.RecordTestingResult(trueResult, predictedResult)
        # End - for index in range(numDataSamples):    
    # Look at each result

    return job
# End - MLEngine_TestOneDataSequence






################################################################################
#
# [TrainOneFilePartitionImpl]
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
def TrainOneFilePartitionImpl(job, currentPartitionStart, currentPartitionStop, 
                            clipNumPatients, localNeuralNet, localLossFunction, 
                            lossDimension, localOptimizer, localScheduler):
    tdfFilePathName = job.GetDataParam("TrainData")
    inputNameListStr = job.GetRequestValueStr("InputValues", -1)
    resultValueName = job.GetRequestValueStr("ResultValue", -1)
    windowStartEvent = job.GetRequestValueStr("WindowStartEvent", "")
    windowStopEvent = job.GetRequestValueStr("WindowStopEvent", "")

    #print("TrainOneFilePartitionImpl. inputNameListStr=" + str(inputNameListStr))
    #print("TrainOneFilePartitionImpl. resultValueName=" + str(resultValueName))
    #print("TrainOneFilePartitionImpl. requireProperties=" + str(requireProperties))
    #print("TrainOneFilePartitionImpl. windowStartEvent=" + str(windowStartEvent))
    #print("TrainOneFilePartitionImpl. windowStopEvent=" + str(windowStopEvent))
    #print("TrainOneFilePartitionImpl. clipNumPatients=" + str(clipNumPatients))
    #print("TrainOneFilePartitionImpl. EpochNum=" + str(job.GetEpochNum()))

    numRequireProperties, requirePropertyRelationList, requirePropertyNameList, requirePropertyValueList = job.GetFilterProperties()

    tdfReader = TDF_CreateTDFFileReader(tdfFilePathName)
    #print("TrainOneFilePartitionImpl. Opened TDF file")
    fEOF = False
    numPatientsProcessed = 0

    #######################################
    # This loop looks at each patient in the current partition
    fFoundPatient, fEOF = tdfReader.GotoFirstPatientInPartition(currentPartitionStart, currentPartitionStop)
    while ((not fEOF) and (fFoundPatient)):
        #print("TrainOneFilePartitionImpl. Found Patient. fEOF=" + str(fEOF) + ", fFoundPatient=" + str(fFoundPatient))
        #job.Log("TrainOneFilePartitionImpl. Found Patient. fEOF=" + str(fEOF) + ", fFoundPatient=" + str(fFoundPatient))

        #######################################
        # This loop looks at each event window in the current patient
        fFoundWindow = tdfReader.SetFirstDataWindow(windowStartEvent, [], windowStopEvent, [])
        while (fFoundWindow):
            # Get all data points for the next window.
            # This is a sequence of data points for a single patient. 
            # We are programming a recurrent neural net, so we process all data points in a sequence.
            numReturnedDataSets, inputTensor, resultTensor = tdfReader.GetDataFromCurrentWindow(inputNameListStr, 
                                                                                    resultValueName, 
                                                                                    "NormInt0-100", 
                                                                                    numRequireProperties,
                                                                                    requirePropertyRelationList,
                                                                                    requirePropertyNameList,
                                                                                    requirePropertyValueList,
                                                                                    12)

            # There must be at least N values. 
            # The hidden state is initialized on the first set of values, 
            # and then the gradient of the intiial state is not available
            # until we have done at least 2 sets of data. If we only use one data set
            # then the gradients are not valid and we fail when updating the weights.
            # So....if there is only 1 data set, then pass it through the neural net twice.
            if (numReturnedDataSets < localNeuralNet.MinNumDataPointsPerBatch()):
                fFoundWindow = tdfReader.SetNextDataWindow()
                continue

            #print("TrainOneFilePartitionImpl. numReturnedDataSets=" + str(numReturnedDataSets))
            #print("TrainOneFilePartitionImpl. inputTensor.size=" + str(inputTensor.size()))
            #print("TrainOneFilePartitionImpl. resultTensor.size=" + str(resultTensor.size()))
            #print("TrainOneFilePartitionImpl. resultTensor=" + str(resultTensor))

            job = MLEngine_TrainOneDataSequence(job, localNeuralNet, localLossFunction, lossDimension,
                                            localOptimizer, inputTensor, resultTensor, numReturnedDataSets)

            fFoundWindow = tdfReader.SetNextDataWindow()
            #print("TrainOneFilePartitionImpl. fFoundWindow = " + str(fFoundWindow))
        # End - while (fFoundWindow):

        # Go to the next patient in this partition
        numPatientsProcessed += 1
        if ((clipNumPatients > 0) and (numPatientsProcessed >= clipNumPatients)):
            #print("TrainOneFilePartitionImpl. Stop at clipped number patients. numPatientsProcessed=" + str(numPatientsProcessed))
            break

        fFoundPatient, fEOF = tdfReader.GotoNextPatientInPartition(currentPartitionStop)
        #print("TrainOneFilePartition. fEOF=" + str(fEOF))
    # End - while ((not fEOF) and (fFoundPatient)):

    tdfReader.Shutdown()
    return job, numPatientsProcessed, fEOF
# End - TrainOneFilePartitionImpl







################################################################################
#
# [TestOneFilePartitionImpl]
#
# This returns one value: fEOF
#   fEOF - True iff we hit the end of the file
#
################################################################################
def TestOneFilePartitionImpl(job, currentPartitionStart, currentPartitionStop, 
                                 clipNumPatients, localNeuralNet):
    tdfFilePathName = job.GetDataParam("TestData")
    inputNameListStr = job.GetRequestValueStr("InputValues", -1)
    resultValueName = job.GetRequestValueStr("ResultValue", -1)
    windowStartEvent = job.GetRequestValueStr("WindowStartEvent", "")
    windowStopEvent = job.GetRequestValueStr("WindowStopEvent", "")
    #print("TestOneFilePartitionImpl. inputNameListStr=" + str(inputNameListStr))
    #print("TestOneFilePartitionImpl. resultValueName=" + str(resultValueName))
    #print("TestOneFilePartitionImpl. windowStartEvent=" + str(windowStartEvent))
    #print("TestOneFilePartitionImpl. windowStopEvent=" + str(windowStopEvent))

    # Parse the optional required and exclusion properties.
    numRequireProperties, requirePropertyRelationList, requirePropertyNameList, requirePropertyValueList = job.GetFilterProperties()

    tdfReader = TDF_CreateTDFFileReader(tdfFilePathName)
    #print("TestOneFilePartitionImpl. Opened TDF file")
    fEOF = False
    numPatientsProcessed = 0

    #######################################
    # This loop looks at each patient in the current partition
    fFoundPatient, fEOF = tdfReader.GotoFirstPatientInPartition(currentPartitionStart, currentPartitionStop)
    while ((not fEOF) and (fFoundPatient)):
        #job.Log("TestOneFilePartitionImpl. Found Patient. fEOF=" + str(fEOF) + ", fFoundPatient=" + str(fFoundPatient))

        #######################################
        # This loop looks at each event window in the current patient
        fFoundWindow = tdfReader.SetFirstDataWindow(windowStartEvent, [], windowStopEvent, [])
        while (fFoundWindow):
            # Get all data points for the next prediction.
            # This is a sequence of data points for a single patient. 
            # We are programming a recurrent neural net, so we process all data points in a sequence.
            numReturnedDataSets, inputTensor, resultTensor = tdfReader.GetDataFromCurrentWindow(inputNameListStr, 
                                                                                    resultValueName, 
                                                                                    "NormInt0-100", 
                                                                                    numRequireProperties,
                                                                                    requirePropertyRelationList,
                                                                                    requirePropertyNameList,
                                                                                    requirePropertyValueList,
                                                                                    12)

            # There must be at least N values. 
            # The hidden state is initialized on the first set of values, 
            # and then the gradient of the intiial state is not available
            # until we have done at least 2 sets of data. If we only use one data set
            # then the gradients are not valid and we fail when updating the weights.
            # So....if there is only 1 data set, then pass it through the neural net twice.
            if (numReturnedDataSets < localNeuralNet.MinNumDataPointsPerBatch()):
                fFoundWindow = tdfReader.SetNextDataWindow()
                continue

            #print("TestOneFilePartitionImpl. numReturnedDataSets=" + str(numReturnedDataSets))
            job = MLEngine_TestOneDataSequence(job, localNeuralNet, inputTensor, 
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
# End - TestOneFilePartitionImpl






################################################################################
#
# [MLEngine_CreateNeuralNetFromJobSpec]
#
################################################################################
def MLEngine_CreateNeuralNetFromJobSpec(sendPipeEnd, job, debugCmd):
    # Create the neural network in this address space.
    valStr = job.GetRequestValueStr("NetworkType", -1).lower()
    #print("NetworkType=" + valStr)
    if (valStr == "simplenet"):
        localNeuralNet = SimpleOneLayerNeuralNet(job)
    elif (valStr == "multilevelnet"):
        localNeuralNet = MultiLayerNeuralNet(job)
    else:
        job.FinishJobExecution(False, "MLEngine_RunJob. Invalid NeuralNet type:" + valStr)
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
# End - MLEngine_CreateNeuralNetFromJobSpec






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
def MLEngine_TrainOneFilePartitionInChildProcess(sendPipeEnd, jobStr, currentPartitionStart, 
                                    currentPartitionStop, clipNumPatients, debugCmd):
    #print("MLEngine_TrainOneFilePartitionInChildProcess")
    #print("MLEngine_TrainOneFilePartitionInChildProcess. jobStr=" + jobStr)

    numPatientsProcessed = 0
    fEOF = False

    # Regenerate the runtime job object from its serialized string form. 
    job = MLJob_CreateMLJobFromString(jobStr)

    # Create the neural network in this address space.
    localNeuralNet = MLEngine_CreateNeuralNetFromJobSpec(sendPipeEnd, job, debugCmd)
    if (None == localNeuralNet):
        return

    # Define the loss function
    # For Regression, 
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
    # For categorization,
    #    nn.BCELoss (Binary Cross Entropy Loss, if the last layer of the RNN is nn.Sigmoid)
    #           loss = -1 * SUM( actual * log(predicted) )
    #
    #    nn.NLLLoss (Negative Log Likelihood, if the last layer of the RNN is nn.LogSoftmax)
    #
    lossTypeStr = job.GetRequestValueStr("LossFunction", "")
    lossTypeStr = lossTypeStr.lower()
    #print("lossTypeStr=" + lossTypeStr)
    if (lossTypeStr == "l1loss"):
        localLossFunction = nn.L1Loss()
        lossDimension = 2
    elif (lossTypeStr == "l2loss"):
        #print("Make L2 loss")
        localLossFunction = nn.MSELoss()
        lossDimension = 2
    elif (lossTypeStr == "nllloss"):
        localLossFunction = nn.NLLLoss()
        lossDimension = 1
    elif (lossTypeStr == "crossentropynllloss"):
        localLossFunction = torch.nn.CrossEntropyLoss()
        lossDimension = 1
    elif (lossTypeStr == "bceloss"):
        localLossFunction = nn.BCELoss()
        lossDimension = 2
    else:
        job.FinishJobExecution(False, "MLEngine_RunJob. Invalid LossFunction type:" + lossTypeStr)
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
    #print("MLEngine_RunJob. learningRate=" + str(learningRate))
    optimizerType = job.GetRequestValueStr("Optimizer", -1)
    #print("MLEngine_RunJob. optimizerType=" + optimizerType)
    optimizerType = optimizerType.lower()
    if (optimizerType == "sgd"):
        #print("Making SGD optimizer")
        localOptimizer = optim.SGD(localNeuralNet.parameters(), lr=learningRate)
        localScheduler = torch.optim.lr_scheduler.StepLR(localOptimizer, 1, gamma=0.9)
    elif (optimizerType == "none"):
        localOptimizer = None
        localScheduler = None
    else:
        job.FinishJobExecution(False, "MLEngine_RunJob. Invalid optimizer type:" + optimizerType)
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
        #print("Check saved test state")
        testInputArray = job.GetTestMatrix("SampleInput", "input")
        testInput = torch.tensor(testInputArray, dtype=torch.float32)
        #print("testInput=" + str(testInput))
        hiddenState = localNeuralNet.initHidden()
        localNeuralNet.zero_grad()
        output, hiddenState = localNeuralNet.forward(testInput, hiddenState)
        #print("Check State Restore. Test output=" + str(output))
        job.CheckTestMatrix("SampleInput", "output", output.detach().numpy())


    # Do the actual work
    job, numPatientsProcessed, fEOF = TrainOneFilePartitionImpl(job, currentPartitionStart, 
                                                            currentPartitionStop, clipNumPatients, 
                                                            localNeuralNet, localLossFunction,
                                                            lossDimension, localOptimizer, localScheduler)


    # During training, we optionally save the updated weights to the job, for later use.
    #print("Saving Neural Net State")
    localNeuralNet.SaveNeuralNetWeights(job)
    #print("Finished saving Neural Net State")

    ###############################
    # DEBUG
    if (debugCmd == "CheckSavedState"):
        #print("Saving debug check state")
        inputSize = localNeuralNet.GetInputSize()
        testInput = torch.rand((1, inputSize), dtype=torch.float32)
        #print("testInput=" + str(testInput))
        job.SetTestMatrix("SampleInput", "input", testInput.detach().numpy())
        hiddenState = localNeuralNet.initHidden()
        localNeuralNet.zero_grad()
        output, hiddenState = localNeuralNet.forward(testInput, hiddenState)
        job.SetTestMatrix("SampleInput", "output", output.detach().numpy())
        #print("Check-State Save. Test output=" + str(output))


    # Send the results back to the control process.
    jobStr = job.WriteJobToString(True)
    resultDict = {}
    resultDict['jobStr'] = jobStr
    resultDict['numPatientsProcessed'] = numPatientsProcessed
    resultDict['fEOF'] = fEOF
    sendPipeEnd.send(resultDict)
    sendPipeEnd.close()

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
                                       currentPartitionStop, clipNumPatients, debugCmd):
    #print("MLEngine_TestOneFilePartitionInChildProcess")
    numPatientsProcessed = 0
    fEOF = False

    # Regenerate the runtime job object from its serialized string form. 
    job = MLJob_CreateMLJobFromString(jobStr)

    # Create the neural network in this address space.
    localNeuralNet = MLEngine_CreateNeuralNetFromJobSpec(sendPipeEnd, job, debugCmd)
    if (None == localNeuralNet):
        return

    ###############################
    # DEBUG
    if ((debugCmd == "CheckSavedState") and (job.HasTestMatrix("SampleInput", "input"))):
        #print("Restore debug state")
        testInputArray = job.GetTestMatrix("SampleInput", "input")
        testInput = torch.tensor(testInputArray, dtype=torch.float32)
        #print("testInput=" + str(testInput))
        hiddenState = localNeuralNet.initHidden()
        localNeuralNet.zero_grad()
        output, hiddenState = localNeuralNet.forward(testInput, hiddenState)
        #print("Check-state Restore. Test output=" + str(output))
        job.CheckTestMatrix("SampleInput", "output", output.detach().numpy())

    # Do the actual work
    job, numPatientsProcessed, fEOF = TestOneFilePartitionImpl(job, currentPartitionStart, 
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
# End - MLEngine_TestOneFilePartitionInChildProcess







################################################################################
#
# [MLEngine_TrainNeuralNet]
#
################################################################################
def MLEngine_TrainNeuralNet(job, partitionSize):
    #print("=======================")
    #print("Training:")

    job.StartTraining()

    numEpochs = job.GetRequestValueInt("NumEpochs", 1)
    clipNumPatients = job.GetRequestValueInt("ClipNumTrainPatients", -1)
    #print("MLEngine_TrainNeuralNet. numEpochs=" + str(numEpochs))
    #print("MLEngine_TrainNeuralNet. clipNumPatients=" + str(clipNumPatients))


    #######################################
    # Iterate one for each Epoch
    for epochNum in range(numEpochs):
        print("Epoch " + str(epochNum))
        job.StartTrainingEpoch()

        numRemainingPatientsInEpoch = -1
        if (clipNumPatients > 0):
            numRemainingPatientsInEpoch = clipNumPatients

        #######################################
        # This loop looks at each partition in the file. One partition is 
        # a large chunk of data and may contain many patients.
        fEOF = False
        debugCmd = "CheckSavedState"
        currentPartitionStart = 0
        currentPartitionStop = currentPartitionStart + partitionSize
        while (not fEOF):
            job.Log("Start Partition. StartPos=" + str(currentPartitionStart))

            # Make a pipe that will be used to return the results. 
            recvPipeEnd, sendPipeEnd = multiprocessing.Pipe(False)

            # Prepare the arguments to go to the worker process.
            # Thia may be another process on this machine or else a remote process on another server.
            jobStr = job.WriteJobToString(True)
            #print("MLEngine_TrainNeuralNet jobStr=" + str(jobStr))

            # Fork the job process.
            processInfo = Process(target=MLEngine_TrainOneFilePartitionInChildProcess, args=(sendPipeEnd, jobStr, 
                                                    currentPartitionStart, currentPartitionStop, 
                                                    numRemainingPatientsInEpoch, debugCmd))
            processInfo.start()

            # Get the results.
            resultDict = recvPipeEnd.recv()
            #print("MLEngine_TrainNeuralNet. Got result back from child process")

            jobStr = resultDict['jobStr']
            numPatientsProcessed = resultDict['numPatientsProcessed']
            fEOF = resultDict['fEOF']
            job.ReadJobFromString(jobStr)
            #print("MLEngine_TrainNeuralNet. jobStr=" + str(jobStr))
            #print("MLEngine_TrainNeuralNet. numPatientsProcessed=" + str(numPatientsProcessed))
            #print("MLEngine_TrainNeuralNet. fEOF=" + str(fEOF))

            # Wait for the process to complete.
            processInfo.join()

            # If we only want to process a limited number of patients, then stop if we
            # have reached the limit.
            if (clipNumPatients > 0):
                numRemainingPatientsInEpoch = numRemainingPatientsInEpoch - numPatientsProcessed
                if (numRemainingPatientsInEpoch <= 0):
                    break
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
# End - MLEngine_TrainNeuralNet()








################################################################################
#
# [MLEngine_TestNeuralNet]
#
################################################################################
def MLEngine_TestNeuralNet(job, partitionSize):
    #print("MLEngine_TestNeuralNet. Start Testing:")

    job.StartTesting()

    clipNumPatients = job.GetRequestValueInt("ClipNumTestPatients", -1)
    numRemainingPatients = -1
    if (clipNumPatients > 0):
        numRemainingPatients = clipNumPatients

    #######################################
    # This loop looks at each partition in the file. One partition is 
    # a large chunk of data and may contain many patients.
    fEOF = False
    debugCmd = ""
    currentPartitionStart = 0
    currentPartitionStop = currentPartitionStart + partitionSize
    while (not fEOF):
        job.Log("Start Partition. StartPos=" + str(currentPartitionStart))

        # Make a pipe that will be used to return the results. 
        recvPipeEnd, sendPipeEnd = multiprocessing.Pipe(False)

        # Prepare the arguments to go to the worker process.
        # This may be another process on this machine or else a remote process on another server.
        jobStr = job.WriteJobToString(True)
        #print("MLEngine_TestNeuralNet jobStr=" + str(jobStr))

        # Fork the job process.
        processInfo = Process(target=MLEngine_TestOneFilePartitionInChildProcess, args=(sendPipeEnd, jobStr, 
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
# End - MLEngine_TestNeuralNet()








################################################################################
#
# [MLEngine_RunJob]
#
################################################################################
def MLEngine_RunJob(filePathName, trainedFilePathName):
    # Open the job.
    job = MLJob_ReadExistingMLJob(filePathName)

    # Initialize the engine.
    job.StartJobExecution()

    partitionSize = 2 * (1024 * 1024)

    trainTDFFilePathName = job.GetDataParam("TrainData")
    if (trainTDFFilePathName != ""):
        job = MLEngine_TrainNeuralNet(job, partitionSize)

    testTDFFilePathName = job.GetDataParam("TestData")
    if (testTDFFilePathName != ""):
        job = MLEngine_TestNeuralNet(job, partitionSize)

    job.FinishJobExecution(True, "")

    # The default is to save the state. We only do NOPT do this if the job
    # explicitly says not to.
    if (not job.GetJobControlBool("SaveNetState", False)):
        job.RemoveAllSavedState()

    if ((None != trainedFilePathName) and (trainedFilePathName != "")):
        job.SaveAs(trainedFilePathName)
# End - MLEngine_RunJob





################################################################################
#
# [MLEngine_MakePrediction]
#
# This sets up a neural net, runs it on a single input, and then returns a prediction.
# This is the core of processing a web request.
################################################################################
def MLEngine_MakePrediction(jobFilePathName, inputValuesStr):
    #print("MLEngine_MakePrediction. jobFilePathName=" + str(jobFilePathName))
    #print("MLEngine_MakePrediction. inputValuesStr=" + str(inputValuesStr))

    # Open the job.
    job = MLJob_ReadExistingMLJob(jobFilePathName)

    job.StartJobExecution()
    debugCmd = ""

    # Create the neural network in this address space.
    localNeuralNet = MLEngine_CreateNeuralNetFromJobSpec(None, job, debugCmd)
    if (None == localNeuralNet):
        resultStr = TDF_GetLog() + "Error making neural network"
        return False, resultStr

    inputNameListStr = job.GetRequestValueStr("InputValues", -1)
    #print("MLEngine_MakePrediction. inputNameListStr=" + str(inputNameListStr))

    foundValues, inputTensor = TDF_ParseUserRequestDataString(inputNameListStr, inputValuesStr)
    if (not foundValues):
        resultStr = TDF_GetLog() + "Error parsing input values"
        return False, resultStr

    hiddenState = localNeuralNet.initHidden()
    # We pass in a 2-dimensional tensor for both the input and hidden state.
    # The first dimension is the batch, which is always a single value
    # The second dimension is the valueIndex, which identifies which value.
    # This is essentially a 1-dimensional array, since the batch index is always 0.
    with torch.no_grad():
        output, hiddenState = localNeuralNet.forward(inputTensor[0], hiddenState)

    # Use this for a category output
    if (job.GetResultValueType() == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
        topValue, topValue = output.topk(1)
        predictedResult = topValue[0].item()
    else:
        predictedResult = output[0].item()
        # <><> FIXME. Use the data type to decide whether to do this.
        # We may round floats, but not ints.
        predictedResult = round(predictedResult, 2)

    # Return the updated job that has been changed by the child processes.
    return True, str(predictedResult)
# End - MLEngine_MakePrediction






################################################################################
#
# [MLEngine_Train]
#
################################################################################
def MLEngine_Train(filePathName, trainedFilePathName):
    # Open the job.
    job = MLJob_ReadExistingMLJob(filePathName)

    # Initialize the engine.
    job.StartJobExecution()
    partitionSize = 2 * (1024 * 1024)

    trainTDFFilePathName = job.GetDataParam("TrainData")
    if (trainTDFFilePathName != ""):
        job = MLEngine_TrainNeuralNet(job, partitionSize)

    job.FinishJobExecution(True, "OK")

    #print("MLEngine_Train. trainedFilePathName=" + str(trainedFilePathName))
    if ((None != trainedFilePathName) and (trainedFilePathName != "")):
        job.SaveAs(trainedFilePathName)
    print("Training Done")


    testTDFFilePathName = job.GetDataParam("TestData")
    if (testTDFFilePathName != ""):
        job = MLEngine_TestNeuralNet(job, partitionSize)
        print("Testing Done")
# End - MLEngine_Train






################################################################################
# TEST CODE
################################################################################
def MLEngine_UnitTest():
    Test_StartModuleTest("MLEngine")

    Test_StartTest("Run BVTJob1")
    filePathName = "/home/ddean/ddRoot/tools/BVTJob1.txt"
    MLEngine_RunJob(filePathName)
# End - MLEngine_UnitTest


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


#<><><>
# Weight
# isMale
# Age
# Platelets
# Hgb
# ALT
# AST
# ALP
#
# Aspirin
# SSRI
# Albumin (nutrition)
# Flagyl
# Bactrim
# Quinolones
# Amiodarone
# Phenytoin


