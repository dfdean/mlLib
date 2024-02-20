####################################################################################
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
#####################################################################################
#
# This is designed to be independant of the specific Machine Learning library, so
# it should work equally well with PyTorch or TensorFlow or other libraries. 
# It does assume numpy, but that is common to Python
#
#####################################################################################
#
# Top Level Elements
# ===============================
#   <JobControl>
#       JobName - A string that identifies the job to a human
#       JobType - Basic
#       JobSpecVersion - Currently 1.0
#       Status - IDLE, TRAIN, TEST
#       AllowGPU - True/False, defaults to True
#       Debug - True/False, defaults to False
#       LogFilePathName - A pathname where the log file for this execution is stored.
#           This file is created/emptied when the job starts.
#       StressTest - True/False, defaults to False
#   </JobControl>
#
#   <Data>
#       DataFormat 
#           TDF
#       StoreType
#           File
#       TrainData - A file pathname
#       TestData - A file pathname
#   </Data>
#
#   <Network>
#       NetworkType
#           SimpleNet | DeepNet | LSTM
#
#       LogisticOutput
#       OutputThreshold
#           A number between 0 and 1 which determines whether the prediction is true.
#           This is only used for Logistic networks
#
#       InputSequence
#       InputSequenceMinSize
#       InputSequenceMaxSize
#           This defaults to 1 for a function that takes a single value and outputs a result.
#    
#       MaxSequenceDurationInDays
#           How far apart a sequence duration can be spread
#
#       StateSize
#           An integer, 0-N, which is the size of a RNN state vector.
#           If not specified, then this is 0
#           If this is 0, then this is a simple deep neural network. It is
#               an RNN iff this value is present and greater than 0
#
#       <InputLayer>
#           layerOutputSize
#           NonLinear - 
#               LogSoftmax | ReLU | Sigmoid
#           InputValues - A comma-separated list of variables, like "Age,Cr,SBP". 
#               See the TDFTools.py documentation for a list of defined names.
#               The value name appeats in a <D> element. 
#               For example, Hgb would extract data from the following <D> element:
#                   <D C="L" T="100:10:30">Hgb=7.0,</D>
#               Each value may be followed by an offset in brackets
#               Examples: Cr[-1]   INR[next]
#               The number in brackets is the number of days from the current point in the timeline.
#               The offset "next" means the next occurrence.    
#               The special value "Dose" is always followed by a "/" and then the name of a medication.
#               For example Dose/Coumadin is the dose of Coumadin given.
#               Doses may also have offsets. For example Dose/Coumadin[-1] is the dose of Coumadin given 1 day before.
#
#       <HiddenLayer>
#           layerOutputSize
#           NonLinear - 
#               LogSoftmax | ReLU | Sigmoid
#
#       <OutputLayer>
#           layerOutputSize
#           NonLinear - 
#               LogSoftmax | ReLU | Sigmoid
#           ResultValue - A variable name. See the TDFTools.py documentation.
#           Different variables have different interpretations as result values.
#           These include:
#               Number - A numeric value, which may be a dose or a lab value
#               FutureEventClass - A number 0-11. See the TDFTools.py documentation.
#               Binary - A number 0-1
#               FutureEventClass or BinaryDiagnosis will count the number of exact matches; the 
#                   predicted class must exactly match the actual value.
#               Number will count buckets:
#               Exact (to 1 decimal place)
#               Within 2%
#               Within 5%
#               Within 10%
#               Within 25%
#
#   </Network>
#
#   <Training>
#       LossFunction
#           NLLLoss | BCELoss
#
#       Optimizer
#           SGD
#
#       LearningRate
#       BatchSize
#       NumEpochs
#   </Training>
#
#   <Results>
#       <PreflightResults>
#           <ResultClassWeightList>
#               <NumResultClasses> Number of classes (int) </NumResultClasses>
#
#               <ResultClassWeight>
#                   <ResultClassID> class ID (int) </ResultClassID>
#                   <ClassWeight> class ID (float) </ClassWeight>
#               </ResultClassWeight>
#               .....
#           </ResultClassWeightList>
#       </PreflightResults>
#
#       <TrainingResults>
#           NumSequencesTrainedPerEpoch
#           NumPatientsTrainedPerEpoch
#           NumPatientsSkippedPerEpoch
#           TrainAvgLossPerEpoch
#          TrainNumItemsPerClass
#       </TrainingResults>
#
#       <TestingResults>
#           <Hist0>
#               NumSequencesTested
#               TestNumItemsPerClass
#               TestNumPredictionsPerClass
#               TestNumCorrectPerClass
#              NumCorrectPredictions
#               Used for int and float results:
#                  NumPredictionsWithin2Percent
#                   NumPredictionsWithin5Percent
#                   NumPredictionsWithin10Percent
#                   NumPredictionsWithin20Percent
#                   NumPredictionsWithin50Percent
#                   NumPredictionsWithin100Percent
#               Used for class results.
#                   NumPredictionsWithin1Class
#               Used for binary results.
#                   NumPredictionsTruePositive
#                   NumPredictionsTrueNegative
#                   NumPredictionsFalsePositive
#                   NumPredictionsFalseNegative
#           </Hist0>
#
#           <Hist1>
#               NumSequencesTested
#               TestNumItemsPerClass
#               TestNumPredictionsPerClass
#               TestNumCorrectPerClass
#              NumCorrectPredictions
#               Used for int and float results:
#                  NumPredictionsWithin2Percent
#                   NumPredictionsWithin5Percent
#                   NumPredictionsWithin10Percent
#                   NumPredictionsWithin20Percent
#                   NumPredictionsWithin50Percent
#                   NumPredictionsWithin100Percent
#               Used for class results.
#                   NumPredictionsWithin1Class
#               Used for binary results.
#                   NumPredictionsTruePositive
#                   NumPredictionsTrueNegative
#                   NumPredictionsFalsePositive
#                   NumPredictionsFalseNegative
#           </Hist1>
#
#       </TestingResults>
#
#   </Results>
#
#   <Runtime>
#   The runtime state for the Job training/testing sequence. It is describes the execution
#   of a job, not the job results.
#       JobFilePathName
#
#       StartRequestTimeStr
#       StopRequestTimeStr
#
#       CurrentEpochNum
#       TotalTrainingLossInCurrentEpoch
#
#       BufferedLogLines
#
#       OS  
#       CPU
#       GPU
#   </Runtime>
#
# <SavedModelState>
#   <PyTorchOptimizerState>
#   <NeuralNetMatrixList>
#   This is part of SavedModelStateXMLNode, and it is used for neural nets (deep and logistics)
#   The runtime weight matrices and bias vectors for a network.
#   This allows a network to suspend and then later resume its state, possibly in a 
#   different process or a different server.
#       <Weight>
#       <Bias>
#
#####################################################################################
import os
import sys
import time
import re
from datetime import datetime
import platform
import random

import hashlib  # For Hashing an array
import json

from xml.dom.minidom import getDOMImplementation

import numpy

from sklearn.metrics import f1_score
from sklearn.metrics import auc
from sklearn.metrics import roc_auc_score
from sklearn.metrics import precision_recall_curve

# Normally we have to set the search path to load these.
# But, this .py file is always in the same directories as these imported modules.
import xmlTools as dxml
import tdfTools as tdf
import dataShow as dataShow


NEWLINE_STR = "\n"
ML_JOB_NUM_NUMERIC_VALUE_BUCKETS            = 20


########################################
# XML Elements

# <MLJob>
ROOT_ELEMENT_NAME = "MLJob"
# Attributes
FORMAT_VERSION_ATTRIBUTE    = "JobVersion"
DEFAULT_JOB_FORMAT_VERSION  = 1

# <JobControl>
JOB_CONTROL_ELEMENT_NAME    = "JobControl"
JOBCTL_STATUS_ELEMENT_NAME  = "Status"
JOBCTL_ERROR_CODE_ELEMENT_NAME  = "ErrCode"
JOBCTL_RESULT_MSG_ELEMENT_NAME  = "ErrMsg"
JOBCTL_RUN_OPTIONS_ELEMENT_NAME  = "RunOptions"
JOBCTL_RUN_OPTION_SEPARATOR_STR = ","

# <Data>
DATA_ELEMENT_NAME = "Data"

# <Training>
TRAINING_ELEMENT_NAME = "Training"
TRAINING_OPTION_BATCHSIZE = "BatchSize"
TRAINING_OPTION_LEARNING_RATE = "LearningRate"
TRAINING_OPTION_NUM_EPOCHS = "NumEpochs"
TRAINING_MAX_NUM_SKIPPED_RESULT_CLASSES = "MaxSkippedResultClasses"

# <Training><ValueInfo>
TRAINING_PRIORITY_VALUE_INFO = "ValueInfo"
TRAINING_PRIORITY_VALUE_NAME = "ValueName"
TRAINING_PRIORITY_SRC_FILE = "SrcFile"
TRAINING_PRIORITY_CREATION_DATE = "DateCollected"
TRAINING_PRIORITY_MIN_VALUE = "MinValue"
TRAINING_PRIORITY_MAX_VALUE = "MaxValue"
TRAINING_PRIORITY_MEAN_VALUE = "MeanValue"
TRAINING_PRIORITY_NUM_CLASSES = "NumPriorities"
TRAINING_PRIORITY_CLASS_PRIORITIES = "ClassPriorities"

# <Runtime>
RUNTIME_ELEMENT_NAME = "Runtime"
RUNTIME_LOG_NODE_ELEMENT_NAME = "Log"
RUNTIME_HASH_DICT_ELEMENT_NAME = "HashDict"
RUNTIME_FILE_PATHNAME_ELEMENT_NAME = "JobFilePathname"
RUNTIME_START_ELEMENT_NAME = "StartRequestTimeStr"
RUNTIME_STOP_ELEMENT_NAME = "StopRequestTimeStr"
RUNTIME_CURRENT_EPOCH_ELEMENT_NAME = "CurrentEpochNum"
RUNTIME_NONCE_ELEMENT_NAME = "Nonce"

# <Results>
RESULTS_ELEMENT_NAME = "Results"
RESULTS_PREFLIGHT_ELEMENT_NAME = "PreflightResults"
RESULTS_TRAINING_ELEMENT_NAME = "TrainingResults"
RESULTS_TESTING_ELEMENT_NAME = "TestingResults"

# <Results><PreflightResults>
RESULTS_PREFLIGHT_NUM_ITEMS_ELEMENT_NAME = "NumSequences"
RESULTS_PREFLIGHT_NUM_ITEMS_PER_CLASS_ELEMENT_NAME = "NumItemsPerClass"
RESULTS_PREFLIGHT_INPUT_MINS_ELEMENT_NAME = "InputMins"
RESULTS_PREFLIGHT_INPUT_MAXS_ELEMENT_NAME = "InputMaxs"
RESULTS_PREFLIGHT_INPUT_RANGES_ELEMENT_NAME = "InputRanges"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_LIST = "ResultClassWeightList"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT = "ResultClassWeight"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_NUM_RESULT_CLASSES = "NumResultClasses"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_ID = "ResultClassID"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_VALUE = "ClassWeight"

# <Results><TestingResults>
RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME = "AllTests"
RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME = "TestSubGroup"

RESULTS_TEST_NUM_ITEMS_ELEMENT_NAME = "NumSequences"
RESULTS_TEST_NUM_ITEMS_PER_CLASS_ELEMENT_NAME = "NumItemsPerClass"
RESULTS_TEST_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME = "NumPredictionsPerClass"
RESULTS_TEST_NUM_CORRECT_PER_CLASS_ELEMENT_NAME  = "NumCorrectPerClass"
RESULTS_TEST_NUM_CORRECT_PER_CLASS_ELEMENT_NAME  = "NumCorrectPerClass"
RESULTS_ROCAUC_ELEMENT_NAME = "ROCAUC"
RESULTS_AUPRC_ELEMENT_NAME = "AUPRC"
RESULTS_F1Score_ELEMENT_NAME = "F1Score"
RESULTS_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME = "LogisticOutputs"

# <Network>
NETWORK_ELEMENT_NAME = "Network"
NETWORK_TYPE_ELEMENT_NAME = "NetworkType"
NETWORK_STATE_SIZE_ELEMENT_NAME = "RecurrentStateSize"
NETWORK_OUTPUT_THRESHOLD_ELEMENT_NAME = "MapOutputToBoolThreshold"
NETWORK_SEQUENCE_ELEMENT_NAME = "InputSequence"
NETWORK_SEQUENCE_SIZE_ELEMENT_NAME = "InputSequenceSize"
NETWORK_SEQUENCE_MAX_DURATION_DAYS_ELEMENT_NAME = "MaxSequenceDurationInDays"

