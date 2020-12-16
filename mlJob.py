#####################################################################################
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
#####################################################################################
#
# This is designed to be INdependant of the specific Machine Learning library, so
# it should work equally well with PyTorch or other libraries. It does assume numpy,
# but that is common to most everythng.
#
#####################################################################################
#
##################
# JobControl
#
#   JobName - A string that identifies the job to a human
#
#   JobType - Basic
#
#   JobSpecVersion - Currently 1.0
#
#   Status - Pending, Running, Partial, Complete
#
#   DateRequested - In the format "yyyy:mm:dd hh:mm:ss"
#
#   Email - Email to a human who may be interested
#
#   SaveNetState - True/False
#
#   SavePrevResults - True/False
#
#   ResultReturnMechanism - { email, localFile, DropBox, ... >
#
#   ResultReturnAddress - emailAdddr
#
#   Debug - True/False, defaults to False
#
#   StressTest - True/False, defaults to False
#
#   PerfProfile - True/False, defaults to False
#
##################
# Data
#
#   DataFormat 
#       TDF
#
#   StoreType
#       File
#
#   TrainData - A file pathname
#
#   TestData - A file pathname
#
##################
# Request
#
#   NetworkType
#       TinyRNN
#       LSTM
#
#   NonLinearType
#       LogSoftmax
#
#   LossFunction
#       NLLLoss
#       BCELoss
#
#   Optimizer
#       SGD
#
#   LearningRate
#
#   HiddenLayerSize
#
#   NumEpochs
#
#   InputValues - A comma-separated list of variables, like "Age,Cr,SBP". 
#       See the TDFTools.py documentation for a list of defined names.
#       The value name appeats in a <D> element. 
#       For example, Hgb would extract data from the following <D> element:
#           <D C="L" T="100:10:30">Hgb=7.0,</D>
#
#       Each value may be followed by an offset in brackets
#       Examples: Cr[-1]   INR[next]
#       The number in brackets is the number of days from the current point in the timeline.
#       The offset "next" means the next occurrence.    
# 
#       The special value "Dose" is always followed by a "/" and then the name of a medication.
#       For example Dose/Coumadin is the dose of Coumadin given.
#       Doses may also have offsets. For example Dose/Coumadin[-1] is the dose of Coumadin given 1 day before.
# 
#   ResultValue - A variable name. See the TDFTools.py documentation.
#       Different variables have different interpretations as result values.
#       These include:
#           Number - A numeric value, which may be a dose or a lab value
#           FutureEventClass - A number 0-11. See the TDFTools.py documentation.
#           Binary - A number 0-1
#
#       FutureEventClass or BinaryDiagnosis will count the number of exact matches; the 
#           predicted class must exactly match the actual value.
#
#       Number will count buckets:
#           Exact (to 1 decimal place)
#           Within 2%
#           Within 5%
#           Within 10%
#           Within 25%
#
#   WindowStartEvent
#   WindowStopEvent
#
#   ClipNumTrainPatients - Used only for debugging
#   ClipNumTestPatients - Used only for debugging
#
##################
# ResultList
#
#   A series of <Results> elements
#
##################
# Results
#
#   StartRequestTimeStr
#
#   StartRequestTimeInSeconds
#
#   StopRequestTimeStr
#
#   StopRequestTimeInSeconds
#
#   CurrentEpochNum
#
#   NumSequencesTrainedPerEpoch
#
#   NumSequencesTested
#
#   NumCorrectPredictionsInTesting
#   NumPredictionsWithin2PercentInTesting
#   NumPredictionsWithin5PercentInTesting
#   NumPredictionsWithin10PercentInTesting
#   NumPredictionsWithin20PercentInTesting
#
#   TrainAvgLossPerEpoch
#
#   TrainNumItemsPerClass
#
#   TestNumItemsPerClass
#
#   Used for binary and class results.
#       NumTruePositivesInTesting
#       NumFalsePositivesInTesting
#       NumTrueNegativesInTesting
#       NumFalseNegativesInTesting
#
#   OS
#   CPU
#   GPU
#
##################
# Runtime
#   The runtime state for the Job object. This is state in the middle of a single
#   job execution.
#
##################
# NeuralNetMatrixListXMLNode
#   The runtime weight matrices and bias vectors for a network.
#   This allows a network to suspend and then later resume its state, possibly in a 
#   different process or a different server.
#
##################
# NeuralNetGradientListXMLNode
#   This is similar to NeuralNetMatrixListXMLNode, except it holds the gradients resulting 
#   from a series of training steps. This is the return value of a remote training session.
#
##################
# TestList
#
#   A list of test elements, each of thich can contain different inputs and outputs.
#   This is very unstructured, and its use depends on the individual tests.
#
#####################################################################################
#Example:
#
# <?xml version="1.0" ?>
# <MLJob>
#     <JobControl>
#         <JobName>myJov</JobName>
#         <JobType>Basic</JobType>
#         <JobSpecVersion>1.0</JobSpecVersion>
#         <Status>Pending</Status>
#         <DateRequested>2020:09:13</DateRequested>
#         <Email>dfdean3@gmail.com</Email>
#         <ResultReturnMechanism>email</ResultReturnMechanism>
#         <ResultReturnAddress>foo@emailAddress.com</ResultReturnAddress>
#         <SaveNetState>True</SaveNetState>
#         <Debug>True</Debug>
#         <StressTest>False</StressTest>
#         <PerfProfile>False</PerfProfile>
#     </JobControl>
# 
#     <Data>
#         <DataFormat>TDF</DataFormat>
#         <StoreType>File</StoreType>
#         <TrainData>/home/ddean/dLargeData/mlData/UKData/UKHospitalOutcomesTrain.tdf</TrainData>
#         <TestData>/home/ddean/dLargeData/mlData/UKData/UKHospitalOutcomesTest.tdf</TestData>
#     </Data>
# 
#     <Request>
#         <NetworkType>SimpleNet</NetworkType>
#         <NonLinearType>LogSoftmax</NonLinearType>
#         <LossFunction>NLLLoss</LossFunction>
#         <Optimizer>SGD</Optimizer>
#         <LearningRate>0.01</LearningRate>
# 
#         <NumEpochs>1</NumEpochs>
#         <ClipNumTrainPatients>100</ClipNumTrainPatients>
#         <ClipNumTestPatients>100</ClipNumTestPatients>
# 
#         <WindowStartEvent></WindowStartEvent>
#         <WindowStopEvent></WindowStopEvent>
# 
#         <InputValues>Dose/Coumadin,INR,Dose/Coumadin[-1],INR[-1],Dose/Coumadin[-3],INR[-3]</InputValues>
# 
#         <ResultValue>INR[next]</ResultValue>
#     </Request>
# 
#     <ResultList>
#     </ResultList>
# 
#     <TestList>
#     </TestList>
# 
# </MLJob>
# 
#####################################################################################

import os
import sys
import string
import time
import re
from datetime import datetime
import platform
import numpy

# Normally we have to set the search path to load these.
# But, this .py file is always in the same directories as these imported modules.
from xmlTools import *
from tdfTools import *  # Needed for constants.

import xml.dom
import xml.dom.minidom
from xml.dom.minidom import parse, parseString, getDOMImplementation

NEWLINE_STR = "\n"
RESULT_SECTION_SEPARATOR_STR = "-------------------------"

MLJOB_LOG_NODE_ELEMENT_NAME = "Log"

ML_JOB_NUM_NUMERIC_VALUE_BUCKETS = 20



################################################################################
#
# [MLJobLowLevelLogImpl]
#
# This is only called when there is not a valid job object to log to.
################################################################################
def MLJobLowLevelLogImpl(message):
    print(message)
# End - MLJobLowLevelLogImpl





