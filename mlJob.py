####################################################################################
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
#   </JobControl>
#
#   <Data>
#   </Data>
#
#   <Network>
#       <InputLayer>
#       <HiddenLayer>
#       <OutputLayer>
#   </Network>
#
#   <Training>
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
#       </TrainingResults>
#
#       <TestingResults>
#       </TestingResults>
#
#   </Results>
#
#   <Runtime>
#   </Runtime>
#
#
# Member Variables for JobControl 
# ===============================
#   JobName - A string that identifies the job to a human
#   JobType - Basic
#   JobSpecVersion - Currently 1.0
#   Status - IDLE, TRAIN, TEST
#   AllowGPU - True/False, defaults to True
#   Debug - True/False, defaults to False
#   LogFilePathName - A pathname where the log file for this execution is stored.
#       This file is created/emptied when the job starts.
#   StressTest - True/False, defaults to False
#
#
# Member Variables for Data
# ===========================
#   DataFormat 
#       TDF
#   StoreType
#       File
#   TrainData - A file pathname
#   TestData - A file pathname
#
#
# Member Variables for Network
# ===========================
#   NetworkType
#       SimpleNet
#       multilevelNet
#       LSTM
#
#   OutputThreshold
#       A number between 0 and 1 which determines whether the prediction is true.
#       This is only used for Logistic networks
#
#   StateSize
#       An integer, 0-N, which is the size of a RNN state vector.
#       If not specified, then this is 0
#       If this is 0, then this is a simple deep neural network. It is
#           an RNN iff this value is present and greater than 0
#
#   InputLayer
#       Contents described below
#
#   HiddenLayer
#       Contents described below
#
#   OutputLayer
#       Contents described below
#
#
# Member Variables for InputLayer
# ===========================
#       InputValues - A comma-separated list of variables, like "Age,Cr,SBP". 
#          See the TDFTools.py documentation for a list of defined names.
#          The value name appeats in a <D> element. 
#          For example, Hgb would extract data from the following <D> element:
#              <D C="L" T="100:10:30">Hgb=7.0,</D>
#          Each value may be followed by an offset in brackets
#          Examples: Cr[-1]   INR[next]
#          The number in brackets is the number of days from the current point in the timeline.
#          The offset "next" means the next occurrence.    
#          The special value "Dose" is always followed by a "/" and then the name of a medication.
#          For example Dose/Coumadin is the dose of Coumadin given.
#          Doses may also have offsets. For example Dose/Coumadin[-1] is the dose of Coumadin given 1 day before.
#
#       layerOutputSize
#       NonLinear - 
#           LogSoftmax
#           ReLU
#           Sigmoid
#
#
# Member Variables for HiddenLayer
# ===========================
#       layerOutputSize
#       NonLinear - 
#           LogSoftmax
#           ReLU
#           Sigmoid
#
#
# Member Variables for OutputLayer
# ===========================
#       layerOutputSize
#       NonLinear - 
#           LogSoftmax
#           ReLU
#           Sigmoid
#
#       ResultValue - A variable name. See the TDFTools.py documentation.
#       Different variables have different interpretations as result values.
#       These include:
#           Number - A numeric value, which may be a dose or a lab value
#           FutureEventClass - A number 0-11. See the TDFTools.py documentation.
#           Binary - A number 0-1
#           FutureEventClass or BinaryDiagnosis will count the number of exact matches; the 
#               predicted class must exactly match the actual value.
#       Number will count buckets:
#           Exact (to 1 decimal place)
#           Within 2%
#           Within 5%
#           Within 10%
#           Within 25%
#
#
# Member Variables for Training
# ===========================
#   LossFunction
#       NLLLoss
#       BCELoss
#
#   Optimizer
#       SGD
#
#   LearningRate
#   BatchSize
#   NumEpochs
# 
#
# Member Variables for TrainingResults
# ===========================
#   NumSequencesTrainedPerEpoch
#   NumPatientsTrainedPerEpoch
#   NumPatientsSkippedPerEpoch
#   TrainAvgLossPerEpoch
#   TrainNumItemsPerClass
#
#
# Member Variables for TestingResults
# ===========================
#   NumSequencesTested
#
#   TestNumItemsPerClass
#   TestNumPredictionsPerClass
#   TestNumCorrectPerClass
#
#   NumCorrectPredictions
#   Used for int and float results:
#       NumPredictionsWithin2Percent
#       NumPredictionsWithin5Percent
#       NumPredictionsWithin10Percent
#       NumPredictionsWithin20Percent
#       NumPredictionsWithin50Percent
#       NumPredictionsWithin100Percent
#   Used for class results.
#       NumPredictionsWithin1Class
#   Used for binary results.
#       NumPredictionsTruePositive
#       NumPredictionsTrueNegative
#       NumPredictionsFalsePositive
#       NumPredictionsFalseNegative
#
#
# Member Variables for Runtime
# The runtime state for the Job training/testing sequence. It is describes the execution
# of a job, not the job results.
# ===========================
#   OriginalFilePathname
#
#   StartRequestTimeStr
#   StopRequestTimeStr
#
#   CurrentEpochNum
#   TotalTrainingLossInCurrentEpoch
#
#   BufferedLogLines
#
#   DebugEvent
#
#   OS
#   CPU
#   GPU
#
#
# SavedModelStateXMLNode
# ===========================
#   NeuralNetMatrixListXMLNode
#
#
# Member Variables for NeuralNetMatrixListXMLNode
# This is part of SavedModelStateXMLNode, and it is used for neural nets (deep and logistics)
# ===========================
#   The runtime weight matrices and bias vectors for a network.
#   This allows a network to suspend and then later resume its state, possibly in a 
#   different process or a different server.
#
#   <Weight>
#   </Weight>
#
#   <Bias>
#   </Bias>
#
#
# Member Variables for TestList
# ===========================
#   A list of test elements, each of thich can contain different inputs and outputs.
#   This is very unstructured, and its use depends on the individual tests.
#
#####################################################################################
import os
import sys
import time
import re
from datetime import datetime
import platform
import random

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

ML_JOB_DEFAULT_MAX_SKIPPED_NUMERIC_VALUE_BUCKETS    = 16
ML_JOB_DEFAULT_MAX_SKIPPED_EVENT_CLASS_BUCKETS      = 10

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

# <Data>
DATA_ELEMENT_NAME = "Data"

# <Training>
TRAINING_ELEMENT_NAME = "Training"
TRAINING_OPTION_BATCHSIZE = "BatchSize"
TRAINING_OPTION_LEARNING_RATE = "LearningRate"
TRAINING_OPTION_NUM_EPOCHS = "NumEpochs"
TRAINING_OPTIONS_ELEMENT_NAME = "TrainingOptions"
TRAINING_MAX_NUM_SKIPPED_RESULT_CLASSES = "MaxSkippedResultClasses"

# <Runtime>
RUNTIME_ELEMENT_NAME        = "Runtime"
RUNTIME_LOG_NODE_ELEMENT_NAME = "Log"

# <Results>
RESULTS_ELEMENT_NAME = "Results"
RESULTS_PREFLIGHT_ELEMENT_NAME = "PreflightResults"
RESULTS_TRAINING_ELEMENT_NAME = "TrainingResults"
RESULTS_NUM_ELEMENT_NAME = "TestingResults"
RESULTS_TESTING_ELEMENT_NAME = "TestingResults"
RESULTS_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME = "LogisticOutputs"

# These are used for preflight, training and testing
RESULTS_NUM_ITEMS_ELEMENT_NAME = "NumSequences"

# These are just for preflight
RESULTS_NUM_ITEMS_PER_CLASS_ELEMENT_NAME = "NumItemsPerClass"
RESULTS_INPUT_MINS_ELEMENT_NAME = "InputMins"
RESULTS_INPUT_MAXS_ELEMENT_NAME = "InputMaxs"
RESULTS_INPUT_TOTALS_ELEMENT_NAME = "InputTotals"
RESULTS_INPUT_MEANS_ELEMENT_NAME = "InputMeans"
RESULTS_INPUT_DIVERGENCE_FROM_MEAN_TOTALS_ELEMENT_NAME = "InputDivergenceTotals"
RESULTS_INPUT_STD_DEV_ELEMENT_NAME = "InputStdDev"
RESULTS_INPUT_SUMS_FOR_EACH_CLASS_ELEMENT_NAME = "InputSumsForEachResultClass"
RESULTS_PREFLIGHT_CENTROID_TYPE = "CentroidType"
RESULTS_PREFLIGHT_NUM_CENTROIDS = "NumCentroids"
RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_VALUES = "GlobalCentroidInputValues"
RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_TOTALS = "GlobalCentroidValTotals"
RESULTS_PREFLIGHT_GLOBAL_CENTROID_NUM_SATELLITES = "GlobalCentroidNumNodes"
RESULTS_PREFLIGHT_GLOBAL_CENTROID_MAX_DISTANCE = "GlobalCentroidMaxDistance"
RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_MEANS = "GlobalCentroidInputValMeans"
RESULTS_PREFLIGHT_GLOBAL_CENTROID_RESULT_CLASSES = "GlobalCentroidResultClasses"
RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_VALS = "ResultClassCentroidInputValues"
RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_TOTALS = "ResultClassCentroidInputValTotals"
RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_VALS_NUM_SATS = "ResultClassCentroidNumNodes"
RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_MAX_DISTANCE = "ResultClassCentroidMaxDistance"
RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_INPUT_MEANS = "ResultClassCentroidInputValMeans"
RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT_LIST = "ResultClassWeightList"
RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT = "ResultClassWeight"
RESULTS_PREFLIGHT_NUM_RESULT_CLASSES = "NumResultClasses"
RESULTS_PREFLIGHT_RESULT_CLASS_ID = "ResultClassID"
RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT_VALUE = "ClassWeight"