NETWORK_LOGISTIC_ELEMENT_NAME       = "LogisticOutput"

# <SavedModelState>
SAVED_MODEL_STATE_ELEMENT_NAME      = "SavedModelState"
RUNTIME_OPTIMIZER_STATE             = "PyTorchOptimizerState"

# <NeuralNetMatrixList>
NETWORK_MATRIX_LIST_NAME = "NeuralNetMatrixList"
NETWORK_MATRIX_WEIGHT_MATRIX_NAME = "Weight"
NETWORK_MATRIX_BIAS_VECTOR_NAME = "Bias"

VALUE_FILTER_LIST_SEPARATOR = "{AND}"

MLJOB_MATRIX_FORMAT_ATTRIBUTE_NAME = "format"
MLJOB_MATRIX_FORMAT_SIMPLE = "simple"

# These are the values found in the <JobControl/Status> element
MLJOB_STATUS_IDLE         = "IDLE"
MLJOB_STATUS_PREFLIGHT    = "PREFLIGHT"
MLJOB_STATUS_TRAINING     = "TRAIN"
MLJOB_STATUS_TESTING      = "TEST"
MLJOB_STATUS_DONE         = "DONE"

# These are specific to Job files. They must be translated into other error codes
# in higher level modules. That's not pretty, but it makes Job a standalone module.
# It also is essentially the same as translating an exception from a low level module
# into another exception from a higher level module
JOB_E_NO_ERROR              = 0
JOB_E_UNKNOWN_ERROR         = 1
JOB_E_UNHANDLED_EXCEPTION   = 2
JOB_E_CANNOT_OPEN_FILE      = 100
JOB_E_INVALID_FILE          = 110

# These are used to read and write vectors and matrices to strings.
VALUE_SEPARATOR_CHAR        = ","
ROW_SEPARATOR_CHAR          = "/"

MLJOB_NAMEVAL_SEPARATOR_CHAR    = ";"

DEBUG_EVENT_TIMELINE_EPOCH          = "Epoch"
DEBUG_EVENT_TIMELINE_CHUNK          = "Chunk"
DEBUG_EVENT_TIMELINE_LOSS           = "Loss"
DEBUG_EVENT_OUTPUT_AVG              = "Out.avg"
DEBUG_EVENT_NONLINEAR_OUTPUT_AVG    = "NLOut.avg"



################################################################################
#
# This class records all results for tests in a single group.
# We may want to track the results of different preconditions, like subgroup analysis.
################################################################################
class MLJobTestResults():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.ResultXMLNode = None

        # These are inherited from the parent, not stored with each results bucket
        self.ResultValueType = tdf.TDF_DATA_TYPE_INT
        self.ResultMinValue = 0
        self.ResultMaxValue = 0
        self.NumResultClasses = 0
        self.BucketSize = 0
        self.IsLogisticNetwork = False
        self.OutputThreshold = 0

        self.NumSamplesTested = 0
        self.TestResults = {}

        self.TestNumItemsPerClass = []
        self.TestNumPredictionsPerClass = []
        self.TestNumCorrectPerClass = []

        self.LogisticResultsTrueValueList = []
        self.LogisticResultsPredictedProbabilityList = []
        self.ROCAUC = -1
        self.AUPRC = -1
        self.F1Score = -1
    # End -  __init__


    #####################################################
    #
    # [MLJobResults::InitResultsXML]
    #
    #####################################################
    def InitResultsXML(self, testResultXMLNode, xmlNodeName):
        self.ResultXMLNode = dxml.XMLTools_GetOrCreateChildNode(testResultXMLNode, xmlNodeName)
    # End of InitResultsXML



    #####################################################
    #
    # [MLJobResults::SetGlobalResultInfo]
    #
    #####################################################
    def SetGlobalResultInfo(self, resultValueType, numResultClasses, resultMinValue, resultMaxValue, bucketSize, isLogisticNetwork, outputThreshold):
        self.ResultValueType = resultValueType
        self.NumResultClasses = numResultClasses

        self.ResultMinValue = resultMinValue
        self.ResultMaxValue = resultMaxValue
        self.BucketSize = bucketSize

        self.IsLogisticNetwork = isLogisticNetwork
        self.OutputThreshold = outputThreshold
    # End of SetGlobalResultInfo



    #####################################################
    #
    # [MLJobTestResults::StartTesting
    # 
    #####################################################
    def StartTesting(self):
        self.NumSamplesTested = 0
        self.TestResults = {"NumCorrectPredictions": 0}
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            self.TestResults["NumPredictionsWithin2Percent"] = 0
            self.TestResults["NumPredictionsWithin5Percent"] = 0
            self.TestResults["NumPredictionsWithin10Percent"] = 0
            self.TestResults["NumPredictionsWithin20Percent"] = 0
            self.TestResults["NumPredictionsWithin50Percent"] = 0
            self.TestResults["NumPredictionsWithin100Percent"] = 0
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            self.TestResults["NumPredictionsWithin1Class"] = 0
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            self.TestResults["NumPredictionsTruePositive"] = 0
            self.TestResults["NumPredictionsTrueNegative"] = 0
            self.TestResults["NumPredictionsFalsePositive"] = 0
            self.TestResults["NumPredictionsFalseNegative"] = 0

        self.TestNumItemsPerClass = [0] * self.NumResultClasses
        self.TestNumPredictionsPerClass = [0] * self.NumResultClasses
        self.TestNumCorrectPerClass = [0] * self.NumResultClasses
    # End - StartTesting




    #####################################################
    #
    # [MLJobTestResults::RecordTestingResult
    # 
    #####################################################
    def RecordTestingResult(self, actualValue, predictedValue):
        fDebug = False
        self.NumSamplesTested += 1

        #########################
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            difference = abs(float(actualValue - predictedValue))

            if (difference == 0):
                self.TestResults["NumCorrectPredictions"] += 1
            if (difference <= (actualValue * 0.02)):
                self.TestResults["NumPredictionsWithin2Percent"] += 1
            elif (difference <= (actualValue * 0.05)):
                self.TestResults["NumPredictionsWithin5Percent"] += 1
            elif (difference <= (actualValue * 0.1)):
                self.TestResults["NumPredictionsWithin10Percent"] += 1
            elif (difference <= (actualValue * 0.2)):
                self.TestResults["NumPredictionsWithin20Percent"] += 1
            elif (difference <= (actualValue * 0.5)):
                self.TestResults["NumPredictionsWithin50Percent"] += 1
            elif (difference <= (actualValue * 1.0)):
                self.TestResults["NumPredictionsWithin100Percent"] += 1

            offset = max(actualValue - self.ResultMinValue, 0)
            actualBucketNum = int(offset / self.BucketSize)
            if (actualBucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                actualBucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
            self.TestNumItemsPerClass[actualBucketNum] += 1

            # Check for extremes, since the prediction may be very huge or very small.
            if (predictedValue >= self.ResultMaxValue):
                predictedBucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
            elif (predictedValue < self.ResultMinValue):
                predictedBucketNum = 0
            else:
                try:
                    offset = max(predictedValue - self.ResultMinValue, 0)
                    predictedBucketNum = int(offset / self.BucketSize)
                    if (predictedBucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                        predictedBucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
                except Exception:
                    predictedBucketNum = 0
            # End - else
            self.TestNumPredictionsPerClass[predictedBucketNum] += 1
            if (predictedBucketNum == actualBucketNum):
                self.TestNumCorrectPerClass[actualBucketNum] += 1
        # End - if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT))

        #########################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            actualValueInt = int(actualValue)
            predictedValueInt = int(predictedValue)
            self.TestNumItemsPerClass[actualValueInt] += 1
            self.TestNumPredictionsPerClass[predictedValue] += 1
            if (actualValueInt == predictedValueInt):
                self.TestResults["NumCorrectPredictions"] += 1
                self.TestResults["NumPredictionsWithin1Class"] += 1
                self.TestNumCorrectPerClass[int(actualValueInt)] += 1
            else:  # if (actualValueInt != predictedValueInt):
                if ((actualValueInt - 1) <= predictedValueInt <= (actualValueInt + 1)):
                    self.TestResults["NumPredictionsWithin1Class"] += 1
        # End - elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):

        #########################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            # If this is a Logistic, then convert the resulting probability into a 0 or 1
            if (fDebug):
                print("RecordTestingResult. Bool. actualValue=" + str(actualValue))
                print("RecordTestingResult. Bool. predictedValue=" + str(predictedValue))
                print("RecordTestingResult. Bool. self.IsLogisticNetwork=" + str(self.IsLogisticNetwork))

            if ((self.IsLogisticNetwork) and (self.OutputThreshold > 0)):
                predictedFloat = float(predictedValue)
                if (fDebug):
                    print("Process a logistic result. predictedValue=" + str(predictedValue) + ", predictedFloat=" 
                            + str(predictedFloat))
                self.LogisticResultsTrueValueList.append(actualValue)
                self.LogisticResultsPredictedProbabilityList.append(predictedFloat)

                # Now, convert the probability to a normal boolean result like we would have for any bool.
                if (predictedFloat >= self.OutputThreshold):
                    predictedValue = 1
                else:
                    predictedValue = 0
            # End - if ((self.IsLogisticNetwork) and (self.OutputThreshold > 0)):

            actualValueInt = int(actualValue)
            predictedValueInt = int(predictedValue)
            if (fDebug):
                print("RecordTestingResult.  actualValueInt = " + str(actualValueInt) 
                        + ", predictedValueInt = " + str(predictedValueInt))

            self.TestNumItemsPerClass[actualValueInt] += 1
            self.TestNumPredictionsPerClass[predictedValueInt] += 1
            if (actualValueInt == predictedValueInt):
                self.TestResults["NumCorrectPredictions"] += 1
                if (predictedValueInt > 0):
                    self.TestResults["NumPredictionsTruePositive"] += 1
                else:
                    self.TestResults["NumPredictionsTrueNegative"] += 1
                self.TestNumCorrectPerClass[int(actualValueInt)] += 1
            else:  # if (actualValueInt != predictedValueInt):
                if (predictedValueInt > 0):
                    self.TestResults["NumPredictionsFalsePositive"] += 1
                else:
                    self.TestResults["NumPredictionsFalseNegative"] += 1
        # End - elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
    # End -  RecordTestingResult



    #####################################################
    #
    # [MLJobTestResults::StopTesting]
    #
    #####################################################
    def StopTesting(self):
        # Normally this is done when we finish testing.
        if (self.IsLogisticNetwork):
            # Get the Receiver Operator Curve AUC
            self.ROCAUC = roc_auc_score(self.LogisticResultsTrueValueList, 
                                        self.LogisticResultsPredictedProbabilityList)

            # Get the Precision-Recall curve and AUPRC
            PrecisionResults, RecallResults, _ = precision_recall_curve(self.LogisticResultsTrueValueList, 
                                            self.LogisticResultsPredictedProbabilityList)
            self.AUPRC = auc(RecallResults, PrecisionResults)

            numSamples = len(self.LogisticResultsPredictedProbabilityList)
            predictedValueList = [0] * numSamples
            for index in range(numSamples):
                currentProbability = self.LogisticResultsPredictedProbabilityList[index]
                if (currentProbability >= self.OutputThreshold):
                    predictedValueList[index] = 1

            self.F1Score = f1_score(self.LogisticResultsTrueValueList, predictedValueList)
        # End - if (self.IsLogisticNetwork):
    # End of StopTesting



    #####################################################
    #
    # [MLJobTestResults::ReadTestResultsFromXML
    #
    #####################################################
    def ReadTestResultsFromXML(self):
        # Every simple value (like <aa>5</aa>) is a named value in the result dict.
        self.TestResults = {}
        currentXMLNode = dxml.XMLTools_GetFirstChildNode(self.ResultXMLNode)
        while (currentXMLNode is not None):
            if (dxml.XMLTools_IsLeafNode(currentXMLNode)):
                nameStr = dxml.XMLTools_GetElementName(currentXMLNode)
                valueStr = dxml.XMLTools_GetTextContents(currentXMLNode)
                try:
                    self.TestResults[nameStr] = int(valueStr)
                except Exception:
                    self.TestResults[nameStr] = valueStr
            # End - if (dxml.XMLTools_IsLeafNode(currentXMLNode)):

            currentXMLNode = dxml.XMLTools_GetAnyPeerNode(currentXMLNode)
        # End - while (currentXMLNode is not None):


        self.NumSamplesTested = dxml.XMLTools_GetChildNodeTextAsInt(self.ResultXMLNode, 
                                                    RESULTS_TEST_NUM_ITEMS_ELEMENT_NAME, 0)
        self.ROCAUC = dxml.XMLTools_GetChildNodeTextAsFloat(self.ResultXMLNode, 
                                                    RESULTS_ROCAUC_ELEMENT_NAME, 0)
        self.AUPRC = dxml.XMLTools_GetChildNodeTextAsInt(self.ResultXMLNode, 
                                                    RESULTS_AUPRC_ELEMENT_NAME, 0)
        self.F1Score = dxml.XMLTools_GetChildNodeTextAsInt(self.ResultXMLNode, 
                                                    RESULTS_F1Score_ELEMENT_NAME, 0)


        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, 
                                                    RESULTS_TEST_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumItemsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, 
                                                    RESULTS_TEST_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumPredictionsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, 
                                                    RESULTS_TEST_NUM_CORRECT_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumCorrectPerClass = MLJob_ConvertStringTo1DVector(resultStr)


        self.LogisticResultsTrueValueList = []
        self.LogisticResultsPredictedProbabilityList = []
        if (self.IsLogisticNetwork):
            resultStr = dxml.XMLTools_GetChildNodeText(self.ResultXMLNode, RESULTS_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME)
            if ((resultStr is not None) and (resultStr != "")):
                resultArray = resultStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)
                for truthProbabilityPair in resultArray:
                    valuePair = truthProbabilityPair.split("=")
                    if (len(valuePair) == 2):
                        try:
                            trueValue = round(float(valuePair[0]))
                            probability = float(valuePair[1])
                        except Exception:
                            print("ReadTestResultsFromXML. EXCEPTION in reading Logistic results")
                            continue

                        #if (probability > 0): 
                        #print("Read Logistic Input. probability=" + str(probability) + ", trueValue=" + str(trueValue))

                        self.LogisticResultsTrueValueList.append(trueValue)
                        self.LogisticResultsPredictedProbabilityList.append(probability)
                # End - for truthProbabilityPair in resultArray:
            # End - if ((resultStr not None) and (resultStr != "")):

            self.ROCAUC = -1
            if ((len(self.LogisticResultsTrueValueList) > 0) and (len(self.LogisticResultsPredictedProbabilityList) > 0)):
                self.ROCAUC = roc_auc_score(self.LogisticResultsTrueValueList, 
                                            self.LogisticResultsPredictedProbabilityList)
        # End - if (self.IsLogisticNetwork):
    # End - ReadTestResultsFromXML





    #####################################################
    #
    # [MLJobTestResults::WriteTestResultsToXML
    #
    #####################################################
    def WriteTestResultsToXML(self):
        for index, (valName, value) in enumerate(self.TestResults.items()):
            dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, valName, str(value))

        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_ITEMS_ELEMENT_NAME, 
                                                        str(self.NumSamplesTested))
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_ROCAUC_ELEMENT_NAME, str(self.ROCAUC))
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_AUPRC_ELEMENT_NAME, str(self.AUPRC))
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_F1Score_ELEMENT_NAME, str(self.F1Score))

        resultStr = MLJob_Convert1DVectorToString(self.TestNumItemsPerClass)
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.TestNumPredictionsPerClass)
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.TestNumCorrectPerClass)
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_CORRECT_PER_CLASS_ELEMENT_NAME, resultStr)


        # This saves the values for Logistic function outputs
        # These are used to compute AUROC and AUPRC
        if (self.IsLogisticNetwork):
            logisticOutputsStr = ""
            listLength = len(self.LogisticResultsTrueValueList)
            for index in range(listLength):
                trueValue = self.LogisticResultsTrueValueList[index]
                probability = self.LogisticResultsPredictedProbabilityList[index]
                logisticOutputsStr = logisticOutputsStr + str(trueValue) + "=" + str(probability) + MLJOB_NAMEVAL_SEPARATOR_CHAR
            if (logisticOutputsStr != ""):
                logisticOutputsStr = logisticOutputsStr[:-1]
                dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME, logisticOutputsStr)
        # End - if (self.IsLogisticNetwork):
    # End - WriteTestResultsToXML