################################################################################
################################################################################
class MLJob():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.jobFilePathName = ""

        # These are the sections of the JOB spec
        self.JobXMLDOM = None
        self.RootXMLNode = None
        self.JobControlXMLNode = None
        self.DataXMLNode = None
        self.RequestXMLNode = None
        self.ResultsXMLNode = None
        self.RuntimeXMLNode = None
        self.TestListXMLNode = None
        self.NeuralNetMatrixListXMLNode = None
        self.NeuralNetGradientListXMLNode = None

        self.DebugMode = False
        self.ResetRuntimeStateImpl()
    # End -  __init__




    #####################################################
    #
    # [MLJob::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return
    # End of destructor




    #####################################################
    #
    # [MLJob::InitNewJobImpl]
    #
    #####################################################
    def InitNewJobImpl(self):
        impl = getDOMImplementation()
        self.JobXMLDOM = impl.createDocument(None, "MLJob", None)
        self.RootXMLNode = self.JobXMLDOM.getElementsByTagName("MLJob")[0]

        self.JobControlXMLNode = self.JobXMLDOM.createElement("JobControl")
        self.RootXMLNode.appendChild(self.JobControlXMLNode)

        self.DataXMLNode = self.JobXMLDOM.createElement("Data")
        self.RootXMLNode.appendChild(self.DataXMLNode)

        self.RequestXMLNode = self.JobXMLDOM.createElement("Request")
        self.RootXMLNode.appendChild(self.RequestXMLNode)

        self.ResultsXMLNode = self.JobXMLDOM.createElement("Results")
        self.RootXMLNode.appendChild(self.ResultsXMLNode)

        self.RuntimeXMLNode = self.JobXMLDOM.createElement("Runtime")
        self.RootXMLNode.appendChild(self.RuntimeXMLNode)

        self.TestListXMLNode = self.JobXMLDOM.createElement("TestList")
        self.RootXMLNode.appendChild(self.TestListXMLNode)

        self.NeuralNetMatrixListXMLNode = self.JobXMLDOM.createElement("NeuralNetMatrixList")
        self.RootXMLNode.appendChild(self.NeuralNetMatrixListXMLNode)

        self.NeuralNetGradientListXMLNode = self.JobXMLDOM.createElement("NeuralNetGradientList")
        self.RootXMLNode.appendChild(self.NeuralNetGradientListXMLNode)

        self.ResultValueType = TDF_DATA_TYPE_FLOAT
        self.MinNumberResultVal = 0
        self.MaxNumberResultVal = 0
        self.ResultNumberBucketSize = 1.0
    # End of InitNewJobImpl





    #####################################################
    #
    # [MLJob::ReadJobFromString]
    #
    #####################################################
    def ReadJobFromString(self, jobString):
        #print("MLJob::ReadJobFromString")

        ###############
        # Parse the text string into am XML DOM
        try:
            self.JobXMLDOM = parseString(jobString)
        except xml.parsers.expat.ExpatError as err:
            MLJobLowLevelLogImpl("MLJob::ReadJobFromString. Error from parsing string:")
            MLJobLowLevelLogImpl("ExpatError:" + str(err))
            MLJobLowLevelLogImpl("Job=[" + jobString + "]")
            return
        except:
            MLJobLowLevelLogImpl("MLJob::ReadJobFromString. Error from parsing string:")
            MLJobLowLevelLogImpl("Job=[" + jobString + "]")
            MLJobLowLevelLogImpl("Unexpected error:", sys.exc_info()[0])
            return

        ###############
        try:
            self.RootXMLNode = self.JobXMLDOM.getElementsByTagName("MLJob")[0]
        except:
            MLJobLowLevelLogImpl("MLJob::ReadJobFromString. Required elements are missing: [" + jobString + "]")
            return

        ###############
        try:
            self.JobControlXMLNode = self.JobXMLDOM.getElementsByTagName("JobControl")[0]
        except:
            # If this is missing, then create it.
            self.JobControlXMLNode = self.JobXMLDOM.createElement("JobControl")
            self.RootXMLNode.appendChild(self.JobControlXMLNode)

        ###############
        try:
            self.DataXMLNode = self.JobXMLDOM.getElementsByTagName("Data")[0]
        except:
            # If this is missing, then create it.
            self.DataXMLNode = self.JobXMLDOM.createElement("Data")
            self.RootXMLNode.appendChild(self.DataXMLNode)

        ###############
        try:
            self.RequestXMLNode = self.JobXMLDOM.getElementsByTagName("Request")[0]
        except:
            # If this is missing, then create it.
            self.RequestXMLNode = self.JobXMLDOM.createElement("Request")
            self.RootXMLNode.appendChild(self.RequestXMLNode)

        ###############
        try:
            self.ResultsXMLNode = self.JobXMLDOM.getElementsByTagName("Results")[0]
        except:
            # If this is missing, then create it.
            self.ResultsXMLNode = self.JobXMLDOM.createElement("Results")
            self.RootXMLNode.appendChild(self.ResultsXMLNode)

        ###############
        try:
            self.RuntimeXMLNode = self.JobXMLDOM.getElementsByTagName("Runtime")[0]
        except:
            # If this is missing, then create it.
            self.RuntimeXMLNode = self.JobXMLDOM.createElement("Runtime")
            self.RootXMLNode.appendChild(self.RuntimeXMLNode)

        ###############
        try:
            self.TestListXMLNode = self.JobXMLDOM.getElementsByTagName("TestList")[0]
        except:
            # If this is missing, then create it.
            self.TestListXMLNode = self.JobXMLDOM.createElement("TestList")
            self.RootXMLNode.appendChild(self.TestListXMLNode)

        ###############
        try:
            self.NeuralNetMatrixListXMLNode = self.JobXMLDOM.getElementsByTagName("NeuralNetMatrixList")[0]
        except:
            # If this is missing, then create it.
            self.NeuralNetMatrixListXMLNode = self.JobXMLDOM.createElement("NeuralNetMatrixList")
            self.RootXMLNode.appendChild(self.NeuralNetMatrixListXMLNode)

        ###############
        try:
            self.NeuralNetGradientListXMLNode = self.JobXMLDOM.getElementsByTagName("NeuralNetGradientList")[0]
        except:
            # If this is missing, then create it.
            self.NeuralNetGradientListXMLNode = self.JobXMLDOM.createElement("NeuralNetGradientList")
            self.RootXMLNode.appendChild(self.NeuralNetGradientListXMLNode)


        self.DebugMode = False
        xmlNode = XMLTools_GetChildNode(self.JobControlXMLNode, "DebugMode")
        if (xmlNode != None):
            resultStr = XMLTools_GetTextContents(xmlNode)
            resultStr = resultStr.lower()
            resultStr = resultStr.lstrip()
            if ((resultStr == "on") or (resultStr == "true") or (resultStr == "yes") or (resultStr == "1")):
                self.DebugMode = True

        # Optionally, read any runtime if it is present. No error if it is missing.
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

        # Figure out the result value type.
        self.GetResultInfoImpl()
    # End of ReadJobFromString






    #####################################################
    #
    # [MLJob::WriteJobToString]
    #
    #####################################################
    def WriteJobToString(self, fIncludeRuntime):
        # Optionally, write the current runtime to a temporary node that is just used for 
        # holding an incomplete request that is currently executing
        #
        # This is used when sending jobs between a dispatcher process and a
        # child worker process, and is not normally stored in a file. It could
        # be saved to a file if we ever want to "suspend" runtime state and
        # resume it at a later date, but that is not supported now and would
        # raise some tricky synchronization issues.
        if (fIncludeRuntime):
            try:
                self.RuntimeXMLNode = self.JobXMLDOM.getElementsByTagName("Runtime")[0]
            except:
                self.RuntimeXMLNode = self.JobXMLDOM.createElement("Runtime")
                self.RootXMLNode.appendChild(self.RuntimeXMLNode)
            self.SaveRuntimeToXML(self.RuntimeXMLNode)
        # End - if (fIncludeRuntime):

        # Don't add indentation or newlines. Those accumulate each time
        # the XML is serialized/deserialized, so for a large job the whitespace
        # grows to dwarf the actual content.        
        resultStr = self.JobXMLDOM.toprettyxml(indent="", newl="", encoding=None)
        #resultStr = resultStr.replace("\n", "")
        #resultStr = resultStr.replace("\r", "")
        #resultStr = resultStr.replace("   ", "")
        #resultStr = resultStr.replace("  ", "")

        return resultStr
    # End of WriteJobToString





    #####################################################
    #
    # [MLJob::ResetRuntimeStateImpl
    # 
    #####################################################
    def ResetRuntimeStateImpl(self):
        self.StartRequestTimeStr = ""
        self.StartRequestTimeInSeconds = 0
        self.StopRequestTimeStr = ""
        self.StopRequestTimeInSeconds = 0
        self.StartTrainingTimeStr = ""
        self.StopTrainingTimeStr = ""
        self.StartTestingTimeStr = ""
        self.StopTestingTimeStr = ""

        self.CurrentEpochNum = 0
        self.NumSequencesTrainedPerEpoch = 0
        self.NumSequencesTested = 0

        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.AvgLossPerEpochList = []

        self.NumCorrectPredictionsInTesting = 0
        self.NumPredictionsWithin2PercentInTesting = 0
        self.NumPredictionsWithin5PercentInTesting = 0
        self.NumPredictionsWithin10PercentInTesting = 0
        self.NumPredictionsWithin20PercentInTesting = 0

        self.TrainNumItemsPerClass = []
        self.TestNumItemsPerClass = []

        self.NumTruePositivesInTesting = []
        self.NumFalsePositivesInTesting = []
        self.NumTrueNegativesInTesting = []
        self.NumFalseNegativesInTesting = []

        self.BufferedLogLines = ""

        self.DebugMode = False
        xmlNode = XMLTools_GetChildNode(self.JobControlXMLNode, "DebugMode")
        if (xmlNode != None):
            resultStr = XMLTools_GetTextContents(xmlNode)
            resultStr = resultStr.lower()
            resultStr = resultStr.lstrip()
            if ((resultStr == "on") or (resultStr == "true") or (resultStr == "yes") or (resultStr == "1")):
                self.DebugMode = True
    # End -  ResetRuntimeStateImpl







    #####################################################
    #
    # [MLJob::ReadRuntimeFromXML]
    #
    #####################################################
    def ReadRuntimeFromXML(self, parentXMLNode):
        # Optionally, read any runtime if it is present.
        # This is only used when sending jobs between a dispatcher process and a
        # child worker process, and is not normally stored in a file. It could
        # be saved to a file if we ever want to "suspend" runtime state and
        # resume it at a later date, but that is not supported now and would
        # raise some tricky synchronization issues.
        #
        # These are all optional. No error if any are missing.
        try:
            self.StartRequestTimeStr = XMLTools_GetChildNodeText(parentXMLNode, "StartRequestTimeStr")
        except:
            pass
        try:
            self.StartRequestTimeInSeconds = int(XMLTools_GetChildNodeText(parentXMLNode, "StartRequestTimeInSeconds"))
        except:
            pass
        try:
            self.StopRequestTimeStr = XMLTools_GetChildNodeText(parentXMLNode, "StopRequestTimeStr")
        except:
            pass
        try:
            self.StopRequestTimeInSeconds = int(XMLTools_GetChildNodeText(parentXMLNode, "StopRequestTimeInSeconds"))
        except:
            pass
        try:
            self.StartTrainingTimeStr = XMLTools_GetChildNodeText(parentXMLNode, "StartTrainingTimeStr")
        except:
            pass
        try:
            self.StopTrainingTimeStr = XMLTools_GetChildNodeText(parentXMLNode, "StopTrainingTimeStr")
        except:
            pass
        try:
            self.StartTestingTimeStr = XMLTools_GetChildNodeText(parentXMLNode, "StartTestingTimeStr")
        except:
            pass
        try:
            self.StopTestingTimeStr = XMLTools_GetChildNodeText(parentXMLNode, "StopTestingTimeStr")
        except:
            pass
        try:
            self.CurrentEpochNum = int(XMLTools_GetChildNodeText(parentXMLNode, "CurrentEpochNum"))
        except:
            pass
        try:
            self.NumSequencesTrainedPerEpoch = int(XMLTools_GetChildNodeText(parentXMLNode, "NumSequencesTrainedPerEpoch"))
        except:
            pass
        try:
            self.NumSequencesTested = int(XMLTools_GetChildNodeText(parentXMLNode, "NumSequencesTested"))
        except:
            pass

        try:
            self.TotalTrainingLossInCurrentEpoch = float(XMLTools_GetChildNodeText(parentXMLNode, "TotalTrainingLossInCurrentEpoch"))
        except:
            pass


        #################
        self.AvgLossPerEpochList = []
        resultStr = XMLTools_GetChildNodeText(parentXMLNode, "TrainAvgLossPerEpoch")
        resultArray = resultStr.split(",")
        for avgLossStr in resultArray:
            try:
                avgLossFloat = float(avgLossStr)
                avgLossFloat = round(avgLossFloat, 4)
                self.AvgLossPerEpochList.append(avgLossFloat)
            except:
                continue

        #################
        self.NumCorrectPredictionsInTesting = 0
        self.NumPredictionsWithin2PercentInTesting = 0
        self.NumPredictionsWithin5PercentInTesting = 0
        self.NumPredictionsWithin10PercentInTesting = 0
        self.NumPredictionsWithin20PercentInTesting = 0
        try:
            self.NumCorrectPredictionsInTesting = int(XMLTools_GetChildNodeText(parentXMLNode, "NumCorrectPredictionsInTesting"))
        except:
            pass
        try:
            self.NumPredictionsWithin2PercentInTesting = int(XMLTools_GetChildNodeText(parentXMLNode, "NumPredictionsWithin2PercentInTesting"))
        except:
            pass
        try:
            self.NumPredictionsWithin5PercentInTesting = int(XMLTools_GetChildNodeText(parentXMLNode, "NumPredictionsWithin5PercentInTesting"))
        except:
            pass
        try:
            self.NumPredictionsWithin10PercentInTesting = int(XMLTools_GetChildNodeText(parentXMLNode, "NumPredictionsWithin10PercentInTesting"))
        except:
            pass
        try:
            self.NumPredictionsWithin20PercentInTesting = int(XMLTools_GetChildNodeText(parentXMLNode, "NumPredictionsWithin20PercentInTesting"))
        except:
            pass

        #################
        self.TrainNumItemsPerClass = []
        resultStr = XMLTools_GetChildNodeText(parentXMLNode, "TrainNumItemsPerClass")
        countArray = resultStr.split(",")
        for numItems in countArray:
            try:
                self.TrainNumItemsPerClass.append(int(numItems))
            except:
                continue

        #################
        self.TestNumItemsPerClass = []
        resultStr = XMLTools_GetChildNodeText(parentXMLNode, "TestNumItemsPerClass")
        countArray = resultStr.split(",")
        for numItems in countArray:
            try:
                self.TestNumItemsPerClass.append(int(numItems))
            except:
                continue

        #################
        self.NumTruePositivesInTesting = []
        try:
            resultStr = XMLTools_GetChildNodeText(parentXMLNode, "NumTruePositivesInTesting")
            countArray = resultStr.split(",")
            for numItems in countArray:
                try:
                    self.NumTruePositivesInTesting.append(int(numItems))
                except:
                    continue
        except:
            pass

        #################
        self.NumFalseNegativesInTesting = []
        try:
            resultStr = XMLTools_GetChildNodeText(parentXMLNode, "NumFalseNegativesInTesting")
            countArray = resultStr.split(",")
            for numItems in countArray:
                try:
                    self.NumFalseNegativesInTesting.append(int(numItems))
                except:
                    continue
        except:
            pass

        #################
        self.NumTrueNegativesInTesting = []
        try:
            resultStr = XMLTools_GetChildNodeText(parentXMLNode, "NumTrueNegativesInTesting")
            countArray = resultStr.split(",")
            for numItems in countArray:
                try:
                    self.NumTrueNegativesInTesting.append(int(numItems))
                except:
                    continue
        except:
            pass

        #################
        self.NumFalsePositivesInTesting = []
        try:
            resultStr = XMLTools_GetChildNodeText(parentXMLNode, "NumFalsePositivesInTesting")
            countArray = resultStr.split(",")
            for numItems in countArray:
                try:
                    self.NumFalsePositivesInTesting.append(int(numItems))
                except:
                    continue
        except:
            pass


        #################
        try:
            self.BufferedLogLines = XMLTools_GetChildNodeText(parentXMLNode, MLJOB_LOG_NODE_ELEMENT_NAME)
        except:
            pass
    # End - ReadRuntimeFromXML






    #####################################################
    #
    # [MLJob::SaveRuntimeToXML]
    #
    #####################################################
    def SaveRuntimeToXML(self, parentXMLNode):
        XMLTools_RemoveAllChildNodes(parentXMLNode)

        XMLTools_AddChildNodeWithText(parentXMLNode, "StartRequestTimeStr", str(self.StartRequestTimeStr))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StartRequestTimeInSeconds", str(self.StartRequestTimeInSeconds))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StopRequestTimeStr", str(self.StopRequestTimeStr))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StopRequestTimeInSeconds", str(self.StopRequestTimeInSeconds))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StartTrainingTimeStr", str(self.StartTrainingTimeStr))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StopTrainingTimeStr", str(self.StopTrainingTimeStr))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StartTestingTimeStr", str(self.StartTestingTimeStr))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StopTestingTimeStr", str(self.StopTestingTimeStr))

        XMLTools_AddChildNodeWithText(parentXMLNode, "CurrentEpochNum", str(self.CurrentEpochNum))
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumSequencesTrainedPerEpoch", str(self.NumSequencesTrainedPerEpoch))
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumSequencesTested", str(self.NumSequencesTested))

        ###################
        XMLTools_AddChildNodeWithText(parentXMLNode, "TotalTrainingLossInCurrentEpoch", str(self.TotalTrainingLossInCurrentEpoch))
        resultStr = ""
        for avgLoss in self.AvgLossPerEpochList:
            avgLoss = round(avgLoss, 4)
            resultStr = resultStr + str(avgLoss) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "TrainAvgLossPerEpoch", resultStr)

        ###################
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumCorrectPredictionsInTesting", str(self.NumCorrectPredictionsInTesting))
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumPredictionsWithin2PercentInTesting", str(self.NumPredictionsWithin2PercentInTesting))
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumPredictionsWithin5PercentInTesting", str(self.NumPredictionsWithin5PercentInTesting))
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumPredictionsWithin10PercentInTesting", str(self.NumPredictionsWithin10PercentInTesting))
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumPredictionsWithin20PercentInTesting", str(self.NumPredictionsWithin20PercentInTesting))

        ###################
        resultStr = ""
        for numItemsInClass in self.TrainNumItemsPerClass:
            resultStr = resultStr + str(numItemsInClass) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "TrainNumItemsPerClass", resultStr)

        ###################
        resultStr = ""
        for numItemsInClass in self.TestNumItemsPerClass:
            resultStr = resultStr + str(numItemsInClass) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "TestNumItemsPerClass", resultStr)

        ###################
        resultStr = ""
        for numItemsInClass in self.NumTruePositivesInTesting:
            resultStr = resultStr + str(numItemsInClass) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumTruePositivesInTesting", resultStr)

        ###################
        XMLTools_AddChildNodeWithText(parentXMLNode, "", str(self.NumFalseNegativesInTesting))
        resultStr = ""
        for numItemsInClass in self.NumFalseNegativesInTesting:
            resultStr = resultStr + str(numItemsInClass) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumFalseNegativesInTesting", resultStr)

        ###################
        resultStr = ""
        for numItemsInClass in self.NumTrueNegativesInTesting:
            resultStr = resultStr + str(numItemsInClass) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumTrueNegativesInTesting", resultStr)

        ###################
        resultStr = ""
        for numItemsInClass in self.NumFalsePositivesInTesting:
            resultStr = resultStr + str(numItemsInClass) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumFalsePositivesInTesting", resultStr)


        ###################
        XMLTools_AddChildNodeWithText(parentXMLNode, "OS", str(platform.platform()))
        XMLTools_AddChildNodeWithText(parentXMLNode, "CPU", str(platform.processor()))
        XMLTools_AddChildNodeWithText(parentXMLNode, "GPU", "None")

        # If there is a log string, then add it to the end of the Result node.
        if (self.BufferedLogLines != ""):
            logXMLNode = XMLTools_GetChildNode(parentXMLNode, MLJOB_LOG_NODE_ELEMENT_NAME)
            if (logXMLNode == None):
                logXMLNode = self.JobXMLDOM.createElement(MLJOB_LOG_NODE_ELEMENT_NAME)
                parentXMLNode.appendChild(logXMLNode)
            XMLTools_SetTextContents(logXMLNode, self.BufferedLogLines)
        # End - if (self.BufferedLogLines != "")
    # End -  SaveRuntimeToXML






    #####################################################
    #
    # [MLJob::ReadJobFromFile]
    #
    #####################################################
    def ReadJobFromFile(self, jobFilePathName):
        self.jobFilePathName = jobFilePathName
        fileH = open(self.jobFilePathName, "r")
        contentsText = fileH.read()
        fileH.close()

        self.ReadJobFromString(contentsText)
    # End of ReadJobFromFile




    #####################################################
    #
    # [MLJob::SaveAs]
    #
    #####################################################
    def SaveAs(self, jobFilePathName):
        #print("MLJob::SaveAs. Path=" + jobFilePathName)

        contentsText = self.WriteJobToString(True)
        #print("MLJob::SaveAs. contentsText=" + contentsText)

        fileH = open(jobFilePathName, "w")
        #print("MLJob::SaveAs. Opened file. fileH=" + str(fileH))

        numCharsWritten = fileH.write(contentsText)
        #print("MLJob::SaveAs. Finished write. numCharsWritten=" + str(numCharsWritten))

        fileH.close()
    # End of SaveAs





    #####################################################
    #
    # [MLJob::Log]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def Log(self, messageStr):
        now = datetime.now()
        timeStr = now.strftime("%Y-%m-%d %H:%M:%S")
        completeLogLine = timeStr + " " + messageStr + NEWLINE_STR
        self.BufferedLogLines = self.BufferedLogLines + completeLogLine

        #print(messageStr)
    # End of Log





    #####################################################
    #
    # [MLJob::GetResultInfoImpl
    # 
    #####################################################
    def GetResultInfoImpl(self):
        self.ResultValueType = TDF_DATA_TYPE_INT
        self.MinNumberResultVal = 0
        self.MaxNumberResultVal = 0
        self.ResultNumberBucketSize = 1.0

        # Figure out the result value type.
        try:
            resultValName = XMLTools_GetChildNodeText(self.RequestXMLNode, "ResultValue")
        except:
            resultValName = "number"

        self.ResultValueType = TDF_GetVariableType(resultValName)
        if ((self.ResultValueType == TDF_DATA_TYPE_INT) or (self.ResultValueType == TDF_DATA_TYPE_FLOAT)):
            self.MinNumberResultVal, self.MaxNumberResultVal = TDF_GetMinMaxValuesForVariable(resultValName)
            range = float(self.MaxNumberResultVal - self.MinNumberResultVal)
            self.ResultNumberBucketSize = float(range) / float(ML_JOB_NUM_NUMERIC_VALUE_BUCKETS)
    # End - GetResultInfoImpl





    #####################################################
    #
    # [MLJob::StartJobExecution]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartJobExecution(self):
        # Discard Previous results
        XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)

        # Each request has a single test. When we finish the test, we have
        # finished the entire reqeust.
        self.SetJobControlStr("Status", "Pending")
        self.SetJobControlStr("Error", "None")

        now = datetime.now()
        self.StartRequestTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")

        self.StartRequestTimeInSeconds = time.time()
    # End of StartJobExecution




    #####################################################
    #
    # [MLJob::FinishJobExecution]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishJobExecution(self, fSuccess, errorMsg):
        # Each request has a single test. When we finish the test, we have
        # finished the entire reqeust.
        if (fSuccess):
            self.SetJobControlStr("Status", "OK")
            self.SetJobControlStr("Error", "")
        else:
            self.SetJobControlStr("Status", "Error")
            self.SetJobControlStr("Error", errorMsg)

        now = datetime.now()
        self.StopRequestTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")
        self.StopRequestTimeInSeconds = time.time()

        # Remove earlier results
        XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)

        # Save the runtime state
        self.SaveRuntimeToXML(self.ResultsXMLNode)
    # End of FinishJobExecution





    #####################################################
    #
    # [MLJob::StartTraining
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartTraining(self):
        now = datetime.now()
        self.StartTrainingTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")

        self.CurrentEpochNum = 0
        self.NumSequencesTrainedPerEpoch = 0

        self.AvgLossPerEpochList = []
        self.TotalTrainingLossInCurrentEpoch = 0.0

        if ((self.ResultValueType == TDF_DATA_TYPE_INT) or (self.ResultValueType == TDF_DATA_TYPE_FLOAT)):
            numClasses = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS
        elif (self.ResultValueType == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            numClasses = TDF_NUM_CATEGORIES_IN_FUTURE_VAL
        elif (self.ResultValueType == TDF_DATA_TYPE_BOOL):
            numClasses = 2
        else:
            numClasses = 1

        self.TrainNumItemsPerClass = [0] * numClasses
        self.NumTruePositivesInTraining = [0] * numClasses
        self.NumFalseNegativesInTraining = [0] * numClasses
        self.NumTrueNegativesInTraining = [0] * numClasses
        self.NumFalsePositivesInTraining = [0] * numClasses
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
    # End - StartTrainingEpoch




    #####################################################
    #
    # [MLJob::FinishTrainingEpoch
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishTrainingEpoch(self):
        if (self.NumSequencesTrainedPerEpoch > 0):
            avgLoss = float(self.TotalTrainingLossInCurrentEpoch / float(self.NumSequencesTrainedPerEpoch))
        else:
            avgLoss = 0.0
        self.AvgLossPerEpochList.append(avgLoss)

        self.CurrentEpochNum += 1
    # End -  FinishTrainingEpoch




    #####################################################
    #
    # [MLJob::RecordTrainingLoss
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def RecordTrainingLoss(self, loss):
        if (self.CurrentEpochNum == 0):
            self.NumSequencesTrainedPerEpoch += 1
        self.TotalTrainingLossInCurrentEpoch += loss
    # End -  RecordTrainingLoss




    #####################################################
    #
    # [MLJob::RecordTrainingResult
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def RecordTrainingResult(self, actualValue, predictedValue):
        # We only record the stats on the first epoch.
        if (self.CurrentEpochNum == 0):
            #####################
            if (self.ResultValueType == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
                self.TrainNumItemsPerClass[int(actualValue)] += 1

            #####################
            elif (self.ResultValueType == TDF_DATA_TYPE_BOOL):
                self.TrainNumItemsPerClass[actualValue] += 1

            #####################
            elif ((self.ResultValueType == TDF_DATA_TYPE_INT) or (self.ResultValueType == TDF_DATA_TYPE_FLOAT)):
                offset = actualValue - self.MinNumberResultVal
                bucketNum = int(offset / self.ResultNumberBucketSize)
                if (bucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                    bucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
                self.TrainNumItemsPerClass[bucketNum] += 1
    # End -  RecordTrainingResult




    #####################################################
    #
    # [MLJob::FinishTraining
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishTraining(self):
        now = datetime.now()
        self.StopTrainingTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")
    # End - FinishTraining





    #####################################################
    #
    # [MLJob::PrintTrainingStats
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def PrintTrainingStats(self):
        indentStr = "   "

        print(" ")
        jobNameStr = self.GetRequestValueStr("JobName", "")
        if (jobNameStr != ""):
            print(jobNameStr)
        print(" ")
        print("Training Results:")
        print(RESULT_SECTION_SEPARATOR_STR)
        print("Start Training: " + self.StartTrainingTimeStr)
        print("Complete Training: " + self.StopTrainingTimeStr)

        ##############
        print(" ")
        print("Each Epoch contains:")
        print(indentStr + "Num Sequences: " + str(self.NumSequencesTrainedPerEpoch))
        print(" ")
        resultStr = ""
        for avgLoss in self.AvgLossPerEpochList:
            avgLoss = round(avgLoss, 4)
            resultStr = resultStr + " " + str(avgLoss)
        print(indentStr + "Average Losses Per Epoch: " + resultStr)

        ##############
        print(" ")
        resultStr = ""
        bucketStartValue = self.MinNumberResultVal
        bucketStopValue =  bucketStartValue + self.ResultNumberBucketSize
        for numItems in self.TrainNumItemsPerClass:
            bucketStartValue = round(bucketStartValue, 2)
            bucketStopValue = round(bucketStopValue, 2)

            resultStr = resultStr + indentStr + indentStr
            resultStr = resultStr + "[" + str(bucketStartValue) + " - " + str(bucketStopValue) + "]:    " 
            resultStr = resultStr + str(numItems) + NEWLINE_STR

            bucketStartValue +=  self.ResultNumberBucketSize
            bucketStopValue +=  self.ResultNumberBucketSize

        print(indentStr + "Num Items in Each Event Class: \n" + resultStr)
    # End - PrintTrainingStats





    #####################################################
    #
    # [MLJob::StartTesting
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartTesting(self):
        now = datetime.now()
        self.StartTestingTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")

        self.NumSequencesTested = 0

        self.NumCorrectPredictionsInTesting = 0
        self.NumPredictionsWithin2PercentInTesting = 0
        self.NumPredictionsWithin5PercentInTesting = 0
        self.NumPredictionsWithin10PercentInTesting = 0
        self.NumPredictionsWithin20PercentInTesting = 0

        if ((self.ResultValueType == TDF_DATA_TYPE_INT) or (self.ResultValueType == TDF_DATA_TYPE_FLOAT)):
            numClasses = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS
        elif (self.ResultValueType == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            numClasses = TDF_NUM_CATEGORIES_IN_FUTURE_VAL
        elif (self.ResultValueType == TDF_DATA_TYPE_BOOL):
            numClasses = 1
        else:
            numClasses = 1

        self.TestNumItemsPerClass = [0] * numClasses
        self.NumTruePositivesInTesting = [0] * numClasses
        self.NumFalseNegativesInTesting = [0] * numClasses
        self.NumTrueNegativesInTesting = [0] * numClasses
        self.NumFalsePositivesInTesting = [0] * numClasses
    # End - StartTesting





    #####################################################
    #
    # [MLJob::RecordTestingResult
    # 
    # This is a public procedure, it is called by the client.
    #
    #####################################################
    def RecordTestingResult(self, actualValue, predictedValue):
        self.NumSequencesTested += 1

        #########################
        if ((self.ResultValueType == TDF_DATA_TYPE_INT) or (self.ResultValueType == TDF_DATA_TYPE_FLOAT)):
            difference = actualValue - predictedValue
            if (difference < 0):
                difference = -difference

            if (difference == 0):
                self.NumCorrectPredictionsInTesting += 1
            if (difference < (actualValue * 0.02)):
                self.NumPredictionsWithin2PercentInTesting += 1
            elif (difference < (actualValue * 0.05)):
                self.NumPredictionsWithin5PercentInTesting += 1
            elif (difference < (actualValue * 0.1)):
                self.NumPredictionsWithin10PercentInTesting += 1
            elif (difference < (actualValue * 0.2)):
                self.NumPredictionsWithin20PercentInTesting += 1

        #########################
        elif (self.ResultValueType == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            actualValueInt = int(actualValue)
            predictedValueInt = int(predictedValue)
            self.TestNumItemsPerClass[actualValueInt] += 1
            if (actualValueInt == predictedValueInt):
                self.NumCorrectPredictionsInTesting += 1

            if (actualValueInt == predictedValueInt):
                self.NumTruePositivesInTesting[actualValueInt] += 1
            else: # if (actualValueInt != predictedValueInt):
                self.NumFalseNegativesInTesting[actualValueInt] += 1
                self.NumFalsePositivesInTesting[predictedValueInt] += 1

        #########################
        elif (self.ResultValueType == TDF_DATA_TYPE_BOOL):
            self.TestNumItemsPerClass[actualValue] += 1
            if (actualValue == predictedValue):
                self.NumCorrectPredictionsInTesting += 1

            if (actualValue > 0):
                if (predictedValue > 0):
                    self.NumTruePositivesInTesting[0] += 1
                else:
                    self.NumFalseNegativesInTesting[0] += 1
            elif (actualValue <= 0):
                if (predictedValue > 0):
                    self.NumFalsePositivesInTesting[0] += 1
                else:
                    self.NumTrueNegativesInTesting[0] += 1
    # End -  RecordTestingResult




    #####################################################
    #
    # [MLJob::FinishTesting
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishTesting(self):
        now = datetime.now()
        self.StopTestingTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")
    # End - FinishTesting





    #####################################################
    #
    # [MLJob::PrintTestingStats
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def PrintTestingStats(self):
        print(" ")
        print("Test Results:")
        print(RESULT_SECTION_SEPARATOR_STR)
        print("Start Job: " + self.StartRequestTimeStr)
        print("Complete Job: " + self.StopRequestTimeStr)
        print("Start Testing: " + self.StartTestingTimeStr)
        print("Complete Testing: " + self.StopTestingTimeStr)

        print("Number Sequences Tested: " + str(self.NumSequencesTested))

        #########################
        if (((self.ResultValueType == TDF_DATA_TYPE_INT) or (self.ResultValueType == TDF_DATA_TYPE_FLOAT)) and (self.NumSequencesTested > 0)):
            percentAccurate = float(self.NumCorrectPredictionsInTesting) / float(self.NumSequencesTested)
            percentAccurate = percentAccurate * 100.0
            fractionInt = round(percentAccurate)
            print("Exact Accuracy: " + str(fractionInt) + "%")

            percentAccurate = float(self.NumPredictionsWithin2PercentInTesting) / float(self.NumSequencesTested)
            percentAccurate = percentAccurate * 100.0
            fractionInt = round(percentAccurate)
            print("Within 2 percent Accuracy: " + str(fractionInt) + "%")

            percentAccurate = float(self.NumPredictionsWithin5PercentInTesting) / float(self.NumSequencesTested)
            percentAccurate = percentAccurate * 100.0
            fractionInt = round(percentAccurate)
            print("Within 5 percent Accuracy: " + str(fractionInt) + "%")

            percentAccurate = float(self.NumPredictionsWithin10PercentInTesting) / float(self.NumSequencesTested)
            percentAccurate = percentAccurate * 100.0
            fractionInt = round(percentAccurate)
            print("Within 10 percent Accuracy: " + str(fractionInt) + "%")

            percentAccurate = float(self.NumPredictionsWithin20PercentInTesting) / float(self.NumSequencesTested)
            percentAccurate = percentAccurate * 100.0
            fractionInt = round(percentAccurate)
            print("Within 20 percent Accuracy: " + str(fractionInt) + "%")

        #########################
        elif (self.ResultValueType == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            totalNumItems = 0
            totalCorrectPositives = 0
            for classNum in range(TDF_NUM_CATEGORIES_IN_FUTURE_VAL):
                totalNumItems += self.TestNumItemsPerClass[classNum]
                totalCorrectPositives += self.NumTruePositivesInTesting[classNum]

                print(NEWLINE_STR + "Class " + str(classNum))
                print("    Num Items in Event Class: " + str(self.TestNumItemsPerClass[classNum]))
                print("    True Positives: " + str(self.NumTruePositivesInTesting[classNum]))
                print("    False Positives: " + str(self.NumFalsePositivesInTesting[classNum]))
                print("    False Negatives: " + str(self.NumTrueNegativesInTesting[classNum]))
                if (float(self.TestNumItemsPerClass[classNum]) <= 0):
                    sens = 0.0
                else:
                    sens = float(self.NumTruePositivesInTesting[classNum]) / float(self.TestNumItemsPerClass[classNum])
                sens = sens * 100.0
                sens = round(sens, 1)
                print("    Sensitivity: " + str(sens) + " percent")
            # End - for classNum in range(TDF_NUM_CATEGORIES_IN_FUTURE_VAL):

            if (totalNumItems > 0):
                totalAcc = float(totalCorrectPositives) / float(totalNumItems)
            else:
                totalAcc = 0.0
            totalAcc = totalAcc * 100.0
            totalAcc = round(totalAcc, 1)
            print(NEWLINE_STR + "Total Cases: " + str(totalNumItems))
            print("Total Correct: " + str(totalCorrectPositives))
            print("Total Accurracy: " + str(totalAcc) + " percent")

        #########################
        elif (self.ResultValueType == TDF_DATA_TYPE_BOOL):
            resultStr = ""
            for numItems in self.TestNumItemsPerClass:
                resultStr = resultStr + "    " + str(numItems)
            print("Num Positive Items: " + resultStr)

            print("True Positives: " + str(self.NumTruePositivesInTesting[0]))
            print("True Negatives: " + str(self.NumTrueNegativesInTesting[0]))
            print("False Positives: " + str(self.NumFalsePositivesInTesting[0]))
            print("False Negatives: " + str(self.NumTruePositivesInTesting[0]))


        print(" ")
    # End - PrintTestingStats




    #####################################################
    #
    # [MLJob::GetRequestValueStr]
    #
    # Returns one parameter from the currently active request.
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetRequestValueStr(self, valName, defaultVal):
        xmlNode = XMLTools_GetChildNode(self.RequestXMLNode, valName)
        if (xmlNode == None):
            #print("MLJob::GetRequestValueStr: No XML Node valName=" + valName)
            return(defaultVal)

        resultStr = XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip()
        if ((resultStr == None) or (resultStr == "")):
            return(defaultVal)

        return(resultStr)
    # End of GetRequestValueStr




    #####################################################
    #
    # [MLJob::GetRequestValueInt]
    #
    # Returns one parameter from the currently active request.
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetRequestValueInt(self, valName, defaultVal):
        xmlNode = XMLTools_GetChildNode(self.RequestXMLNode, valName)
        if (xmlNode == None):
            #print("MLJob::GetRequestValueInt: No XML Node. valName=[" + valName + "]")
            return(defaultVal)

        resultStr = XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip()
        if ((resultStr == None) or (resultStr == "")):
            return(defaultVal)

        try:
            resultInt = int(resultStr)
        except:
            resultInt = defaultVal
    
        return(resultInt)
    # End of GetRequestValueInt





    #####################################################
    #
    # [MLJob::GetRequestValueBool]
    #
    # Returns one parameter from the currently active request.
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetRequestValueBool(self, valName, defaultVal):
        xmlNode = XMLTools_GetChildNode(self.RequestXMLNode, valName)
        if (xmlNode == None):
            print("MLJob::GetRequestValueBool: No XML Node. valName=" + valName)
            return(defaultVal)

        resultStr = XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip()
        if ((resultStr == None) or (resultStr == "")):
            return(defaultVal)

        resultStr = resultStr.lower()
        if ((resultStr == "true") or (resultStr == "1") or (resultStr == "on") or (resultStr == "yes")):
            return(True)
        else:
            return(False)
    # End of GetRequestValueBool





    #####################################################
    #
    # [MLJob::SetRequestValueStr]
    #
    # Sets one parameter in the currently active request.
    # This is a public procedure, it is called by the client.
    #####################################################
    def SetRequestValueStr(self, valName, valueStr):
        xmlNode = XMLTools_GetChildNode(self.RequestXMLNode, valName)
        if (xmlNode == None):
            xmlNode = self.JobXMLDOM.createElement(valName)
            self.RequestXMLNode.appendChild(xmlNode)

        XMLTools_RemoveAllChildNodes(xmlNode)
        textNode = self.JobXMLDOM.createTextNode(valueStr)
        xmlNode.appendChild(textNode)
    # End of SetRequestValueStr





    #####################################################
    #
    # [MLJob::GetJobControlStr]
    #
    # Returns one parameter to the <JobControl> node.
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetJobControlStr(self, valName, defaultVal):
        xmlNode = XMLTools_GetChildNode(self.JobControlXMLNode, valName)
        if (xmlNode == None):
            return(defaultValue)

        resultStr = XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip()
        if ((resultStr == None) or (resultStr == "")):
            return(defaultValue)

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
        xmlNode = XMLTools_GetChildNode(self.JobControlXMLNode, valName)
        if (xmlNode == None):
            xmlNode = self.JobXMLDOM.createElement(valName)
            self.JobControlXMLNode.appendChild(xmlNode)

        XMLTools_RemoveAllChildNodes(xmlNode)
        textNode = self.JobXMLDOM.createTextNode(valueStr)
        xmlNode.appendChild(textNode)
    # End of SetJobControlStr




    #####################################################
    #
    # [MLJob::GetJobControlBool]
    #
    # Returns one parameter to the <JobControl> node.
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetJobControlBool(self, valName, defaultVal):
        if (defaultVal):
            defaultValStr = "True"
        else:
            defaultValStr = "False"

        resultStr = self.GetJobControlStr(valName, defaultValStr)
        resultStr = resultStr.lower()
        if ((resultStr == "true") or (resultStr == "1") or (resultStr == "on") or (resultStr == "yes")):
            return(True)
        else:
            return(False)
    # End of GetRequestValueBool




    #####################################################
    #
    # [MLJob::GetDataParam]
    #
    # Returns one parameter to the <Data> node.
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetDataParam(self, valName):
        xmlNode = XMLTools_GetChildNode(self.DataXMLNode, valName)
        if (xmlNode == None):
            return("")

        resultStr = XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip()
        if ((resultStr == None) or (resultStr == "")):
            return("")

        return(resultStr)
    # End of GetDataParam




    #####################################################
    #
    # [MLJob::SetDataParam]
    #
    # Updates one parameter to the <Data> node.
    # This is a public procedure, it is called by the client.
    #####################################################
    def SetDataParam(self, valName, valueStr):
        xmlNode = XMLTools_GetChildNode(self.DataXMLNode, valName)
        if (xmlNode == None):
            xmlNode = self.JobXMLDOM.createElement(valName)
            self.DataXMLNode.appendChild(xmlNode)

        XMLTools_RemoveAllChildNodes(xmlNode)
        textNode = self.JobXMLDOM.createTextNode(valueStr)
        xmlNode.appendChild(textNode)
    # End of SetDataParam





    #####################################################
    #
    # [MLJob::IsDebugMode]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def IsDebugMode(self):
        return(self.DebugMode)
    # End of IsDebugMode





    #####################################################
    #
    # [MLJob::GetEpochNum]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetEpochNum(self):
        return(self.CurrentEpochNum)
    # End of GetEpochNum



    #####################################################
    #
    # [MLJob::GetResultValueType]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetResultValueType(self):
        return(self.ResultValueType)
    # End of GetResultValueType






    #####################################################
    #
    # [MLJob::GetFilterProperties]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetFilterProperties(self):
        numProperties = 0
        propertyRelationList = []
        propertyNameList = []
        propertyValueList = []

        propertyListStr = self.GetRequestValueStr("ValueFilter", "")
        if (propertyListStr != ""):
            propList = propertyListStr.split(';')
            for propNamePair in propList:
                #print("propNamePair=" + propNamePair)
                namePairParts = re.split("(.LT.|.LTE.|=|.GTE.|.GT.)", propNamePair)
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
    # End - GetFilterProperties





    #####################################################
    #
    # [MLJob::HasTestMatrix]
    # 
    #####################################################
    def HasTestMatrix(self, testName, matrixName):
        if (self.TestListXMLNode == None):
            return False

        testXMLNode = XMLTools_GetChildNode(self.TestListXMLNode, testName)
        if (testXMLNode == None):
            return False

        matrixXMLNode = XMLTools_GetOrCreateChildNode(testXMLNode, matrixName)
        if (matrixXMLNode == None):
            return False

        return True
    # End - HasTestMatrix




    #####################################################
    #
    # [MLJob::GetTestMatrix
    # 
    #####################################################
    def GetTestMatrix(self, testName, matrixName):
        if (self.TestListXMLNode == None):
            return None

        testXMLNode = XMLTools_GetChildNode(self.TestListXMLNode, testName)
        if (testXMLNode == None):
            return None

        matrixXMLNode = XMLTools_GetChildNode(testXMLNode, matrixName)
        if (matrixXMLNode == None):
            return None

        matrixStr = XMLTools_GetTextContents(matrixXMLNode)
        matrixStr = matrixStr.lstrip()
        #print("MLJob::GetTestMatrix. matrixStr=" + matrixStr)
        matrix = self.MLJob_ConvertStringTo2DMatrix(matrixStr)

        return matrix
    # End - GetTestMatrix





    #####################################################
    #
    # [MLJob::SetTestMatrix
    # 
    #####################################################
    def SetTestMatrix(self, testName, matrixName, matrix):
        #print("SetTestMatrix. testName=" + testName + ", matrixName=" + matrixName)
        #print("SetTestMatrix. matrix=" + str(matrix))

        testXMLNode = XMLTools_GetOrCreateChildNode(self.TestListXMLNode, testName)
        if (testXMLNode == None):
            return

        matrixXMLNode = XMLTools_GetOrCreateChildNode(testXMLNode, matrixName)
        if (matrixXMLNode == None):
            return

        matrixStr = self.MLJob_Convert2DMatrixToString(matrix)
        #print("MLJob::SetTestMatrix. matrixStr=" + matrixStr)
        XMLTools_SetTextContents(matrixXMLNode, matrixStr)
    # End - SetTestMatrix






    #####################################################
    #
    # [MLJob::CheckTestMatrix
    # 
    #####################################################
    def CheckTestMatrix(self, testName, matrixName, matrix):
        #print("CheckTestMatrix. matrix=" + str(matrix))

        if (self.TestListXMLNode == None):
            print("ERROR!!!!!!!! Missing Matrix! testName=" + testName + ", matrixName=" + matrixName)
            sys.exit(0)

        testXMLNode = XMLTools_GetChildNode(self.TestListXMLNode, testName)
        if (testXMLNode == None):
            print("ERROR!!!!!!!! Missing Matrix! testName=" + testName + ", matrixName=" + matrixName)
            sys.exit(0)

        matrixXMLNode = XMLTools_GetChildNode(testXMLNode, matrixName)
        if (matrixXMLNode == None):
            print("ERROR!!!!!!!! Missing Matrix! testName=" + testName + ", matrixName=" + matrixName)
            sys.exit(0)

        matrixStr = XMLTools_GetTextContents(matrixXMLNode)
        matrixStr = matrixStr.lstrip()

        correctMatrix = self.MLJob_ConvertStringTo2DMatrix(matrixStr)
        #print("CheckTestMatrix. correctMatrix=" + str(correctMatrix))

        matrixSize = matrix.shape
        correctMatrixSize = correctMatrix.shape
        numDimensions = len(correctMatrixSize)
        if (len(matrixSize) != len(correctMatrixSize)):
            print("ERROR!!!!!!!! Different Number of Matrix dimensions! testName=" + testName + ", matrixName=" + matrixName)
            sys.exit(0)
        if (len(matrixSize) != 2):
            print("ERROR!!!!!!!! Matrix is not two-dimensional! testName=" + testName + ", matrixName=" + matrixName)
            sys.exit(0)
        if (matrixSize[0] != correctMatrixSize[0]):
            print("ERROR!!!!!!!! Matrix dimensions Are Different! testName=" + testName + ", matrixName=" + matrixName)
            sys.exit(0)
        if (matrixSize[0] != correctMatrixSize[0]):
            print("ERROR!!!!!!!! Matrix dimensions Are Different! testName=" + testName + ", matrixName=" + matrixName)
            sys.exit(0)

        isClose = numpy.allclose(matrix, correctMatrix, atol=0.00001)
        if (not isClose):
            print("ERROR!!!!!!!! Matrices Are Different (fail numpy.array_equiv)! testName=" + testName + ", matrixName=" + matrixName)
            print("CheckTestMatrix. isEqual=" + str(isEqual))
            print("CheckTestMatrix. matrix.size=" + str(matrix.shape))
            print("CheckTestMatrix. correctMatrix.size=" + str(correctMatrix.shape))
            print("CheckTestMatrix. correctMatrix.dtype=" + str(correctMatrix.dtype))
            print("CheckTestMatrix. matrix.dtype=" + str(correctMatrix.dtype))
            print("CheckTestMatrix. correctMatrix.type=" + str(type(correctMatrix).__name__))
            print("CheckTestMatrix. matrix.type=" + str(type(matrix).__name__))
            print("CheckTestMatrix. matrix=" + str(matrix))
            print("CheckTestMatrix. correctMatrix=" + str(correctMatrix))
            sys.exit(0)

        #isEqual = True        
        #for x in range(matrixSize[0]):
        #    for y in range(matrixSize[1]):
        #        #print("Check x=" + str(x) + ", y=" + str(y))
        #        valA = round(float(matrix[x][y]), 4)
        #        valB = round(float(correctMatrix[x][y]), 4)
        #        #print("matrix[0][" + str(y) + "]=" + str(matrix[0][y]))
        #        #print("correctMatrix[0][" + str(y) + "]=" + str(correctMatrix[0][y]))
        #        #print("valA=" + str(valA) + ", valB=" + str(valB))
        #        #if (float(matrix[0][y]) != float(correctMatrix[0][y])):
        #        if (valA != valB):
        #            isEqual = False
        #            print("ERROR!!!!!!!! Different Matrix! testName=" + testName + ", matrixName=" + matrixName)
        #            print("Element [" + str(x) + "][" + str(y) + "] is different")
        #            print("matrix=" + str(matrix))
        #            print("correctMatrix=" + str(correctMatrix))
        #            print("type of valA=" + str(type(valA)))
        #            print("type of valB=" + str(type(valB)))
        #            sys.exit(0)
        #            break

        #print("CheckTestMatrix. OK")
    # End - CheckTestMatrix





    #####################################################
    #
    # [MLJob::RemoveAllSavedState]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def RemoveAllSavedState(self):
        if (self.NeuralNetMatrixListXMLNode != None):
            XMLTools_RemoveAllChildNodes(self.NeuralNetMatrixListXMLNode)
        if (self.NeuralNetGradientListXMLNode != None):
            XMLTools_RemoveAllChildNodes(self.NeuralNetGradientListXMLNode)
    # End of RemoveAllSavedState





    #####################################################
    #
    # [MLJob::GetNeuralNetLinearUnitMatrices
    # 
    # Returns:
    #   FoundIt (True/False)
    #   weightMatrix
    #   biasMatrix
    #####################################################
    def GetNeuralNetLinearUnitMatrices(self, name):
        linearUnitNode = XMLTools_GetChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (linearUnitNode == None):
            return False,None,None

        weightXMLNode = XMLTools_GetChildNode(linearUnitNode, "Weight")
        biasXMLNode = XMLTools_GetChildNode(linearUnitNode, "Bias")
        if ((weightXMLNode == None) or (biasXMLNode == None)):
            return False,None,None

        weightStr = XMLTools_GetTextContents(weightXMLNode)
        weightStr = weightStr.lstrip()
        biasStr = XMLTools_GetTextContents(biasXMLNode)
        biasStr = biasStr.lstrip()
        #print("GetNeuralNetLinearUnitMatrices. weightStr=" + weightStr)
        #print("GetNeuralNetLinearUnitMatrices. biasStr=" + biasStr)

        weightMatrix = self.MLJob_ConvertStringTo2DMatrix(weightStr)
        biasMatrix = self.MLJob_ConvertStringTo1DVector(biasStr)
        #print("GetNeuralNetLinearUnitMatrices. weightMatrix=" + str(weightMatrix))
        #print("GetNeuralNetLinearUnitMatrices. biasMatrix=" + str(biasMatrix))

        return True, weightMatrix, biasMatrix
    # End - GetNeuralNetLinearUnitMatrices


     

    #####################################################
    #
    # [MLJob::SetNeuralNetLinearUnitMatrices
    # 
    #####################################################
    def SetNeuralNetLinearUnitMatrices(self, name, weightMatrix, biasMatrix):
        #print("SetNeuralNetLinearUnitMatrices. weightMatrix=" + str(weightMatrix))
        #print("SetNeuralNetLinearUnitMatrices. biasMatrix=" + str(biasMatrix))

        linearUnitNode = XMLTools_GetOrCreateChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (linearUnitNode == None):
            return

        weightXMLNode = XMLTools_GetOrCreateChildNode(linearUnitNode, "Weight")
        biasXMLNode = XMLTools_GetOrCreateChildNode(linearUnitNode, "Bias")
        if ((weightXMLNode == None) or (biasXMLNode == None)):
            return

        weightStr = self.MLJob_Convert2DMatrixToString(weightMatrix)
        biasStr = self.MLJob_Convert1DVectorToString(biasMatrix)
        #print("SetNeuralNetLinearUnitMatrices. weightStr=" + str(weightStr))
        #print("SetNeuralNetLinearUnitMatrices. biasStr=" + str(biasStr))
    
        XMLTools_SetTextContents(biasXMLNode, biasStr)
        XMLTools_SetTextContents(weightXMLNode, weightStr)
    # End - SetNeuralNetLinearUnitMatrices





    #####################################################
    #
    # [MLJob::GetNeuralNetMatrix
    # 
    #####################################################
    def GetNeuralNetMatrix(self, name):
        matrixXMLNode = XMLTools_GetChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (matrixXMLNode == None):
            return None

        matrixStr = XMLTools_GetTextContents(matrixXMLNode)
        matrixStr = matrixStr.lstrip()

        resultMatrix = self.MLJob_ConvertStringTo2DMatrix(matrixStr)

        return resultMatrix
    # End - GetNeuralNetMatrix




    #####################################################
    #
    # [MLJob::SetNeuralNetMatrix
    # 
    #####################################################
    def SetNeuralNetMatrix(self, name, inputMatrix):
        matrixXMLNode = XMLTools_GetOrCreateChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (matrixXMLNode == None):
            return

        matrixStr = self.MLJob_Convert2DMatrixToString(inputMatrix)
        XMLTools_SetTextContents(matrixXMLNode, matrixStr)
    # End - SetNeuralNetMatrix





    #####################################################
    #
    # [MLJob::GetNeuralNetVector
    # 
    #####################################################
    def GetNeuralNetVector(self, name):
        vectorXMLNode = XMLTools_GetChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (vectorXMLNode == None):
            return None

        vectorStr = XMLTools_GetTextContents(vectorXMLNode)
        vectorStr = vectorStr.lstrip()

        resultVector = MLJob_ConvertStringTo1DVector(vectorStr)

        return resultVector
    # End - GetNeuralNetVector



    #####################################################
    #
    # [MLJob::SetNeuralNetVector
    # 
    #####################################################
    def SetNeuralNetVector(self, name, inputVector):
        vectorXMLNode = XMLTools_GetOrCreateChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (vectorXMLNode == None):
            return

        vectorStr = self.MLJob_Convert2DMatrixToString(inputVector)
        XMLTools_SetTextContents(vectorXMLNode, vectorStr)
    # End - SetNeuralNetVector




    #####################################################
    #
    # [MLJob::GetNeuralNetLinearUnitGradient
    # 
    #####################################################
    def GetNeuralNetLinearUnitGradient(self, name):
        linearUnitNode = XMLTools_GetChildNode(self.NeuralNetGradientListXMLNode, name)
        if (linearUnitNode == None):
            return None,None

        weightXMLNode = XMLTools_GetChildNode(linearUnitNode, "Weight")
        biasXMLNode = XMLTools_GetChildNode(linearUnitNode, "Bias")
        if ((weightXMLNode == None) or (biasXMLNode == None)):
            return None,None

        weightStr = XMLTools_GetTextContents(weightXMLNode)
        weightStr = weightStr.lstrip()
        biasStr = XMLTools_GetTextContents(biasXMLNode)
        biasStr = biasStr.lstrip()

        weightMatrix = self.MLJob_ConvertStringTo2DMatrix(weightStr)
        biasMatrix = self.MLJob_ConvertStringTo1DVector(biasStr)

        return weightMatrix, biasMatrix
    # End - GetNeuralNetLinearUnitGradient





    #####################################################
    #
    # [MLJob::SetNeuralNetLinearUnitGradient
    # 
    #####################################################
    def SetNeuralNetLinearUnitGradient(self, name, weightMatrix, biasMatrix):
        linearUnitNode = XMLTools_GetOrCreateChildNode(self.NeuralNetGradientListXMLNode, name)
        if (linearUnitNode == None):
            return

        weightXMLNode = XMLTools_GetOrCreateChildNode(linearUnitNode, "Weight")
        biasXMLNode = XMLTools_GetOrCreateChildNode(linearUnitNode, "Bias")
        if ((weightXMLNode == None) or (biasXMLNode == None)):
            return

        weightStr = self.MLJob_Convert2DMatrixToString(weightMatrix)
        biasStr = self.MLJob_Convert1DVectorToString(biasMatrix)

        XMLTools_SetTextContents(biasXMLNode, biasStr)
        XMLTools_SetTextContents(weightXMLNode, weightStr)
    # End - SetNeuralNetLinearUnitGradient





    ################################################################################
    #
    # [MLJob_Convert2DMatrixToString]
    #
    # inputArray is a numpy array.
    ################################################################################
    def MLJob_Convert2DMatrixToString(self, inputArray):
        numRows = len(inputArray)
        numCols = len(inputArray[0])

        resultString = "NumD=2;D=" + str(numRows) + "," + str(numCols) + ";T=float;/"
        for rowNum in range(numRows):
            row = inputArray[rowNum]
            #print("Row" + str(rowNum) + " = " + str(row))
            for numVal in row:
                resultString = resultString + str(numVal) + ","
            resultString = resultString[:-1]
            resultString = resultString + "/"

        return(resultString)
    # End - MLJob_Convert2DMatrixToString





    ################################################################################
    #
    # [MLJob_Convert1DVectorToString]
    #
    ################################################################################
    def MLJob_Convert1DVectorToString(self, inputArray):
        dimension = len(inputArray)
        #print("dimension=" + str(dimension))
    
        resultString = "NumD=1;D=" + str(dimension) + ";T=float;/"

        for numVal in inputArray:
            resultString = resultString + str(numVal) + ","
        resultString = resultString[:-1]
        resultString = resultString + "/"

        return(resultString)
    # End - MLJob_Convert1DVectorToString





    ################################################################################
    #
    # [MLJob_ConvertStringTo2DMatrix]
    #
    ################################################################################
    def MLJob_ConvertStringTo2DMatrix(self, tensorStr):
        sectionList = tensorStr.split(";")
        tensorAllRowsStr = sectionList[len(sectionList) - 1]
        #print(">>tensorAllRowsStr = " + tensorAllRowsStr)

        dimensionStr = ""
        typeStr = "float"
        numDimensions = 2
        for propertyStr in sectionList:
            propertyParts = propertyStr.split("=")
            if (len(propertyParts) < 2):
                continue

            propName = propertyParts[0]
            propValue = propertyParts[1]
            if (propName == "D"):
                dimensionStr = propValue
            elif (propName == "T"):
                typeStr = propValue
            elif (propName == "NumD"):
                numDimensions = int(propValue)
        # End - for propertyStr in sectionList:

        dimensionList = dimensionStr.split(",")
        numRows = int(dimensionList[0])
        numCols = int(dimensionList[1])
        #print(">>numRows = " + str(numRows))
        #print(">>numCols = " + str(numCols))

        newMatrix = numpy.empty([numRows, numCols])

        tensorRowStrList = tensorAllRowsStr.split("/")
        rowNum = 0    
        for singleRowStr in tensorRowStrList:
            if (singleRowStr != ""):
                #print("Row=" + singleRowStr)
                valueList = singleRowStr.split(",")
                colNum = 0
                for value in valueList:
                    #print("Convert one val[" + str(value) + "]")
                    newMatrix[rowNum][colNum] = float(value)
                    colNum += 1
                rowNum += 1
        # End - for singleRowStr in tensorRowStrList:

        return(newMatrix)
    # End - MLJob_ConvertStringTo2DMatrix




    ################################################################################
    #
    # [MLJob_ConvertStringTo1DVector]
    #
    ################################################################################
    def MLJob_ConvertStringTo1DVector(self, tensorStr):
        sectionList = tensorStr.split(";")
        tensorAllRowsStr = sectionList[len(sectionList) - 1]
        #print(">>tensorAllRowsStr = " + tensorAllRowsStr)

        dimensionStr = ""
        typeStr = "float"
        numDimensions = 1
        for propertyStr in sectionList:
            propertyParts = propertyStr.split("=")
            if (len(propertyParts) < 2):
                continue

            propName = propertyParts[0]
            propValue = propertyParts[1]
            if (propName == "D"):
                dimensionStr = propValue
            elif (propName == "T"):
                typeStr = propValue
            elif (propName == "NumD"):
                numDimensions = int(propValue)
        # End - for propertyStr in sectionList:

        dimensionList = dimensionStr.split(",")
        numCols = int(dimensionList[0])
        #print(">>numCols = " + str(numCols))

        newMatrix = numpy.empty([numCols])

        tensorValueStrList = tensorAllRowsStr.split("/")
        for singleRowStr in tensorValueStrList:
            if (singleRowStr != ""):
                #print("Row=" + singleRowStr)
                valueList = singleRowStr.split(",")
                colNum = 0
                for value in valueList:
                    newMatrix[colNum] = float(value)
                    colNum += 1
        # End - for singleRowStr in tensorValueStrList:

        return(newMatrix)
    # End - MLJob_ConvertStringTo1DVector
    


# End - class MLJob
################################################################################









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
def MLJob_CreateMLJobFromString(str):
    job = MLJob()
    job.InitNewJobImpl()
    job.ReadJobFromString(str)

    return job
# End - MLJob_CreateMLJobFromString



################################################################################
# 
# This is a public procedure, it is called by the client.
################################################################################
def MLJob_ReadExistingMLJob(jobFilePathName):
    job = MLJob()
    job.ReadJobFromFile(jobFilePathName)

    return job
# End - MLJob_ReadExistingMLJob






################################################################################
# TEST CODE
################################################################################



################################################################################
#
# [MLJob_UnitTest]
#
################################################################################
def MLJob_UnitTest():
    jobFilePath = "/home/ddean/ddRoot/tools/BVTJob1.txt"

    Test_StartModuleTest("MLJob")

    Test_StartTest("Read Existing Job")
    try:
        job = MLJob_ReadExistingMLJob(jobFilePath)

        val = job.GetDataParam("StoreType")
        Test_CheckString(val, "File")
    
        val = job.GetDataParam("DataFormat")
        Test_CheckString(val, "TDF")

        val = job.GetDataParam("TrainData")
        val = job.GetDataParam("TestData")

        val = job.GetRequestValueStr("InputValues", "aaaa")
        Test_CheckString(val, "AgeInYrs,Cr")

        val = job.GetRequestValueStr("ResultValue", "aaaa")
        Test_CheckString(val, "Future_CKD5")

        val = job.GetRequestValueStr("NetworkType", "aaaa")
        Test_CheckString(val, "TinyRNN")

        val = job.GetRequestValueStr("NonLinearType", "aaaa")
        Test_CheckString(val, "LogSoftmax")

        val = job.GetRequestValueStr("LossFunction", "aaaa")
        Test_CheckString(val, "NLLLoss")

        val = job.GetRequestValueStr("NumEpochs", "aaaa")
        Test_CheckInt(int(val), 2)

        val = job.GetRequestValueStr("WindowStartEvent", "")
        Test_CheckString(val, "")

        val = job.GetRequestValueStr("WindowStopEvent", "")
        Test_CheckString(val, "")
    except:
        Test_Error("Unhandled exception")
# End - MLJob_UnitTest






##############################################################################################################
#g_TestPathName = "/home/ddean/fooTest.txt"
#job = MLJob_CreateNewMLJob()

#inputSize = 71
#outputSize = 13
#origLinearUnit = nn.Linear(inputSize, outputSize)
#job.SetNeuralNetLinearUnitMatrices("test1", origLinearUnit.weight.detach().numpy(), origLinearUnit.bias.detach().numpy())
#job.SaveAs(g_TestPathName)

#newJob = MLJob_ReadExistingMLJob(g_TestPathName)
#weightMatrix, biasMatrix = newJob.GetNeuralNetLinearUnitMatrices("test1")
#weightTensor = torch.tensor(weightMatrix, dtype=torch.float32)
#biasTensor = torch.tensor(biasMatrix, dtype=torch.float32)
#newLinearUnit = nn.Linear(inputSize, outputSize)
#newLinearUnit.weight = torch.nn.Parameter(weightTensor)
#newLinearUnit.bias = torch.nn.Parameter(biasTensor)

#testInput = torch.rand((inputSize))
#print("inputSize=" + str(inputSize))

#resultFromOrig = origLinearUnit(testInput)
#resultFromRecon = newLinearUnit(testInput)
#print("resultFromOrig=" + str(resultFromOrig))
#print("resultFromRecon=" + str(resultFromRecon))

#for index in range(outputSize):
#    origVal = resultFromOrig[index]
#    reconVal = resultFromRecon[index]
#    if (origVal != reconVal):
#        print("Different")
#        sys.exit(0)
#print("They seem to be the same")