# These are just for Training
RESULTS_TRAINING_TOTAL_DEV_ELEMENT_NAME = "TotalDev"
RESULTS_TRAINING_STANDARD_DEV_ELEMENT_NAME = "StdDev"

# These are used only for testing
RESULTS_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME = "NumPredictionsPerClass"
RESULTS_NUM_CORRECT_PER_CLASS_ELEMENT_NAME  = "NumCorrectPerClass"
RESULTS_ROCAUC_ELEMENT_NAME = "ROCAUC"
RESULTS_AUPRC_ELEMENT_NAME = "AUPRC"
RESULTS_F1Score_ELEMENT_NAME = "F1Score"

# <Network>
NETWORK_ELEMENT_NAME = "Network"
NETWORK_TYPE_ELEMENT_NAME = "NetworkType"
NETWORK_STATE_SIZE_ELEMENT_NAME = "StateSize"
NETWORK_OUTPUT_THRESHOLD_ELEMENT_NAME = "MapOutputToBoolThreshold"

NETWORK_LOGISTIC_ELEMENT_NAME       = "LogisticOutput"

# <SavedModelState>
SAVED_MODEL_STATE_ELEMENT_NAME      = "SavedModelState"
RUNTIME_OPTIMIZER_STATE             = "PyTorchOptimizerState"
SAVED_STATE_TYPE_ELEMENT_NAME       = "SavedStateType"
SAVED_STATE_FILE_PATH_ELEMENT_NAME  = "SavedStateFilePath"
SAVED_STATE_XGBoost_ELEMENT_NAME    = "XGBoostSavedState"

# <NeuralNetMatrixList>
NETWORK_MATRIX_LIST_NAME = "NeuralNetMatrixList"
NETWORK_MATRIX_WEIGHT_MATRIX_NAME = "Weight"
NETWORK_MATRIX_BIAS_VECTOR_NAME = "Bias"

VALUE_FILTER_LIST_SEPARATOR = "{AND}"

MLJOB_MATRIX_FORMAT_ATTRIBUTE_NAME = "format"
MLJOB_MATRIX_FORMAT_SIMPLE = "simple"

MLJOB_CENTROID_TYPE_FIXED = "Fixed"

# These are the values found in the <JobControl/Status> element
MLJOB_STATUS_IDLE         = "IDLE"
MLJOB_STATUS_PREFLIGHT    = "PREFLIGHT"
MLJOB_STATUS_TRAINING     = "TRAIN"
MLJOB_STATUS_TESTING      = "TEST"
MLJOB_STATUS_DONE         = "DONE"

TEST_LIST_XML_NODE_NAME     = "TestList"

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

ADDITIONAL_MULTIPLIER_FOR_UNDERREPRESENTED_CLASSES = 2.0
# We still want some of the information from pre-test probability. 
# We just don't want so much of the common cases that they completely
# overwhelms the rare cases.
CLASS_WEIGHTS_LEVEL_FOR_REINTRODUCING_PRETEST_PROBABILITY = 0.25

DEBUG_EVENT_TIMELINE_EPOCH          = "Epoch"
DEBUG_EVENT_TIMELINE_CHUNK          = "Chunk"
DEBUG_EVENT_TIMELINE_LOSS           = "Loss"
DEBUG_EVENT_OUTPUT_AVG              = "Out.avg"
DEBUG_EVENT_NONLINEAR_OUTPUT_AVG    = "NLOut.avg"


################################################################################
################################################################################
def GetCurrentTimeInMS():
    return round(time.time() * 1000)