# End - class MLJobTestResults
################################################################################






################################################################################
################################################################################
class MLJob():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.JobFilePathName = ""
        self.FormatVersion = DEFAULT_JOB_FORMAT_VERSION

        # These are the sections of the JOB spec
        self.JobXMLDOM = None
        self.RootXMLNode = None
        self.JobControlXMLNode = None
        self.DataXMLNode = None
        self.NetworkLayersXMLNode = None
        self.TrainingXMLNode = None
        self.RuntimeXMLNode = None

        self.ResultsXMLNode = None
        self.ResultsPreflightXMLNode = None
        self.ResultsTrainingXMLNode = None
        self.ResultsTestingXMLNode = None

        self.AllTestResults = MLJobTestResults()
        self.NumResultsSubgroups = 10
        self.TestResultsSubgroupList = []
        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList.append(MLJobTestResults())

        self.NumResultClasses = 0
        self.numInputVars = -1

        self.SavedModelStateXMLNode = None
        self.NeuralNetMatrixListXMLNode = None

        self.NumSamplesTrainedPerEpoch = 0
        self.NumPatientsTrainedPerEpoch = 0
        self.NumPatientsSkippedPerEpoch = 0
        self.NumDataPointsTrainedPerEpoch = 0

        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0
        self.AvgLossPerEpochList = []

        self.NetworkType = ""
        self.AllowGPU = False

        self.HashDict = {}
        self.RuntimeNonce = 0

        self.TrainingValueName = ""
        self.TrainingValueInfoSrc = ""
        self.TrainingValueRefDate = ""
        self.TrainingResultMinValue = -1
        self.TrainingResultMaxValue = -1
        self.TrainingResultMeanValue = -1
        self.TrainingNumResultPriorities = 0
        self.TrainingResultBucketSize = 1
        self.TrainingResultClassPriorities = []

        # Preflight state
        self.NumResultsInPreflight = 0
        self.PreflightNumItemsPerClass = []
        self.PreflightInputMins = []
        self.PreflightInputMaxs = []
        self.PreflightInputRanges = []
        self.ResultValMinValue = 0
        self.ResultValMaxValue = 0
        self.ResultValBucketSize = 0

        # Runtime state
        self.StartRequestTimeStr = ""
        self.StopRequestTimeStr = ""
        self.CurrentEpochNum = 0
        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0
        self.BufferedLogLines = ""
        self.ResultValueType = tdf.TDF_DATA_TYPE_INT
        self.TrainingPriorities = [-1] * 1
        self.PreflightResultClassWeights = []

        self.TrainNumItemsPerClass = []

        self.Debug = False
        self.LogFilePathname = ""

        self.OutputThreshold = -1
        self.IsLogisticNetwork = False

        # Runtime State
        self.StartRequestTimeStr = ""
        self.StopRequestTimeStr = ""
        self.CurrentEpochNum = 0
        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0

        self.BufferedLogLines = ""
    # End -  __init__




    #####################################################
    #
    # [MLJob::InitNewJobImpl]
    #
    #####################################################
    def InitNewJobImpl(self):
        impl = getDOMImplementation()

        # This creates the document and the root node.
        self.JobXMLDOM = impl.createDocument(None, ROOT_ELEMENT_NAME, None)
        self.RootXMLNode = dxml.XMLTools_GetNamedElementInDocument(self.JobXMLDOM, ROOT_ELEMENT_NAME)
        self.FormatVersion = DEFAULT_JOB_FORMAT_VERSION
        dxml.XMLTools_SetAttribute(self.RootXMLNode, FORMAT_VERSION_ATTRIBUTE, str(self.FormatVersion))

        # JobControl and its children
        self.JobControlXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, JOB_CONTROL_ELEMENT_NAME)
        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_IDLE)
        self.SetJobControlStr(JOBCTL_RESULT_MSG_ELEMENT_NAME, "")
        self.SetJobControlStr(JOBCTL_ERROR_CODE_ELEMENT_NAME, str(JOB_E_NO_ERROR))
        self.SetJobControlStr(JOBCTL_RUN_OPTIONS_ELEMENT_NAME, "")

        self.DataXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, DATA_ELEMENT_NAME)
        self.NetworkLayersXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_ELEMENT_NAME)
        self.TrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, TRAINING_ELEMENT_NAME)
        self.RuntimeXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RUNTIME_ELEMENT_NAME)

        self.ResultsXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RESULTS_ELEMENT_NAME)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                        RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                        RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                        RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        # The saved state
        self.SavedModelStateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, 
                                                        SAVED_MODEL_STATE_ELEMENT_NAME)
        self.NeuralNetMatrixListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.SavedModelStateXMLNode, 
                                                        NETWORK_MATRIX_LIST_NAME)

        self.HashDict = {}
        self.RuntimeNonce = 0

        self.InferResultInfo()
    # End of InitNewJobImpl





    #####################################################
    #
    # [MLJob::ReadJobFromFile]
    #
    # Returns: Error code
    #####################################################
    def ReadJobFromFile(self, jobFilePathName):
        err = JOB_E_NO_ERROR

        try:
            fileH = open(jobFilePathName, "r")
            contentsText = fileH.read()
            fileH.close()
        except Exception:
            return JOB_E_CANNOT_OPEN_FILE
       
        err = self.ReadJobFromString(contentsText)

        # Update the file name. If we renamed a file when it was closed,
        # we need to save this new file name.
        self.JobFilePathName = jobFilePathName

        return err
    # End of ReadJobFromFile



    #####################################################
    #
    # [MLJob::SaveAs]
    #
    # Insert the runtime node and results node
    #####################################################
    def SaveAs(self, jobFilePathName):
        # Update the file name. If we renamed a file when it was closed,
        # we need to save this new file name.
        self.JobFilePathName = jobFilePathName

        contentsText = self.WriteJobToString()

        fileH = open(jobFilePathName, "w")
        fileH.write(contentsText)
        fileH.close()
    # End of SaveAs



    #####################################################
    #
    # [MLJob::SaveJobWithoutRuntime]
    #
    #####################################################
    def SaveJobWithoutRuntime(self, jobFilePathName):
        # Update the file name. If we renamed a file when it was closed,
        # we need to save this new file name.
        self.JobFilePathName = jobFilePathName

        # Do not call self.WriteJobToString();
        # That will insert the runtime node and results node, which
        # can be confusing for an input job.

        # Remove any previous formatting text so we can format
        dxml.XMLTools_RemoveAllWhitespace(self.RootXMLNode)

        # Don't add indentation or newlines. Those accumulate each time
        # the XML is serialized/deserialized, so for a large job the whitespace
        # grows to dwarf the actual content.        
        contentsText = self.JobXMLDOM.toprettyxml(indent="    ", newl="\n", encoding=None)
        #resultStr = resultStr.replace("\n", "")
        #resultStr = resultStr.replace("\r", "")
        #resultStr = resultStr.replace("   ", "")
        #resultStr = resultStr.replace("  ", "")

        fileH = open(jobFilePathName, "w")
        fileH.write(contentsText)
        fileH.close()
    # End of SaveJobWithoutRuntime




    #####################################################
    #
    # [MLJob::LogMsg]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def LogMsg(self, messageStr):
        if (self.LogFilePathname == ""):
            return

        #now = datetime.now()
        #timeStr = now.strftime("%Y-%m-%d %H:%M:%S")
        #completeLogLine = timeStr + " " + messageStr + NEWLINE_STR
        completeLogLine = messageStr + NEWLINE_STR

        try:
            fileH = open(self.LogFilePathname, "a+")
            fileH.write(completeLogLine) 
            fileH.flush()
            fileH.close()
        except Exception:
            pass

        # The old, now unused, way to log.
        #self.BufferedLogLines = self.BufferedLogLines + completeLogLine
        
        #print(messageStr)
    # End of LogMsg





    #####################################################
    #
    # [MLJob::ReadJobFromString]
    #
    # Return JOB_E_NO_ERROR or an error
    #####################################################
    def ReadJobFromString(self, jobString):
        #print("MLJob::ReadJobFromString. jobString=" + jobString)

        if (jobString == ""):
            return JOB_E_INVALID_FILE

        # Parse the text string into am XML DOM
        self.JobXMLDOM = dxml.XMLTools_ParseStringToDOM(jobString)
        if (self.JobXMLDOM is None):
            return JOB_E_INVALID_FILE

        self.RootXMLNode = dxml.XMLTools_GetNamedElementInDocument(self.JobXMLDOM, ROOT_ELEMENT_NAME)
        if (self.RootXMLNode is None):
            return JOB_E_INVALID_FILE

        self.FormatVersion = DEFAULT_JOB_FORMAT_VERSION
        attrStr = dxml.XMLTools_GetAttribute(self.RootXMLNode, FORMAT_VERSION_ATTRIBUTE)
        if ((attrStr is not None) and (attrStr != "")):
            self.FormatVersion = int(attrStr)

        ###############
        self.JobControlXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, JOB_CONTROL_ELEMENT_NAME)
        self.DataXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, DATA_ELEMENT_NAME)
        self.NetworkLayersXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_ELEMENT_NAME)
        self.TrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, TRAINING_ELEMENT_NAME)

        self.ResultsXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RESULTS_ELEMENT_NAME)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        self.RuntimeXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RUNTIME_ELEMENT_NAME)

        self.SavedModelStateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, SAVED_MODEL_STATE_ELEMENT_NAME)
        self.NeuralNetMatrixListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.SavedModelStateXMLNode, NETWORK_MATRIX_LIST_NAME)

        self.NetworkType = self.GetNetworkType().lower()
        self.IsLogisticNetwork = dxml.XMLTools_GetChildNodeTextAsBool(self.NetworkLayersXMLNode, 
                                                                    NETWORK_LOGISTIC_ELEMENT_NAME, False)

        self.OutputThreshold = -1
        # The default is any probability over 50% is True. This is a coin-toss.
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkLayersXMLNode, 
                                                                    NETWORK_OUTPUT_THRESHOLD_ELEMENT_NAME, "0.5")
        if ((resultStr is not None) and (resultStr != "")):
            try:
                self.OutputThreshold = float(resultStr)
            except Exception:
                self.OutputThreshold = -1

        self.Debug = False
        xmlNode = dxml.XMLTools_GetChildNode(self.JobControlXMLNode, "Debug")
        if (xmlNode is not None):
            resultStr = dxml.XMLTools_GetTextContents(xmlNode)
            resultStr = resultStr.lower().lstrip()
            if (resultStr in ("on", "true", "yes", "1")):
                self.Debug = True

        self.AllowGPU = True
        xmlNode = dxml.XMLTools_GetChildNode(self.JobControlXMLNode, "AllowGPU")
        if (xmlNode is not None):
            resultStr = dxml.XMLTools_GetTextContents(xmlNode)
            resultStr = resultStr.lower().lstrip()
            if (resultStr in ("off", "false", "no", "0")):
                self.AllowGPU = True

        xmlNode = dxml.XMLTools_GetChildNode(self.JobControlXMLNode, "LogFilePathname")
        if (xmlNode is not None):
            resultStr = dxml.XMLTools_GetTextContents(xmlNode)
            resultStr = resultStr.lstrip().rstrip()
            self.LogFilePathname = resultStr

        self.ReadTrainingConfigFromXML(self.TrainingXMLNode)

        # Read any runtime if it is present. No error if it is missing.
        #
        # This is used when 
        # 1. Sending jobs between a dispatcher process and a child worker process
        #    In this case, it is not normally stored in a file. 
        #
        # 2. Using a pre-trained neural network to make a prediction on some new data.
        #
        # 3. To "suspend" runtime state and resume it at a later date.
        #    This is not supported now and would raise some tricky synchronization issues.
        self.ReadRuntimeFromXML(self.RuntimeXMLNode)

        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InferResultInfo()

        # Read the results for both testing and training
        # This will overwrite any values that were intiialized.
        # But, initializing first means anything not stored in the XML file will still be initialized
        self.ReadPreflightResultsFromXML(self.ResultsPreflightXMLNode)
        self.ReadTraingResultsFromXML(self.ResultsTrainingXMLNode)
        self.ReadTestResultsFromXML(self.ResultsTestingXMLNode)

        return JOB_E_NO_ERROR
    # End of ReadJobFromString




    #####################################################
    #
    # [MLJob::WriteJobToString]
    #
    #####################################################
    def WriteJobToString(self):
        # Write the current runtime to a temporary node that is just used for 
        # holding an incomplete request that is currently executing
        # This is used when sending jobs between a dispatcher process and a
        # child worker process, and is not normally stored in a file. It could
        # be saved to a file if we ever want to "suspend" runtime state and
        # resume it at a later date, but that is not supported now and would
        # raise some tricky synchronization issues.
        self.RuntimeXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RUNTIME_ELEMENT_NAME)
        self.WriteRuntimeToXML(self.RuntimeXMLNode)

        self.WritePreflightResultsToXML(self.ResultsPreflightXMLNode)
        self.WriteTrainResultsToXML(self.ResultsTrainingXMLNode)
        self.WriteTestResultsToXML(self.ResultsTestingXMLNode)

        # Remove any previous formatting text so we can format
        dxml.XMLTools_RemoveAllWhitespace(self.RootXMLNode)

        # Don't add indentation or newlines. Those accumulate each time
        # the XML is serialized/deserialized, so for a large job the whitespace
        # grows to dwarf the actual content.        
        resultStr = self.JobXMLDOM.toprettyxml(indent="    ", newl="\n", encoding=None)
        #resultStr = resultStr.replace("\n\r ", "")
        #resultStr = resultStr.replace("\r", "")
        #resultStr = resultStr.replace("   ", "")
        #resultStr = resultStr.replace("  ", "")

        return resultStr
    # End of WriteJobToString




    #####################################################
    #
    # [MLJob::ReadTrainingConfigFromXML]
    #
    # There are two similar but importantly different procedures:
    #
    # 1. ReadTrainingConfigFromXML - Read the training configuration from 
    #   the Training section. This is read, but never written, because it
    #   is static configuration that is in the file, not results from execution.
    #
    # 2. ReadTraingResultsFromXML - Read the results of training, from the
    #   results section.
    #####################################################
    def ReadTrainingConfigFromXML(self, parentXMLNode):
        valueInfoNode = dxml.XMLTools_GetChildNode(parentXMLNode, TRAINING_PRIORITY_VALUE_INFO)

        self.TrainingValueName = dxml.XMLTools_GetChildNodeTextAsStr(valueInfoNode, 
                                                            TRAINING_PRIORITY_VALUE_NAME, "")
        self.TrainingValueInfoSrc = dxml.XMLTools_GetChildNodeTextAsStr(valueInfoNode, 
                                                            TRAINING_PRIORITY_SRC_FILE, "")
        self.TrainingValueRefDate = dxml.XMLTools_GetChildNodeTextAsStr(valueInfoNode, 
                                                            TRAINING_PRIORITY_CREATION_DATE, "")
        self.TrainingResultMinValue = dxml.XMLTools_GetChildNodeTextAsFloat(valueInfoNode, 
                                                            TRAINING_PRIORITY_MIN_VALUE, -1)
        self.TrainingResultMaxValue = dxml.XMLTools_GetChildNodeTextAsFloat(valueInfoNode, 
                                                            TRAINING_PRIORITY_MAX_VALUE, -1)
        self.TrainingResultMeanValue = dxml.XMLTools_GetChildNodeTextAsFloat(valueInfoNode, 
                                                            TRAINING_PRIORITY_MEAN_VALUE, -1)
        self.TrainingNumResultPriorities = dxml.XMLTools_GetChildNodeTextAsInt(valueInfoNode, 
                                                            TRAINING_PRIORITY_NUM_CLASSES, -1)

        valueRange = self.TrainingResultMaxValue - self.TrainingResultMinValue
        self.TrainingResultBucketSize = (valueRange / self.TrainingNumResultPriorities)

        listStr = dxml.XMLTools_GetChildNodeTextAsStr(valueInfoNode, TRAINING_PRIORITY_CLASS_PRIORITIES, "")
        priorityStrList = listStr.split(",")
        self.TrainingResultClassPriorities = [int(i) for i in priorityStrList]
    # End - ReadTrainingConfigFromXML




    #####################################################
    #
    # [MLJob::ReadRuntimeFromXML]
    #
    #####################################################
    def ReadRuntimeFromXML(self, parentXMLNode):
        ###################
        # Basics
        # These are all optional. No error if any are missing.
        # Save the current file pathname in the XML so it can be restored when we pass a job back and 
        # forth in memory between processes.
        self.JobFilePathName = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                            RUNTIME_FILE_PATHNAME_ELEMENT_NAME, "")
        self.StartRequestTimeStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                            RUNTIME_START_ELEMENT_NAME, "")
        self.StopRequestTimeStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                            RUNTIME_STOP_ELEMENT_NAME, "")
        self.CurrentEpochNum = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                            RUNTIME_CURRENT_EPOCH_ELEMENT_NAME, -1)
        self.RuntimeNonce = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, RUNTIME_NONCE_ELEMENT_NAME, 0)


        self.TotalTrainingLossInCurrentEpoch = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                            "TotalTrainingLossInCurrentEpoch", -1.0)
        self.NumTrainLossValuesCurrentEpoch = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                            "NumTrainLossValuesCurrentEpoch", -1.0)

        ###################
        self.BufferedLogLines = dxml.XMLTools_GetChildNodeText(parentXMLNode, RUNTIME_LOG_NODE_ELEMENT_NAME)

        ###################
        # Read the latest Hash table
        hashStr = dxml.XMLTools_GetChildNodeText(parentXMLNode, RUNTIME_HASH_DICT_ELEMENT_NAME)
        if ((hashStr is not None) and (hashStr != "")):
            self.HashDict = json.loads(hashStr)
    # End - ReadRuntimeFromXML





    #####################################################
    #
    # [MLJob::WriteRuntimeToXML]
    #
    #####################################################
    def WriteRuntimeToXML(self, parentXMLNode):
        dxml.XMLTools_RemoveAllChildNodes(parentXMLNode)

        ###################
        # Basics
        # Save the current file pathname in the XML so it can be restored when we pass a job back and 
        # forth in memory between processes.
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_FILE_PATHNAME_ELEMENT_NAME, str(self.JobFilePathName))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_START_ELEMENT_NAME, str(self.StartRequestTimeStr))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_STOP_ELEMENT_NAME, str(self.StopRequestTimeStr))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_CURRENT_EPOCH_ELEMENT_NAME, str(self.CurrentEpochNum))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_NONCE_ELEMENT_NAME, str(self.RuntimeNonce))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "OS", str(platform.platform()))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "CPU", str(platform.processor()))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "GPU", "None")

        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "TotalTrainingLossInCurrentEpoch", 
                                            str(self.TotalTrainingLossInCurrentEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "NumTrainLossValuesCurrentEpoch", 
                                            str(self.NumTrainLossValuesCurrentEpoch))

        ###################
        # If there is a log string, then add it to the end of the Result node.
        if (self.BufferedLogLines != ""):
            logXMLNode = dxml.XMLTools_GetChildNode(parentXMLNode, RUNTIME_LOG_NODE_ELEMENT_NAME)
            if (logXMLNode is None):
                logXMLNode = self.JobXMLDOM.createElement(RUNTIME_LOG_NODE_ELEMENT_NAME)
                parentXMLNode.appendChild(logXMLNode)
            dxml.XMLTools_SetTextContents(logXMLNode, self.BufferedLogLines)
        # End - if (self.BufferedLogLines != "")

        ###################
        # Save the list of Matrix hash values
        hashStr = json.dumps(self.HashDict)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_HASH_DICT_ELEMENT_NAME, hashStr)
    # End -  WriteRuntimeToXML




    #####################################################
    #
    # [MLJob::StartJobExecution]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartJobExecution(self):
        # Discard Previous results
        dxml.XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        # Each request has a single test. When we finish the test, we have
        # finished the entire reqeust.
        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_IDLE)
        self.SetJobControlStr(JOBCTL_RESULT_MSG_ELEMENT_NAME, "")
        self.SetJobControlStr(JOBCTL_ERROR_CODE_ELEMENT_NAME, str(JOB_E_NO_ERROR))

        now = datetime.now()
        self.StartRequestTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")

        # Reset the log file if there is one.
        if (self.LogFilePathname != ""):
            try:
                os.remove(self.LogFilePathname) 
            except Exception:
                pass
            try:
                fileH = open(self.LogFilePathname, "w+")
                fileH.flush()
                fileH.close()
            except Exception:
                pass
        # End - if (self.LogFilePathname != ""):
    # End of StartJobExecution






    #####################################################
    #
    # [MLJob::FinishJobExecution]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishJobExecution(self, errCode, errorMsg):
        # Each request has a single test. When we finish the test, we have
        # finished the entire reqeust.
        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_DONE)
        self.SetJobControlStr(JOBCTL_ERROR_CODE_ELEMENT_NAME, str(errCode))
        if (errCode == JOB_E_NO_ERROR):
            self.SetJobControlStr(JOBCTL_RESULT_MSG_ELEMENT_NAME, "OK")
        else:
            self.SetJobControlStr(JOBCTL_RESULT_MSG_ELEMENT_NAME, errorMsg)

        # Discard all of the hash values. Those are only used for debugging.
        xmlNode = dxml.XMLTools_GetChildNode(self.RuntimeXMLNode, RUNTIME_HASH_DICT_ELEMENT_NAME)
        if (xmlNode is not None):
            dxml.XMLTools_RemoveAllChildNodes(xmlNode)
        self.HashDict = {}

        now = datetime.now()
        self.StopRequestTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")

        # Remove earlier results. We will write the final results when we save the job to XML
        dxml.XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        self.AllTestResults.StopTesting()
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].StopTesting()
    # End of FinishJobExecution




    #####################################################
    #
    # [MLJob::InferResultInfo
    # 
    # This is a private procedure, which takes the reuslt var
    # and computes its type, and more values used to collect result statistics.
    # This is done anytime we restore a job from meory, and also
    # when we start pre-flight or training.
    #####################################################
    def InferResultInfo(self):
        resultValName = self.GetNetworkOutputVarName()
        if (resultValName != ""):
            self.ResultValueType = tdf.TDF_GetVariableType(resultValName)
        else:
            self.ResultValueType = tdf.TDF_DATA_TYPE_FLOAT

        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            self.NumResultClasses = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS
            self.ResultValMinValue, self.ResultValMaxValue = tdf.TDF_GetMinMaxValuesForVariable(resultValName)
            valRange = float(self.ResultValMaxValue - self.ResultValMinValue)
            self.ResultValBucketSize = float(valRange) / float(ML_JOB_NUM_NUMERIC_VALUE_BUCKETS)
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            self.NumResultClasses = tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES
            self.ResultValMinValue = 0
            self.ResultValMaxValue = tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES - 1
            self.ResultValBucketSize = 1
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            self.NumResultClasses = 2
            self.ResultValMinValue = 0
            self.ResultValMaxValue = 1
            self.ResultValBucketSize = 1
        else:
            self.NumResultClasses = 1
            self.ResultValMinValue = 0
            self.ResultValMaxValue = 0
            self.ResultValBucketSize = 1

        inputVarNameListStr = self.GetNetworkInputVarNames()
        inputVarArray = inputVarNameListStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)
        self.numInputVars = len(inputVarArray)

        self.AllTestResults.SetGlobalResultInfo(self.ResultValueType, 
                                    self.NumResultClasses, 
                                    self.ResultValMinValue, 
                                    self.ResultValMaxValue, 
                                    self.ResultValBucketSize, 
                                    self.IsLogisticNetwork, 
                                    self.OutputThreshold)

        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList[index].SetGlobalResultInfo(self.ResultValueType, 
                                    self.NumResultClasses, 
                                    self.ResultValMinValue, 
                                    self.ResultValMaxValue, 
                                    self.ResultValBucketSize, 
                                    self.IsLogisticNetwork, 
                                    self.OutputThreshold)
    # End - InferResultInfo




    #####################################################
    #
    # [MLJob::StartPreflight]
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartPreflight(self):
        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InferResultInfo()

        self.PreflightNumItemsPerClass = numpy.zeros(self.NumResultClasses)
        self.PreflightInputMins = numpy.full((self.numInputVars), 1000000)
        self.PreflightInputMaxs = numpy.full((self.numInputVars), -1)
        self.PreflightInputRanges = numpy.full((self.numInputVars), 0)

        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_PREFLIGHT)
    # End - StartPreflight




    #####################################################
    #
    # [MLJob::PreflightData
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def PreflightData(self, inputVec, resultVal):
        for valNum in range(self.numInputVars):
            currentValue = inputVec[valNum]
            if (currentValue < self.PreflightInputMins[valNum]):
                self.PreflightInputMins[valNum] = currentValue
            if (currentValue > self.PreflightInputMaxs[valNum]):
                self.PreflightInputMaxs[valNum] = currentValue
        # End - for valNum in range(self.numInputVars)
    # End - PreflightData



    #####################################################
    #
    # [MLJob::FinishPreflight
    # 
    #####################################################
    def FinishPreflight(self):
        for inputNum in range(self.numInputVars):
            self.PreflightInputRanges[inputNum] = self.PreflightInputMaxs[inputNum] - self.PreflightInputMins[inputNum]
        # End - for inputNum in range(self.numInputVars):
    # End - FinishPreflight


    #####################################################
    # [MLJob::GetPreflightResults]
    #####################################################
    def GetPreflightResults(self):
        return self.numInputVars, self.PreflightInputMins, self.PreflightInputRanges
    # End - GetPreflightResults


    #####################################################
    # [MLJob::GetNumTrainingPriorities]
    #####################################################
    def GetNumTrainingPriorities(self):
        return self.TrainingNumResultPriorities


    #####################################################
    #
    # [MLJob::GetTrainingPriority]
    # 
    #####################################################
    def GetTrainingPriority(self, resultVal):
        fDebug = False

        #####################
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            offset = max((resultVal - self.TrainingResultMinValue), 0.0)
            resultBucket = int(offset / self.TrainingResultBucketSize)
            resultBucket = min(resultBucket, self.TrainingNumResultPriorities - 1)
            if (fDebug):
                print("GetTrainingPriority. resultVal = " + str(resultVal))
                print("    self.TrainingResultMinValue=" + str(self.TrainingResultMinValue))
                print("    offset=" + str(offset))
                print("    self.TrainingResultBucketSize=" + str(self.TrainingResultBucketSize))
                print("    resultBucket=" + str(resultBucket))
                print("    self.TrainingResultClassPriorities=" + str(self.TrainingResultClassPriorities))
                print("    Priority=" + str(self.TrainingResultClassPriorities[resultBucket]))
            # End - if (fDebug):

            return self.TrainingResultClassPriorities[resultBucket]
        #####################
        elif (self.ResultValueType in (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS, tdf.TDF_DATA_TYPE_BOOL)):
            return 0
        else:
            return(0)
    # End - GetTrainingPriority






    #####################################################
    #
    # [MLJob::StartTraining
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartTraining(self):
        random.seed()

        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InferResultInfo()

        self.CurrentEpochNum = 0
        self.NumSamplesTrainedPerEpoch = 0
        self.NumPatientsTrainedPerEpoch = 0
        self.NumPatientsSkippedPerEpoch = 0
        self.NumDataPointsTrainedPerEpoch = 0

        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0
        self.AvgLossPerEpochList = []

        self.TrainNumItemsPerClass = [0] * self.NumResultClasses

        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_TRAINING)
    # End - StartTraining




    #####################################################
    #
    # [MLJob::StartTrainingEpoch
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartTrainingEpoch(self):
        # Reset the counters for the new epoch
        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0
    # End - StartTrainingEpoch



    #####################################################
    #
    # [MLJob::RecordTrainingLoss
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def RecordTrainingLoss(self, loss):
        # Be careful, the loss may be positive or negative
        self.TotalTrainingLossInCurrentEpoch += abs(loss)
        self.NumTrainLossValuesCurrentEpoch += 1
    # End -  RecordTrainingLoss



    #####################################################
    #
    # [MLJob::RecordTrainingSample
    # 
    # This is a public procedure, it is called by the client.
    #
    # The standard deviation is the square root of the average of the squared deviations from the mean, 
    # i.e., std = sqrt(mean(x)) , where x = abs(a - a. mean())**2 . 
    # The average squared deviation is typically calculated as x. sum() / N , where N = len(x) .
    #####################################################
    def RecordTrainingSample(self, inputVec, actualValue):
        # We only record the stats on the first epoch.
        if (self.CurrentEpochNum > 0):
            return
        self.NumSamplesTrainedPerEpoch += 1

        #####################
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            offset = max(actualValue - self.ResultValMinValue, 0)
            bucketNum = int(offset / self.ResultValBucketSize)
            if (bucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                bucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
            self.TrainNumItemsPerClass[bucketNum] += 1
        #####################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            intActualValue = max(int(actualValue), 0)
            intActualValue = min(int(actualValue), 1)
            self.TrainNumItemsPerClass[intActualValue] += 1
        #####################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            intActualValue = max(int(actualValue), 0)
            intActualValue = min(int(actualValue), tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES - 1)
            self.TrainNumItemsPerClass[intActualValue] += 1
    # End -  RecordTrainingSample




    #####################################################
    #
    # [MLJob::FinishTrainingEpoch
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishTrainingEpoch(self):
        if (self.NumTrainLossValuesCurrentEpoch > 0):
            avgLoss = float(self.TotalTrainingLossInCurrentEpoch / float(self.NumTrainLossValuesCurrentEpoch))
        else:
            avgLoss = 0.0

        self.AvgLossPerEpochList.append(avgLoss)
        self.CurrentEpochNum += 1
    # End -  FinishTrainingEpoch




    #####################################################
    #
    # [MLJob::StartTesting
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartTesting(self):
        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InferResultInfo()

        self.AllTestResults.StartTesting()
        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList[index].StartTesting()

        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_TESTING)
    # End - StartTesting




    #####################################################
    #
    # [MLJob::RecordTestingResult
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def RecordTestingResult(self, actualValue, predictedValue, subGroupNum):
        self.AllTestResults.RecordTestingResult(actualValue, predictedValue)
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            self.TestResultsSubgroupList[index].RecordTestingResult(actualValue, predictedValue)
    # End -  RecordTestingResult




    #####################################################
    #
    # [MLJob::TrainingCanPauseResume]
    #
    # For discussion on why XGBoost cannot do this, see:
    #   https://github.com/dmlc/xgboost/issues/3055
    #
    # And for more discussion on XGBoost and incremental training:
    #   https://stackoverflow.com/questions/38079853/how-can-i-implement-incremental-training-for-xgboost/47900435#47900435
    #   https://discuss.xgboost.ai/t/incremental-training-of-xgboost-with-fewer-classes-present/2374
    #   https://xgboost.readthedocs.io/en/latest/python/examples/continuation.html
    #####################################################
    def TrainingCanPauseResume(self):
        if ((self.NetworkType is not None) and (self.NetworkType.lower() == "xgboost")):
            return False

        return True
    # End of TrainingCanPauseResume




    #####################################################
    #
    # [MLJob::GetNamedStateAsStr
    # 
    # This is used by the different models to restore their 
    # runtime state
    #####################################################
    def GetNamedStateAsStr(self, name, defaultVal):
        stateXMLNode = dxml.XMLTools_GetChildNode(self.SavedModelStateXMLNode, name)
        if (stateXMLNode is None):
            return defaultVal

        stateStr = dxml.XMLTools_GetTextContents(stateXMLNode)
        if (stateStr is None):
            return defaultVal

        stateStr = stateStr.lstrip().rstrip()
        return stateStr
    # End - GetNamedStateAsStr




    #####################################################
    #
    # [MLJob::SetNamedStateAsStr
    # 
    # This is used by the different models to restore their 
    # runtime state
    #####################################################
    def SetNamedStateAsStr(self, name, stateStr):
        stateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.SavedModelStateXMLNode, name)
        if (stateXMLNode is None):
            return

        dxml.XMLTools_SetTextContents(stateXMLNode, stateStr)
    # End - SetNamedStateAsStr




    #####################################################
    #
    # [MLJob::GetLinearUnitMatrices
    # 
    # Returns:
    #   FoundIt (True/False)
    #   weightMatrix
    #   biasMatrix
    #####################################################
    def GetLinearUnitMatrices(self, name):
        fDebug = False

        linearUnitNode = dxml.XMLTools_GetChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (linearUnitNode is None):
            if (fDebug):
                print("MLJob::GetLinearUnitMatrices. Error. Linear Unit node is None")
            return False, None, None

        weightXMLNode = dxml.XMLTools_GetChildNode(linearUnitNode, NETWORK_MATRIX_WEIGHT_MATRIX_NAME)
        biasXMLNode = dxml.XMLTools_GetChildNode(linearUnitNode, NETWORK_MATRIX_BIAS_VECTOR_NAME)
        if ((weightXMLNode is None) or (biasXMLNode is None)):
            if (fDebug):
                print("MLJob::GetLinearUnitMatrices. Error. weightXMLNode is None")
            return False, None, None

        weightStr = dxml.XMLTools_GetTextContents(weightXMLNode).lstrip().rstrip()
        biasStr = dxml.XMLTools_GetTextContents(biasXMLNode).lstrip().rstrip()

        weightMatrix = self.MLJob_ConvertStringTo2DMatrix(weightStr)
        biasMatrix = MLJob_ConvertStringTo1DVector(biasStr)

        if (fDebug):
            print("GetLinearUnitMatrices. name=" + name)
            print("   WeightChecksum=" + str(self.ComputeArrayChecksum(weightMatrix)))
            print("   weightStr=" + str(weightStr))
            print("   weightMatrix=" + str(weightMatrix))
            print("   biasStr=" + str(biasStr))
            print("   biasChecksum=" + str(self.ComputeArrayChecksum(biasMatrix)))

        return True, weightMatrix, biasMatrix
    # End - GetLinearUnitMatrices


     

    #####################################################
    #
    # [MLJob::SetLinearUnitMatrices
    # 
    #####################################################
    def SetLinearUnitMatrices(self, name, weightMatrix, biasMatrix):
        fDebug = False

        linearUnitNode = dxml.XMLTools_GetOrCreateChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (linearUnitNode is None):
            return
        weightXMLNode = dxml.XMLTools_GetOrCreateChildNode(linearUnitNode, NETWORK_MATRIX_WEIGHT_MATRIX_NAME)
        biasXMLNode = dxml.XMLTools_GetOrCreateChildNode(linearUnitNode, NETWORK_MATRIX_BIAS_VECTOR_NAME)
        if ((weightXMLNode is None) or (biasXMLNode is None)):
            return

        weightStr = self.MLJob_Convert2DMatrixToString(weightMatrix)
        biasStr = MLJob_Convert1DVectorToString(biasMatrix)
        if (fDebug):
            print("MLJob::SetLinearUnitMatrices Name=" + name)
            print("   WeightChecksum=" + str(self.ComputeArrayChecksum(weightMatrix)))
            print("   weightStr=" + str(weightStr))
            print("   weightMatrix=" + str(weightMatrix))
            print("   biasStr=" + str(biasStr))
            print("   biasChecksum=" + str(self.ComputeArrayChecksum(biasMatrix)))

        dxml.XMLTools_SetTextContents(biasXMLNode, biasStr)
        dxml.XMLTools_SetTextContents(weightXMLNode, weightStr)
    # End - SetLinearUnitMatrices




    ################################################################################
    #
    # [MLJob_Convert2DMatrixToString]
    #
    # inputArray is a numpy array.
    ################################################################################
    def MLJob_Convert2DMatrixToString(self, inputArray):
        numRows = len(inputArray)
        if (numRows <= 0):
            numCols = 0
        else:
            numCols = len(inputArray[0])

        resultString = "NumD=2;D=" + str(numRows) + VALUE_SEPARATOR_CHAR + str(numCols) + ";T=float;" + ROW_SEPARATOR_CHAR
        for rowNum in range(numRows):
            row = inputArray[rowNum]
            for numVal in row:
                resultString = resultString + str(numVal) + VALUE_SEPARATOR_CHAR
            resultString = resultString[:-1]
            resultString = resultString + ROW_SEPARATOR_CHAR

        return(resultString)
    # End - MLJob_Convert2DMatrixToString





    ################################################################################
    #
    # [MLJob_ConvertStringTo2DMatrix]
    #
    ################################################################################
    def MLJob_ConvertStringTo2DMatrix(self, matrixStr):
        # Read the dimension property
        sectionList = matrixStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)
        dimensionStr = ""
        for propertyStr in sectionList:
            propertyParts = propertyStr.split("=")
            if (len(propertyParts) < 2):
                continue

            propName = propertyParts[0]
            propValue = propertyParts[1]
            if (propName == "D"):
                dimensionStr = propValue
        # End - for propertyStr in sectionList:

        # Parse the dimension property.
        numRows = 0
        numCols = 0
        if (dimensionStr != ""):
            dimensionList = dimensionStr.split(VALUE_SEPARATOR_CHAR)
            if (len(dimensionList) == 2):
                numRows = int(dimensionList[0])
                numCols = int(dimensionList[1])
            else:
                print("\n\nERROR! MLJob_ConvertStringTo2DMatrix. Invalid dimension for a matrixStr. dimensionStr=[" + dimensionStr + "]")
                sys.exit(0)
        # End - if (dimensionStr != ""):

        # Make an empty matrix which will be filled below.
        newMatrix = numpy.empty([numRows, numCols])

        # Read each 1-D vector and put it in the next position inside the result matrix
        matrixAllRowsStr = sectionList[len(sectionList) - 1]
        matrixRowStrList = matrixAllRowsStr.split(ROW_SEPARATOR_CHAR)
        rowNum = 0    
        for singleRowStr in matrixRowStrList:
            if (singleRowStr != ""):
                # Place a vector into the current spot of the result matrix
                valueList = singleRowStr.split(VALUE_SEPARATOR_CHAR)
                colNum = 0
                for value in valueList:
                    if (colNum >= numCols):
                        print("\n\nERROR! MLJob_ConvertStringTo2DMatrix. Overran a matrix. dimensionStr=[" + dimensionStr + "]")
                        sys.exit(0)
                    newMatrix[rowNum][colNum] = float(value)
                    colNum += 1
                # End - for value in valueList:

                # We should have filled it completely, and will stop at the end of the matrix
                if (colNum != numCols):
                    print("\n\nERROR! MLJob_ConvertStringTo2DMatrix. Underfilled a row in the matrix. dimensionStr=[" + dimensionStr + "]")
                    sys.exit(0)

                # Advance the position where we will next fill the result matrix
                rowNum += 1
            # End - if (singleRowStr != ""):
        # End - for singleRowStr in matrixRowStrList:

        # We should have filled it completely, and will stop at the end of the matrix
        if (rowNum != numRows):
            print("\n\nERROR! MLJob_ConvertStringTo2DMatrix. Underfilled the entire matrix. dimensionStr=[" + dimensionStr + "]")
            sys.exit(0)

        return(newMatrix)
    # End - MLJob_ConvertStringTo2DMatrix






    #####################################################
    #
    # [MLJob::ReadPreflightResultsFromXML
    # 
    #####################################################
    def ReadPreflightResultsFromXML(self, parentXMLNode):
        self.NumResultsInPreflight = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_NUM_ITEMS_ELEMENT_NAME, 0)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, "")
        self.PreflightNumItemsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_INPUT_MINS_ELEMENT_NAME, "")
        self.PreflightInputMins = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_INPUT_MAXS_ELEMENT_NAME, "")
        self.PreflightInputMaxs = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_INPUT_RANGES_ELEMENT_NAME, "")
        self.PreflightInputRanges = MLJob_ConvertStringTo1DVector(resultStr)



        ################################
        # Find the existing list of class weights
        classWeightsListXMLNode = dxml.XMLTools_GetChildNode(self.ResultsPreflightXMLNode, RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_LIST)
        if (classWeightsListXMLNode is None):
            return

        # Get the number of classes so we can easily rebuild the data structures when reading the job.
        retrievedNumClasses = dxml.XMLTools_GetChildNodeTextAsInt(classWeightsListXMLNode, 
                                                                  RESULTS_PREFLIGHT_TRAINING_PRIORITY_NUM_RESULT_CLASSES, -1)
        #if (retrievedNumClasses != self.NumResultClasses):

        # Make a new runtime object for each resultClass element
        self.PreflightResultClassWeights = [0] * self.NumResultClasses

        # Read each resultClass
        resultClassXMLNode = dxml.XMLTools_GetChildNode(classWeightsListXMLNode, 
                                                        RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT)
        while (resultClassXMLNode is not None):
            resultClassID = dxml.XMLTools_GetChildNodeTextAsInt(resultClassXMLNode, 
                                                                RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_ID, -1)
            classWeight = dxml.XMLTools_GetChildNodeTextAsFloat(resultClassXMLNode, 
                                                                RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_VALUE, -1)
            if ((resultClassID >= 0) and (classWeight >= 0)):
                self.PreflightResultClassWeights[resultClassID] = classWeight
        
            resultClassXMLNode = dxml.XMLTools_GetPeerNode(resultClassXMLNode, 
                                                            RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT)
        # End - while (resultClassXMLNode is not None):

        self.FinishPreflight()
    # End - ReadPreflightResultsFromXML





    #####################################################
    #
    # [MLJob::WritePreflightResultsToXML
    # 
    #####################################################
    def WritePreflightResultsToXML(self, parentXMLNode):
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_NUM_ITEMS_ELEMENT_NAME, str(self.NumResultsInPreflight))

        resultStr = MLJob_Convert1DVectorToString(self.PreflightNumItemsPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputMins)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_INPUT_MINS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputMaxs)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_INPUT_MAXS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputRanges)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_INPUT_RANGES_ELEMENT_NAME, resultStr)



        #############################
        # Write the derived training weights
        classWeightsListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsPreflightXMLNode, 
                                                                    RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_LIST)
        if (classWeightsListXMLNode is None):
            return
        dxml.XMLTools_RemoveAllChildNodes(classWeightsListXMLNode)

        # Save the number of classes so we can easily rebuild the data structures when reading the job.
        dxml.XMLTools_AddChildNodeWithText(classWeightsListXMLNode, 
                                            RESULTS_PREFLIGHT_TRAINING_PRIORITY_NUM_RESULT_CLASSES, 
                                            str(self.NumResultClasses))

        # Make a new element for each resultClass weight
        for resultClassID, classWeight in enumerate(self.PreflightResultClassWeights):
            resultClassXMLNode = dxml.XMLTools_AppendNewChildNode(classWeightsListXMLNode, 
                                                            RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT)
            dxml.XMLTools_AddChildNodeWithText(resultClassXMLNode, 
                                                RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_VALUE, 
                                                str(classWeight))
            dxml.XMLTools_AddChildNodeWithText(resultClassXMLNode, 
                                                RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_ID, 
                                                str(resultClassID))
        # End - for resultClassID, classWeight in enumerate(self.PreflightResultClassWeights.items())
    # End - WritePreflightResultsToXML





    #####################################################
    #
    # [MLJob::ReadTraingResultsFromXML
    # 
    #####################################################
    def ReadTraingResultsFromXML(self, parentXMLNode):
        ###################
        self.NumSamplesTrainedPerEpoch = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                            "NumSequencesTrainedPerEpoch", 0)
        self.NumPatientsTrainedPerEpoch = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                            "NumPatientsTrainedPerEpoch", 0)
        self.NumPatientsSkippedPerEpoch = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                            "NumPatientsSkippedPerEpoch", 0)
        self.NumDataPointsTrainedPerEpoch = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                            "NumDataPointsTrainedPerEpoch", 0)

        ###################
        self.AvgLossPerEpochList = []
        resultStr = dxml.XMLTools_GetChildNodeText(parentXMLNode, "TrainAvgLossPerEpoch")
        resultArray = resultStr.split(",")
        for avgLossStr in resultArray:
            try:
                avgLossFloat = float(avgLossStr)
                avgLossFloat = round(avgLossFloat, 4)
                self.AvgLossPerEpochList.append(avgLossFloat)
            except Exception:
                continue

        #################
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, "TrainNumItemsPerClass", "")
        self.TrainNumItemsPerClass = MLJob_ConvertStringTo1DVector(resultStr)
    # End - ReadTraingResultsFromXML




    #####################################################
    #
    # [MLJob::WriteTrainResultsToXML
    # 
    #####################################################
    def WriteTrainResultsToXML(self, parentXMLNode):
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "NumSequencesTrainedPerEpoch", 
                                            str(self.NumSamplesTrainedPerEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "NumPatientsTrainedPerEpoch", 
                                            str(self.NumPatientsTrainedPerEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "NumPatientsSkippedPerEpoch", 
                                            str(self.NumPatientsSkippedPerEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "NumDataPointsTrainedPerEpoch", 
                                            str(self.NumDataPointsTrainedPerEpoch))

        ###################
        resultStr = ""
        for avgLoss in self.AvgLossPerEpochList:
            avgLoss = round(avgLoss, 4)
            resultStr = resultStr + str(avgLoss) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "TrainAvgLossPerEpoch", resultStr)

        ###################
        resultStr = MLJob_Convert1DVectorToString(self.TrainNumItemsPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "TrainNumItemsPerClass", resultStr)
    # End - WriteTrainResultsToXML





    #####################################################
    #
    # [MLJob::ReadTestResultsFromXML
    # 
    #####################################################
    def ReadTestResultsFromXML(self, parentXMLNode):
        self.AllTestResults.ReadTestResultsFromXML()
        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList[index].ReadTestResultsFromXML()
    # End - ReadTestResultsFromXML





    #####################################################
    #
    # [MLJob::WriteTestResultsToXML
    # 
    #####################################################
    def WriteTestResultsToXML(self, parentXMLNode):
        self.AllTestResults.WriteTestResultsToXML()
        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList[index].WriteTestResultsToXML()
    # End - WriteTestResultsToXML





    #####################################################
    # [MLJob::SetDebug]
    #####################################################
    def SetDebug(self, fDebug):
        self.Debug = fDebug
        dxml.XMLTools_SetChildNodeTextAsBool(self.JobControlXMLNode, "Debug", fDebug)
    # End - SetDebug



    ################################################################################
    #
    # [RecordMatrixAsDebugVal]
    #
    # inputArray is a numpy array.
    ################################################################################
    def RecordMatrixAsDebugVal(self, name, inputArray, arrayFunc):
        if (not self.Debug):
            return
        if (inputArray is None):
            return

        arrayFunc = arrayFunc.lower()
        arrayNum = 0.0
        numEntries = 0

        numDimensions = inputArray.ndim
        if (numDimensions == 1):
            for numVal in inputArray:
                if (arrayFunc == "avg"):
                    arrayNum += numVal
                elif (arrayFunc == "sum"):
                    arrayNum += numVal
            # End - for numVal in row:
            numEntries += len(inputArray)
        elif (numDimensions == 2):
            numRows = len(inputArray)
            for rowNum in range(numRows):
                row = inputArray[rowNum]
                for numVal in row:
                    if (arrayFunc == "avg"):
                        arrayNum += numVal
                    elif (arrayFunc == "sum"):
                        arrayNum += numVal
                # End - for numVal in row:
                numEntries += len(row)
            # End - for rowNum in range(numRows):
        elif (numDimensions == 3):
            dim1 = len(inputArray)
            for index1 in range(dim1):
                matrix2d = inputArray[index1]
                dim2 = len(matrix2d)
                for index2 in range(dim2):
                    row = matrix2d[index2]
                    for numVal in row:
                        if (arrayFunc == "avg"):
                            arrayNum += numVal
                        elif (arrayFunc == "sum"):
                            arrayNum += numVal
                    # End - for numVal in row:
                    numEntries += len(row)
                # End - for index2 in range(dim2):
            # End - for index1 in range(dim1):
        else:
            print("RecordMatrixAsDebugVal. numDimensions=" + str(numDimensions))
            return

        if (arrayFunc == "avg"):
            arrayNum = arrayNum / numEntries
            #print("RecordDebug1DVectorAsEvent: numEntries=" + str(numEntries))
            #print("RecordDebug1DVectorAsEvent: arrayNum=" + str(arrayNum))

        #print("RecordMatrixAsDebugVal: Final arrayNum=" + str(arrayNum))
        #print("RecordMatrixAsDebugVal: type=" + str(type(arrayNum)))
        #print("\n\nBAIL\n\n")
        #sys.exit(0)

        self.RecordDebugVal(name, arrayNum)
    # End - RecordMatrixAsDebugVal





    #####################################################
    #
    #   ACCESSOR METHODS
    #
    # A lot of the use of Job objects is to store hypervariables
    # to control execution, and also to store the results of 
    # execution for later analysis. These methods are used for both.
    #####################################################

    #####################################################
    #
    # [MLJob::GetNetworkType]
    #
    #####################################################
    def GetNetworkType(self):
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkLayersXMLNode, NETWORK_TYPE_ELEMENT_NAME, "")
        if (resultStr is None):
            return("")
        return(resultStr)
    # End of GetNetworkType
            


    #####################################################
    # [MLJob::GetJobStatus]
    #####################################################
    def GetJobStatus(self):
        jobStatus = self.GetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_IDLE)
        jobErrStr = self.GetJobControlStr(JOBCTL_ERROR_CODE_ELEMENT_NAME, str(JOB_E_NO_ERROR))
        errorMsg = self.GetJobControlStr(JOBCTL_RESULT_MSG_ELEMENT_NAME, "")
        try:
            errCode = int(jobErrStr)
        except Exception:
            errCode = JOB_E_UNKNOWN_ERROR

        return jobStatus, errCode, errorMsg
    # End - GetJobStatus


    #####################################################
    # [MLJob::GetTrainingParamStr]
    #####################################################
    def GetTrainingParamStr(self, valName, defaultVal):
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.TrainingXMLNode, valName, defaultVal)
        if ((resultStr is None) or (resultStr == "")):
            return(defaultVal)
        return(resultStr)

    #####################################################
    # [MLJob::GetTrainingParamInt]
    #####################################################
    def GetTrainingParamInt(self, valName, defaultVal):
        return(dxml.XMLTools_GetChildNodeTextAsInt(self.TrainingXMLNode, valName, defaultVal))

    #####################################################
    # [MLJob::GetRunOptionsStr]
    #####################################################
    def GetRunOptionsStr(self):
        return self.GetJobControlStr(JOBCTL_RUN_OPTIONS_ELEMENT_NAME, "")

    #####################################################
    # [MLJob::IsRunOptionSet]
    #####################################################
    def IsRunOptionSet(self, optionName):
        optionStr = self.GetJobControlStr(JOBCTL_RUN_OPTIONS_ELEMENT_NAME, "")
        optionList = optionStr.split(JOBCTL_RUN_OPTION_SEPARATOR_STR) 
        return (optionName in optionList)

    #####################################################
    # [MLJob::GetNetworkLayerSpec]
    #####################################################
    def GetNetworkLayerSpec(self, name):
        return(dxml.XMLTools_GetChildNode(self.NetworkLayersXMLNode, name))

    #####################################################
    # [MLJob::OKToUseGPU]
    #####################################################
    def OKToUseGPU(self):
        return(self.AllowGPU)

    #####################################################
    # [MLJob::GetDebug]
    #####################################################
    def GetDebug(self):
        return(self.Debug)

    #####################################################
    # [MLJob::GetIsLogisticNetwork]
    #####################################################
    def GetIsLogisticNetwork(self):
        return self.IsLogisticNetwork

    #####################################################
    # [MLJob::GetEpochNum]
    #####################################################
    def GetEpochNum(self):
        return(self.CurrentEpochNum)

    #####################################################
    # [MLJob::GetResultValueType]
    #####################################################
    def GetResultValueType(self):
        return(self.ResultValueType)

    #####################################################
    # [MLJob::GetNumResultClasses]
    #####################################################
    def GetNumResultClasses(self):
        return(self.NumResultClasses)

    #####################################################
    # [MLJob::GetNumSequencesTrainedPerEpoch
    #####################################################
    def GetNumSequencesTrainedPerEpoch(self):
        return(self.NumSamplesTrainedPerEpoch)

    #####################################################
    # [MLJob::GetNumPatientsSkippedPerEpoch
    #####################################################
    def GetNumPatientsSkippedPerEpoch(self):
        return(self.NumPatientsSkippedPerEpoch)

    #####################################################
    # [MLJob::SetNumPatientsSkippedPerEpoch
    #####################################################
    def SetNumPatientsSkippedPerEpoch(self, num):
        self.NumPatientsSkippedPerEpoch = num

    #####################################################
    # [MLJob::GetNumPatientsTrainedPerEpoch
    #####################################################
    def GetNumPatientsTrainedPerEpoch(self):
        return(self.NumPatientsTrainedPerEpoch)

    #####################################################
    # [MLJob::SetNumPatientsTrainedPerEpoch
    #####################################################
    def SetNumPatientsTrainedPerEpoch(self, num):
        self.NumPatientsTrainedPerEpoch = num

    #####################################################
    # [MLJob::GetNumDataPointsPerEpoch
    #####################################################
    def GetNumDataPointsPerEpoch(self):
        return(self.NumDataPointsTrainedPerEpoch)

    #####################################################
    # [MLJob::SetNumDataPointsPerEpoch
    #####################################################
    def SetNumDataPointsPerEpoch(self, num):
        self.NumDataPointsTrainedPerEpoch = num

    #####################################################
    # [MLJob::GetNumSequencesTested
    #####################################################
    def GetNumSequencesTested(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].NumSamplesTested
        else:
            return self.AllTestResults.NumSamplesTested

    #####################################################
    # [MLJob::GetAvgLossPerEpochList
    #####################################################
    def GetAvgLossPerEpochList(self):
        return self.AvgLossPerEpochList

    #####################################################
    # [MLJob::GetResultValMinValue
    #####################################################
    def GetResultValMinValue(self):
        return self.ResultValMinValue

    #####################################################
    # [MLJob::GetResultValBucketSize
    #####################################################
    def GetResultValBucketSize(self):
        return self.ResultValBucketSize

    #####################################################
    # [MLJob::GetTrainNumItemsPerClass
    #####################################################
    def GetTrainNumItemsPerClass(self):
        return self.TrainNumItemsPerClass

    #####################################################
    # [MLJob::GetTestResults
    #####################################################
    def GetTestResults(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].TestResults
        else:
            return self.AllTestResults.TestResults

    #####################################################
    # [MLJob::GetTestNumItemsPerClass
    #####################################################
    def GetTestNumItemsPerClass(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].TestNumItemsPerClass
        else:
            return self.AllTestResults.TestNumItemsPerClass

    #####################################################
    # [MLJob::GetROCAUC
    #####################################################
    def GetROCAUC(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].ROCAUC
        else:
            return self.AllTestResults.ROCAUC

    #####################################################
    # [MLJob::GetAUPRC
    #####################################################
    def GetAUPRC(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].AUPRC
        else:
            return self.AllTestResults.AUPRC

    #####################################################
    # [MLJob::GetF1Score
    #####################################################
    def GetF1Score(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].F1Score
        else:
            return self.AllTestResults.F1Score

    #####################################################
    # [MLJob::GetTestNumCorrectPerClass
    #####################################################
    def GetTestNumCorrectPerClass(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].TestNumCorrectPerClass
        else:
            return self.AllTestResults.TestNumCorrectPerClass

    #####################################################
    # [MLJob::GetTestNumPredictionsPerClass
    #####################################################
    def GetTestNumPredictionsPerClass(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].TestNumPredictionsPerClass
        else:
            return self.AllTestResults.TestNumPredictionsPerClass

    #####################################################
    # [MLJob::GetStartRequestTimeStr]
    #####################################################
    def GetStartRequestTimeStr(self):
        return(self.StartRequestTimeStr)

    #####################################################
    # [MLJob::GetStopRequestTimeStr]
    #####################################################
    def GetStopRequestTimeStr(self):
        return(self.StopRequestTimeStr)

    #####################################################
    # [MLJob::GetLogisticResultsTrueValueList]
    #####################################################
    def GetLogisticResultsTrueValueList(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].LogisticResultsTrueValueList
        else:
            return self.AllTestResults.LogisticResultsTrueValueList

    #####################################################
    # [MLJob::GetLogisticResultsPredictedProbabilityList]
    #####################################################
    def GetLogisticResultsPredictedProbabilityList(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[index].LogisticResultsPredictedProbabilityList
        else:
            return self.AllTestResults.LogisticResultsPredictedProbabilityList

    #####################################################
    #
    # [MLJob::GetNetworkStateSize]
    #
    #####################################################
    def GetNetworkStateSize(self):
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkLayersXMLNode, 
                                            NETWORK_STATE_SIZE_ELEMENT_NAME, "")
        if ((resultStr is None) or (resultStr == "")):
            return(0)

        try:
            resultInt = int(resultStr)
        except Exception:
            resultInt = 0

        return(resultInt)
    # End of GetNetworkStateSize



    #####################################################
    #
    # [MLJob::GetNetworkInputVarNames]
    #
    #####################################################
    def GetNetworkInputVarNames(self):
        inputLayerXMLNode = dxml.XMLTools_GetChildNode(self.NetworkLayersXMLNode, "InputLayer")
        if (inputLayerXMLNode is None):
            return("")

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(inputLayerXMLNode, "InputValues", "")
        if (resultStr is None):
            return("")

        # Allow whitespace to be sprinkled around the file. Later the parsing code
        # assumes no unnecessary whitespace is present, but don't be that strict with the file format.
        resultStr = resultStr.replace(' ', '')

        #print("GetNetworkInputVarNames. resultStr=" + resultStr)
        return(resultStr)
    # End of GetNetworkInputVarNames




    #####################################################
    #
    # [MLJob::GetNetworkOutputVarName]
    #
    #####################################################
    def GetNetworkOutputVarName(self):
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkLayersXMLNode, "ResultValue", "")
        if ((resultStr is not None) and (resultStr != "")):
            # Allow whitespace to be sprinkled around the file. Later the parsing code
            # assumes no unnecessary whitespace is present, but don't be that strict with the file format.
            resultStr = resultStr.replace(' ', '')

            #print("GetNetworkOutputVarName. resultStr=" + resultStr)
            return(resultStr)
        # End - if ((resultStr is not None) and (resultStr != ""))


        # Otherwise, look in the old, legacy places.
        outputLayerXMLNode = dxml.XMLTools_GetChildNode(self.NetworkLayersXMLNode, "OutputLayer")
        if (outputLayerXMLNode is None):
            outputLayerXMLNode = dxml.XMLTools_GetChildNode(self.NetworkLayersXMLNode, "InputLayer")
        if (outputLayerXMLNode is None):
            return("")

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(outputLayerXMLNode, "ResultValue", "")
        if (resultStr is None):
            return("")

        # Allow whitespace to be sprinkled around the file. Later the parsing code
        # assumes no unnecessary whitespace is present, but don't be that strict with the file format.
        resultStr = resultStr.replace(' ', '')

        #print("GetNetworkOutputVarName. resultStr=" + resultStr)
        return(resultStr)
    # End of GetNetworkOutputVarName



    #####################################################
    #
    # [MLJob::GetFilterProperties]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetFilterProperties(self):
        propertyListStr = self.GetDataParam("ValueFilter", "")
        numProperties, propertyRelationList, propertyNameList, propertyValueList = self.ParseConditionExpression(propertyListStr)

        return numProperties, propertyRelationList, propertyNameList, propertyValueList
    # End - GetFilterProperties



    #####################################################
    #
    # [MLJob::GetJobControlStr]
    #
    # Returns one parameter to the <JobControl> node.
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetJobControlStr(self, valName, defaultVal):
        xmlNode = dxml.XMLTools_GetChildNode(self.JobControlXMLNode, valName)
        if (xmlNode is None):
            return(defaultVal)

        resultStr = dxml.XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip()
        if ((resultStr is None) or (resultStr == "")):
            return(defaultVal)

        return(resultStr)
    # End of GetJobControlStr




    #####################################################
    #
    # [MLJob::SetJobControlStr]
    #
    # Updates one parameter to the <JobControl> node.
    # This is a public procedure, it is called by the client.
    #####################################################
    def SetJobControlStr(self, valName, valueStr):
        xmlNode = dxml.XMLTools_GetChildNode(self.JobControlXMLNode, valName)
        if (xmlNode is None):
            xmlNode = self.JobXMLDOM.createElement(valName)
            self.JobControlXMLNode.appendChild(xmlNode)

        dxml.XMLTools_RemoveAllChildNodes(xmlNode)
        textNode = self.JobXMLDOM.createTextNode(valueStr)
        xmlNode.appendChild(textNode)
    # End of SetJobControlStr




    #####################################################
    #
    # [MLJob::GetDataParam]
    #
    # Returns one parameter to the <Data> node.
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetDataParam(self, valName, defaultVal):
        xmlNode = dxml.XMLTools_GetChildNode(self.DataXMLNode, valName)
        if (xmlNode is None):
            return(defaultVal)

        resultStr = dxml.XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip()
        if ((resultStr is None) or (resultStr == "")):
            return(defaultVal)

        return(resultStr)
    # End of GetDataParam




    #####################################################
    #
    # [MLJob::SetDataParam]
    #
    # Set one parameter to the <Data> node.
    # This is a public procedure, it is called by the client.
    #####################################################
    def SetDataParam(self, valName, newVal):
        xmlNode = dxml.XMLTools_GetChildNode(self.DataXMLNode, valName)
        if (xmlNode is None):
            return JOB_E_UNKNOWN_ERROR

        dxml.XMLTools_SetTextContents(xmlNode, newVal)
        return JOB_E_NO_ERROR
    # End of SetDataParam



    #####################################################
    #
    # [MLJob::ParseConditionExpression]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def ParseConditionExpression(self, propertyListStr):
        numProperties = 0
        propertyRelationList = []
        propertyNameList = []
        propertyValueList = []

        if (propertyListStr != ""):
            propList = propertyListStr.split(VALUE_FILTER_LIST_SEPARATOR)
            for propNamePair in propList:
                #print("propNamePair=" + propNamePair)
                namePairParts = re.split("(.LT.|.LTE.|.EQ.|.NEQ.|.GTE.|.GT.)", propNamePair)
                if (len(namePairParts) == 3):
                    partStr = namePairParts[0]
                    partStr = partStr.replace(' ', '')
                    #print("propNamePair. Name=" + str(partStr))
                    propertyNameList.append(partStr)

                    partStr = namePairParts[1]
                    partStr = partStr.replace(' ', '')
                    # Tokens like ".GT. are case insensitive
                    partStr = partStr.upper()
                    #print("propNamePair. op=" + str(partStr))
                    propertyRelationList.append(partStr)

                    partStr = namePairParts[2]
                    partStr = partStr.replace(' ', '')
                    #print("propNamePair. value=" + str(partStr))
                    propertyValueList.append(partStr)

                    numProperties += 1
            # End - for propNamePair in propList:
        # End - if (requirePropertiesStr != ""):

        return numProperties, propertyRelationList, propertyNameList, propertyValueList
    # End - ParseConditionExpression


    ################################################################################
    #
    # [GetNonce]
    #
    ################################################################################
    def GetNonce(self):
        return self.RuntimeNonce
    # End - GetNonce


    ################################################################################
    #
    # [IncrementNonce]
    #
    ################################################################################
    def IncrementNonce(self):
        self.RuntimeNonce += 1
    # End - IncrementNonce


    ################################################################################
    #
    # [ChecksumExists]
    #
    ################################################################################
    def ChecksumExists(self, hashName):
        if (hashName in self.HashDict):
            return True
        return False
    # End - ChecksumExists


    ################################################################################
    #
    # [SetArrayChecksum]
    #
    # inputArray is a numpy array, and may be 1, 2, or 3 dimensional.
    ################################################################################
    def SetArrayChecksum(self, inputArray, hashName):
        if (numpy.isnan(inputArray).any()):
            print("ERROR!:\nSetArrayChecksum passed an Invalid Array")
            print("SetArrayChecksum. hashName = " + str(hashName))
            print("SetArrayChecksum. inputArray = " + str(inputArray))
            print("Exiting process...")
            raise Exception()

        hashVal = self.ComputeArrayChecksum(inputArray)
        #print("SetArrayChecksum. Save hash " + hashName + " = " + hashVal)
        self.HashDict[hashName] = hashVal
    # End - SetArrayChecksum



    ################################################################################
    #
    # [CompareArrayChecksum]
    #
    # inputArray is a numpy array, and may be 1, 2, or 3 dimensional.
    ################################################################################
    def CompareArrayChecksum(self, inputArray, hashName):
        fDebug = False

        newHashVal = self.ComputeArrayChecksum(inputArray)
        if (fDebug):
            print("CompareArrayChecksum. hashName = " + str(hashName) + ", newHashVal = " + str(newHashVal))
        
        if (hashName not in self.HashDict):
            print("CompareArrayChecksum. hashName not in self.HashDict hashName = " + str(hashName))
            return False

        if (fDebug):
            print("Compare hash " + hashName + ", Saved=" + str(self.HashDict[hashName]) + ", Expect=" + newHashVal)

        isEqual = (newHashVal == self.HashDict[hashName])
        return(isEqual)
    # End - CompareArrayChecksum




    ################################################################################
    #
    # [ComputeArrayChecksum]
    #
    # inputArray is a numpy array, and may be 1, 2, or 3 dimensional.
    ################################################################################
    def ComputeArrayChecksum(self, inputArray):
        if (numpy.isnan(inputArray).any()):
            print("ERROR!:\nComputeArrayChecksum passed an Invalid Array")
            print("ComputeArrayChecksum. hashName = " + str(hashName))
            print("ComputeArrayChecksum. inputArray = " + str(inputArray))
            print("Exiting process...")
            raise Exception()

        rawByteArray = inputArray.tobytes('C')
        newHashVal = hashlib.sha256(rawByteArray).hexdigest()
        return(newHashVal)
    # End - ComputeArrayChecksum



    ################################################################################
    #
    # [GetArrayChecksum]
    #
    ################################################################################
    def GetSavedArrayChecksum(self, hashName):
        if (hashName not in self.HashDict):
            return "NOT IN DICTIONARY"
        return(self.HashDict[hashName])
    # End - GetSavedArrayChecksum



