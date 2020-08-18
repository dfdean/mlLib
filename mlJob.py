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
#   JobType - DMSBasic
#
#   JobSpecVersion - Currently 1.0
#
#   Status - Pending, Running, Partial, Complete
#
#   SaveNetState - True/False
#
#   SavePrevResults - True/False
#
#   ResultReturnMechanism - { email, localFile, DropBox, ... >
#
#   ResultReturnAddress - emailAdddr
#
#   ResultNotifyMechanism - { email, text, file, socket, ... }
#
#   ResultNotifyPolicy - { onFinal, progressUpdates }
#
#   ResultNotifyAddress - { emailAddr }
#
#   DateRequested - In the format "yyyy:mm:dd hh:mm:ss"
#
#   Requestor - User-readable name of the person who requested the file
#
#   Email - Email to a human who may be interested
#
#   x_BailOut - { BeforeInit, AfterInit, AfterTrain
#
#   x_Debug - Number between 0..5 where 0 means no debugging.
#
#   x_StressTest - True/False
#
#   x_PerfProfile - True/False
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
#   LossFunction
#       NLLLoss
#       BCELoss
#
#   NonLinearType
#       LogSoftmax
#
#   Optimizer
#       SGD
#
#   HiddenLayerSize
#
#   NumEpochs
#
#   InputValues - A comma-separated list of variables, like "Age,Cr,SBP". See the TDFTools.py documentation.
#   ResultValue - A variable name. See the TDFTools.py documentation.
#
#   ResultValueType - The data type of the output variable.
#       BinaryDiagnosis - A number 0-1
#       FutureEventClass - A number 0-11. See the TDFTools.py documentation.
#
#   WindowStartEvent
#
#   WindowStopEvent
#
#   PredictionGroup - "Window" or "Sample"
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
#   VariantIndex
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
#
#   TrainAvgLossPerEpoch
#
#   TrainNumItemsPerClass
#
#   TestNumItemsPerClass
#
#   Only used for binary results.
#       NumTrueNegativesInTraining
#       NumFalsePositivesInTraining
#       NumFalseNegativesInTraining
#       NumTruePositivesInTraining
#
#       NumTrueNegativesInTesting
#       NumFalsePositivesInTesting
#       NumFalseNegativesInTesting
#       NumTruePositivesInTesting
#
#   OS
#   CPU
#   GPU
#
##################
# TestList
#
#   A list of test elements, each of thich can contain different inputs and outputs.
#   This is very unstructured, and its use depends on the individual tests.
#
##################
# ExpectedResults
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
#####################################################################################
#Example:
#
#<MLJob>
#</MLJob>
#
#####################################################################################

import os
import sys
import shutil
import string
import time
from datetime import datetime
from time import gmtime, strftime
import platform
import numpy

# Normally we have to set the search path to load these.
# But, this .py file is always in the same directories as these imported modules.
from xmlTools import *
#from ddToolsLib import *
from testUtils import *
from tdfTools import *

import xml.dom
import xml.dom.minidom
from xml.dom.minidom import parse, parseString
from xml.dom.minidom import getDOMImplementation

NEWLINE_STR = "\n"
MLJOB_SINGLE_INDENT_STR = "    "

MLJOB_LOG_NODE_ELEMENT_NAME = "Log"

#TDF_NUM_CATEGORIES_IN_FUTURE_VAL = 14

################################################################################
#
# [MLJob_Log]
#
################################################################################
def MLJob_Log(message):
    return