################################################################################
################################################################################
class MLJob():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.JobFilePathName = ""
        self.OriginalFilePathname = ""

        self.FormatVersion = DEFAULT_JOB_FORMAT_VERSION

        # These are the sections of the JOB spec
        self.JobXMLDOM = None
        self.RootXMLNode = None
        self.JobControlXMLNode = None
        self.DataXMLNode = None
        self.NetworkLayersXMLNode = None
        self.TrainingXMLNode = None

        self.ResultsXMLNode = None
        self.ResultsPreflightXMLNode = None
        self.ResultsTrainingXMLNode = None
        self.ResultsTestingXMLNode = None

        self.RuntimeXMLNode = None
        self.TestListXMLNode = None

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

        self.NumSamplesTested = 0
        self.TestResults = {}

        self.NumResultClasses = 0
        self.numInputVars = -1

        self.NumResultsInPreflight = 0
        self.PreflightNumItemsPerClass = []
        self.PreflightInputMins = []
        self.PreflightInputMaxs = []
        self.PreflightInputSums = []
        self.PreflightMeanInput = []
        self.InputDivergenceFromMeanTotal = []
        self.InputStdDevList = []

        self.ResultValMinValue = 0
        self.ResultValMaxValue = 0
        self.ResultValBucketSize = 0

        self.StartRequestTimeStr = ""
        self.StopRequestTimeStr = ""
        self.CurrentEpochNum = 0
        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0
        self.BufferedLogLines = ""
        self.DebugEvents = dataShow.EventTimeline()
        self.ResultValueType = tdf.TDF_DATA_TYPE_INT
        self.TrainingPriorities = [-1] * 1
        self.PreflightCentroidType = MLJOB_CENTROID_TYPE_FIXED
        self.PreflightNumCentroids = 0
        self.PreflightGlobalCentroidInputVals = None
        self.PreflightGlobalCentroidInputTotals = None
        self.PreflightGlobalCentroidInputMeans = None
        self.PreflightGlobalCentroidResultClassNums = None
        self.PreflightGlobalCentroidNumChildren = None
        self.PreflightGlobalCentroidMaxDistance = None
        self.PreflightResultClassCentroidInputVals = None
        self.PreflightResultClassCentroidInputTotals = None
        self.PreflightResultClassCentroidInputMean = None
        self.PreflightResultClassCentroidNumChildren = None
        self.PreflightResultClassCentroidPerMaxDistance = None
        self.PreflightInputSumsPerClass = [[0] * 1 for i in range(1)]
        self.PreflightResultClassDict = {}
        self.PreflightResultClassWeights = []

        self.TrainingTotalDevInputVar = None
        self.TrainingStdDevInputVar = None

        self.TrainNumItemsPerClass = []

        self.TestNumItemsPerClass = []
        self.TestNumPredictionsPerClass = []
        self.TestNumCorrectPerClass = []

        self.Debug = False
        self.LogFilePathname = ""

        self.OutputThreshold = -1
        self.IsLogisticNetwork = False
        self.LogisticResultsTrueValueList = []
        self.LogisticResultsPredictedProbabilityList = []
        self.ROCAUC = -1
        self.AUPRC = -1
        self.F1Score = -1

        self.InitRuntimeStateImpl()
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

        self.DataXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, DATA_ELEMENT_NAME)

        self.NetworkLayersXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_ELEMENT_NAME)

        self.TrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, TRAINING_ELEMENT_NAME)

        self.ResultsXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RESULTS_ELEMENT_NAME)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TESTING_ELEMENT_NAME)

        self.RuntimeXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RUNTIME_ELEMENT_NAME)

        self.TestListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, TEST_LIST_XML_NODE_NAME)

        # The saved state
        self.SavedModelStateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, SAVED_MODEL_STATE_ELEMENT_NAME)
        self.NeuralNetMatrixListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.SavedModelStateXMLNode, NETWORK_MATRIX_LIST_NAME)

        self.InferResultInfo()
        # TestResults is initialized when we start testing or when we read a job from meomory or file
    # End of InitNewJobImpl





    #####################################################
    #
    # [MLJob::ReadJobFromString]
    #
    # Return JOB_E_NO_ERROR or an error
    #####################################################
    def ReadJobFromString(self, jobString):
        #print("MLJob::ReadJobFromString")

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

        self.RuntimeXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RUNTIME_ELEMENT_NAME)
        self.TestListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, TEST_LIST_XML_NODE_NAME)

        self.SavedModelStateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, SAVED_MODEL_STATE_ELEMENT_NAME)
        self.NeuralNetMatrixListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.SavedModelStateXMLNode, NETWORK_MATRIX_LIST_NAME)

        self.NetworkType = self.GetNetworkType().lower()
        self.IsLogisticNetwork = dxml.XMLTools_GetChildNodeTextAsBool(self.NetworkLayersXMLNode, 
                                                                    NETWORK_LOGISTIC_ELEMENT_NAME, False)

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
        self.ReadTrainResultsFromXML(self.ResultsTrainingXMLNode)
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
        #resultStr = resultStr.replace("\n", "")
        #resultStr = resultStr.replace("\r", "")
        #resultStr = resultStr.replace("   ", "")
        #resultStr = resultStr.replace("  ", "")

        return resultStr
    # End of WriteJobToString




    #####################################################
    #
    # [MLJob::InitRuntimeStateImpl
    # 
    #####################################################
    def InitRuntimeStateImpl(self):
        self.OriginalFilePathname = ""
        self.StartRequestTimeStr = ""
        self.StopRequestTimeStr = ""
    
        self.CurrentEpochNum = 0
        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0

        self.BufferedLogLines = ""

        self.DebugEvents = dataShow.EventTimeline()
    # End -  InitRuntimeStateImpl





    #####################################################
    #
    # [MLJob::ReadRuntimeFromXML]
    #
    #####################################################
    def ReadRuntimeFromXML(self, parentXMLNode):
        #print("MLJob::ReadRuntimeFromXML. Starting")

        # Optionally, read any runtime if it is present.
        # This is only used when sending jobs between a dispatcher process and a
        # child worker process, and is not normally stored in a file. It could
        # be saved to a file if we ever want to "suspend" runtime state and
        # resume it at a later date, but that is not supported now and would
        # raise some tricky synchronization issues.
        #
        # These are all optional. No error if any are missing.
        self.OriginalFilePathname = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, "OriginalFilePathname", "")
        self.StartRequestTimeStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, "StartRequestTimeStr", "")
        self.StopRequestTimeStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, "StopRequestTimeStr", "")
        self.CurrentEpochNum = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, "CurrentEpochNum", -1)
        self.TotalTrainingLossInCurrentEpoch = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, "TotalTrainingLossInCurrentEpoch", -1.0)
        self.NumTrainLossValuesCurrentEpoch = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, "NumTrainLossValuesCurrentEpoch", -1.0)

        self.BufferedLogLines = dxml.XMLTools_GetChildNodeText(parentXMLNode, RUNTIME_LOG_NODE_ELEMENT_NAME)

        ###################
        # Debugging
        self.DebugEvents = dataShow.EventTimeline()
        xmlNode = dxml.XMLTools_GetChildNode(parentXMLNode, "DebugEvents")
        if (xmlNode is not None):
            resultStr = dxml.XMLTools_GetTextContents(xmlNode)
            resultStr = resultStr.lstrip()
            if (resultStr != ""):
                self.DebugEvents.DeserializeFromString(resultStr)
            # End - if (resultStr != ""):
        # End - if (xmlNode is not None):
        self.DebugEvents.RecordOnlyNthValue(100)
    # End - ReadRuntimeFromXML




    #####################################################
    #
    # [MLJob::WriteRuntimeToXML]
    #
    #####################################################
    def WriteRuntimeToXML(self, parentXMLNode):
        dxml.XMLTools_RemoveAllChildNodes(parentXMLNode)

        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "OriginalFilePathname", str(self.OriginalFilePathname))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "StartRequestTimeStr", str(self.StartRequestTimeStr))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "StopRequestTimeStr", str(self.StopRequestTimeStr))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "CurrentEpochNum", str(self.CurrentEpochNum))

        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "TotalTrainingLossInCurrentEpoch", str(self.TotalTrainingLossInCurrentEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "NumTrainLossValuesCurrentEpoch", str(self.NumTrainLossValuesCurrentEpoch))

        ###################
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "OS", str(platform.platform()))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "CPU", str(platform.processor()))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, "GPU", "None")

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
        # Debugging
        debugEventsXMLNode = dxml.XMLTools_GetOrCreateChildNode(parentXMLNode, "DebugEvents")
        if (debugEventsXMLNode is not None):
            serialStr = self.DebugEvents.SerializeToString()
            dxml.XMLTools_SetTextContents(debugEventsXMLNode, serialStr)
        # End - if (debugEventsXMLNode is not None):

    # End -  WriteRuntimeToXML




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
        self.OriginalFilePathname = jobFilePathName

        return err
    # End of ReadJobFromFile



    #####################################################
    #
    # [MLJob::SaveAs]
    #
    # Insert the runtime node and results node
    #####################################################
    def SaveAs(self, jobFilePathName):
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

        # Each request has a single test. When we finish the test, we have
        # finished the entire reqeust.
        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_IDLE)
        self.SetJobControlStr(JOBCTL_RESULT_MSG_ELEMENT_NAME, "")
        self.SetJobControlStr(JOBCTL_ERROR_CODE_ELEMENT_NAME, str(JOB_E_NO_ERROR))

        # Discard any previous saved state
        self.SetNamedStateAsStr(SAVED_STATE_TYPE_ELEMENT_NAME, "")
        self.SetNamedStateAsStr(SAVED_STATE_FILE_PATH_ELEMENT_NAME, "")

        # Save the current file pathname in the XML so it can be restored when we pass a job back and 
        # forth in memory between processes.
        self.OriginalFilePathname = self.JobFilePathName

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

        now = datetime.now()
        self.StopRequestTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")

        # Remove earlier results
        dxml.XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, RESULTS_TESTING_ELEMENT_NAME)

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
            self.ResultValMinValue = 0
            self.ResultValMaxValue = 0
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            self.NumResultClasses = tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES
            self.ResultValMinValue = 0
            self.ResultValMaxValue = tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES - 1
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            self.NumResultClasses = 2
            self.ResultValMinValue = 0
            self.ResultValMaxValue = 1
        else:
            self.NumResultClasses = 1
            self.ResultValMinValue = 0
            self.ResultValMaxValue = 0

        # Figure out the result value type.
        self.ResultValBucketSize = 1
        if ((resultValName != "") and (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT))):
            self.ResultValMinValue, self.ResultValMaxValue = tdf.TDF_GetMinMaxValuesForVariable(resultValName)
            valRange = float(self.ResultValMaxValue - self.ResultValMinValue)
            self.ResultValBucketSize = float(valRange) / float(ML_JOB_NUM_NUMERIC_VALUE_BUCKETS)

        inputVarNameListStr = self.GetNetworkInputVarNames()
        inputVarArray = inputVarNameListStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)

        self.numInputVars = len(inputVarArray)
    # End - InferResultInfo


    #####################################################
    #
    # [MLJob::GetNumTrainingPriorities]
    # 
    #####################################################
    def GetNumTrainingPriorities(self):
        return self.NumResultClasses
    # End - GetNumTrainingPriorities


    #####################################################
    #
    # [MLJob::GetMaxSkippedTrainingPriorities]
    # 
    #####################################################
    def GetMaxSkippedTrainingPriorities(self):
        configVal = dxml.XMLTools_GetChildNodeTextAsInt(self.TrainingXMLNode, TRAINING_MAX_NUM_SKIPPED_RESULT_CLASSES, -1)
        if (configVal > 0):
            return configVal

        if (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            return 1
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            return ML_JOB_DEFAULT_MAX_SKIPPED_EVENT_CLASS_BUCKETS
        else:  # self.ResultValueType == tdf.TDF_DATA_TYPE_FLOAT or self.ResultValueType == tdf.TDF_DATA_TYPE_INT):
            return ML_JOB_DEFAULT_MAX_SKIPPED_NUMERIC_VALUE_BUCKETS
    # End - GetMaxSkippedTrainingPriorities



    #####################################################
    #
    # [MLJob::StartPrioritizingTrainingSamplesInPartition]
    # 
    # This is called when we start using the priorities during training.
    # The priorities have already been established, now we apply them.
    #####################################################
    def StartPrioritizingTrainingSamplesInPartition(self):
        fDebug = False

        unsortedList = []
        for resultClassNum in range(self.NumResultClasses):
            numInstances = self.PreflightNumItemsPerClass[resultClassNum]
            unsortedList.append({"c": resultClassNum, "n": numInstances})

        newlist = sorted(unsortedList, key=lambda k: k["n"])
        if (fDebug):
            print("StartPrioritizingTrainingSamplesInPartition. newlist=" + str(newlist))

        self.TrainingPriorities = [-1] * self.NumResultClasses
        priority = 0
        for resultClassInfo in newlist:
            self.TrainingPriorities[resultClassInfo["c"]] = priority
            priority += 1
        # End - for resultClassInfo in newlist
    # End - StartPrioritizingTrainingSamplesInPartition





    #####################################################
    #
    # [MLJob::GetTrainingPriority]
    # 
    #####################################################
    def GetTrainingPriority(self, trueResult):
        fDebug = False

        if (fDebug):
            if ((int(trueResult) < 0) or (int(trueResult) > self.NumResultClasses)):
                print("GetTrainingPriority. Invalid trueResult=" + str(trueResult))
            print("GetTrainingPriority. self.TrainingPriorities=" + str(self.TrainingPriorities))
            print("        self.NumResultClasses=" + str(self.NumResultClasses))
        # End - if (fDebug):

        #####################
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS, tdf.TDF_DATA_TYPE_BOOL)):
            resultBucket = int(trueResult)
        #####################
        elif (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            offset = max(int(trueResult) - self.ResultValMinValue, 0)
            resultBucket = int(offset / self.ResultValBucketSize)
            if (resultBucket >= self.NumResultClasses):
                resultBucket = self.NumResultClasses - 1
        else:
            return(0)

        return self.TrainingPriorities[resultBucket]
    # End - GetTrainingPriority




    #####################################################
    #
    # [MLJob::StartPreflight]
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartPreflight(self):
        #print("MLJob::StartPreflight. Start")

        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InferResultInfo()

        self.PreflightNumItemsPerClass = numpy.zeros(self.NumResultClasses)
        self.PreflightInputMins = numpy.full((self.numInputVars), 1000000)
        self.PreflightInputMaxs = numpy.full((self.numInputVars), -1)
        self.PreflightInputSums = numpy.zeros(self.numInputVars)
        self.PreflightMeanInput = numpy.zeros(self.numInputVars)
        self.InputDivergenceFromMeanTotal = numpy.zeros(self.numInputVars)
        self.InputStdDevList = numpy.zeros(self.numInputVars)

        # self.PreflightInputSumsPerClass is indexed as self.PreflightInputSumsPerClass[classNum][varNum]
        self.PreflightInputSumsPerClass = numpy.zeros((self.NumResultClasses, self.numInputVars))

        self.PreflightCentroidType = MLJOB_CENTROID_TYPE_FIXED
        # We *could* have 1 centroid for every combination of a low and high value of a variable.
        # This is 2 possible values per variable, for N variables. This is similar to a
        # binary number of N digits, so there are 2**N combinations (which is a lot).
        # Instead, let's do N centroids, each is all low values and 1 high value.
        inputVarNameListStr = self.GetNetworkInputVarNames()
        inputVarArray = inputVarNameListStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)
        self.PreflightNumCentroids = self.numInputVars

        # Assign each Centroid to a random spot in the space.
        # We *could* have 1 centroid for every combination of a low and high value of a variable.
        # This is 2 possible values per variable, for N variables. This is similar to a
        # binary number of N digits, so there are N**2 combinations (which is a lot)
        self.PreflightGlobalCentroidInputVals = numpy.zeros((self.PreflightNumCentroids, self.numInputVars))
        random.seed()
        for valNum in range(self.numInputVars):
            inputName = inputVarArray[valNum]
            _, nameStem, _, _ = tdf.TDF_ParseOneVariableName(inputName)
            labMinVal, labMaxVal = tdf.TDF_GetMinMaxValuesForVariable(nameStem)
            varType = tdf.TDF_GetVariableType(nameStem)
            valRange = max(labMaxVal - labMinVal, 0)
            for centroidNum in range(self.PreflightNumCentroids):
                randNum = random.uniform(0, 1)
                if (varType == tdf.TDF_DATA_TYPE_BOOL):
                    self.PreflightGlobalCentroidInputVals[centroidNum][valNum] = round(randNum)
                elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FLOAT):
                    self.PreflightGlobalCentroidInputVals[centroidNum][valNum] = (labMinVal + (randNum * valRange))
                else:  # elif ((varType == tdf.TDF_DATA_TYPE_INT) or (varType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS)):
                    self.PreflightGlobalCentroidInputVals[centroidNum][valNum] = round(labMinVal + (randNum * valRange))
            # End - for centroidNum in range(self.PreflightNumCentroids):
        # End - for valNum in range(self.numInputVars):

        self.PreflightGlobalCentroidInputTotals = numpy.zeros((self.PreflightNumCentroids, self.numInputVars))
        self.PreflightGlobalCentroidInputMeans = numpy.zeros((self.PreflightNumCentroids, self.numInputVars))
        self.PreflightGlobalCentroidResultClassNums = numpy.zeros((self.PreflightNumCentroids, self.NumResultClasses))
        self.PreflightGlobalCentroidNumChildren = numpy.zeros(self.PreflightNumCentroids)
        self.PreflightGlobalCentroidMaxDistance = numpy.zeros(self.PreflightNumCentroids)

        self.PreflightResultClassCentroidInputVals = numpy.zeros((self.NumResultClasses, 
                                                                    self.PreflightNumCentroids, 
                                                                    self.numInputVars))
        for valNum in range(self.numInputVars):
            inputName = inputVarArray[valNum]
            _, nameStem, _, _ = tdf.TDF_ParseOneVariableName(inputName)
            labMinVal, labMaxVal = tdf.TDF_GetMinMaxValuesForVariable(nameStem)
            varType = tdf.TDF_GetVariableType(nameStem)
            valRange = max(labMaxVal - labMinVal, 0)

            for resultClassNum in range(self.NumResultClasses):
                for centroidNum in range(self.PreflightNumCentroids):
                    randNum = random.uniform(0, 1)
                    if (varType == tdf.TDF_DATA_TYPE_BOOL):
                        self.PreflightResultClassCentroidInputVals[resultClassNum][centroidNum][valNum] = round(randNum)
                    elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FLOAT):
                        self.PreflightResultClassCentroidInputVals[resultClassNum][centroidNum][valNum] = (labMinVal + (randNum * valRange))
                    else:  # elif ((varType == tdf.TDF_DATA_TYPE_INT) or (varType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS)):
                        self.PreflightResultClassCentroidInputVals[resultClassNum][centroidNum][valNum] = round(labMinVal + (randNum * valRange))
                # End - for centroidNum in range(self.PreflightNumCentroids):
            # End - for classNum in range(self.NumResultClasses):
        # End - for valNum in range(self.numInputVars):

        self.PreflightResultClassCentroidInputTotals = numpy.zeros((self.NumResultClasses, 
                                                                    self.PreflightNumCentroids,
                                                                    self.numInputVars))
        self.PreflightResultClassCentroidInputMean = numpy.zeros((self.NumResultClasses, 
                                                                    self.PreflightNumCentroids,
                                                                    self.numInputVars))
        self.PreflightResultClassCentroidNumChildren = numpy.zeros((self.NumResultClasses, self.PreflightNumCentroids))
        self.PreflightResultClassCentroidPerMaxDistance = numpy.zeros((self.NumResultClasses, self.PreflightNumCentroids))

        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_PREFLIGHT)
    # End - StartPreflight





    #####################################################
    #
    # [MLJob::PreflightData
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def PreflightData(self, inputVec, resultVal):
        fDebug = False

        # Get the bucket for this result value
        #####################
        if (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            resultBucket = int(resultVal)
        #####################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            resultBucket = int(resultVal)
        #####################
        elif (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            offset = max(resultVal - self.ResultValMinValue, 0)
            resultBucket = int(offset / self.ResultValBucketSize)
            if (resultBucket >= self.NumResultClasses):
                resultBucket = self.NumResultClasses - 1

        if (fDebug):
            print("PreflightData. self.ResultValueType = " + str(self.ResultValueType))
            print("PreflightData. resultBucket = " + str(resultBucket))
       
        self.NumResultsInPreflight += 1
        self.PreflightNumItemsPerClass[resultBucket] += 1
        if (fDebug):
            print("PreflightData. self.PreflightNumItemsPerClass=" + str(self.PreflightNumItemsPerClass))

        if (fDebug):
            print("PreflightData. self.PreflightInputMins = " + str(self.PreflightInputMins))
            print("PreflightData. self.PreflightInputMaxs = " + str(self.PreflightInputMaxs))
            print("PreflightData. self.PreflightInputSums = " + str(self.PreflightInputSums))
            print("PreflightData. self.NumInputVars=" + str(self.numInputVars))

        self.PreflightInputSums += inputVec

        for valNum in range(self.numInputVars):
            currentValue = inputVec[valNum]
            if (currentValue < self.PreflightInputMins[valNum]):
                self.PreflightInputMins[valNum] = currentValue
            if (currentValue > self.PreflightInputMaxs[valNum]):
                self.PreflightInputMaxs[valNum] = currentValue
        # End - for valNum in range(self.numInputVars)

        if (fDebug):
            print("self.PreflightInputMins = " + str(self.PreflightInputMins))
            print("self.PreflightInputMaxs = " + str(self.PreflightInputMaxs))
            print("self.PreflightInputSums = " + str(self.PreflightInputSums))

        # self.PreflightInputSumsPerClass is indexed as self.PreflightInputSumsPerClass[classNum][varNum]
        self.PreflightInputSumsPerClass[resultBucket] = self.PreflightInputSumsPerClass[resultBucket] + inputVec

        # Find the centroid that is closest to this data point.
        chosenCentroid = -1
        smallestDistance = -1
        for centroidNum in range(self.PreflightNumCentroids):
            currentCentroid = self.PreflightGlobalCentroidInputVals[centroidNum]
            # Compute the Euclidean distance.
            # For performance, this uses a trick: the L2 normal (ie the L2 loss) is the sqrt of the sum of squares of distance.
            currentDistance = numpy.linalg.norm(inputVec - currentCentroid)
            if ((chosenCentroid < 0) or ((chosenCentroid > 0) and (currentDistance < smallestDistance))):
                chosenCentroid = centroidNum
                smallestDistance = currentDistance
        # for centroidNum in range(self.PreflightNumCentroids):

        # Update stats for the chosen Centroid.
        if (chosenCentroid >= 0):
            self.PreflightGlobalCentroidInputTotals[chosenCentroid] += inputVec
            self.PreflightGlobalCentroidNumChildren[chosenCentroid] += 1
            self.PreflightGlobalCentroidResultClassNums[chosenCentroid][resultBucket] += 1
            # If this new child is farther fromthe centroid than any other child of the same centroid, then
            # record this. It is the outer border of the orbit for this centroid.
            if (smallestDistance > self.PreflightGlobalCentroidMaxDistance[chosenCentroid]):
                self.PreflightGlobalCentroidMaxDistance[chosenCentroid] = smallestDistance
        # End - if (chosenCentroid >= 0):

        # Now, repeat this process for the resultClass.
        # <> Not sure if this is useful. Let's collect some data and see if it is meaningful/useful.
        # If it isn't then remove this.
        chosenCentroid = -1
        smallestDistance = -1
        for centroidNum in range(self.PreflightNumCentroids):
            currentCentroid = self.PreflightResultClassCentroidInputVals[resultBucket][centroidNum]
            # Compute the Euclidean distance.
            # For performance, this uses a trick: the L2 normal (ie the L2 loss) is the sqrt of the sum of squares of distance.
            currentDistance = numpy.linalg.norm(inputVec - currentCentroid)
            if ((chosenCentroid < 0) or ((chosenCentroid > 0) and (currentDistance < smallestDistance))):
                chosenCentroid = centroidNum
                smallestDistance = currentDistance
        # for centroidNum in range(self.PreflightNumCentroids):

        # Update stats for the chosen Centroid.
        if (chosenCentroid >= 0):
            self.PreflightResultClassCentroidNumChildren[resultBucket][chosenCentroid] += 1
            self.PreflightResultClassCentroidInputTotals[resultBucket][chosenCentroid] += inputVec
            # If this new child is farther fromthe centroid than any other child of the same centroid, then
            # record this. It is the outer border of the orbit for this centroid.
            if (smallestDistance > self.PreflightResultClassCentroidPerMaxDistance[resultBucket][chosenCentroid]):
                self.PreflightResultClassCentroidPerMaxDistance[resultBucket][chosenCentroid] = smallestDistance
        # End - if (chosenCentroid >= 0):

        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_PREFLIGHT)
    # End - PreflightData




    #####################################################
    #
    # [MLJob::FinishPreflight
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishPreflight(self):
        # Compute the mean for each input val. This will be used to determine Std Dev 
        # during training.
        for inputNum in range(self.numInputVars):
            if (self.NumResultsInPreflight > 0):
                self.PreflightMeanInput[inputNum] = self.PreflightInputSums[inputNum] / self.NumResultsInPreflight
            else:
                self.PreflightMeanInput[inputNum] = 0
        # End - for inputNum in range(self.numInputVars):

        # Get the average number of items per class.
        avgNumItemsPerClass = self.NumResultsInPreflight / self.NumResultClasses

        # Compute the weight for each class
        self.PreflightResultClassWeights = [0] * self.NumResultClasses
        for resultClassNum in range(self.NumResultClasses):
            numItemsInClass = self.PreflightNumItemsPerClass[resultClassNum]

            if (numItemsInClass <= 0):
                classWeight = 0
            else:
                classWeight = avgNumItemsPerClass / numItemsInClass

            if (classWeight > 1.0):
                classWeight = ADDITIONAL_MULTIPLIER_FOR_UNDERREPRESENTED_CLASSES * round(classWeight)
            classWeight = max(classWeight, CLASS_WEIGHTS_LEVEL_FOR_REINTRODUCING_PRETEST_PROBABILITY)

            self.PreflightResultClassWeights[resultClassNum] = classWeight
        # End - for resultClassNum in range(self.NumResultClasses)

        # Make a new runtime object for each resultClass element
        self.PreflightResultClassDict = {}
        for resultClassNum in range(self.NumResultClasses):
            newResultClassInfo = {'weight': self.PreflightResultClassWeights[resultClassNum]}
            self.PreflightResultClassDict[resultClassNum] = newResultClassInfo
        # End - for resultClassNum in range(self.NumResultClasses)      
    # End - FinishPreflight





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

        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            self.NumResultClasses = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            self.NumResultClasses = tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            self.NumResultClasses = 2
        else:
            self.NumResultClasses = 1

        self.TrainNumItemsPerClass = [0] * self.NumResultClasses

        self.TrainingTotalDevInputVar = numpy.zeros(self.numInputVars)
        self.TrainingStdDevInputVar = numpy.zeros(self.numInputVars)

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
        self.TotalTrainingLossInCurrentEpoch += loss
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
        if (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            intActualValue = max(int(actualValue), 0)
            intActualValue = min(int(actualValue), tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES - 1)
            self.TrainNumItemsPerClass[intActualValue] += 1
        #####################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            intActualValue = max(int(actualValue), 0)
            intActualValue = min(int(actualValue), 1)
            self.TrainNumItemsPerClass[intActualValue] += 1
        #####################
        elif (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            offset = max(actualValue - self.ResultValMinValue, 0)
            bucketNum = int(offset / self.ResultValBucketSize)
            if (bucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                bucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
            self.TrainNumItemsPerClass[bucketNum] += 1


        # Now, compute the divergence of each input from the mean.
        for inputNum in range(self.numInputVars):
            delta = inputVec[inputNum] - self.PreflightMeanInput[inputNum]
            delta = delta * delta
            self.InputDivergenceFromMeanTotal[inputNum] += delta
        # End - for inputNum in range(self.numInputVars):
    # End -  RecordTrainingSample




    #####################################################
    #
    # [MLJob::FinishTrainingEpoch
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishTrainingEpoch(self):
        avgLoss = self.GetRunningAvgLossInCurrentEpoch()
        self.AvgLossPerEpochList.append(avgLoss)

        # On finishing the first Epoch, we compute the StdDev
        # Variance of given variable is the expected value of the squared difference between the 
        # variable and its expected value
        #    Var(x) = E(SUM(  ( x[i] - E(x) )**2   ))
        #           = SUM(  ( x[i] - E(x) )**2   )  * P(x[i]-E(x))
        #           = SUM(  ( x[i] - E(x) )**2   )  * 1/N)
        #           = SUM(  ( x[i] - E(x) )**2   )  ) * 1/N
        # 
        # Standard deviation is the square root of variance
        #    Std(x) = SQRT( E(SUM(  ( x[i] - E(x) )**2   )) )
        #           ...
        #           = SQRT( SUM(  ( x[i] - E(x) )**2   )  ) * 1/N )
        # 
        # But, expected Value is just the weighted average of all values, which is the mean
        # if all values are the same
        #    E(x) = SUM(x[i] * P(x[i]))
        # If all values have the name probability and there are N possible values
        #    E(x) = SUM(x[i] * 1/N)
        #    E(x) = 1/N * SUM(x[i])
        #    E(x) = mean
        if (self.CurrentEpochNum == 0):
            for inputNum in range(self.numInputVars):
                try:
                    self.InputStdDevList[inputNum] = self.InputDivergenceFromMeanTotal[inputNum] / self.NumSamplesTrainedPerEpoch
                except Exception:
                    print("Exception from FinishTrainingEpoch.")
                    print("CurrentEpochNum = " + str(self.CurrentEpochNum))
                    print("inputNum = " + str(inputNum))
                    print("self.NumSamplesTrainedPerEpoch = " + str(self.NumSamplesTrainedPerEpoch))
                    print("self.InputDivergenceFromMeanTotal[inputNum] = " + str(self.InputDivergenceFromMeanTotal[inputNum]))
            # End - for inputNum in range(self.numInputVars):
        # End - if (self.CurrentEpochNum == 0):

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


        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            self.NumResultClasses = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            self.NumResultClasses = tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            self.NumResultClasses = 2
        else:
            self.NumResultClasses = 1

        self.TestNumItemsPerClass = [0] * self.NumResultClasses
        self.TestNumPredictionsPerClass = [0] * self.NumResultClasses
        self.TestNumCorrectPerClass = [0] * self.NumResultClasses

        self.SetJobControlStr(JOBCTL_STATUS_ELEMENT_NAME, MLJOB_STATUS_TESTING)
    # End - StartTesting




    #####################################################
    #
    # [MLJob::RecordTestingResult
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def RecordTestingResult(self, actualValue, predictedValue):
        fDebug = False
        self.NumSamplesTested += 1

        #########################
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            difference = float(actualValue - predictedValue)
            if (difference < 0):
                difference = -difference

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

            offset = max(actualValue - self.ResultValMinValue, 0)
            actualBucketNum = int(offset / self.ResultValBucketSize)
            if (actualBucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                actualBucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
            self.TestNumItemsPerClass[actualBucketNum] += 1

            # Check for extremes, since the prediction may be very huge or very small.
            if (predictedValue >= self.ResultValMaxValue):
                predictedBucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
            elif (predictedValue < self.ResultValMinValue):
                predictedBucketNum = 0
            else:
                try:
                    offset = max(predictedValue - self.ResultValMinValue, 0)
                    predictedBucketNum = int(offset / self.ResultValBucketSize)
                    if (predictedBucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                        predictedBucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
                except Exception:
                    predictedBucketNum = 0
            # End - else
            self.TestNumPredictionsPerClass[predictedBucketNum] += 1
            if (predictedBucketNum == actualBucketNum):
                self.TestNumCorrectPerClass[actualBucketNum] += 1

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

        #########################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            # If this is a Logistic, then convert the resulting probability into a 0 or 1
            if (fDebug):
                print("RecordTestingResult. Bool. actualValue=" + str(actualValue))
                print("RecordTestingResult. Bool. predictedValue=" + str(predictedValue))
                print("RecordTestingResult. Bool. self.IsLogisticNetwork=" + str(self.IsLogisticNetwork))
                print("RecordTestingResult. Bool. self.OutputThreshold=" + str(self.OutputThreshold))

            if ((self.IsLogisticNetwork) and (self.OutputThreshold > 0)):
                predictedFloat = float(predictedValue)
                if ((fDebug) and (predictedValue != 0)):
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
    # [MLJob::GetOutputThreshold]
    #
    #####################################################
    def GetOutputThreshold(self):
        if (not self.IsLogisticNetwork):
            return(-1)

        # The default is any probability over 50% is True. This is a coin-toss.
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkLayersXMLNode, 
                                                        NETWORK_OUTPUT_THRESHOLD_ELEMENT_NAME, "0.5")
        if ((resultStr is None) or (resultStr == "")):
            return(-1)

        try:
            resultFloat = float(resultStr)
        except Exception:
            resultFloat = -1

        #print("GetOutputThreshold. resultFloat=" + str(resultFloat))
        return(resultFloat)
    # End of GetOutputThreshold




    #####################################################
    # [MLJob::GetPreflightResults]
    #####################################################
    def GetPreflightResults(self):
        inputVarNameListStr = self.GetNetworkInputVarNames()
        inputVarArray = inputVarNameListStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)

        inputVarNameStemArray = ["" for x in range(self.numInputVars)]
        inputTypeArray = [0 for x in range(self.numInputVars)]
        for inputNum in range(self.numInputVars):
            inputName = inputVarArray[inputNum]
            _, nameStem, _, _ = tdf.TDF_ParseOneVariableName(inputName)
            varType = tdf.TDF_GetVariableType(nameStem)

            inputVarNameStemArray[inputNum] = nameStem
            inputTypeArray[inputNum] = varType
            #labMinVal, labMaxVal = tdf.TDF_GetMinMaxValuesForVariable(nameStem)
        # End - for inputNum in range(self.numInputVars):

        return self.numInputVars, inputVarNameStemArray, inputTypeArray, self.PreflightInputMins, self.PreflightInputMaxs, self.PreflightMeanInput
    # End - GetPreflightResults




    #####################################################
    #
    # [MLJob::MakeStateFilePathname]
    #
    # Returns: Error code
    #####################################################
    def MakeStateFilePathname(self, newFileExtension):
        fDebug = False

        if (fDebug):
            print("MakeStateFilePathname. self.JobFilePathName = " + self.JobFilePathName)
            print("MakeStateFilePathname. self.OriginalFilePathname = " + self.OriginalFilePathname)

        pathName = self.JobFilePathName

        # When we pass a job back and forth in memory between processes, we 
        # lose the original pathname from JobFilePathName
        if ((pathName is None) or (pathName == "")):
            pathName = self.OriginalFilePathname            

        if ((pathName is None) or (pathName == "")):
            print("ERROR! pathName is useless: " + str(pathName))
            return ""

        newDirName = os.path.dirname(pathName)
        fileName = os.path.basename(pathName)

        fileNameParts = os.path.splitext(fileName)
        fileName = fileNameParts[0]
        if (newFileExtension != ""):
            fileName = fileName + "." + newFileExtension

        newPathName = os.path.join(newDirName, fileName)
        return newPathName
    # End of MakeStateFilePathname




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

        stateStr = stateStr.lstrip()
        stateStr = stateStr.rstrip()
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
        if (fDebug):
            print("MLJob::GetLinearUnitMatrices")

        linearUnitNode = dxml.XMLTools_GetChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (linearUnitNode is None):
            if (fDebug):
                print("MLJob::GetLinearUnitMatrices. Error. Linear Unit node is None")
            return False, None, None

        #formatStr = dxml.XMLTools_GetAttribute(linearUnitNode, MLJOB_MATRIX_FORMAT_ATTRIBUTE_NAME)
        #if ((formatStr is None) or (formatStr == "")): formatStr = MLJOB_MATRIX_FORMAT_SIMPLE

        weightXMLNode = dxml.XMLTools_GetChildNode(linearUnitNode, NETWORK_MATRIX_WEIGHT_MATRIX_NAME)
        biasXMLNode = dxml.XMLTools_GetChildNode(linearUnitNode, NETWORK_MATRIX_BIAS_VECTOR_NAME)
        if ((weightXMLNode is None) or (biasXMLNode is None)):
            if (fDebug):
                print("MLJob::GetLinearUnitMatrices. Error. weightXMLNode is None")
            return False, None, None

        weightStr = dxml.XMLTools_GetTextContents(weightXMLNode)
        weightStr = weightStr.lstrip()
        biasStr = dxml.XMLTools_GetTextContents(biasXMLNode)
        biasStr = biasStr.lstrip()
        #print("GetLinearUnitMatrices. weightStr=" + weightStr)
        #print("GetLinearUnitMatrices. biasStr=" + biasStr)

        weightMatrix = self.MLJob_ConvertStringTo2DMatrix(weightStr)
        biasMatrix = MLJob_ConvertStringTo1DVector(biasStr)

        if (fDebug):
            #print("GetLinearUnitMatrices. weightMatrix=" + str(weightMatrix))
            #print("GetLinearUnitMatrices. biasMatrix=" + str(biasMatrix))
            pass

        return True, weightMatrix, biasMatrix
    # End - GetLinearUnitMatrices


     

    #####################################################
    #
    # [MLJob::SetLinearUnitMatrices
    # 
    #####################################################
    def SetLinearUnitMatrices(self, name, weightMatrix, biasMatrix):
        fDebug = False
        if (fDebug):
            print("MLJob::SetLinearUnitMatrices")

        linearUnitNode = dxml.XMLTools_GetOrCreateChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (linearUnitNode is None):
            return

        weightXMLNode = dxml.XMLTools_GetOrCreateChildNode(linearUnitNode, NETWORK_MATRIX_WEIGHT_MATRIX_NAME)
        biasXMLNode = dxml.XMLTools_GetOrCreateChildNode(linearUnitNode, NETWORK_MATRIX_BIAS_VECTOR_NAME)
        if ((weightXMLNode is None) or (biasXMLNode is None)):
            return

        if (fDebug):
            print("MLJob::SetLinearUnitMatrices - setting the values")

        weightStr = self.MLJob_Convert2DMatrixToString(weightMatrix)
        biasStr = MLJob_Convert1DVectorToString(biasMatrix)
    
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
    # [MLJob_Convert3DMatrixToString]
    #
    # inputArray is a numpy array.
    ################################################################################
    def MLJob_Convert3DMatrixToString(self, inputArray):
        dim1 = len(inputArray)
        if (dim1 > 0):
            dim2 = len(inputArray[0])
        else:
            dim2 = 0
        if (dim2 > 0):
            dim3 = len(inputArray[0][0])
        else:
            dim3 = 0

        resultString = "NumD=3;D=" + str(dim1) + VALUE_SEPARATOR_CHAR + str(dim2) + VALUE_SEPARATOR_CHAR + str(dim3) + ";T=float;" + ROW_SEPARATOR_CHAR
        for index1 in range(dim1):
            matrix2d = inputArray[index1]
            for index2 in range(dim2):
                row = matrix2d[index2]
                for numVal in row:
                    resultString = resultString + str(numVal) + VALUE_SEPARATOR_CHAR
                resultString = resultString[:-1]
                resultString = resultString + ROW_SEPARATOR_CHAR
            # End - for index2 in range(dim2):
        # End - for index1 in range(dim1):

        return(resultString)
    # End - MLJob_Convert3DMatrixToString





    ################################################################################
    #
    # [MLJob_ConvertStringTo3DMatrix]
    #
    ################################################################################
    def MLJob_ConvertStringTo3DMatrix(self, matrixStr):
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
        dim1 = 0
        dim2 = 0
        dim3 = 0
        if (dimensionStr != ""):
            dimensionList = dimensionStr.split(VALUE_SEPARATOR_CHAR)
            if (len(dimensionList) == 3):
                dim1 = int(dimensionList[0])
                dim2 = int(dimensionList[1])
                dim3 = int(dimensionList[2])
            else:
                print("\n\nERROR! MLJob_ConvertStringTo3DMatrix. Invalid dimension for a matrixStr. dimensionStr=[" + dimensionStr + "]")
                sys.exit(0)
        # End - if (dimensionStr != ""):

        # Make an empty matrix which will be filled below.
        newMatrix = numpy.empty([dim1, dim2, dim3])

        # Read each 1-D vector and put it in the next place of the result matrix
        matrixAllRowsStr = sectionList[len(sectionList) - 1]
        matrixRowStrList = matrixAllRowsStr.split(ROW_SEPARATOR_CHAR)
        index1 = 0    
        index2 = 0    
        for singleRowStr in matrixRowStrList:
            if (singleRowStr != ""):
                # Place a vector into the current spot of the result matrix
                valueList = singleRowStr.split(VALUE_SEPARATOR_CHAR)
                index3 = 0
                for value in valueList:
                    if (index3 >= dim3):
                        print("\n\nERROR! MLJob_ConvertStringTo3DMatrix. Overran a matrix. dimensionStr=[" + dimensionStr + "]")
                        sys.exit(0)
                    newMatrix[index1][index2][index3] = float(value)
                    index3 += 1
                # End - for value in valueList:

                # We should have filled it completely, and will stop at the end of the matrix
                if (index3 != dim3):
                    print("\n\nERROR! MLJob_ConvertStringTo3DMatrix. Underfilled a row in the matrix. dimensionStr=[" + dimensionStr + "]")
                    sys.exit(0)

                # Advance the position where we will next fill the result matrix
                index2 += 1
                if (index2 >= dim2):
                    index1 += 1
                    index2 = 0
            # End - if (singleRowStr != ""):
        # End - for singleRowStr in matrixRowStrList:

        # We should have filled it completely, and will stop at the end of the matrix
        if (index1 != dim1):
            print("\n\nERROR! MLJob_ConvertStringTo3DMatrix. Underfilled the entire matrix. dimensionStr=[" + dimensionStr + "]")
            sys.exit(0)

        return(newMatrix)
    # End - MLJob_ConvertStringTo3DMatrix




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

        # Read each 1-D vector and put it in the next place of the result matrix
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
                                                        RESULTS_NUM_ITEMS_ELEMENT_NAME, 0)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, "")
        self.PreflightNumItemsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_INPUT_MINS_ELEMENT_NAME, "")
        self.PreflightInputMins = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_INPUT_MAXS_ELEMENT_NAME, "")
        self.PreflightInputMaxs = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_INPUT_TOTALS_ELEMENT_NAME, "")
        self.PreflightInputSums = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_INPUT_MEANS_ELEMENT_NAME, "")
        self.PreflightMeanInput = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_INPUT_DIVERGENCE_FROM_MEAN_TOTALS_ELEMENT_NAME, "")
        self.InputDivergenceFromMeanTotal = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_INPUT_STD_DEV_ELEMENT_NAME, "")
        self.InputStdDevList = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_INPUT_SUMS_FOR_EACH_CLASS_ELEMENT_NAME, "")
        self.PreflightInputSumsPerClass = self.MLJob_ConvertStringTo2DMatrix(resultStr)

        self.PreflightCentroidType = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_CENTROID_TYPE, MLJOB_CENTROID_TYPE_FIXED)

        self.PreflightNumCentroids = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_NUM_CENTROIDS, -1)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_VALUES, "")
        self.PreflightGlobalCentroidInputVals = self.MLJob_ConvertStringTo2DMatrix(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_TOTALS, "")
        self.PreflightGlobalCentroidInputTotals = self.MLJob_ConvertStringTo2DMatrix(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_MEANS, "")
        self.PreflightGlobalCentroidInputMeans = self.MLJob_ConvertStringTo2DMatrix(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_GLOBAL_CENTROID_RESULT_CLASSES, "")
        self.PreflightGlobalCentroidResultClassNums = self.MLJob_ConvertStringTo2DMatrix(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_GLOBAL_CENTROID_NUM_SATELLITES, "")
        self.PreflightGlobalCentroidNumChildren = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_GLOBAL_CENTROID_MAX_DISTANCE, "")
        self.PreflightGlobalCentroidMaxDistance = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_VALS, "")
        self.PreflightResultClassCentroidInputVals = self.MLJob_ConvertStringTo3DMatrix(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_TOTALS, "")
        self.PreflightResultClassCentroidInputTotals = self.MLJob_ConvertStringTo3DMatrix(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_INPUT_MEANS, "")
        self.PreflightResultClassCentroidInputMean = self.MLJob_ConvertStringTo3DMatrix(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_VALS_NUM_SATS, "")
        self.PreflightResultClassCentroidNumChildren = self.MLJob_ConvertStringTo2DMatrix(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_MAX_DISTANCE, "")
        self.PreflightResultClassCentroidPerMaxDistance = self.MLJob_ConvertStringTo2DMatrix(resultStr)

        self.ReadResultClassWeightsFromXML()
    # End - ReadPreflightResultsFromXML




    #####################################################
    #
    # [MLJob::WritePreflightResultsToXML
    # 
    #####################################################
    def WritePreflightResultsToXML(self, parentXMLNode):
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_NUM_ITEMS_ELEMENT_NAME, str(self.NumResultsInPreflight))

        resultStr = MLJob_Convert1DVectorToString(self.PreflightNumItemsPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputMins)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_INPUT_MINS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputMaxs)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_INPUT_MAXS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputSums)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_INPUT_TOTALS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightMeanInput)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_INPUT_MEANS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.InputDivergenceFromMeanTotal)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_INPUT_DIVERGENCE_FROM_MEAN_TOTALS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.InputStdDevList)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_INPUT_STD_DEV_ELEMENT_NAME, resultStr)

        resultStr = self.MLJob_Convert2DMatrixToString(self.PreflightInputSumsPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_INPUT_SUMS_FOR_EACH_CLASS_ELEMENT_NAME, resultStr)

        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_CENTROID_TYPE, self.PreflightCentroidType)

        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_NUM_CENTROIDS, str(self.PreflightNumCentroids))

        resultStr = self.MLJob_Convert2DMatrixToString(self.PreflightGlobalCentroidInputVals)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_VALUES, resultStr)

        resultStr = self.MLJob_Convert2DMatrixToString(self.PreflightGlobalCentroidInputTotals)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_TOTALS, resultStr)

        resultStr = self.MLJob_Convert2DMatrixToString(self.PreflightGlobalCentroidInputMeans)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_GLOBAL_CENTROID_INPUT_MEANS, resultStr)

        resultStr = self.MLJob_Convert2DMatrixToString(self.PreflightGlobalCentroidResultClassNums)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_GLOBAL_CENTROID_RESULT_CLASSES, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightGlobalCentroidNumChildren)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_GLOBAL_CENTROID_NUM_SATELLITES, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightGlobalCentroidMaxDistance)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_GLOBAL_CENTROID_MAX_DISTANCE, resultStr)

        resultStr = self.MLJob_Convert3DMatrixToString(self.PreflightResultClassCentroidInputVals)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_VALS, resultStr)

        resultStr = self.MLJob_Convert3DMatrixToString(self.PreflightResultClassCentroidInputTotals)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_TOTALS, resultStr)

        resultStr = self.MLJob_Convert3DMatrixToString(self.PreflightResultClassCentroidInputMean)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_INPUT_MEANS, resultStr)

        resultStr = self.MLJob_Convert2DMatrixToString(self.PreflightResultClassCentroidNumChildren)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_VALS_NUM_SATS, resultStr)

        resultStr = self.MLJob_Convert2DMatrixToString(self.PreflightResultClassCentroidPerMaxDistance)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_RESULT_CLASS_CENTROIDS_MAX_DISTANCE, resultStr)

        self.WriteResultClassWeightsToXML()
    # End - WritePreflightResultsToXML




    #####################################################
    #
    # [MLJob::ReadResultClassWeightsFromXML
    # 
    #####################################################
    def ReadResultClassWeightsFromXML(self):
        fDebug = False
        if (fDebug):
            print("ReadResultClassWeightsFromXML")

        # Find the existing list of class weights
        classWeightsListXMLNode = dxml.XMLTools_GetChildNode(self.ResultsPreflightXMLNode, RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT_LIST)
        if (classWeightsListXMLNode is None):
            return

        # Get the number of classes so we can easily rebuild the data structures when reading the job.
        self.NumResultClasses = dxml.XMLTools_GetChildNodeTextAsInt(classWeightsListXMLNode, 
                                                                    RESULTS_PREFLIGHT_NUM_RESULT_CLASSES, -1)

        # Make a new runtime object for each resultClass element
        self.PreflightResultClassDict = {}
        self.PreflightResultClassWeights = [0] * self.NumResultClasses

        # Read each resultClass
        resultClassXMLNode = dxml.XMLTools_GetChildNode(classWeightsListXMLNode, RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT)
        while (resultClassXMLNode is not None):
            resultClassID = dxml.XMLTools_GetChildNodeTextAsInt(resultClassXMLNode, 
                                                                RESULTS_PREFLIGHT_RESULT_CLASS_ID, -1)
            classWeight = dxml.XMLTools_GetChildNodeTextAsFloat(resultClassXMLNode, 
                                                                RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT_VALUE, -1)

            if ((resultClassID >= 0) and (classWeight >= 0)):
                self.PreflightResultClassWeights[resultClassID] = classWeight

                newResultClassInfo = {'weight': classWeight}
                self.PreflightResultClassDict[resultClassID] = newResultClassInfo
            # End - if ((resultClassID >= 0) and (resultClassID >= 0)):
        
            resultClassXMLNode = dxml.XMLTools_GetPeerNode(resultClassXMLNode, 
                                                            RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT)
        # End - while (resultClassXMLNode is not None):

        if (fDebug):
            print("ReadResultClassWeightsFromXML: self.PreflightResultClassWeights = " + str(self.PreflightResultClassWeights))
    # End - ReadResultClassWeightsFromXML




    #####################################################
    #
    # [MLJob::WriteResultClassWeightsToXML
    # 
    #####################################################
    def WriteResultClassWeightsToXML(self):
        # Make an empty list of resultClass weights
        classWeightsListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsPreflightXMLNode, 
                                                                    RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT_LIST)
        if (classWeightsListXMLNode is None):
            return
        dxml.XMLTools_RemoveAllChildNodes(classWeightsListXMLNode)

        # Save the number of classes so we can easily rebuild the data structures when reading the job.
        dxml.XMLTools_AddChildNodeWithText(classWeightsListXMLNode, 
                                            RESULTS_PREFLIGHT_NUM_RESULT_CLASSES, 
                                            str(self.NumResultClasses))

        # Make a new element for each resultClass weight
        for _, (resultClassID, resultClassInfo) in enumerate(self.PreflightResultClassDict.items()):
            resultClassXMLNode = dxml.XMLTools_AppendNewChildNode(classWeightsListXMLNode, 
                                                            RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT)

            classWeight = resultClassInfo['weight']
            dxml.XMLTools_AddChildNodeWithText(resultClassXMLNode, 
                                                RESULTS_PREFLIGHT_RESULT_CLASS_WEIGHT_VALUE, 
                                                str(classWeight))
            dxml.XMLTools_AddChildNodeWithText(resultClassXMLNode, 
                                                RESULTS_PREFLIGHT_RESULT_CLASS_ID, 
                                                str(resultClassID))
        # End - for _, (resultClassID, resultClassInfo) in enumerate(self.PreflightResultClassDict.items()):
    # End - WriteResultClassWeightsToXML





    #####################################################
    #
    # [MLJob::ReadTrainResultsFromXML
    # 
    #####################################################
    def ReadTrainResultsFromXML(self, parentXMLNode):
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

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, RESULTS_TRAINING_TOTAL_DEV_ELEMENT_NAME, "")
        self.TrainingTotalDevInputVar = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, RESULTS_TRAINING_STANDARD_DEV_ELEMENT_NAME, "")
        self.TrainingStdDevInputVar = MLJob_ConvertStringTo1DVector(resultStr)
    # End - ReadTrainResultsFromXML




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

        resultStr = MLJob_Convert1DVectorToString(self.TrainingTotalDevInputVar)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_TRAINING_TOTAL_DEV_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.TrainingStdDevInputVar)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_TRAINING_STANDARD_DEV_ELEMENT_NAME, resultStr)
    # End - WriteTrainResultsToXML





    #####################################################
    #
    # [MLJob::ReadTestResultsFromXML
    # 
    #####################################################
    def ReadTestResultsFromXML(self, parentXMLNode):
        # Every simple value (like <aa>5</aa>) is a named value in the result dict.
        self.TestResults = {}
        currentXMLNode = dxml.XMLTools_GetFirstChildNode(parentXMLNode)
        while (currentXMLNode is not None):
            if (dxml.XMLTools_IsLeafNode(currentXMLNode)):
                nameStr = dxml.XMLTools_GetElementName(currentXMLNode)
                valueStr = dxml.XMLTools_GetTextContents(currentXMLNode)
                #print("ReadGenericResultsFromXML. nameStr=" + nameStr + ", valueStr=" + valueStr)
                try:
                    self.TestResults[nameStr] = int(valueStr)
                except Exception:
                    self.TestResults[nameStr] = valueStr
            # End - if (dxml.XMLTools_IsLeafNode(currentXMLNode)):

            currentXMLNode = dxml.XMLTools_GetAnyPeerNode(currentXMLNode)
        # End - while (currentXMLNode is not None):


        self.NumSamplesTested = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                    RESULTS_NUM_ITEMS_ELEMENT_NAME, 0)
        self.ROCAUC = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                    RESULTS_ROCAUC_ELEMENT_NAME, 0)
        #print(">>> XMLTools_GetChildNodeTextAsFloat. self.ROCAUC = " + str(self.ROCAUC) + ", PathName=" + self.JobFilePathName)

        self.AUPRC = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                    RESULTS_AUPRC_ELEMENT_NAME, 0)
        self.F1Score = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                    RESULTS_F1Score_ELEMENT_NAME, 0)


        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, RESULTS_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumItemsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, RESULTS_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumPredictionsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, RESULTS_NUM_CORRECT_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumCorrectPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        self.OutputThreshold = self.GetOutputThreshold()
        self.LogisticResultsTrueValueList = []
        self.LogisticResultsPredictedProbabilityList = []
        if (self.IsLogisticNetwork):
            resultStr = dxml.XMLTools_GetChildNodeText(parentXMLNode, RESULTS_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME)
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
    # [MLJob::WriteTestResultsToXML
    # 
    #####################################################
    def WriteTestResultsToXML(self, parentXMLNode):
        for index, (valName, value) in enumerate(self.TestResults.items()):
            dxml.XMLTools_AddChildNodeWithText(parentXMLNode, valName, str(value))

        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_NUM_ITEMS_ELEMENT_NAME, 
                                                        str(self.NumSamplesTested))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_ROCAUC_ELEMENT_NAME, str(self.ROCAUC))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_AUPRC_ELEMENT_NAME, str(self.AUPRC))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_F1Score_ELEMENT_NAME, str(self.F1Score))

        resultStr = MLJob_Convert1DVectorToString(self.TestNumItemsPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.TestNumPredictionsPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.TestNumCorrectPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_NUM_CORRECT_PER_CLASS_ELEMENT_NAME, resultStr)


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
                dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RESULTS_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME, logisticOutputsStr)
        # End - if (self.IsLogisticNetwork):
    # End - WriteTestResultsToXML





    #####################################################
    # [MLJob::GetRunningAvgLossInCurrentEpoch
    #####################################################
    def GetRunningAvgLossInCurrentEpoch(self):
        if (self.NumTrainLossValuesCurrentEpoch > 0):
            avgLoss = float(self.TotalTrainingLossInCurrentEpoch / float(self.NumTrainLossValuesCurrentEpoch))
        else:
            avgLoss = 0.0
        return avgLoss
    # End - GetRunningAvgLossInCurrentEpoch



    #####################################################
    # [MLJob::SetJobFilePathName]
    #####################################################
    def SetJobFilePathName(self, name):
        self.JobFilePathName = name


    #####################################################
    # [MLJob::SetDebug]
    #####################################################
    def SetDebug(self, fDebug):
        self.Debug = fDebug
        dxml.XMLTools_SetChildNodeTextAsBool(self.JobControlXMLNode, "Debug", fDebug)
    # End - SetDebug


    #####################################################
    # [MLJob::RecordDebugEvent]
    #####################################################
    def RecordDebugEvent(self, name):
        if (self.Debug):
            self.DebugEvents.AddEvent(name)
    # End - RecordDebugEvent


    #####################################################
    # [MLJob::RecordDebugVal]
    #####################################################
    def RecordDebugVal(self, name, value):
        if (self.Debug):
            self.DebugEvents.AddValue(name, value)
    # End - RecordDebugVal


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
    # [MLJob::DrawDebugTimeline]
    #####################################################
    def DrawDebugTimeline(self, titleStr, eventNameList, filePath):
        # , DEBUG_EVENT_TIMELINE_CHUNK: "yellow"
        vertLineDict = {DEBUG_EVENT_TIMELINE_EPOCH: "red"}

        self.DebugEvents.DrawTimeline(titleStr, 
                                "",  # xLabelStr,
                                "",  # yLabelStr,
                                eventNameList, 
                                vertLineDict,
                                filePath)
    # End - DrawDebugTimeline




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
    # [MLJob::SetTrainingParamNumber]
    #####################################################
    def SetTrainingParamNumber(self, valName, newValue):
        dxml.XMLTools_SetChildNodeWithNumber(self.TrainingXMLNode, valName, newValue)

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
    def GetNumSequencesTested(self):
        return(self.NumSamplesTested)

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
    def GetTestResults(self):
        return self.TestResults

    #####################################################
    # [MLJob::GetTestNumItemsPerClass
    #####################################################
    def GetTestNumItemsPerClass(self):
        return self.TestNumItemsPerClass

    #####################################################
    # [MLJob::GetROCAUC
    #####################################################
    def GetROCAUC(self):
        #print(">>> GetROCAUC(). self.ROCAUC = " + str(self.ROCAUC) + ", PathName=" + self.JobFilePathName)
        return self.ROCAUC

    #####################################################
    # [MLJob::GetAUPRC
    #####################################################
    def GetAUPRC(self):
        return self.AUPRC

    #####################################################
    # [MLJob::GetF1Score
    #####################################################
    def GetF1Score(self):
        return self.F1Score

    #####################################################
    # [MLJob::GetTestNumCorrectPerClass
    #####################################################
    def GetTestNumCorrectPerClass(self):
        return self.TestNumCorrectPerClass

    #####################################################
    # [MLJob::GetTestNumPredictionsPerClass
    #####################################################
    def GetTestNumPredictionsPerClass(self):
        return self.TestNumPredictionsPerClass

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
    def GetLogisticResultsTrueValueList(self):
        return(self.LogisticResultsTrueValueList)

    #####################################################
    # [MLJob::GetLogisticResultsPredictedProbabilityList]
    #####################################################
    def GetLogisticResultsPredictedProbabilityList(self):
        return(self.LogisticResultsPredictedProbabilityList)


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
    # [MLJob::SetNetworkInputVarNames]
    #
    #####################################################
    def SetNetworkInputVarNames(self, newVal):
        inputLayerXMLNode = dxml.XMLTools_GetChildNode(self.NetworkLayersXMLNode, "InputLayer")
        if (inputLayerXMLNode is None):
            return

        dxml.XMLTools_AddChildNodeWithText(inputLayerXMLNode, "InputValues", newVal)
    # End of SetNetworkInputVarNames



    #####################################################
    #
    # [MLJob::SetNetworkOutputVarName]
    #
    #####################################################
    def SetNetworkOutputVarName(self, newVal):
        dxml.XMLTools_AddChildNodeWithText(self.NetworkLayersXMLNode, "ResultValue", newVal)
    # End of SetNetworkOutputVarName



    #####################################################
    #
    # [MLJob::SetLogFilePathname
    # 
    #####################################################
    def SetLogFilePathname(self, newPathName, addDateSuffix):
        if (addDateSuffix):
            now = datetime.now()
            timeStr = now.strftime("%Y-%m-%d_%H_%M")
            newPathName = newPathName + timeStr + ".txt"
            #print("SetLogFilePathname. Revised - newPathName=" + newPathName)
        # End - if (addDateSuffix)

        self.LogFilePathname = newPathName

        xmlNode = dxml.XMLTools_GetOrCreateChildNode(self.JobControlXMLNode, "LogFilePathname")
        if (xmlNode is None):
            return
        dxml.XMLTools_SetTextContents(xmlNode, newPathName)
    # End - SetLogFilePathname




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
    # [MLJob::SetFilterProperties]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def SetFilterProperties(self, newValue):
        self.SetDataParam("ValueFilter", newValue)
        return JOB_E_NO_ERROR
    # End - GetFilterProperties




    #####################################################
    #
    # [MLJob::IsTrainingOptionSet]
    #
    #####################################################
    def IsTrainingOptionSet(self, optionName):
        optionsStr = dxml.XMLTools_GetChildNodeTextAsStr(self.TrainingXMLNode, 
                                                TRAINING_OPTIONS_ELEMENT_NAME, "")
        optionsStr = optionsStr.lower()
        optionName = optionName.lower()
        if (optionName in optionsStr):
            return True

        return False
    # End of IsTrainingOptionSet




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
    job.InitNewJobImpl()
    
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