# End - class MLJob
################################################################################





################################################################################
#
# [MLJob_Convert1DVectorToString]
#
################################################################################
def MLJob_Convert1DVectorToString(inputArray):
    dimension = len(inputArray)

    resultString = "NumD=1;D=" + str(dimension) + ";T=float;" + ROW_SEPARATOR_CHAR

    for numVal in inputArray:
        resultString = resultString + str(numVal) + VALUE_SEPARATOR_CHAR
    resultString = resultString[:-1]
    resultString = resultString + ROW_SEPARATOR_CHAR

    return(resultString)
# End - MLJob_Convert1DVectorToString




################################################################################
#
# [MLJob_ConvertStringTo1DVector]
#
################################################################################
def MLJob_ConvertStringTo1DVector(vectorStr):
    sectionList = vectorStr.split(";")
    matrixAllRowsStr = sectionList[len(sectionList) - 1]

    dimensionStr = ""
    for propertyStr in sectionList:
        propertyParts = propertyStr.split("=")
        if (len(propertyParts) < 2):
            continue

        propName = propertyParts[0]
        propValue = propertyParts[1]
        if (propName == "D"):
            dimensionStr = propValue
    # End - for propertyStr in sectionList:

    numCols = 0
    if (dimensionStr != ""):
        dimensionList = dimensionStr.split(VALUE_SEPARATOR_CHAR)
        if (len(dimensionList) > 0):
            numCols = int(dimensionList[0])

    newVector = numpy.empty([numCols])

    matrixValueStrList = matrixAllRowsStr.split(ROW_SEPARATOR_CHAR)
    for singleRowStr in matrixValueStrList:
        if (singleRowStr != ""):
            valueList = singleRowStr.split(VALUE_SEPARATOR_CHAR)
            colNum = 0
            for value in valueList:
                newVector[colNum] = float(value)
                colNum += 1
    # End - for singleRowStr in matrixValueStrList:

    return(newVector)
# End - MLJob_ConvertStringTo1DVector





################################################################################
# 
# This is a public procedure, it is called by the client.
################################################################################
def MLJob_CreateNewMLJob():
    job = MLJob()
    job.InitNewJobImpl()

    return job
# End - MLJob_CreateNewMLJob




################################################################################
# 
# This is a public procedure, it is called by the client.
################################################################################
def MLJob_CreateMLJobFromString(jobStr):
    job = MLJob()
    err = job.ReadJobFromString(jobStr)
    if (err != JOB_E_NO_ERROR):
        job = None

    return job
# End - MLJob_CreateMLJobFromString




################################################################################
# 
# This is a public procedure, it is called by the client.
#
# Returns:    err, job
################################################################################
def MLJob_ReadExistingMLJob(jobFilePathName):
    err = JOB_E_NO_ERROR

    job = MLJob()
    err = job.ReadJobFromFile(jobFilePathName)
    if (err != JOB_E_NO_ERROR):
        #print("MLJob_ReadExistingMLJob. err = " + str(err))
        return err, None

    return JOB_E_NO_ERROR, job
# End - MLJob_ReadExistingMLJob