# End - MLJob_Log






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
        self.OriginalRequestXMLNode = None
        self.CurrentRequestXMLNode = None
        self.ResultsListXMLNode = None
        self.RuntimeXMLNode = None
        self.ExpectedResultsXMLNode = None
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

        self.OriginalRequestXMLNode = self.JobXMLDOM.createElement("Request")
        self.RootXMLNode.appendChild(self.OriginalRequestXMLNode)

        self.RequestVariantList = self.JobXMLDOM.createElement("RequestVariantList")
        self.RootXMLNode.appendChild(self.RequestVariantList)

        self.ResultsListXMLNode = self.JobXMLDOM.createElement("ResultList")
        self.RootXMLNode.appendChild(self.ResultsListXMLNode)

        self.RuntimeXMLNode = self.JobXMLDOM.createElement("Runtime")
        self.RootXMLNode.appendChild(self.RuntimeXMLNode)

        self.ExpectedResultsXMLNode = self.JobXMLDOM.createElement("ExpectedResults")
        self.RootXMLNode.appendChild(self.ExpectedResultsXMLNode)

        self.TestListXMLNode = self.JobXMLDOM.createElement("TestList")
        self.RootXMLNode.appendChild(self.TestListXMLNode)

        self.NeuralNetMatrixListXMLNode = self.JobXMLDOM.createElement("NeuralNetMatrixList")
        self.RootXMLNode.appendChild(self.NeuralNetMatrixListXMLNode)

        self.NeuralNetGradientListXMLNode = self.JobXMLDOM.createElement("NeuralNetGradientList")
        self.RootXMLNode.appendChild(self.NeuralNetGradientListXMLNode)
    # End of InitNewJobImpl





    #####################################################
    #
    # [MLJob::ReadJobFromString]
    #
    #####################################################
    def ReadJobFromString(self, jobString):
        #print("MLJob::ReadJobFromString")

        # Parse the text string into am XML DOM
        try:
            self.JobXMLDOM = parseString(jobString)
        except xml.parsers.expat.ExpatError as err:
            MLJob_Log("MLJob::ReadJobFromString. Error from parsing string:")
            MLJob_Log("[" + jobString + "]")
            MLJob_Log("ExpatError:" + str(err))
            return
        except:
            MLJob_Log("MLJob::ReadJobFromString. Error from parsing string:")
            MLJob_Log("[" + jobString + "]")
            MLJob_Log("Unexpected error:", sys.exc_info()[0])
            return

        try:
            self.RootXMLNode = self.JobXMLDOM.getElementsByTagName("MLJob")[0]
        except:
            MLJob_Log("MLJob::ReadJobFromString. Required elements are missing: [" + jobString + "]")
            return

        try:
            self.JobControlXMLNode = self.JobXMLDOM.getElementsByTagName("JobControl")[0]
        except:
            # If this is missing, then create it.
            self.JobControlXMLNode = self.JobXMLDOM.createElement("JobControl")
            self.RootXMLNode.appendChild(self.JobControlXMLNode)

        try:
            self.DataXMLNode = self.JobXMLDOM.getElementsByTagName("Data")[0]
        except:
            # If this is missing, then create it.
            self.DataXMLNode = self.JobXMLDOM.createElement("Data")
            self.RootXMLNode.appendChild(self.DataXMLNode)

        try:
            self.OriginalRequestXMLNode = self.JobXMLDOM.getElementsByTagName("Request")[0]
        except:
            # If this is missing, then create it.
            self.OriginalRequestXMLNode = self.JobXMLDOM.createElement("Request")
            self.RootXMLNode.appendChild(self.OriginalRequestXMLNode)

        try:
            self.RequestVariantList = self.JobXMLDOM.getElementsByTagName("RequestVariantList")[0]
        except:
            # If this is missing, then create it.
            self.RequestVariantList = self.JobXMLDOM.createElement("RequestVariantList")
            self.RootXMLNode.appendChild(self.RequestVariantList)

        try:
            self.ResultsListXMLNode = self.JobXMLDOM.getElementsByTagName("ResultList")[0]
        except:
            # If this is missing, then create it.
            self.ResultsListXMLNode = self.JobXMLDOM.createElement("ResultList")
            self.RootXMLNode.appendChild(self.ResultsListXMLNode)

        try:
            self.RuntimeXMLNode = self.JobXMLDOM.getElementsByTagName("Runtime")[0]
        except:
            # If this is missing, then create it.
            self.RuntimeXMLNode = self.JobXMLDOM.createElement("Runtime")
            self.RootXMLNode.appendChild(self.RuntimeXMLNode)

        try:
            self.ExpectedResultsXMLNode = self.JobXMLDOM.getElementsByTagName("ExpectedResults")[0]
        except:
            # If this is missing, then create it.
            self.ExpectedResultsXMLNode = self.JobXMLDOM.createElement("ExpectedResults")
            self.RootXMLNode.appendChild(self.ExpectedResultsXMLNode)

        try:
            self.TestListXMLNode = self.JobXMLDOM.getElementsByTagName("TestList")[0]
        except:
            # If this is missing, then create it.
            self.TestListXMLNode = self.JobXMLDOM.createElement("TestList")
            self.RootXMLNode.appendChild(self.TestListXMLNode)

        try:
            self.NeuralNetMatrixListXMLNode = self.JobXMLDOM.getElementsByTagName("NeuralNetMatrixList")[0]
        except:
            # If this is missing, then create it.
            self.NeuralNetMatrixListXMLNode = self.JobXMLDOM.createElement("NeuralNetMatrixList")
            self.RootXMLNode.appendChild(self.NeuralNetMatrixListXMLNode)

        try:
            self.NeuralNetGradientListXMLNode = self.JobXMLDOM.getElementsByTagName("NeuralNetGradientList")[0]
        except:
            # If this is missing, then create it.
            self.NeuralNetGradientListXMLNode = self.JobXMLDOM.createElement("NeuralNetGradientList")
            self.RootXMLNode.appendChild(self.NeuralNetGradientListXMLNode)


        # Optionally, read any runtime if it is present.
        # This is only used when sending jobs between a dispatcher process and a
        # child worker process, and is not normally stored in a file. It could
        # be saved to a file if we ever want to "suspend" runtime state and
        # resume it at a later date, but that is not supported now and would
        # raise some tricky synchronization issues.
        #
        # This is optional. No error if it is missing.
        self.ReadRuntimeFromXML(self.RuntimeXMLNode)

        self.DebugMode = False
        if (self.CurrentRequestXMLNode != None):
            xmlNode = XMLTools_GetChildNode(self.CurrentRequestXMLNode, "DebugMode")
            if (xmlNode != None):
                resultStr = XMLTools_GetTextContents(xmlNode).lower()
                if ((resultStr == "on") or (resultStr == "true") or (resultStr == "yes") or (resultStr == "1")):
                    self.DebugMode = True

        self.SelectFirstRequestVariant()
    # End of ReadJobFromString






    #####################################################
    #
    # [MLJob::WriteJobToString]
    #
    #####################################################
    def WriteJobToString(self, fIncludeRuntime):
        # Optionally, write the current runtime to a remporary node that is just used for 
        # holding an incomplete request that is currently executing
        #
        # This is only used when sending jobs between a dispatcher process and a
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

        resultStr = self.JobXMLDOM.toprettyxml(indent=" ", newl="\n", encoding=None)
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

        self.CurrentEpochNum = 0
        self.NumSequencesTrainedPerEpoch = 0
        self.NumSequencesTested = 0

        self.AvgLossPerEpochList = []
        self.TotalTrainingLossInCurrentEpoch = 0.0
        #print("ResetRuntimeStateImpl. self.TotalTrainingLossInCurrentEpoch=" + str(self.TotalTrainingLossInCurrentEpoch))
        self.NumCorrectPredictionsInTesting = 0

        self.TrainNumItemsPerClass = []
        self.TestNumItemsPerClass = []

        self.NumTrueNegativesInTraining = 0
        self.NumFalsePositivesInTraining = 0
        self.NumFalseNegativesInTraining = 0
        self.NumTruePositivesInTraining = 0

        self.NumTrueNegativesInTesting = 0
        self.NumFalsePositivesInTesting = 0
        self.NumFalseNegativesInTesting = 0
        self.NumTruePositivesInTesting = 0

        self.BufferedLogLines = ""

        self.DebugMode = False
        if (self.CurrentRequestXMLNode != None):
            xmlNode = XMLTools_GetChildNode(self.CurrentRequestXMLNode, "DebugMode")
            if (xmlNode != None):
                resultStr = XMLTools_GetTextContents(xmlNode).lower()
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
            self.NumCorrectPredictionsInTesting = int(XMLTools_GetChildNodeText(parentXMLNode, "NumCorrectPredictionsInTesting"))
        except:
            pass

        try:
            self.TotalTrainingLossInCurrentEpoch = float(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "TotalTrainingLossInCurrentEpoch"))
        except:
            pass
        #print("ReadJobFromString. self.TotalTrainingLossInCurrentEpoch=" + str(self.TotalTrainingLossInCurrentEpoch))


        resultStr = XMLTools_GetChildNodeText(parentXMLNode, "TrainAvgLossPerEpoch")
        self.AvgLossPerEpochList = []
        resultArray = resultStr.split(",")
        for avgLossStr in resultArray:
            try:
                avgLossFloat = float(avgLossStr)
                avgLossFloat = round(avgLossFloat, 4)
                self.AvgLossPerEpochList.append(avgLossFloat)
            except:
                continue


        resultStr = XMLTools_GetChildNodeText(parentXMLNode, "TrainNumItemsPerClass")
        self.TrainNumItemsPerClass = []
        countArray = resultStr.split(",")
        for numItems in countArray:
            try:
                self.TrainNumItemsPerClass.append(int(numItems))
            except:
                continue


        resultStr = XMLTools_GetChildNodeText(parentXMLNode, "TestNumItemsPerClass")
        self.TestNumItemsPerClass = []
        countArray = resultStr.split(",")
        for numItems in countArray:
            try:
                self.TestNumItemsPerClass.append(int(numItems))
            except:
                continue


        try:
            self.NumTrueNegativesInTraining = int(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "NumTrueNegativesInTraining"))
        except:
            pass
        try:
            self.NumFalsePositivesInTraining = int(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "NumFalsePositivesInTraining"))
        except:
            pass
        try:
            self.NumFalseNegativesInTraining = int(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "NumFalseNegativesInTraining"))
        except:
            pass
        try:
            self.NumTruePositivesInTraining = int(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "NumTruePositivesInTraining"))
        except:
            pass

        try:
            self.NumTrueNegativesInTesting = int(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "NumTrueNegativesInTesting"))
        except:
            pass
        try:
            self.NumFalsePositivesInTesting = int(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "NumFalsePositivesInTesting"))
        except:
            pass
        try:
            self.NumFalseNegativesInTesting = int(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "NumFalseNegativesInTesting"))
        except:
            pass
        try:
            self.NumTruePositivesInTesting = int(XMLTools_GetChildNodeText(self.RuntimeXMLNode, "NumTruePositivesInTesting"))
        except:
            pass
        try:
            self.BufferedLogLines = XMLTools_GetChildNodeText(self.RuntimeXMLNode, MLJOB_LOG_NODE_ELEMENT_NAME)
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

        XMLTools_AddChildNodeWithText(parentXMLNode, "VariantIndex", str(0))

        XMLTools_AddChildNodeWithText(parentXMLNode, "StartRequestTimeStr", str(self.StartRequestTimeStr))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StartRequestTimeInSeconds", str(self.StartRequestTimeInSeconds))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StopRequestTimeStr", str(self.StopRequestTimeStr))
        XMLTools_AddChildNodeWithText(parentXMLNode, "StopRequestTimeInSeconds", str(self.StopRequestTimeInSeconds))

        XMLTools_AddChildNodeWithText(parentXMLNode, "CurrentEpochNum", str(self.CurrentEpochNum))
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumSequencesTrainedPerEpoch", str(self.NumSequencesTrainedPerEpoch))
        XMLTools_AddChildNodeWithText(parentXMLNode, "NumSequencesTested", str(self.NumSequencesTested))

        XMLTools_AddChildNodeWithText(parentXMLNode, "NumCorrectPredictionsInTesting", str(self.NumCorrectPredictionsInTesting))
        resultStr = ""
        for avgLoss in self.AvgLossPerEpochList:
            avgLoss = round(avgLoss, 4)
            resultStr = resultStr + str(avgLoss) + ","
        # Remove the last comma
        if (len(self.AvgLossPerEpochList) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "TrainAvgLossPerEpoch", resultStr)


        resultStr = ""
        for numItemsInClass in self.TrainNumItemsPerClass:
            resultStr = resultStr + str(numItemsInClass) + ","
        # Remove the last comma
        if (len(self.TrainNumItemsPerClass) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "TrainNumItemsPerClass", resultStr)


        resultStr = ""
        for numItemsInClass in self.TestNumItemsPerClass:
            resultStr = resultStr + str(numItemsInClass) + ","
        # Remove the last comma
        if (len(self.TestNumItemsPerClass) > 0):
            resultStr = resultStr[:-1]
        XMLTools_AddChildNodeWithText(parentXMLNode, "TestNumItemsPerClass", resultStr)


        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "TotalTrainingLossInCurrentEpoch", str(self.TotalTrainingLossInCurrentEpoch))

        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "NumTrueNegativesInTraining", str(self.NumTrueNegativesInTraining))
        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "NumFalsePositivesInTraining", str(self.NumFalsePositivesInTraining))
        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "NumFalseNegativesInTraining", str(self.NumFalseNegativesInTraining))
        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "NumTruePositivesInTraining", str(self.NumTruePositivesInTraining))

        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "NumTrueNegativesInTesting", str(self.NumTrueNegativesInTesting))
        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "NumFalsePositivesInTesting", str(self.NumFalsePositivesInTesting))
        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "NumFalseNegativesInTesting", str(self.NumFalseNegativesInTesting))
        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "NumTruePositivesInTesting", str(self.NumTruePositivesInTesting))

        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "OS", str(platform.platform()))
        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "CPU", str(platform.processor()))
        XMLTools_AddChildNodeWithText(self.RuntimeXMLNode, "GPU", "None")

        # If there is a log string, then add it to the end of the Result node.
        if (self.BufferedLogLines != ""):
            logXMLNode = XMLTools_GetChildNode(self.RuntimeXMLNode, MLJOB_LOG_NODE_ELEMENT_NAME)
            if (logXMLNode == None):
                logXMLNode = self.JobXMLDOM.createElement(MLJOB_LOG_NODE_ELEMENT_NAME)
                self.RuntimeXMLNode.appendChild(logXMLNode)
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
        self.ReadJobFromString(contentsText)

        fileH.close()
    # End of ReadJobFromFile





    #####################################################
    #
    # [MLJob::SaveAs]
    #
    #####################################################
    def SaveAs(self, jobFilePathName):
        fileH = open(jobFilePathName, "w+")

        contentsText = self.WriteJobToString(True)

        fileH.write(contentsText)
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

        MLJob_Log(messageStr)
    # End of Log






    #####################################################
    #
    # [MLJob::SelectFirstRequestVariant
    # 
    # This is called BOTH internally, when we open a new job, and
    # may also be called externally.
    #####################################################
    def SelectFirstRequestVariant(self):
        #print("SelectFirstRequestVariant")

        self.CurrentRequestXMLNode = self.OriginalRequestXMLNode.cloneNode(True)
        self.CurrentRequestVariantXMLNode = None

        # The variant list is optional. If there is none, then there is no "first" variant.
        # If there is no first variant, then just use the request itself.
        if (self.RequestVariantList != None):
            #print("MLJob::SelectFirstRequestVariant. Set the first variant")
            self.CurrentRequestVariantXMLNode = XMLTools_GetChildNode(self.RequestVariantList, "Variant")
            if (self.CurrentRequestVariantXMLNode != None):
                #print("MLJob::SelectFirstRequestVariant. Apply a variant")
                self.ApplyVariantToCurrentRequestImpl()

        return(True)
    # End - SelectFirstRequestVariant





    #####################################################
    #
    # [MLJob::SelectNextRequestVariant
    # 
    # This is externally by the client
    #####################################################
    def SelectNextRequestVariant(self):
        #print("SelectNextRequestVariant. RequestVariantList=" + str(self.RequestVariantList))
        #print("SelectNextRequestVariant. CurrentRequestVariantXMLNode=" + str(self.CurrentRequestVariantXMLNode))
        #debugStr = self.CurrentRequestVariantXMLNode.toprettyxml(indent=" ", newl="", encoding=None)
        #print(">>>" + debugStr)

        # The variant list is optional. If there is none, then there is no "next" variant.
        if ((self.RequestVariantList == None) or (self.CurrentRequestVariantXMLNode == None)):
            print("MLJob::SelectNextRequestVariant. (self.RequestVariantList == None)")
            return(False)

        # Try advancing to the next variant.
        self.CurrentRequestVariantXMLNode = XMLTools_GetPeerNode(self.CurrentRequestVariantXMLNode, "Variant")

        # If we are at the end, then we are done.
        if (self.CurrentRequestVariantXMLNode == None):
            print("MLJob::SelectNextRequestVariant 2. (self.CurrentRequestVariantXMLNode == None)")
            return(False)

        self.CurrentRequestXMLNode = self.OriginalRequestXMLNode.cloneNode(True)
        self.ApplyVariantToCurrentRequestImpl()

        return(True)
    # End - SelectNextRequestVariant





    #####################################################
    #
    # [MLJob::ApplyVariantToCurrentRequestImpl
    # 
    #####################################################
    def ApplyVariantToCurrentRequestImpl(self):
        valueNode = XMLTools_GetFirstChildNode(self.CurrentRequestVariantXMLNode)
        while (valueNode != None):
            name = XMLTools_GetElementName(valueNode)
            value = XMLTools_GetTextContents(valueNode)
            #print("MLJob::ApplyVariantToCurrentRequestImpl. Overwrite name=" + name)
            #print("MLJob::ApplyVariantToCurrentRequestImpl. Overwrite value=" + value)

            currentChildNode = XMLTools_GetChildNode(self.CurrentRequestXMLNode, name)
            if (currentChildNode == None):
                currentChildNode = self.JobXMLDOM.createElement(name)
                self.RootXMLNode.appendChild(currentChildNode)
            XMLTools_SetTextContents(currentChildNode, value)

            valueNode = XMLTools_GetAnyPeerNode(valueNode)
        # End - while (valueNode != None):
    # End - ApplyVariantToCurrentRequestImpl





    #####################################################
    #
    # [MLJob::DiscardPastResults
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def DiscardPastResults(self):
        XMLTools_RemoveAllChildNodes(self.ResultsListXMLNode)
    # End - DiscardPastResults




    #####################################################
    #
    # [MLJob::StartNewResult
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartNewResult(self):
        currentResultXMLNode = self.JobXMLDOM.createElement("Result")
        self.ResultsListXMLNode.appendChild(currentResultXMLNode)
    # End - StartNewResult




    #####################################################
    #
    # [MLJob::GetLatestResultNodeImpl
    # 
    #####################################################
    def GetLatestResultNodeImpl(self):
        currentResultXMLNode = XMLTools_GetLastChildNode(self.ResultsListXMLNode)
        return(currentResultXMLNode)
    # End - GetLatestResultNodeImpl




    #####################################################
    #
    # [MLJob::StartJobExecution]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartJobExecution(self):
        # Each request has a single test. When we finish the test, we have
        # finished the entire reqeust.
        self.SetJobControlStr("Status", "Pending")
        self.SetJobControlStr("Error", "None")

        self.StartRequestTimeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
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
            MLJob_Log("Job Success")
        else:
            self.SetJobControlStr("Status", "Error")
            self.SetJobControlStr("Error", errorMsg)
            MLJob_Log(errorMsg)

        self.StopRequestTimeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self.StopRequestTimeInSeconds = time.time()


        # Make a new XML Node
        resultXMLNode = self.JobXMLDOM.createElement("Results")
        self.ResultsListXMLNode.appendChild(self.ResultsListXMLNode)

        # If there is a request variant that made this request, then save a copy of it to the results.
        # This makes it easier to see the configuration that generated each result.
        if (self.CurrentRequestVariantXMLNode != None):
            variantCopy = self.CurrentRequestVariantXMLNode.cloneNode(True)
            resultXMLNode.appendChild(variantCopy)

        # Save the runtime state
        self.SaveRuntimeToXML(resultXMLNode)
    # End of FinishJobExecution





    #####################################################
    #
    # [MLJob::StartTraining
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartTraining(self):
        self.NumSequencesTrainedPerEpoch = 0

        self.AvgLossPerEpochList = []
        self.TotalTrainingLossInCurrentEpoch = 0.0

        self.TrainNumItemsPerClass = [0] * TDF_NUM_CATEGORIES_IN_FUTURE_VAL

        self.NumTrueNegativesInTraining = 0
        self.NumFalsePositivesInTraining = 0
        self.NumFalseNegativesInTraining = 0
        self.NumTruePositivesInTraining = 0
    # End - StartTraining




    #####################################################
    #
    # [MLJob::StartTrainingEpoch
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartTrainingEpoch(self):
        # Reset the counters for the new epoch
        self.NumSequencesTrainedPerEpoch = 0

        self.TotalTrainingLossInCurrentEpoch = 0.0
        #print("StartTrainingEpoch. self.TotalTrainingLossInCurrentEpoch=" + str(self.TotalTrainingLossInCurrentEpoch))
    # End - StartTrainingEpoch




    #####################################################
    #
    # [MLJob::FinishTrainingEpoch
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishTrainingEpoch(self):
        #print("FinishTrainingEpoch")

        if (self.NumSequencesTrainedPerEpoch > 0):
            avgLoss = float(self.TotalTrainingLossInCurrentEpoch / float(self.NumSequencesTrainedPerEpoch))
        else:
            avgLoss = 0.0
        #print("FinishTrainingEpoch. avgLoss=" + str(avgLoss))

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
        #print("RecordTrainingLoss. loss=" + str(loss))

        self.NumSequencesTrainedPerEpoch += 1
        self.TotalTrainingLossInCurrentEpoch += loss
    # End -  RecordTrainingLoss




    #####################################################
    #
    # [MLJob::RecordTrainingForFutureEvent
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def RecordTrainingForFutureEvent(self, actualClass, predictedClass):
        #print("RecordTrainingForFutureEvent. loss=" + str(loss))

        # We only record the stats on the first epoch.
        if (self.CurrentEpochNum == 0):
            self.TrainNumItemsPerClass[actualClass] += 1
    # End -  RecordTrainingForFutureEvent




    #####################################################
    #
    # [MLJob::FinishTraining
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishTraining(self):
        #print("In FinishTraining")
        resultsNode = self.GetLatestResultNodeImpl()
    # End - FinishTraining




    #####################################################
    #
    # [MLJob::PrintTrainingStats
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def PrintTrainingStats(self):
        print("Each Epoch contains:")
        print("    Num Sequences = " + str(self.NumSequencesTrainedPerEpoch))

        resultStr = ""
        for avgLoss in self.AvgLossPerEpochList:
            avgLoss = round(avgLoss, 4)
            resultStr = resultStr + "    " + str(avgLoss)
        print("Average Losses Per Epoch:" + resultStr)

        resultStr = ""
        for numItems in self.TrainNumItemsPerClass:
            resultStr = resultStr + "    " + str(numItems)
        print("Num Items in Each Event Class: " + resultStr)
    # End - PrintTrainingStats






    #####################################################
    #
    # [MLJob::StartTesting
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def StartTesting(self):
        self.NumSequencesTested = 0
        self.NumCorrectPredictionsInTesting = 0

        self.TestNumItemsPerClass = [0] * TDF_NUM_CATEGORIES_IN_FUTURE_VAL

        self.NumTrueNegativesInTesting = 0
        self.NumFalsePositivesInTesting = 0
        self.NumFalseNegativesInTesting = 0
        self.NumTruePositivesInTesting = 0
    # End - StartTesting





    #####################################################
    #
    # [MLJob::RecordTestingResultForFutureEvent
    # 
    # This is a public procedure, it is called by the client.
    #
    #####################################################
    def RecordTestingResultForFutureEvent(self, actualDiagnosisClass, predictedDiagnosis):
        #print("RecordTestingResultForFutureEvent")

        self.NumSequencesTested += 1

        # Categorize the result.
        if (actualDiagnosisClass == predictedDiagnosis):
            self.NumCorrectPredictionsInTesting += 1
        self.TestNumItemsPerClass[actualDiagnosisClass] += 1
    # End -  RecordTestingResultForFutureEvent





    #####################################################
    #
    # [MLJob::RecordTestingResultForDiagnosis
    # 
    # This is a public procedure, it is called by the client
    #
    #####################################################
    def RecordTestingResultForDiagnosis(self, actualDiagnosisClass, predictedDiagnosis):
        self.NumSequencesTested += 1

        # Categorize the result.
        if (actualDiagnosisClass == predictedDiagnosis):
            self.NumCorrectPredictionsInTesting += 1

        # Categorize the result.
        if (actualDiagnosisClass == 0):
            if (predictedDiagnosis == 0):
                self.NumTrueNegativesInTesting += 1
            elif (predictedDiagnosis == 1):
                self.NumFalsePositivesInTesting += 1
            else:
                print("Invalid predictedDiagnosis: " + str(predictedDiagnosis))
        elif (actualDiagnosisClass == 1):
            if (predictedDiagnosis == 0):
                self.NumTruePositivesInTesting += 1
            elif (predictedDiagnosis == 1):
                self.NumTruePositivesInTesting += 1
            else:
                print("Invalid predictedDiagnosis: " + str(predictedDiagnosis))
        else:
            print("Invalid actualDiagnosisClass: " + str(actualDiagnosisClass))
    # End -  RecordTestingResultForDiagnosis





    #####################################################
    #
    # [MLJob::FinishTesting
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def FinishTesting(self):
        return
    # End - FinishTesting





    #####################################################
    #
    # [MLJob::PrintTestingStats
    # 
    # This is a public procedure, it is called by the client.
    #####################################################
    def PrintTestingStats(self):
        print("Test Results:")

        resultStr = ""
        for numItems in self.TestNumItemsPerClass:
            resultStr = resultStr + "    " + str(numItems)
        print("Num Items in Each Event Class: " + resultStr)

        if ((self.NumCorrectPredictionsInTesting > 0) and (self.NumSequencesTested > 0)):
            percentAccurate = float(self.NumCorrectPredictionsInTesting) / float(self.NumSequencesTested)
            percentAccurate = percentAccurate * 100.0
            fractionInt = round(percentAccurate)
            print("Accuracy: " + str(fractionInt) + "%")

        #print("True Positives: " + str(self.NumSequencesTested))
        #print("True Positives: " + str(self.NumCorrectPredictionsInTesting))

        #print("True Positives: " + str(self.NumTruePositivesInTesting))
        #print("True Negatives: " + str(self.NumTrueNegativesInTesting))
        #print("False Positives: " + str(self.NumFalsePositivesInTesting))
        #print("False Negatives: " + str(self.NumTruePositivesInTesting))
    
        if (False):
            total = float(self.NumTruePositivesInTesting + self.NumTruePositivesInTesting)
            if (total > 0):
                fractionFloat = float(float(self.NumTruePositivesInTesting) / total)
                fractionFloat = fractionFloat * 100.0
                fractionInt = round(fractionFloat)
                print("Sensitivity: " + str(fractionInt) + "%")
    
            total = float(self.NumTrueNegativesInTesting + self.NumFalsePositivesInTesting)
            if (total > 0):
                fractionFloat = float(float(self.NumTrueNegativesInTesting) / total)
                fractionFloat = fractionFloat * 100.0
                fractionInt = round(fractionFloat)
                print("Specificity: " + str(fractionInt) + "%")
        # End - if (False)
    # End - PrintTestingStats




    #####################################################
    #
    # [MLJob::GetRequestValueStr]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetRequestValueStr(self, valName, defaultVal):
        xmlNode = XMLTools_GetChildNode(self.CurrentRequestXMLNode, valName)
        if (xmlNode == None):
            print("MLJob::GetRequestValueStr: No XML Node valName=" + valName)
            return(defaultVal)

        resultStr = XMLTools_GetTextContents(xmlNode)
        if ((resultStr == None) or (resultStr == "")):
            return(defaultVal)

        return(resultStr)
    # End of GetRequestValueStr




    #####################################################
    #
    # [MLJob::GetRequestValueInt]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetRequestValueInt(self, valName, defaultVal):
        xmlNode = XMLTools_GetChildNode(self.CurrentRequestXMLNode, valName)
        if (xmlNode == None):
            print("MLJob::GetRequestValueInt: No XML Node. valName=[" + valName + "]")
            return(defaultVal)

        resultStr = XMLTools_GetTextContents(xmlNode)
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
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetRequestValueBool(self, valName, defaultVal):
        xmlNode = XMLTools_GetChildNode(self.CurrentRequestXMLNode, valName)
        if (xmlNode == None):
            print("MLJob::GetRequestValueBool: No XML Node. valName=" + valName)
            return(defaultVal)

        resultStr = XMLTools_GetTextContents(xmlNode)
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
    # This is a public procedure, it is called by the client.
    #####################################################
    def SetRequestValueStr(self, valName, valueStr):
        xmlNode = XMLTools_GetChildNode(self.OriginalRequestXMLNode, valName)
        if (xmlNode == None):
            xmlNode = self.JobXMLDOM.createElement(valName)
            self.OriginalRequestXMLNode.appendChild(xmlNode)

        XMLTools_RemoveAllChildNodes(xmlNode)
        textNode = self.JobXMLDOM.createTextNode(valueStr)
        xmlNode.appendChild(textNode)
    # End of SetRequestValueStr





    #####################################################
    #
    # [MLJob::GetJobControlStr]
    #
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetJobControlStr(self, valName, defaultVal):
        xmlNode = XMLTools_GetChildNode(self.JobControlXMLNode, valName)
        if (xmlNode == None):
            return(defaultValue)

        resultStr = XMLTools_GetTextContents(xmlNode)
        if ((resultStr == None) or (resultStr == "")):
            return(defaultValue)

        return(resultStr)
    # End of GetJobControlStr




    #####################################################
    #
    # [MLJob::SetJobControlStr]
    #
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
    # This is a public procedure, it is called by the client.
    #####################################################
    def GetDataParam(self, valName):
        xmlNode = XMLTools_GetChildNode(self.DataXMLNode, valName)
        if (xmlNode == None):
            return("")

        resultStr = XMLTools_GetTextContents(xmlNode)
        if ((resultStr == None) or (resultStr == "")):
            return("")

        return(resultStr)
    # End of GetDataParam




    #####################################################
    #
    # [MLJob::SetDataParam]
    #
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
        #print("MLJob::GetTestMatrix. matrixStr=" + matrixStr)
        matrix = self.MLJob_ConvertStringTo2DMatrix(matrixStr)

        return matrix
    # End - GetTestMatrix





    #####################################################
    #
    # [MLJob::CheckTestMatrix
    # 
    #####################################################
    def CheckTestMatrix(self, testName, matrixName, matrix):
        #print("CheckTestMatrix. matrix=" + str(matrix))

        if (self.TestListXMLNode == None):
            print("ERROR!!!!!!!! Missing Matrix! testName=" + testName + ", matrixName=" + matrixName)

        testXMLNode = XMLTools_GetChildNode(self.TestListXMLNode, testName)
        if (testXMLNode == None):
            print("ERROR!!!!!!!! Missing Matrix! testName=" + testName + ", matrixName=" + matrixName)

        matrixXMLNode = XMLTools_GetChildNode(testXMLNode, matrixName)
        if (matrixXMLNode == None):
            print("ERROR!!!!!!!! Missing Matrix! testName=" + testName + ", matrixName=" + matrixName)

        matrixStr = XMLTools_GetTextContents(matrixXMLNode)
        correctMatrix = self.MLJob_ConvertStringTo2DMatrix(matrixStr)
        #print("CheckTestMatrix. correctMatrix=" + str(correctMatrix))

        matrixSize = matrix.shape
        correctMatrixSize = correctMatrix.shape
        numDimensions = len(correctMatrixSize)
        if (len(matrixSize) != len(correctMatrixSize)):
            print("ERROR!!!!!!!! Different Number of Matrix dimensions! testName=" + testName + ", matrixName=" + matrixName)
            return
        if (len(matrixSize) != 2):
            print("ERROR!!!!!!!! Matrix is not two-dimensional! testName=" + testName + ", matrixName=" + matrixName)
            return
        if (matrixSize[0] != correctMatrixSize[0]):
            print("ERROR!!!!!!!! Matrix dimensions Are Different! testName=" + testName + ", matrixName=" + matrixName)
            return
        if (matrixSize[0] != correctMatrixSize[0]):
            print("ERROR!!!!!!!! Matrix dimensions Are Different! testName=" + testName + ", matrixName=" + matrixName)
            return

        #isEqual = (matrix == correctMatrix).all()
        isEqual = numpy.array_equiv(matrix, correctMatrix)
        #print("isEqual=" + str(isEqual))
        #print("CheckTestMatrix. matrix.size=" + str(matrix.shape))
        #print("CheckTestMatrix. correctMatrix.size=" + str(correctMatrix.shape))

        isEqual = True        
        for x in range(matrixSize[0]):
            for y in range(matrixSize[1]):
                #print("Check x=" + str(x) + ", y=" + str(y))
                valA = round(float(matrix[x][y]), 4)
                valB = round(float(correctMatrix[x][y]), 4)
                #print("matrix[0][" + str(y) + "]=" + str(matrix[0][y]))
                #print("correctMatrix[0][" + str(y) + "]=" + str(correctMatrix[0][y]))
                #print("valA=" + str(valA) + ", valB=" + str(valB))
                #if (float(matrix[0][y]) != float(correctMatrix[0][y])):
                if (valA != valB):
                    isEqual = False
                    print("ERROR!!!!!!!! Different Matrix! testName=" + testName + ", matrixName=" + matrixName)
                    print("Element [" + str(x) + "][" + str(y) + "] is different")
                    print("matrix=" + str(matrix))
                    print("correctMatrix=" + str(correctMatrix))
                    print("type of valA=" + str(type(valA)))
                    print("type of valB=" + str(type(valB)))
                    sys.exit(0)
                    break
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
        biasStr = XMLTools_GetTextContents(biasXMLNode)
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
    # [MLJob::GetNeuralNetMatrix
    # 
    #####################################################
    def GetNeuralNetMatrix(self, name):
        matrixXMLNode = XMLTools_GetChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (matrixXMLNode == None):
            return None

        matrixStr = XMLTools_GetTextContents(matrixXMLNode)
        resultMatrix = self.MLJob_ConvertStringTo2DMatrix(matrixStr)

        return resultMatrix
    # End - GetNeuralNetMatrix




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
        resultVector = MLJob_ConvertStringTo1DVector(vectorStr)

        return resultVector
    # End - GetNeuralNetVector




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
        biasStr = XMLTools_GetTextContents(biasXMLNode)

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



