#!/usr/bin/python3
################################################################################
#
# Copyright (c) 2023 Dawson Dean
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
# ML Experiment
#
################################################################################
import os
import sys
import math
import random
import xml.dom
from os.path import isfile
import decimal  # For float-to-string workaround

import statistics
from scipy import stats
from scipy.stats import spearmanr
import numpy as np

import xmlTools as xml
import tdfTools as tdf
import dataShow as DataShow
import mlJob as mlJob
import mlEngine as mlEngine
import tdfTimeFunctions as timefunc

# ROC
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error

# Cox Regression
import pandas as pd
from sksurv.linear_model import CoxnetSurvivalAnalysis


NEWLINE_STR = "\n"

MIN_SEQUENCE_LENGTH_FOR_CORRELATION  = 4

g_FloatFractionInTrain = 0.80






################################################################################
#
#
################################################################################
class TDFHistogram():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, varName):
        self.varName = ""
        self.varType = tdf.TDF_DATA_TYPE_INT
        self.DiscardValuesOutOfRange = False
        self.minVal = 0
        self.maxVal = 10
        self.numClasses = 1
        self.bucketSize = 1

        self.numVals = 0
        self.histogramBuckets = []
        self.histogramBucketCounts = []

        if ((varName is not None) and (varName != "")):
            self.Init(varName)
    # End -  __init__



    #####################################################
    # [TDFHistogram::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #
    # [TDFHistogram::Init]
    #
    #####################################################
    def Init(self, varName):
        labInfo, _, _, _ = tdf.TDF_ParseOneVariableName(varName)
        if (labInfo is None):
            print("!Error! Cannot parse variable: " + varName)
            return

        self.varName = varName
        self.varType = labInfo['dataType']
        self.minVal = labInfo['minVal']
        self.maxVal = labInfo['maxVal']

        if (self.varType == tdf.TDF_DATA_TYPE_INT):
            self.numClasses = 20
            valRange = float(self.maxVal - self.minVal)
            self.bucketSize = float(valRange) / float(self.numClasses)
        elif (self.varType == tdf.TDF_DATA_TYPE_FLOAT):
            self.numClasses = 20
            valRange = float(self.maxVal - self.minVal)
            self.bucketSize = float(valRange) / float(self.numClasses)
        elif (self.varType == tdf.TDF_DATA_TYPE_BOOL):
            self.numClasses = 2
            self.bucketSize = 1
        elif (self.varType == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
            self.numClasses = tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES
            self.bucketSize = 1
        else:
            self.numClasses = 1
            self.bucketSize = 1

        self.numVals = 0
        self.histogramBuckets = [0] * self.numClasses        
        self.histogramBucketCounts = [0] * self.numClasses        
    # End - Init



    #####################################################
    #
    # [TDFHistogram::InitEx]
    #
    #####################################################
    def InitEx(self, fIntType, fDiscardValuesOutOfRange, numBuckets, minVal, maxVal):
        self.varName = ""
        if (fIntType):
            self.varType = tdf.TDF_DATA_TYPE_INT
        else:
            self.varType = self.varType == tdf.TDF_DATA_TYPE_FLOAT

        self.DiscardValuesOutOfRange = fDiscardValuesOutOfRange
        self.numClasses = numBuckets
        self.minVal = minVal
        self.maxVal = maxVal

        if (self.varType == tdf.TDF_DATA_TYPE_INT):
            valRange = float(self.maxVal - self.minVal)
            self.bucketSize = float(valRange) / float(self.numClasses)
        elif (self.varType == tdf.TDF_DATA_TYPE_FLOAT):
            valRange = float(self.maxVal - self.minVal)
            self.bucketSize = float(valRange) / float(self.numClasses)
        else:
            self.bucketSize = 1

        self.numVals = 0
        self.histogramBuckets = [0] * self.numClasses        
        self.histogramBucketCounts = [0] * self.numClasses        
    # End - InitEx




    #####################################################
    #
    # [TDFHistogram::WriteToFile]
    #
    #####################################################
    def WriteToFile(self, filePathName):
        fDebug = False
        if (fDebug):
            print("TDFHistogram::WriteToFile. Start. filePathName=" + str(filePathName))

        try:
            fileH = os.remove(filePathName)
        except Exception:
            pass
        try:
            fileH = open(filePathName, "w+")
        except Exception:
            print("WriteToFile Error! Cannot open file: " + filePathName)
            return

        resultLine = "Histogram, Vers=1"
        resultLine += ", VarType=" + str(self.varType)
        resultLine += ", DiscardValuesOutOfRange=" + str(self.DiscardValuesOutOfRange)
        resultLine += ", Min=" + str(self.minVal)
        resultLine += ", Max=" + str(self.maxVal) 
        resultLine += ", BucketSize=" + str(self.bucketSize)
        resultLine += ", NumClasses=" + str(self.numClasses)
        resultLine += ", NumVals=" + str(self.numVals)
        resultLine += NEWLINE_STR
        fileH.write(resultLine)

        if (fDebug):
            print("TDFHistogram::WriteToFile. Saved Header. resultLine=" + str(resultLine))

        for bucketNum in range(self.numClasses):
            weight = self.histogramBuckets[bucketNum]
            count = self.histogramBucketCounts[bucketNum]
            resultLine = str(bucketNum) + ":" + str(weight) + "/" + str(count) + NEWLINE_STR

            fileH.write(resultLine)
            if (fDebug):
                print("TDFHistogram::WriteToFile. resultLine=" + str(resultLine))
        # End - for index in range(self.numClasses):

        fileH.close()
    # End - WriteToFile




    #####################################################
    #
    # [TDFHistogram::ReadFromFile]
    #
    #####################################################
    def ReadFromFile(self, filePathName):
        fDebug = False
        lineNum = 0

        try:
            fileH = open(filePathName, "r")
        except Exception:
            print("ReadFromFile Error! Cannot open file: " + filePathName)
            return

        for line in fileH:
            line = line.lstrip().rstrip()
            if (fDebug):
                print(">> line=" + line)

            # The first line is the header, which lets 
            if (lineNum == 0):
                assignmentList = line.split(";")
                for assignment in assignmentList:
                    words = assignment.split("=")
                    propName = words[0]
                    if (propName == "Vers"):
                        pass
                    elif (propName == "VarType"):
                        self.varType = int(words[1])
                    elif (propName == "DiscardValuesOutOfRange"):
                        self.DiscardValuesOutOfRange = int(words[1])
                    elif (propName == "Min"):
                        self.minVal = float(words[1])
                    elif (propName == "Max"):
                        self.maxVal = float(words[1])
                    elif (propName == "BucketSize"):
                        self.bucketSize = float(words[1])
                    elif (propName == "NumClasses"):
                        self.numClasses = int(words[1])
                    elif (propName == "NumVals"):
                        self.numVals = int(words[1])
                # End - for assignment in assignmentList:

                self.InitEx((self.varType == tdf.TDF_DATA_TYPE_INT), 
                            self.DiscardValuesOutOfRange, 
                            self.numClasses, 
                            self.minVal, 
                            self.maxVal)             
            # End - if (lineNum == 0):
            else:  # Data line
                words = line.split(":")
                bucketNum = int(words[0])
                weightCountStr = words[1]
                words2 = weightCountStr.split("/")
                weight = float(words2[0])
                count = int(words2[1])
                self.histogramBuckets[bucketNum] = weight
                self.histogramBucketCounts[bucketNum] = count
            # End - else (normal data line)

            lineNum += 1
        # End - for line in fileH:

        fileH.close()
    # End - ReadFromFile




    #####################################################
    #
    # [TDFHistogram::AddValue]
    #
    #####################################################
    def AddValue(self, value):
        # Ignore values of 0
        if (value <= 0):
            return

        if ((self.DiscardValuesOutOfRange) and ((value < self.minVal) or (value > self.maxVal))):
            return

        if (value < self.minVal):
            value = self.minVal
        offset = value - self.minVal

        bucketNum = round(offset / self.bucketSize)
        if (bucketNum >= self.numClasses):
            bucketNum = self.numClasses - 1

        self.numVals += 1
        self.histogramBuckets[bucketNum] += 1
        self.histogramBucketCounts[bucketNum] += 1
    # End - AddValue



    #####################################################
    #
    # [TDFHistogram::AddWeightedValue]
    #
    #####################################################
    def AddWeightedValue(self, value, weight):
        fDebug = False
        if (fDebug):
            print("TDFHistogram::AddWeightedValue. value=" + str(value) + ", weight=" + str(weight))

        # Ignore values of less than 0. However, some 0 values are meaningful, so keep those.
        if (value < 0):
            if (fDebug):
                print("TDFHistogram::AddWeightedValue. Discard 0 val")
            return

        if ((self.DiscardValuesOutOfRange) and ((value < self.minVal) or (value > self.maxVal))):
            if (fDebug):
                print("TDFHistogram::AddWeightedValue. Discard value out of range")
                print("    minVal=" + str(self.minVal) + ", maxVal=" + str(self.maxVal))
            return

        if (fDebug):
            print("TDFHistogram::AddWeightedValue. Keeping value=" + str(value) + ", weight=" + str(weight))

        if (value < self.minVal):
            value = self.minVal

        offset = value - self.minVal
        bucketNum = round(offset / self.bucketSize)
        if (bucketNum >= self.numClasses):
            bucketNum = self.numClasses - 1

        if (fDebug):
            print("TDFHistogram::AddWeightedValue. offset=" + str(offset) + ", bucketNum=" + str(bucketNum))

        self.numVals += 1
        self.histogramBuckets[bucketNum] += weight
        self.histogramBucketCounts[bucketNum] += 1
    # End - AddWeightedValue



    #####################################################
    #
    # [TDFHistogram::AverageAllValues]
    #
    #####################################################
    def AverageAllValues(self):
        for bucketNum in range(self.numClasses):
            weight = self.histogramBuckets[bucketNum]
            count = self.histogramBucketCounts[bucketNum]

            if (count > 0):
                weight = weight / count
                count = 1
            else:
                weight = 0
                count = 0

            self.histogramBuckets[bucketNum] = weight
            self.histogramBucketCounts[bucketNum] = count
        # End - for index in range(self.numClasses):
    # End - AverageAllValues




    #####################################################
    # [TDFHistogram::GetNumBuckets]
    #####################################################
    def GetNumBuckets(self):
        return self.numClasses
    # End - GetNumBuckets()

    #####################################################
    # [TDFHistogram::GetBuckets]
    #####################################################
    def GetBuckets(self):
        return self.histogramBuckets
    # End - GetBuckets()

    #####################################################
    # [TDFHistogram::GetTotalNumVals]
    #####################################################
    def GetTotalNumVals(self):
        return self.numVals
    # End - GetTotalNumVals()



    #####################################################
    # [TDFHistogram::GetMeanNumVal]
    #####################################################
    def GetMeanNumVal(self):
        totalSum = 0
        for bucketNum in range(self.numClasses):
            totalSum += self.histogramBuckets[bucketNum]
        # End - for index in range(self.numClasses):

        meanVal = round((totalSum / self.numVals), 2)
        return meanVal
    # End - GetMeanNumVal()



    #####################################################
    #
    # [TDFHistogram::GetBucketsAsPercentages]
    #
    #####################################################
    def GetBucketsAsPercentages(self):
        fDebug = False
        if (fDebug):
            print("GetBucketsAsPercentages. self.numClasses = " + str(self.numClasses))

        resultArray = self.histogramBuckets
        if (fDebug):
            print("GetBucketsAsPercentages. resultArray = " + str(resultArray))
        sumOfElements = sum(resultArray)
        if (fDebug):
            print("GetBucketsAsPercentages. sumOfElements = " + str(sumOfElements))

        if (sumOfElements <= 0):
            scaledList = [0] * len(resultArray)
        else:
            scaledList = [(float(x) / sumOfElements) * 100.0 for x in resultArray]
        if (fDebug):
            print("GetBucketsAsPercentages. scaledList = " + str(scaledList))

        return scaledList
    # End - GetBucketsAsPercentages()


    #####################################################
    #
    # [TDFHistogram::DrawBarGraph]
    #
    #####################################################
    def DrawBarGraph(self, graphTitleStr, xLabelStr, yLabelStr, graphFilePath):
        xAxisList = []
        for index in range(self.numClasses):
            bucketNameStr = str(self.minVal + (self.bucketSize * index))
            if (index % 1):
                bucketNameStr = "\n" + bucketNameStr
            xAxisList.append(bucketNameStr)
        # End - for index in range(self.histogramBuckets)

        DataShow.DrawBarGraph(graphTitleStr, 
                        xLabelStr, xAxisList, 
                        yLabelStr, self.histogramBuckets, 
                        False, graphFilePath)
    # End - DrawBarGraph()



    #####################################################
    #
    # [TDFHistogram::PrintStats]
    #
    #####################################################
    def PrintStats(self):
        print("Num values: " + str(self.numVals))
        print("Mean value: " + str(self.GetMeanNumVal()))
    # End - PrintStats()

# End - class TDFHistogram

















################################################################################
#
# Class MLResultsFile
#
################################################################################
class MLResultsFile():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, filePathname):
        self.resultFilePathName = filePathname
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    # [GetResultForInputOutputPair]
    #####################################################
    def GetResultForInputOutputPair(self, inputName, outputName):
        fDebug = False
        resultLine = inputName + "~" + outputName + ":"
        if (fDebug):
            print("Look for " + resultLine)

        # Make sure the result file name exists.
        if (not os.path.isfile(self.resultFilePathName)):
            fileH = open(self.resultFilePathName, "a")
            fileH.close()

        # It is possible we already found this correlation on a previous instance
        # of this program that crashed. In this case, we are running on a restarted
        # process, so do not waste time recomputing work that is already done.
        # Look for this pair in the result file
        with open(self.resultFilePathName) as fileH:
            for line in fileH:
                line = line.lstrip().rstrip()
                # <><><> Remove this when I both (1) fix existing data files (2) fix the generator code
                #line = line.replace("::", ":")

                if (fDebug):
                    print("Line = " + line)
                if (line.startswith(resultLine)):
                    lineParts = line.split(':')
                    if (fDebug):
                        print("lineParts = " + str(lineParts))
                    resultStr = "Unknown"
                    if (len(lineParts) > 1):
                        resultStr = lineParts[1].rstrip()
                        if (fDebug):
                            print("resultStr = " + str(resultStr))

                    return True, resultStr
                # End - if (line.startswith(resultLine)):
            # End - for line in fileH:
        # End - with open(resultFilePathName) as fileH:

        return False, ""
    # End - GetResultForInputOutputPair



    #####################################################
    # [AppendResult]
    #####################################################
    def AppendResult(self, inputName, outputName, resultValue):
        fDebug = False
        resultLine = inputName + "~" + outputName + ":" + str(resultValue) + NEWLINE_STR
        if (fDebug):
            print("AppendResult. resultValue=" + str(resultValue) + ", resultLine = " + str(resultLine))

        fileH = open(self.resultFilePathName, "a")
        fileH.write(resultLine)
        fileH.close()
    # End - AppendResult



    ################################################################################
    #
    # [GetInputsForOneOutput]
    #
    ################################################################################
    def GetInputsForOneOutput(self, outputName, inputVarList, fIncludeMissingValues):
        fDebug = False
        inputValueDistList = []

        if (fDebug):
            print("GetInputsForOneOutput. outputName = " + str(outputName))
            print("GetInputsForOneOutput. inputVarList = " + str(inputVarList))

        # Make a list of input variables with their values
        with open(self.resultFilePathName) as fileH:
            for inputVarname in inputVarList:
                resultFloat = tdf.TDF_INVALID_VALUE
                fileH.seek(0)
                resultLine = inputVarname + "~" + outputName + ":"
                for line in fileH:
                    line = line.lstrip()
                    # <><><> Remove this when I both (1) fix existing data files (2) fix the generator code
                    #line = line.replace("::", ":")
                    if (line.startswith(resultLine)):
                        if (fDebug):
                            print("GetInputsForOneOutput. Found inputVarname = " + inputVarname 
                                + ", outputName = " + outputName 
                                + ", resultLine=" + line)
                        lineParts = line.split(':')
                        if (len(lineParts) > 1):
                            resultStr = lineParts[1].rstrip()
                            if (fDebug):
                                print("GetInputsForOneOutputFromResultsFile. resultStr = " + resultStr)
                            try:
                                resultFloat = float(resultStr)
                            except Exception:
                                print("BUG!!!! GetInputsForOneOutputFromResultsFile hit an exception when converting a number")
                                print("           resultStr=" + str(resultStr))
                                print("           line=" + str(line))
                                sys.exit(0)
                        # End - if (len(lineParts) > 1):

                        # Stop looking when we find a value
                        break
                    # End - if (line.startswith(resultLine)):               
                # End - for line in fileH:

                if ((math.isnan(resultFloat)) or (resultFloat == tdf.TDF_INVALID_VALUE)):
                    if (fIncludeMissingValues):
                        inputValueDistList.append({'n': inputVarname, 'v': resultFloat, 'av': tdf.TDF_INVALID_VALUE})
                # Otherwise, it is a valid number
                else:
                    inputValueDistList.append({'n': inputVarname, 'v': resultFloat, 'av': abs(resultFloat)})
            # End - for inputVarname in inputVarList:
        # End - with open(self.resultFilePathName) as fileH:

        return inputValueDistList
    # End - GetInputsForOneOutput




    ################################################################################
    #
    # [GetOneInputForOneOutput]
    #
    # A public procedure.
    ################################################################################
    def GetOneInputForOneOutput(self, outputName):
        fDebug = False
        resultFloat = tdf.TDF_INVALID_VALUE

        # Make a list of input variables with their values
        with open(self.resultFilePathName) as fileH:
            fileH.seek(0)
            resultLine = inputVarname + "~" + outputName + ":"
            for line in fileH:
                line = line.lstrip()
                # <><><> Remove this when I both (1) fix existing data files (2) fix the generator code
                #line = line.replace("::", ":")
                if (line.startswith(resultLine)):
                    if (fDebug):
                        print("GetOneInputForOneOutput. Found inputVarname = " + inputVarname 
                            + ", outputName = " + outputName 
                            + ", resultLine=" + line)
                    lineParts = line.split(':')
                    if (len(lineParts) > 1):
                        resultStr = lineParts[1].rstrip()
                        if (fDebug):
                            print("GetOneInputForOneOutput. resultStr = " + resultStr)
                        try:
                            resultFloat = float(resultStr)
                        except Exception:
                            print("BUG!!!! GetOneInputForOneOutput hit an exception when converting a number")
                            print("           resultStr=" + str(resultStr))
                            print("           line=" + str(line))
                            sys.exit(0)
                    # End - if (len(lineParts) > 1):

                    # Stop looking when we find a value
                    break
                # End - if (line.startswith(resultLine)):               
            # End - for line in fileH:

            if ((math.isnan(resultFloat)) or (resultFloat == tdf.TDF_INVALID_VALUE)):
                resultFloat = tdf.TDF_INVALID_VALUE
         # End - with open(self.resultFilePathName) as fileH:

        return resultFloat
    # End - GetOneInputForOneOutput




    ################################################################################
    #
    # [MakeRelationshipBarGraphs]
    #
    ################################################################################
    def MakeRelationshipBarGraphs(self, 
                                numImportantVariables, 
                                relationName,
                                graphFilePathNamePrefix):
        fDebug = False

        # Load the raw result file into a list in memory
        allInputVars, allOutputVars, allResults = self.LoadIntoDicts()
        if (fDebug):
            print("allInputVars = " + str(allInputVars))
            print("allOutputVars = " + str(allOutputVars))
            print("allResults = " + str(allResults))

        for outputVarname in allOutputVars:
            if (outputVarname not in allResults):
                continue
            relationshipDict = allResults[outputVarname]
            if (fDebug):
                print("outputVarname = " + str(outputVarname))
                print("relationshipDict = " + str(relationshipDict))

            sortedList = sorted(relationshipDict.items(), key=SortFunction, reverse=True)
            if (fDebug):
                print("sortedList = " + str(sortedList))

            MakeNInputsToSingleOutputBarGraph(
                                sortedList, 
                                outputVarname, 
                                numImportantVariables, 
                                relationName, 
                                graphFilePathNamePrefix + outputVarname + ".jpg")
        # for outputVarname in allOutputVars:
    # End - MakeRelationshipBarGraphs




    ################################################################################
    #
    # [LoadIntoDicts]
    #
    ################################################################################
    def LoadIntoDicts(self):
        fDebug = False
        allInputVars = []
        allOutputVars = []
        allResults = {}

        # Load the file into a list in memory
        with open(self.resultFilePathName) as fileH:
            for line in fileH:
                line = line.lstrip()
                line = line.rstrip()
                if (fDebug):
                    print(">> line=" + line)

                words = line.split(":")
                varList = words[0]
                coeffStr = words[1]
                coeffFloat = float(coeffStr)
                words = varList.split("~")
                inputVar = words[0]
                outputVar = words[1]
                if (fDebug):
                    print("in=" + inputVar + ", out=" + outputVar + "r=" + str(coeffFloat))

                # Find the list of inputs for this output variable.
                if outputVar in allResults:
                    coeffDict = allResults[outputVar]
                else:
                    coeffDict = {}

                coeffDict[inputVar] = coeffFloat
                allResults[outputVar] = coeffDict
                if (inputVar not in allInputVars):
                    allInputVars.append(inputVar)
                if (outputVar not in allOutputVars):
                    allOutputVars.append(outputVar)
            # End - for line in fileH:

            fileH.close()
        # End - with open(self.resultFilePathName) as fileH:

        return allInputVars, allOutputVars, allResults
    # End - LoadIntoDicts





    ################################################################################
    #
    # [GraphTopNValuesForOneResult]
    #
    # "DATASHOW_ONLY_SHOW_VALUE_SUFFIX"
    #
    ################################################################################
    def GraphTopNValuesForOneResult(self, 
                    graphTitleStr,
                    outputName, 
                    inputVarList,
                    xAxisName,
                    maxItemsInGraph,
                    formatOptionsStr,
                    graphFilePathName):
        fDebug = False
        if (fDebug):
            print("GraphTopNValuesForOneResult. outputName = " + str(outputName))
            print("GraphTopNValuesForOneResult. inputVarList = " + str(inputVarList))
            print("GraphTopNValuesForOneResult. graphFilePathName = " + str(graphFilePathName))

        # Make sure the result file name exists.
        if (not os.path.isfile(self.resultFilePathName)):
            print("ERROR!!! GraphTopNValuesForOneResult. Missing Results file. resultsFilePathname = " + str(self.resultFilePathName))
            return

        # Make a list of input variables with their values
        inputValueDistList = self.GetInputsForOneOutput(outputName, inputVarList, False)
        if (fDebug):
            print("GraphTopNValuesForOneResult. inputValueDistList = " + str(inputValueDistList))

         # Rank them from highest to lowest
        sortedInputValueDistList = sorted(inputValueDistList, key=ImportanceDictionarySortFunction, reverse=True) 
        if (fDebug):
            print("GraphTopNValuesForOneResult. sortedInputValueDistList = " 
                            + str(sortedInputValueDistList))

        # Build separate lists of the N-highest labels and values
        yAxisNameList = []
        xAxisValueList = []
        for currentEntry in sortedInputValueDistList:
            yAxisNameList.append(currentEntry['n'])
            xAxisValueList.append(currentEntry['av'])
            if (len(yAxisNameList) >= maxItemsInGraph):
                break
        # End - for currentEntry in sortedInputValueDistList:
        if (fDebug):
            print("GraphTopNValuesForOneResult. yAxisNameList = " + str(yAxisNameList))
            print("GraphTopNValuesForOneResult. xAxisValueList = " + str(xAxisValueList))

        # Reverse the lists. This puts the highest score at top, and the lowest at the origin.
        yAxisNameList.reverse()
        xAxisValueList.reverse()
        if (fDebug):
            print("Reversed")
            print("GraphTopNValuesForOneResult. yAxisNameList = " + str(yAxisNameList))
            print("GraphTopNValuesForOneResult. xAxisValueList = " + str(xAxisValueList))


        if ("DATASHOW_ONLY_SHOW_VALUE_SUFFIX" in formatOptionsStr):
            numItems = len(yAxisNameList)
            for index in range(numItems):
                valueStr = yAxisNameList[index]
                strParts = valueStr.split(".")
                numParts = len(strParts)
                valueStr = strParts[numParts - 1]
                yAxisNameList[index] = valueStr
            # End - for index in range(numItems)
        # if ("DATASHOW_ONLY_SHOW_VALUE_SUFFIX" in formatOptionsStr):

        DataShow.DrawHorizontalBarGraph(graphTitleStr,
                                yAxisNameList,
                                xAxisName,
                                xAxisValueList,
                                False,
                                graphFilePathName)
    # End - GraphTopNValuesForOneResult






    ################################################################################
    #
    # [GraphValuesForOneResult]
    #
    # A public procedure.
    ################################################################################
    def GraphValuesForOneResult(self, 
                    graphTitleStr,
                    outputName, 
                    inputVarList,
                    xAxisName,
                    xAxisNameList,
                    graphFilePathName):
        fDebug = False
        if (fDebug):
            print("GraphValuesForOneResult. outputName = " + str(outputName))
            print("GraphValuesForOneResult. inputVarList = " + str(inputVarList))
            print("GraphValuesForOneResult. graphFilePathName = " + str(graphFilePathName))

        # Make sure the result file name exists.
        if (not os.path.isfile(self.resultFilePathName)):
            print("ERROR!!! GraphTopNValuesForOneResult. Missing Results file. resultsFilePathname = " + str(self.resultFilePathName))
            return

        # Make a list of input variables with their values
        inputValueDistList = self.GetInputsForOneOutput(outputName, inputVarList, True)
        if (fDebug):
            print("GraphTopNValuesForOneResult. inputValueDistList = " + str(inputValueDistList))

        # Build separate lists of the labels and values
        yAxisValueList = []
        for currentEntry in inputValueDistList:
            yAxisValueList.append(currentEntry['av'])
        # End - for currentEntry in sortedInputValueDistList:

        if (fDebug):
            print("GraphTopNValuesForOneResult. yAxisValueList = " + str(yAxisValueList))
            print("GraphTopNValuesForOneResult. xAxisNameList = " + str(xAxisNameList))


        DataShow.DrawBarGraph(graphTitleStr, 
                 xAxisName, 
                xAxisNameList, 
                "", 
                yAxisValueList, 
                False, 
                graphFilePathName)
    # End - GraphTopNValuesForOneResult









    ################################################################################
    #
    # [MakeExcelFile]
    #
    ################################################################################
    def MakeExcelFile(self, outputNamePrefix, tableFilePathName):
        fDebug = False

        # Load the raw result file into a list in memory
        allInputVars, allOutputVars, allResults = self.LoadIntoDicts()
        if (fDebug):
            print("allInputVars = " + str(allInputVars))
            print("allOutputVars = " + str(allOutputVars))
            print("allResults = " + str(allResults))

        # Make a list of all of the input variables. The column starts with a blank
        # entry, which will be the row name in each row.
        columnHeaderStr = " ,"
        for inputVarname in allInputVars:
            columnHeaderStr += (inputVarname + ",")
        columnHeaderStr = columnHeaderStr[:-1]
        if (fDebug):
            print("columnHeaderStr = " + str(columnHeaderStr))
            print("tableFilePathName = " + str(tableFilePathName))

        fileH = DataShow.StartExcelFile(tableFilePathName, columnHeaderStr)

        # For each output variable, make a bar graph and excel file
        for outputVarname in allOutputVars:
            if (fDebug):
                print("outputVarname = " + str(outputVarname))

            if (outputVarname not in allResults):
                print("ERROR! MakeExcelFile tried to find an output var not in list. var=" 
                        + outputVarname)
                continue
            relationshipDict = allResults[outputVarname]
            if (fDebug):
                print("outputVarname = " + str(outputVarname) + ", relationshipDict = " + str(relationshipDict))

            currentRowStr = outputNamePrefix + outputVarname + ","
            for inputVarname in allInputVars:
                if (inputVarname in relationshipDict):
                    corrValue = round(relationshipDict[inputVarname], 4)
                    currentRowStr += (str(corrValue) + ",")
                else:
                    currentRowStr += ("-,")
            # for inputVarname in inputVarList:
            currentRowStr = currentRowStr[:-1]

            if (fDebug):
                print("currentRowStr = " + str(currentRowStr))

            DataShow.WriteOneLineToExcelFile(fileH, currentRowStr)
        # for outputVarname in outputVarList:

        DataShow.FinishExcelFile(fileH)
    # End - MakeExcelFile




    ################################################################################
    #
    # [WriteExcelFileForOneResult]
    #
    # A public procedure.
    ################################################################################
    def WriteExcelFileForOneResult(self,
                            relationNameStr,
                            outputName, 
                            inputVarList,
                            excelFileNameName):
        fDebug = False
        if (fDebug):
            print("WriteExcelFileForOneResult. outputName = " + str(outputName))
            print("WriteExcelFileForOneResult. inputVarList = " + str(inputVarList))
            print("WriteExcelFileForOneResult. excelFileNameName = " + str(excelFileNameName))

        # Make sure the result file name exists.
        if (not os.path.isfile(self.resultFilePathName)):
            print("ERROR!!! WriteExcelFileForOneResult. Missing Results file. self.resultFilePathName = " 
                    + str(self.resultFilePathName))
            return

        # Make a list of input variables with their values
        inputValueDistList = self.GetInputsForOneOutput(outputName, inputVarList, False)
        if (fDebug):
            print("WriteExcelFileForOneResult. inputValueDistList = " + str(inputValueDistList))

         # Rank them from highest to lowest
        sortedInputValueDistList = sorted(inputValueDistList, key=ImportanceDictionarySortFunction, reverse=True) 
        if (fDebug):
            print("WriteExcelFileForOneResult. sortedInputValueDistList = " 
                            + str(sortedInputValueDistList))

        # Build separate lists of the N-highest labels and values
        varColumn = []
        valueColumn = []
        for currentEntry in sortedInputValueDistList:
            varColumn.append(currentEntry['n'])
            valueColumn.append(currentEntry['av'])
        # End - for currentEntry in sortedInputValueDistList:

        if (fDebug):
            print("WriteExcelFileForOneResult. varColumn = " + str(varColumn))
            print("WriteExcelFileForOneResult. valueColumn = " + str(valueColumn))

        # Reverse the lists. This puts the highest score at top, and the lowest at the origin.
        #varColumn.reverse()
        #valueColumn.reverse()

        columnHeaderStr = "Variable, " + relationNameStr
        DataShow.WriteReportToExcelFile(excelFileNameName, columnHeaderStr, (varColumn, valueColumn))
    # End - WriteExcelFileForOneResult

# End - class MLResultsFile












################################################################################
# A public procedure.
################################################################################
def MLExperiment_StartExperiment(labDirPathName):
    fDebug = False

    if not os.path.exists(labDirPathName):
        if (fDebug):
            print("MLExperiment_StartExperiment. Create dir")
        os.makedirs(labDirPathName)
    # End - if not os.path.exists(labDirPathName):
# End - MLExperiment_StartExperiment




################################################################################
#
# [UpdateOneJobFile]
#
# <><> TODO <><> Move this into mlJob once the format is finalized.
################################################################################
def UpdateOneJobFile(srcFilePathName, contentTransformList, destFilePathName):
    fDebug = False

    # Read the template file into an XML object that we can edit.
    fileH = open(srcFilePathName, "r")
    fileContentsText = fileH.read()
    fileH.close()

    # Parse the text string into am XML DOM
    jobFileXMLDOM = xml.XMLTools_ParseStringToDOM(fileContentsText)
    if (jobFileXMLDOM is None):
        print("\n\nError. Cannot parse the file: " + srcFilePathName)
        return

    jobFileRootXMLNode = xml.XMLTools_GetNamedElementInDocument(jobFileXMLDOM, 
                                mlJob.ROOT_ELEMENT_NAME)
    if (jobFileRootXMLNode is None):
        print("\n\nError. Invalid Job in the file: " + srcFilePathName)
        return
   
    # This loop applies each transform.
    # We often have to change several things in a single file to make a new file
    # that is internally consistent.
    for contentTransform in contentTransformList:
        if (fDebug):
            print("UpdateOneJobFile: contentTransform=" + str(contentTransform))
            print("UpdateOneJobFile: Look for node: " + contentTransform["xmlPath"])
        xmlNode = xml.XMLTools_GetChildNodeFromPath(jobFileRootXMLNode, 
                                                    contentTransform["xmlPath"])

        # Don't freak out if a node we want to edit is missing. There may be several transforms,
        # each changes a different type of file.
        if (xmlNode is None):
            continue
        nodeContentsStr = xml.XMLTools_GetTextContents(xmlNode)
        if (fDebug):
            print("UpdateOneJobFile. Found old node contents: [" + nodeContentsStr + "]")

        # This is old code used for conditional transforms, that only change nodes with specific values.
        #oldVal = contentTransform["oldValue"].lower()
        #if ((oldVal != "") and (oldVal != nodeContentsStr.lower())):
        #   continue

        ###################
        if (contentTransform["op"].lower() == "set"):
            nodeContentsStr = contentTransform["newValue"]
        ###################
        elif (contentTransform["op"].lower() == "modify"):
            if (fDebug):            
                print("UpdateOneJobFile. modify: " + contentTransform["oldValue"]
                        + "   with: " + contentTransform["newValue"])
            nodeContentsStr = nodeContentsStr.replace(contentTransform["oldValue"], 
                                                    contentTransform["newValue"])
        ###################
        elif (contentTransform["op"].lower() == "append"):
            pass
        ###################
        elif (contentTransform["op"].lower() == "increment"):
            pass

        xml.XMLTools_SetTextContents(xmlNode, nodeContentsStr)
    # End - for contentTransform in contentTransformList:

    newContentsText = jobFileXMLDOM.toprettyxml(indent="", newl="", encoding=None)
    # The prettyprinter does not end with a newline. Add one if it is necessary.
    # But, don't always add one, or else they can accumulate with each pass 
    # through this code.
    if (not newContentsText.endswith("\n")):
        newContentsText = newContentsText + "\n"
    if (fDebug):
        print("UpdateOneJobFile. Found old node contents: [" + nodeContentsStr + "]")

    # Write the modified file to the new location.
    # This may be the same or different than the original template we edited.
    fileH = open(destFilePathName, "w+")
    fileH.write(newContentsText)
    fileH.close()
# End - UpdateOneJobFile





################################################################################
#
# [MakeTestJobWithNewInputs]
#
################################################################################
def MakeTestJobWithNewInputs(templateFilePathName, inputStr, outputVarName, 
                            valueFilterStr, newPropName, newPropValueStr, destFilePathName):
    fDebug = False

    # Do not overwrite a lab.
    # This is tricky - but once we run a test, the program may be stopped, crashed, whaveter,
    # and restart later. Do not repeat old work, since a single experiment of N tests may
    # take a long time to run (like 1 or 2 weeks). So, to re-do an experiment, requires
    # deleting the job files and reconstructing them.
    if os.path.exists(destFilePathName):
        if (fDebug):
            print("MakeTestJobWithNewInputs. File already exists: =" 
                    + str(templateFilePathName))
        return
    # End - if os.path.exists(destFilePathName):

    # Build the transform list
    contentTransformList = [
        {"op": "set", "xmlPath": "Network/InputLayer/InputValues", "newValue": inputStr},
        {"op": "set", "xmlPath": "Network/ResultValue", "newValue": outputVarName},
        {"op": "set", "xmlPath": "Data/ValueFilter", "newValue": valueFilterStr},
        {"op": "set", "xmlPath": "Training/NumEpochs", "newValue": "15"}
    ]
    if ((newPropValueStr is not None) and (newPropValueStr != "")):
        contentTransformList.append({"op": "set", "xmlPath": newPropName, "newValue": newPropValueStr})

    if (fDebug):
        print("MakeTestJobWithNewInputs. Make new file. contentTransformList=" + str(contentTransformList))

    # Use the template to make a new job file
    UpdateOneJobFile(templateFilePathName, contentTransformList, destFilePathName)
# End - MakeTestJobWithNewInputs






################################################################################
#
# [MLExperiment_RunAllJobsInDirectory]
#
################################################################################
def MLExperiment_RunAllJobsInDirectory(dirPathName):
    fDebug = False
    if (fDebug):
        print("MLExperiment_RunAllJobsInDirectory. dirPathName=" + dirPathName)

    # Run each job. This ASSUMES we run every job in the directory
    fileNameList = os.listdir(dirPathName)
    for fileName in fileNameList:
        srcFilePathName = os.path.join(dirPathName, fileName)
        if (fDebug):
            print("MLExperiment_RunAllJobsInDirectory. fileName = " + fileName 
                    + ", srcFilePathName = " + srcFilePathName)

        if ((os.path.exists(srcFilePathName)) and (isfile(srcFilePathName))):
            # Read the job to see if it has completed
            fRunJob = True
            jobErr, job = mlJob.MLJob_ReadExistingMLJob(srcFilePathName)
            if (mlJob.JOB_E_NO_ERROR == jobErr):
                jobStatus, _, _ = job.GetJobStatus()
                if (fDebug):
                    print("MLExperiment_RunOneJob. jobStatus=" + str(jobStatus))

                if (mlJob.MLJOB_STATUS_DONE == jobStatus):
                    fRunJob = False
            # End - if (mlJob.JOB_E_NO_ERROR == jobErr):

            print("\n========================================\n" + srcFilePathName)
            if (fRunJob):
                mlEngine.MLEngine_RunJob(srcFilePathName, srcFilePathName, False)
            else:
                print("    Done")
        # End - if ((os.path.exists(srcFilePathName)) and (isfile(srcFilePathName))):
    # End - for fileName in fileNameList:
# End - MLExperiment_RunAllJobsInDirectory






################################################################################
#
# [MLExperiment_RunAllJobsInSpecificDirectories]
#
################################################################################
def MLExperiment_RunAllJobsInSpecificDirectories(dirPathName, subDirList):
    fDebug = False
    if (fDebug):
        print("MLExperiment_RunAllJobsInSpecificDirectories. dirPathName=" + dirPathName)

    for subDirName in subDirList:
        subDirPathName = os.path.join(dirPathName, subDirName)
        if (fDebug):
            print("MLExperiment_RunAllJobsInSpecificDirectories. fileName = " + fileName 
                    + ", srcFilePathName = " + srcFilePathName)

        if (os.path.exists(subDirPathName)):
            MLExperiment_RunAllJobsInDirectory(subDirPathName)
        # End - if (os.path.exists(subDirPathName))
    # End - for subDirName in subDirList:
# End - MLExperiment_RunAllJobsInSpecificDirectories





################################################################################
#
# [MLExperiment_RunJobsWithDifferentLR]
#
# Try a template job with different LR values.
################################################################################
def MLExperiment_RunJobsWithDifferentLR(labDirPathName,
                                        jobTemplateFilePathName,
                                        jobInputVariablesStr,
                                        outputVarName,
                                        valueFilterStr):
    fDebug = False
    newLRName = "Training/LearningRate"

    if (fDebug):
        print("MLExperiment_RunJobsWithDifferentLR.")
        print("    labDirPathName=" + str(labDirPathName))
        print("    jobTemplateFilePathName=" + str(jobTemplateFilePathName))
        print("    jobInputVariablesStr=" + str(jobInputVariablesStr))
        print("    outputVarName=" + str(outputVarName))
        print("    valueFilterStr=" + str(valueFilterStr))

    MLExperiment_StartExperiment(labDirPathName)

    # Workaround for avoiding scientific notation when converting small floats to a string.
    ctx = decimal.Context()
    ctx.prec = 20

    # Now make a separate job for each test.
    experimentNum = 0
    LRList = [0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 50]
    for currentLR in LRList:
        if (fDebug):
            print("Make job for experiment " + str(experimentNum))
        lrStr = format(ctx.create_decimal(repr(currentLR)), 'f')

        testJobFilePath = labDirPathName + outputVarName + "_test" + str(experimentNum) + ".txt"
        if (fDebug):
            print("   labDirPathName=" + str(labDirPathName))
            print("   testJobFilePath=" + str(testJobFilePath))

        MakeTestJobWithNewInputs(jobTemplateFilePathName, jobInputVariablesStr, outputVarName, 
                                valueFilterStr, newLRName, lrStr, testJobFilePath)

        experimentNum += 1
    # End - for currentLR in LRList

    # Run each job. This ASSUMES we run every job in the directory
    MLExperiment_RunAllJobsInDirectory(labDirPathName)
# End - MLExperiment_RunJobsWithDifferentLR






################################################################################
# [ImportanceDictionarySortFunction]
################################################################################
def ImportanceDictionarySortFunction(dictItem):
    val = dictItem['av']
    if (math.isnan(val)):
        return 0 

    return abs(val)
# End - ImportanceDictionarySortFunction




################################################################################
# [SortFunction]
################################################################################
def SortFunction(item):
    if (math.isnan(item[1])):
        return 0 
    return abs(item[1])
# End - SortFunction




################################################################################
#
# [MakeNInputsToSingleOutputBarGraph]
#
################################################################################
def MakeNInputsToSingleOutputBarGraph(sortedList, outputVarname, numImportantVariables, 
                                    relationName, barGraphFilePathName):
    fDebug = False
    xValueList = []
    yValueList = []

    for entry in sortedList:
        inputName = entry[0]
        coeffFloat = round(entry[1], 4)
        if (fDebug):
            print("inputName = " + str(inputName))
            print("coeffFloat = " + str(coeffFloat))

        yValueList.append(coeffFloat)
        if ((len(xValueList) % 2) == 0):
            xValueList.append(inputName)
        else:
            xValueList.append("\n" + inputName)

        if (len(xValueList) >= numImportantVariables):
            break
    # End for entry in sortedList:

    if (len(xValueList) <= 0):
        return

    # Make the bar graph
    graphTitleStr = relationName + " with " + outputVarname + " (Top " + str(len(xValueList)) + " of " + str(len(sortedList)) + ")"
    DataShow.DrawBarGraph(graphTitleStr,
                          " ", xValueList, 
                          relationName, yValueList, 
                          False, barGraphFilePathName)

    if (fDebug):
        print("graphTitleStr = " + str(graphTitleStr))
        print("barGraphFilePathName = " + str(barGraphFilePathName))
# End - MakeNInputsToSingleOutputBarGraph





#####################################################
#
# [GetCorrelationBetweenTwoVars]
#
#####################################################
def GetCorrelationBetweenTwoVars(
                    tdfFilePathName, 
                    valueName1, 
                    valueName2,
                    requirePropertyNameList, 
                    requirePropertyRelationList, 
                    requirePropertyValueList,
                    correlationResultFilePathName):
    fDebug = False

    # It is possible we already found this correlation on a previous instance
    # of this program that crashed. In this case, we are running on a restarted
    # process, so do not waste time recomputing work that is already done.
    # Look for this pair in the result file
    resultFileInfo = MLResultsFile(correlationResultFilePathName)
    foundIt, resultStr = resultFileInfo.GetResultForInputOutputPair(valueName1, valueName2)
    if (foundIt):
        if (fDebug):
            print("GetCorrelationBetweenTwoVars. Found resultStr=" + resultStr)
        return resultStr
    # End - if (foundIt)

    # Get information about the requested variables. This splits
    # complicated name values like "eGFR[-30]" into a name and an 
    # offset, like "eGFR" and "-30"
    functionObject1 = None
    functionObject2 = None
    labInfo1, nameStem1, valueOffset1, functionName1 = tdf.TDF_ParseOneVariableName(valueName1)
    if (labInfo1 is None):
        print("!Error! GetCorrelationBetweenTwoVars Cannot parse variable: " + valueName1)
        return None, None
    labInfo2, nameStem2, valueOffset2, functionName2 = tdf.TDF_ParseOneVariableName(valueName2)
    if (labInfo2 is None):
        print("!Error! GetCorrelationBetweenTwoVars Cannot parse variable: " + valueName2)
        return None, None
    if (functionName1 != ""):
        functionObject1 = timefunc.CreateTimeValueFunction(functionName1, nameStem1)
        if (functionObject1 is None):
            print("\n\n\nERROR!! GetCorrelationBetweenTwoVars Undefined function1: " + functionName1)
            sys.exit(0)
    if (functionName2 != ""):
        functionObject2 = timefunc.CreateTimeValueFunction(functionName2, nameStem2)
        if (functionObject2 is None):
            print("\n\n\nERROR!! GetCorrelationBetweenTwoVars Undefined function2: " + functionName2)
            sys.exit(0)

    var1Type = tdf.TDF_GetVariableType(nameStem1)
    var2Type = tdf.TDF_GetVariableType(nameStem2)
    if (fDebug):
        print("GetCorrelationBetweenTwoVars. varName1=" + nameStem1 + ", type=" + str(var1Type))
        print("      nameStem1=" + nameStem1 + ", valueOffset1=" + str(valueOffset1))
        print("      functionName1=" + functionName1 + ", functionObject1=" + str(functionObject1))
        print("      varName2=" + nameStem2 + ", type=" + str(var2Type))
        print("      nameStem2=" + nameStem2 + ", valueOffsets=" + str(valueOffset2))
        print("      functionName2=" + functionName2 + ", functionObject2=" + str(functionObject2))


    # Open the file
    if (fDebug):
        print("GetCorrelationBetweenTwoVars. tdfFilePathName = " + str(tdfFilePathName))
    tdfFile = tdf.TDF_CreateTDFFileReader(tdfFilePathName, 
                                          valueName1, 
                                          valueName2,
                                          requirePropertyNameList)

    # Iterate over every patient to build a list of values.
    # These lists will span patients, so they are useful for boolean values
    # that are always true for one patient and never true for a different patient.
    list1 = []
    list2 = []
    fFoundPatient = tdfFile.GotoFirstPatient()
    while (fFoundPatient):
        currentList1, currentList2 = tdfFile.GetSyncedPairOfValueListsForCurrentPatient(
                                                    nameStem1, valueOffset1, functionObject1,
                                                    nameStem2, valueOffset2, functionObject2,
                                                    requirePropertyNameList,
                                                    requirePropertyRelationList,
                                                    requirePropertyValueList)

        if (len(currentList1) > 0):
            list1.extend(currentList1)
            list2.extend(currentList2)
        # End - if (len(currentList1) > 0):

        fFoundPatient = tdfFile.GotoNextPatient()
    # End - while (patientNode):

    tdfFile.Shutdown()

    # We are done searching the entire file. 
    # If we were combining the lists of all patients, then get the correlation
    # for the total aggregate list now.
    correlation = 0
    if (len(list1) > MIN_SEQUENCE_LENGTH_FOR_CORRELATION):
        if (fDebug):
            print("GetCorrelationBetweenTwoVars using combined lists")
        try:
            # For Boolean, we can use the Point-biserial correlation coefficient.
            if ((var1Type == tdf.TDF_DATA_TYPE_BOOL) 
                    or (var2Type == tdf.TDF_DATA_TYPE_BOOL)):
                correlation, pValue = stats.pointbiserialr(list1, list2)
            else:
                correlation, pValue = spearmanr(list1, list2)
        except Exception:
            correlation = 0
    # End - if (len(list1) > 2):

    if (fDebug):
        print("GetCorrelationBetweenTwoVars. correlation=" + str(correlation))

    # Append the result to the file.
    resultFileInfo.AppendResult(valueName1, valueName2, correlation)

    return correlation
# End - GetCorrelationBetweenTwoVars





################################################################################
#
# [GetAccuracyForSingleInputAndOutputPair]
#
################################################################################
def GetAccuracyForSingleInputAndOutputPair(fullInputName, outputName, 
                            requirePropertyNameList, requirePropertyRelationList, requirePropertyValueList, 
                            tdfFilePathName, 
                            resultFilePathName):
    fDebug = False
    numPatients = 0
    numTrainDataSetsFound = 0
    numTestDataSetsFound = 0
    numDataSetsFound = 0

    if (fDebug):
        print("GetAccuracyForSingleInputAndOutputPair. tdfFilePathName = " + tdfFilePathName)
        print("GetAccuracyForSingleInputAndOutputPair. fullInputName = " + fullInputName)
        print("GetAccuracyForSingleInputAndOutputPair. outputName = " + str(outputName))
        print("GetAccuracyForSingleInputAndOutputPair: resultFilePathName = " + str(resultFilePathName))

    resultFileInfo = MLResultsFile(resultFilePathName)
    # It is possible we already found this correlation on a previous instance
    # of this program that crashed. In this case, we are running on a restarted
    # process, so do not waste time recomputing work that is already done.
    # Look for this pair in the result file
    foundIt, resultStr = resultFileInfo.GetResultForInputOutputPair(fullInputName, outputName)
    if (foundIt):
        if (fDebug):
            print("GetAccuracyForSingleInputAndOutputPair. Found resultStr=" + resultStr)
        return resultStr
    # End - if (foundIt):

    # Get information about the requested variables. This splits
    # complicated name values like "eGFR[-30]" into a name and an 
    # offset, like "eGFR" and "-30"
    inputLabInfo, inputNameStem, inputValueOffset, inputFunctionName = tdf.TDF_ParseOneVariableName(fullInputName)
    if (inputLabInfo is None):
        print("GetAccuracyForSingleInputAndOutputPair Error! Cannot parse variable: " + fullInputName)
        sys.exit(0)

    outputLabInfo, outputNameStem, outputValueOffset, outputFunctionName = tdf.TDF_ParseOneVariableName(outputName)
    if (outputLabInfo is None):
        print("GetAccuracyForSingleInputAndOutputPair Error! Cannot parse variable: " + outputName)
        sys.exit(0)

    inputFunctionObject = None
    if (inputFunctionName != ""):
        inputFunctionObject = timefunc.CreateTimeValueFunction(inputFunctionName, inputNameStem)
        if (inputFunctionObject is None):
            print("GetAccuracyForSingleInputAndOutputPair Error! Undefined function: " + inputFunctionName)
            sys.exit(0)

    outputFunctionObject = None
    if (outputFunctionName != ""):
        outputFunctionObject = timefunc.CreateTimeValueFunction(outputFunctionName, outputName)
        if (outputFunctionObject is None):
            print("GetAccuracyForSingleInputAndOutputPair Error! Undefined function: " + outputFunctionName)
            sys.exit(0)


    #print("Accuracy between " + fullInputName + " and " + outputName)
    srcTDF = tdf.TDF_CreateTDFFileReader(tdfFilePathName, fullInputName, outputName, requirePropertyNameList)

    totalTrainInputList = []
    totalTrainOutputList = []
    totalTestInputList = []
    totalTestOutputList = []

    # Iterate over every patient
    fFoundPatient = srcTDF.GotoFirstPatient()
    while (fFoundPatient):
        numPatients += 1

        # Get a list of marker values
        inputList, outputList = srcTDF.GetSyncedPairOfValueListsForCurrentPatient(
                                        inputNameStem, 
                                        inputValueOffset, 
                                        inputFunctionObject, 
                                        outputNameStem, 
                                        outputValueOffset, 
                                        outputFunctionObject,
                                        requirePropertyNameList,
                                        requirePropertyRelationList,
                                        requirePropertyValueList)
        if (False):
            print("GetAccuracyForSingleInputAndOutputPair. inputList=" + str(inputList))
            print("GetAccuracyForSingleInputAndOutputPair. outputList=" + str(outputList))

        if ((len(inputList) > 0) and (len(outputList) > 0)):
            if (random.random() <= g_FloatFractionInTrain):
                totalTrainInputList.extend(inputList)
                totalTrainOutputList.extend(outputList)
                numTrainDataSetsFound += 1
            else:
                totalTestInputList.extend(inputList)
                totalTestOutputList.extend(outputList)
                numTestDataSetsFound += 1

            numDataSetsFound += 1
        # End - if ((len(inputList) > 0) and (len(inputList) > 0)):

        fFoundPatient = srcTDF.GotoNextPatient()
    # End - while (fFoundPatient):

    srcTDF.Shutdown() 

    # Use Linear Regression when mapping inputs to a continuous output.
    # Use Logistic regression when mapping inputs to a Boolean or class output
    score = 0
    if ((len(totalTrainInputList) == 0) or (len(totalTrainOutputList) == 0)
            or (len(totalTestInputList) == 0) or (len(totalTestOutputList) == 0)):
        score = 0
    ###################################################
    elif ((outputLabInfo['dataType'] == tdf.TDF_DATA_TYPE_INT) 
        or (outputLabInfo['dataType'] == tdf.TDF_DATA_TYPE_FLOAT)):
        # Convert inputs to numpy.
        # LinearRegression.fit() takes 2 inputs of shape (n_samples, n_features)
        #   trainInputArray is a 2D Matrix with 1 column where each row has a single value
        #   trainOutputArray is also a 2-D matrix
        trainInputArray = np.array(totalTrainInputList).reshape(-1, 1)
        trainOutputArray = np.array(totalTrainOutputList).reshape(-1, 1)
        if (fDebug):
            print("Compute Linear Regression")
            print("GetAccuracyForSingleInputAndOutputPair. trainInputArray=" + str(trainInputArray))
            print("GetAccuracyForSingleInputAndOutputPair. trainOutputArray=" + str(trainOutputArray))
        try:
            regressModel = LinearRegression()
        except Exception:
            print("GetAccuracyForSingleInputAndOutputPair Error! LinearRegression.fit() failed")
        regressModel.fit(trainInputArray, trainOutputArray)
        testInputArray = np.array(totalTestInputList).reshape(-1, 1)
        testOutputArray = np.array(totalTestOutputList).reshape(-1, 1)
        predictedTestOutput = regressModel.predict(testInputArray)  # [::, 1]
        score = mean_squared_error(testOutputArray, predictedTestOutput, squared=False)
    ###################################################
    elif (outputLabInfo['dataType'] == tdf.TDF_DATA_TYPE_BOOL):
        # Convert inputs to numpy.
        # LinearRegression.fit() takes inputs of shape (n_samples, n_features) and (n_samples)
        #   trainInputArray is a 2D Matrix with 1 column where each row has a single value
        #   trainOutputArray is a 1-D vector
        trainInputArray = np.array(totalTrainInputList).reshape(-1, 1)
        trainOutputArray = np.array(totalTrainOutputList)
        if (fDebug):
            print("Compute Logistic Regression")
            print("GetAccuracyForSingleInputAndOutputPair. trainInputArray=" + str(trainInputArray))
            print("GetAccuracyForSingleInputAndOutputPair. trainOutputArray=" + str(trainOutputArray))
        regressModel = LogisticRegression()
        try:
            regressModel.fit(trainInputArray, trainOutputArray)
        except Exception:
            print("GetAccuracyForSingleInputAndOutputPair Error! LogisticRegression.fit() failed")
        if (fDebug):
            print("GetAccuracyForSingleInputAndOutputPair. fit the model")
        # This estimates the probabilities of each output.
        # LinearRegression.predict_proba() takes input of shape (n_samples, n_features)
        # The output is of shape (n_samples, n_classes), so there is a probability for each class.
        testInputArray = np.array(totalTestInputList).reshape(-1, 1)
        testOutputArray = np.array(totalTestOutputList)
        try:
            predictedTestOutput = regressModel.predict_proba(testInputArray)
            if (fDebug):
                print("GetAccuracyForSingleInputAndOutputPair. predictedTestOutput=" + str(predictedTestOutput))
            # The predicted output is of shape (n_samples, n_features)
            # For a boolean, we only care about the probability of true
            score = metrics.roc_auc_score(testOutputArray, predictedTestOutput[:, 1])
        except Exception:
            score = 0
    ###################################################
    elif (outputLabInfo['dataType'] == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
        # Convert inputs to numpy.
        # LinearRegression.fit() takes inputs of shape (n_samples, n_features) and (n_samples)
        #   trainInputArray is a 2D Matrix with 1 column where each row has a single value
        #   trainOutputArray is a 1-D vector
        trainInputArray = np.array(totalTrainInputList).reshape(-1, 1)
        trainOutputArray = np.array(totalTrainOutputList)
        if (fDebug):
            print("Compute Logistic Regression")
            print("GetAccuracyForSingleInputAndOutputPair. trainInputArray=" + str(trainInputArray))
            print("GetAccuracyForSingleInputAndOutputPair. trainOutputArray=" + str(trainOutputArray))
        regressModel = LogisticRegression()
        try:
            regressModel.fit(trainInputArray, trainOutputArray)
        except Exception:
            print("GetAccuracyForSingleInputAndOutputPair Error! LogisticRegression.fit() failed")

        # This estimates the probabilities of each output.
        # LinearRegression.predict_proba() takes input of shape (n_samples, n_features)
        # The output is of shape (n_samples, n_classes), so there is a probability for each class.
        testInputArray = np.array(totalTestInputList).reshape(-1, 1)
        testOutputArray = np.array(totalTestOutputList)

        try:        
            predictedTestOutput = regressModel.predict(testInputArray)
            # F1-score = 2*(Recall*Precision)/Recall+Precision 
            # where:
            #     Precision = TP/TP+FP
            #     Recall = TP/TP+FN
            # The predicted output is of shape (n_samples, n_features)
            # For a boolean, we only care about the probability of true
            score = metrics.f1_score(testOutputArray, predictedTestOutput, average='weighted')
        except Exception:
            score = 0

        if (fDebug):
            print("GetAccuracyForSingleInputAndOutputPair. testOutputArray=" + str(testOutputArray))
            print("GetAccuracyForSingleInputAndOutputPair. predictedTestOutput=" + str(predictedTestOutput))
    else:
        print("GetAccuracyForSingleInputAndOutputPair Error! Undefined function: " + outputFunctionName)
        sys.exit(0)

    if (fDebug):
        print("GetAccuracyForSingleInputAndOutputPair. score=" + str(score))

    # Append the result to the file.
    resultFileInfo.AppendResult(fullInputName, outputName, score)

    return str(score)
# End - GetAccuracyForSingleInputAndOutputPair






################################################################################
#
# [GetClusteringScoreForSingleInputAndOutputPair]
#
################################################################################
def GetClusteringScoreForSingleInputAndOutputPair(fullInputName, outputName, 
                            requirePropertyNameList, requirePropertyRelationList, requirePropertyValueList, 
                            tdfFilePathName, 
                            resultFilePathName):
    fDebug = False
    numPatients = 0

    if (fDebug):
        print("GetClusteringScoreForSingleInputAndOutputPair. tdfFilePathName = " + tdfFilePathName)
        print("GetClusteringScoreForSingleInputAndOutputPair. fullInputName = " + fullInputName)
        print("GetClusteringScoreForSingleInputAndOutputPair. outputName = " + str(outputName))
        print("GetClusteringScoreForSingleInputAndOutputPair: resultFilePathName = " + str(resultFilePathName))

    # It is possible we already found this correlation on a previous instance
    # of this program that crashed. In this case, we are running on a restarted
    # process, so do not waste time recomputing work that is already done.
    # Look for this pair in the result file
    resultFileInfo = MLResultsFile(resultFilePathName)
    foundIt, resultStr = resultFileInfo.GetResultForInputOutputPair(fullInputName, outputName)
    if (foundIt):
        if (fDebug):
            print("GetClusteringScoreForSingleInputAndOutputPair. Found resultStr=" + resultStr)
        return resultStr
    # End - if (foundIt):

    # Get information about the requested variables. This splits
    # complicated name values like "eGFR[-30]" into a name and an 
    # offset, like "eGFR" and "-30"
    inputLabInfo, inputNameStem, inputValueOffset, inputFunctionName = tdf.TDF_ParseOneVariableName(fullInputName)
    if (inputLabInfo is None):
        print("GetClusteringScoreForSingleInputAndOutputPair Error! Cannot parse variable: " + fullInputName)
        sys.exit(0)

    outputLabInfo, outputNameStem, outputValueOffset, outputFunctionName = tdf.TDF_ParseOneVariableName(outputName)
    if (outputLabInfo is None):
        print("GetClusteringScoreForSingleInputAndOutputPair Error! Cannot parse variable: " + outputName)
        sys.exit(0)

    inputFunctionObject = None
    if (inputFunctionName != ""):
        inputFunctionObject = timefunc.CreateTimeValueFunction(inputFunctionName, inputNameStem)
        if (inputFunctionObject is None):
            print("GetClusteringScoreForSingleInputAndOutputPair Error! Undefined function: " + inputFunctionName)
            sys.exit(0)

    outputFunctionObject = None
    if (outputFunctionName != ""):
        outputFunctionObject = timefunc.CreateTimeValueFunction(outputFunctionName, outputName)
        if (outputFunctionObject is None):
            print("GetClusteringScoreForSingleInputAndOutputPair Error! Undefined function: " + outputFunctionName)
            sys.exit(0)

    # Get the properties of the features
    numFeatures = 1
    featureNameList = [inputNameStem]
    featureTypes = [0] * numFeatures
    featureMin = [0] * numFeatures
    featureMax = [0] * numFeatures
    featureRange = [0] * numFeatures
    for featureNum in range(numFeatures):
        featureName = featureNameList[featureNum]
        featureTypes[featureNum] = tdf.TDF_GetVariableType(featureName)
        labMinVal, labMaxVal = tdf.TDF_GetMinMaxValuesForVariable(featureName)
        featureMin[featureNum] = labMinVal
        featureMax[featureNum] = labMaxVal
        featureRange[featureNum] = labMaxVal - labMinVal
    # End - for featureNum in range(numFeatures):


    if (fDebug):
        print("GetClusteringScoreForSingleInputAndOutputPair. numFeatures = " + str(numFeatures))
        print("     featureNameList = " + str(featureNameList))
        print("     featureTypes = " + str(featureTypes))
        print("     featureMin = " + str(featureMin))
        print("     featureMax = " + str(featureMax))
        print("     featureRange = " + str(featureRange))


    srcTDF = tdf.TDF_CreateTDFFileReader(tdfFilePathName, fullInputName, outputName, requirePropertyNameList)

    # Iterate over every patient
    inputList = []
    outputList = []
    fFoundPatient = srcTDF.GotoFirstPatient()    
    while (fFoundPatient):
        numPatients += 1

        # Get a list of marker values
        currentInputList, currentOutputList = srcTDF.GetSyncedPairOfValueListsForCurrentPatient(
                                    inputNameStem, 
                                    inputValueOffset, 
                                    inputFunctionObject, 
                                    outputNameStem, 
                                    outputValueOffset, 
                                    outputFunctionObject,
                                    requirePropertyNameList,
                                    requirePropertyRelationList,
                                    requirePropertyValueList)
        if ((len(currentInputList) > 0) and (len(currentOutputList) > 0)):
            inputList.extend(currentInputList)
            outputList.extend(currentOutputList)

        fFoundPatient = srcTDF.GotoNextPatient()
    # End - while (fFoundPatient):

    srcTDF.Shutdown() 

    score = 0
    if ((len(inputList) > 0) and (len(outputList) > 0)):
        numDataPoints = len(inputList)

        # Partition the input variables into clusters
        numCentroids = 10
        featureList = [[x] for x in inputList]

        if (fDebug):
            print("GetClusteringScoreForSingleInputAndOutputPair. numCentroids = " + str(numCentroids))
            print("GetClusteringScoreForSingleInputAndOutputPair. featureList = " + str(featureList))
            print("GetClusteringScoreForSingleInputAndOutputPair. outputList = " + str(outputList))

        predictedGroups = PartitionDataIntoGroups(featureList, numDataPoints, numCentroids,
                                            numFeatures, featureMin, featureMax, featureRange)

        if (fDebug):
            print("GetClusteringScoreForSingleInputAndOutputPair. predictedGroups = " + str(predictedGroups))
            print("GetClusteringScoreForSingleInputAndOutputPair. outputList = " + str(outputList))

        intOutputList = [int(i) for i in outputList]
        intPredictedGroups = [int(i) for i in predictedGroups]

        # There are a number of scores to evaluate clustering. Many of these use true labels,
        # which are the gold standard of how items should be partitioned.
        # Many of these evaluate the patitioning algorithm, which can have variable performance
        # depending on parameters like the number of clusters. Here, I assume the algorighm is
        # "good enough" and use the metrics to pmeasure how useful each input is for partitioning.
        # See https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation
        score = metrics.adjusted_mutual_info_score(intOutputList, intPredictedGroups)  

        if (fDebug):
            print("GetClusteringScoreForSingleInputAndOutputPair. score = " + str(score))
    # End - if ((len(inputList) > 0) and (len(inputList) > 0)):


    if (fDebug):
        print("GetClusteringScoreForSingleInputAndOutputPair. score=" + str(score))

    # Append the result to the file.
    resultFileInfo.AppendResult(fullInputName, outputName, score)

    return score
# End - GetClusteringScoreForSingleInputAndOutputPair






################################################################################
#
# [PartitionDataIntoGroups]
#
# There are several clustering algorithms. See:
#   https://scikit-learn.org/stable/modules/clustering.html
#
# This uses K-Means to partition a set of points into K groups.
# Params:
#   dataSet: This is a 2D matrix. Each row is a data point. Each column is
#           different attribute. It has shape (numDataPoints x numFeatures)
#   numDataPoints
#   numFeatures
#   numCentroids
#
# Alternate between:
#   (1) assigning data points to clusters based on the current centroids 
#   (2) chosing centroids (points which are the center of a cluster) based on the current assignment of data points to clusters
#
# https://stanford.edu/~cpiech/cs221/handouts/kmeans.html
################################################################################
def PartitionDataIntoGroups(dataSet, numDataPoints, numCentroids,
                            numFeatures, featureMin, featureMax, featureRange):
    fDebug = False
    fNormalizeValues = False
    maxIterations = 20

    # Normalize the values.
    # Otherwise, a value with a larger range will have larger distances and
    # so it will have a bigger effect on distances to centroids.
    if (fNormalizeValues):
        for pointNum in range(numDataPoints):
            for featureNum in range(numFeatures):
                dataValue = dataSet[pointNum][featureNum]
                if (dataValue < featureMin[featureNum]):
                    dataValue = featureMin[featureNum]
                if (dataValue > featureMax[featureNum]):
                    dataValue = featureMax[featureNum]
                offset = dataValue - featureMin[featureNum]
                dataSet[pointNum][featureNum] = (offset / featureRange[featureNum]) * 100.0
            # End - for featureNum in range(numFeatures):
        # End - for pointNum in range(numDataPoints):
    # End - if (fNormalizeValues)


    # Make random centroids
    centroidPoints = []
    for centroidNum in range(numCentroids):
        currentPoint = [0] * numFeatures
        for featureNum in range(numFeatures):
            if (fNormalizeValues):
                currentPoint[featureNum] = random.uniform(0, 100.0)
            else:
                currentPoint[featureNum] = random.uniform(featureMin[featureNum], featureMax[featureNum])
        centroidPoints.append(currentPoint)
    # End - for centroidNum in range(numCentroids):
    centroidForEachDataPoint = [-1] * numDataPoints


    if (fDebug):
        print("PartitionDataIntoGroups. dataSet = " + str(dataSet))
        print("PartitionDataIntoGroups. centroidPoints = " + str(centroidPoints))
        print("PartitionDataIntoGroups. centroidForEachDataPoint = " + str(centroidForEachDataPoint))


    # Run the main k-means algorithm
    numIterations = 0
    while (numIterations < maxIterations):
        # Save old centroids for convergence test
        oldCentroidList = centroidForEachDataPoint.copy()
        numDataPointsForCentroid = [0] * numCentroids

        # Assign labels to each datapoint based on centroids
        for pointNum in range(numDataPoints):
            closestCentroid = -1
            closestDistance = -1
            for centroidNum in range(numCentroids):
                currentDataSet = np.array(dataSet[pointNum])
                currentCentroid = np.array(centroidPoints[centroidNum])
                if (fDebug):
                    print(">> dataSet[pointNum] = " + str(dataSet[pointNum]))
                    print(">> centroidPoints[centroidNum] = " + str(centroidPoints[centroidNum]))
                    print(">> currentDataSet = " + str(currentDataSet))
                    print(">> currentCentroid = " + str(currentCentroid))

                distance = np.sqrt(sum((currentDataSet - currentCentroid) ** 2))
                if ((closestCentroid == -1) or (distance < closestDistance)):
                    closestCentroid = centroidNum
                    closestDistance = distance
            # End - for centroidNum in range(numCentroids)

            centroidForEachDataPoint[pointNum] = closestCentroid
            numDataPointsForCentroid[closestCentroid] = 1
        # End - for pointNum in range(numDataPoints):

        if (fDebug):
            print("PartitionDataIntoGroups. Assigned points to centroid")
            print("     oldCentroidList = " + str(oldCentroidList))
            print("     centroidPoints = " + str(centroidPoints))
            print("     centroidForEachDataPoint = " + str(centroidForEachDataPoint))

        # If no points changed their centroids, then we are done
        if (oldCentroidList == centroidForEachDataPoint):
            if (fDebug):
                print("PartitionDataIntoGroups. Quitting. oldCentroidList == centroidForEachDataPoint")
                print("     oldCentroidList = " + str(oldCentroidList))
                print("     centroidForEachDataPoint = " + str(centroidForEachDataPoint))
            break

        # Reposition the centroids to the geomtric mean of their associated points.
        # Each centroid is the geometric mean of the points associated with that centroid
        if (fDebug):
            print("PartitionDataIntoGroups. Start Reposition")
            print("     centroidForEachDataPoint = " + str(centroidForEachDataPoint))
            print("     centroidPoints = " + str(centroidPoints))
        for centroidNum in range(numCentroids):
            # If a centroid is empty (no points have that centroid's label) then randomly re-initialize it.
            if (numDataPointsForCentroid[centroidNum] == 0):
                if (fDebug):
                    print("PartitionDataIntoGroups. Re-randomize centroid. centroidNum=" + str(centroidNum))
                for featureNum in range(numFeatures):
                    if (fNormalizeValues):
                        centroidPoints[centroidNum][featureNum] = random.uniform(0, 100.0)
                    else:
                        centroidPoints[centroidNum][featureNum] = random.uniform(featureMin[featureNum], 
                                                                                featureMax[featureNum])
            # End - if (numDataPointsForCentroid[centroidNum] == 0):
            else:
                if (fDebug):
                    print("PartitionDataIntoGroups. Reposition w/ Geomtetric Mean. centroidNum=" + str(centroidNum))
                productOfFeaturesForCurrentCentroid = [1] * numFeatures
                numDataPointsForCurrentCentroid = 0
                for pointNum in range(numDataPoints):
                    if (centroidForEachDataPoint[pointNum] == centroidNum):
                        for featureNum in range(numFeatures):
                            productOfFeaturesForCurrentCentroid[featureNum] *= dataSet[pointNum][featureNum]
                        numDataPointsForCurrentCentroid += 1
                    # End - if (centroidForEachDataPoint[pointNum] == centroidNum):
                # End - for pointNum in range(numDataPoints):

                if (numDataPointsForCurrentCentroid > 0):
                    for featureNum in range(numFeatures):
                        try:
                            centroidPoints[centroidNum][featureNum] = (productOfFeaturesForCurrentCentroid[featureNum]) ** (1 / numDataPointsForCurrentCentroid)
                        except Exception:
                            centroidPoints[centroidNum][featureNum] = 0
            # End - else
        # End - for centroidNum in range(numCentroids)

        if (fDebug):
            print("PartitionDataIntoGroups. Repositioned centroids")
            print("     centroidPoints = " + str(centroidPoints))

        numIterations += 1
    # End - while not shouldStop(oldCentroids, centroids, iterations):

    if (fDebug):
        print("PartitionDataIntoGroups. Done. numIterations=" + str(numIterations))

    return centroidForEachDataPoint
# End - PartitionDataIntoGroups






################################################################################
#
# [GetCoxScoreForAllInputsAndOneOutput]
#
# There seems to be a bug in pyspark or Pandas Data Bricks or something else
# One workaround is to downgrade pandas
#   pip install -U pandas==1.5.3
# See https://stackoverflow.com/questions/75926636/databricks-issue-while-creating-spark-data-frame-from-pandas
#
################################################################################
def GetCoxScoreForAllInputsAndOneOutput(outputName, allSimpleInputsStr, allSimpleInputsList,
                                    ReqNameList, ReqRelationList, ReqValueList, 
                                    tdfFilePathName, 
                                    resultFilePathName):
    fDebug = False
    resultLine = outputName + ":"

    # https://sphweb.bumc.bu.edu/otlt/mph-modules/bs/bs704_survival/BS704_Survival_print.html
    if (fDebug):
        print("GetCoxScoreForAllInputsAndOneOutput")
        print("GetCoxScoreForAllInputsAndOneOutput: tdfFilePathName = " + str(tdfFilePathName))
        print("GetCoxScoreForAllInputsAndOneOutput: allSimpleInputsStr = " + str(allSimpleInputsStr))
        print("GetCoxScoreForAllInputsAndOneOutput: outputName = " + str(outputName))

    # Make sure the result file name exists.
    if (not os.path.isfile(resultFilePathName)):
        fileH = open(resultFilePathName, "a")
        fileH.close()

    # It is possible we already found this correlation on a previous instance
    # of this program that crashed. In this case, we are running on a restarted
    # process, so do not waste time recomputing work that is already done.
    # Look for this pair in the result file
    with open(resultFilePathName) as fileH:
        for line in fileH:
            line = line.lstrip()
            if (line.startswith(resultLine)):
                if (fDebug):
                    print("GetCoxScoreForAllInputsAndOneOutput. Found line. resultLine=" + line)
                lineParts = line.split(':')
                resultValue = "Unknown"
                if (len(lineParts) > 1):
                    resultValue = lineParts[1].rstrip()
                if (fDebug):
                    print("Found it. line=" + str(line))
                    print("Found it. resultValue=" + str(resultValue))
                return resultValue
            # End - if (line.startswith(resultLine)):
        # End - for line in fileH:
    # End - with open(resultFilePathName) as fileH:


    tdfFile = tdf.TDF_CreateTDFFileReader(tdfFilePathName, allSimpleInputsStr, outputName, ReqNameList)
    tdfFile.SetConvertResultsToBools(True)
    testNumInputs = tdfFile.GetNumInputValues()

    numInputVars = len(allSimpleInputsList)
    totalInputArray = np.empty([0, numInputVars])
    totalResultArray = np.empty([0, 1], dtype=int)
    if (testNumInputs != numInputVars):
        fooList = allSimpleInputsStr.split(";")
        fooNumInputValues = len(fooList)
        print("BAIL!!!!")
        print(">> numInputVars=" + str(numInputVars))
        print(">> testNumInputs=" + str(testNumInputs))
        print(">> allSimpleInputsStr=" + str(allSimpleInputsStr))
        print(">> allSimpleInputsList=" + str(allSimpleInputsList))
        print(">> fooNumInputValues=" + str(fooNumInputValues))
        print(">> fooList=" + str(fooList))
        for index in range(numInputVars):
            print(str(index) + ":" + str(allSimpleInputsList[index]) + " - " + str(fooList[index]))
        print(str(numInputVars) + ":" + str(allSimpleInputsList[numInputVars]))
        sys.exit(0)

    # Iterate over every patient to build a list of values.
    fFoundPatient = tdfFile.GotoFirstPatient()
    numPatientsFound = 0
    while (fFoundPatient):
        # Get the data.
        # Be Careful! Normalize all inputs so the coefficients are comparable.
        # We must assume that the inputs are scaled to be the same, say all are between 0..1 or between 0...100.
        # If we do not do this scaling, then the coefficients will have different scales.
        numReturnedDataSets, inputArray, resultArray = tdfFile.GetDataForCurrentPatient(ReqRelationList, 
                                                                        ReqNameList,
                                                                        ReqValueList,
                                                                        False,  # fAddMinibatchDimension,
                                                                        True)  # fNormalize inmputs
        if (numReturnedDataSets < 1):
            fFoundPatient = tdfFile.GotoNextPatient()
            continue

        # <><><><>
        # ValueError: all the input array dimensions for the concatenation axis must match exactly, but along dimension 1, the array at index 0 has size 134 and the array at index 1 has size 148
        try:
            totalInputArray = np.append(totalInputArray, inputArray, axis=0)
        except Exception:
            print("Exception!")

            print(">>> numInputVars=" + str(numInputVars))
            print(">>> totalInputArray.size=" + str(totalInputArray.size))
            print(">>> len(inputArray)=" + str(len(inputArray)))
            print(">>> len(inputArray[0])=" + str(len(inputArray[0])))
            print(">>> totalInputArray.size=" + str(totalInputArray.size))
            print(">>> totalInputArray=" + str(totalInputArray))
            print(">>> inputArray=" + str(inputArray))
            sys.exit(0)

        totalResultArray = np.append(totalResultArray, resultArray)

        numPatientsFound += 1
        fFoundPatient = tdfFile.GotoNextPatient()
    # End - while (fFoundPatient):

    tdfFile.Shutdown()

    # Assemble the resuls in an array of pairs
    resultListArray = []
    for resultVal in totalResultArray:
        entryList = ((resultVal != 0), 100.0)
        resultListArray.append(entryList)
    # End - for resultVal in totalResultArray:
    if (fDebug):
        print(">>> resultListArray = " + str(resultListArray))

    if (len(resultListArray) > 0):
        # Assemble the inputs into a Pandas dataframe
        # This stackoverflow answer seems to be the best source.
        # https://stackoverflow.com/questions/68869020/valueerror-y-must-be-a-structured-array-with-the-first-field-being-a-binary-cla
        resultNPArray = np.array(resultListArray, dtype=[('Status', '?'), ('Survival_in_days', '<f8')])
        inputsDataFrame = pd.DataFrame(totalInputArray, columns=allSimpleInputsList)

        if (fDebug):
            print(">>> type(resultNPArray) = " + str(type(resultNPArray)))
            print(">>> type(resultNPArray[0]) = " + str(type(resultNPArray[0])))
            print(">>> resultNPArray = " + str(resultNPArray))

        #estimator = CoxPHSurvivalAnalysis()
        estimator = CoxnetSurvivalAnalysis()
        estimator.fit(inputsDataFrame, resultNPArray)

        # The relative risk exp(β) can be:
        #   >1 (or β>0) for an increased risk of event (death).
        #   <1 (or β<0) for a reduced risk of event.
        numInputVars = len(allSimpleInputsList)
        coefficientList = estimator.coef_
        coeffStr = ""
        for inputVar, coeff in zip(allSimpleInputsList, coefficientList):
            coeffStr = coeffStr + inputVar + "=" + str(coeff) + ","
        # End - for inputVar in allSimpleInputsList:
        # Remove the last comma
        coeffStr = coeffStr[:-1]
    # End - if (len(resultListArray) > 0):
    else:
        coeffStr = ""

    # Append the result to the file.
    resultLine = resultLine + coeffStr + NEWLINE_STR
    fileH = open(resultFilePathName, "a")
    fileH.write(resultLine)
    fileH.close()

    if (fDebug):
        print("resultLine = " + resultLine)
        print("\n\nGetCoxScoreForAllInputsAndOneOutput. Done looking at patients\n\n")

    return coeffStr
# End - GetCoxScoreForAllInputsAndOneOutput








#####################################################
#
# [GetStatsForList]
#
#####################################################
def GetStatsForList(valueList):
    # Compute the mean, which is the average of the values.
    # Make sure to treat these as floats to avoid truncation or rounding errors.
    #avgValue = 0
    refAvgValue = 0
    listLen = len(valueList)
    if (listLen > 0):
        #avgValue = float(sum(valueList)) / listLen
        refAvgValue = statistics.mean(valueList)
    #print("Derived avgValue=" + str(avgValue))
    #print("Reference refAvgValue=" + str(refAvgValue))

    # Next, compute the variance.
    # This is a measure of how far spread out the numbers are.
    # Intuitively, this is the average distance from members of the set and the mean.
    # This uses the "Sample Variance" where avgValue is the sample mean, not the
    # mean of some superset "population" from which the sample is drawn.
    # As a result, we divide by listLen-1, but if we used the "population mean" then
    # we would divide by listLen
    #variance = sum((x - avgValue) ** 2 for x in valueList) / listLen
    refVariance = np.var(valueList)
    #print("Derived variance=" + str(variance))
    #print("Reference variance=" + str(refVariance))

    # Standard deviation is simply the sqrt of the Variance
    #stdDev = math.sqrt(variance)
    refStdDev = np.std(valueList)
    #print("Derived stdDev=" + str(stdDev))
    #print("Reference stdDev=" + str(refStdDev))

    return listLen, refAvgValue, refVariance, refStdDev
# End - GetStatsForList





#####################################################
#
# [CalculatePearsonCorrelationForLists]
#
#####################################################
def CalculatePearsonCorrelationForLists(valueList1, valueList2):
    length1, meanVal1, _, _ = GetStatsForList(valueList1)
    _, meanVal2, _, _ = GetStatsForList(valueList2)

    # Compute the correlation. 
    # This is the tendency for the variables to have a linear relationship.
    # ???It is the slope of the regression line.???
    # It is computed by the average of the products of distances from each list element and the list mean.
    #
    # If a list is sorted in increasing order, then the difference between list elements and the list mean will
    # start with a negative number (the smallest value, so farthest below the mean) and end with a positive number
    # (the largest value, so farthest greater than the mean). 
    # Each value in the list will have a difference to the mean that lays somewhere in the middle 
    # between the most negative and most positive.
    # The two lists are correlated if small values in one list correspond to small values in the other list, and
    # large values in one list correspond to large values in the other list. In other words, the two corresponding
    # values will have distances with the same sign, either both positive or both negative. In either case, their
    # product is a positive value.
    # If the two lists are not correlated, then a number above average in one list will be associated with a
    # number below average in the other list. when they are very different, then their differences to the respective 
    # means will have different polarity, one is positice and one is negative. The product is a negative number.
    # The sum of all of these will be a mix of positive and negative products.
    correlation = 0
    for i in range(0, length1):
        correlation += ((valueList1[i] - meanVal1) * (valueList2[i] - meanVal2))
    # This is the sample correlation, so we should use length-1 to compute the mean.
    # However, the Python library seems to use the population variance, so uses length to compute the mean
    correlation = correlation / length1  # (length1 - 1)
    #refCorrelation = np.cov(valueList1, valueList2)[0][1]
    #print("Derived correlation=" + str(correlation))
    #print("Reference correlation=" + str(refCorrelation))

    # The absolute value of the correlation can be any number, from -infinity to +infinity.
    # Its absolute value does not tell you anything about how well the lists are correlated.
    # So, normalize the correlation by the variability of the data. This essentially normalizes
    # the correlation by some measure of the range of values (largest - smallest). Now, why don't
    # we normalize the the products of the two ranges like (largest - smallest of set 1) * (largest - smallest of set2)
    # Not sure.
    # Pearson assumes a Gaussian distribution of the data, because it uses the mean value of each list
    # in its calculation.
    # It has values between -1 (negative correlation) and 1 (positive correlation). 0 means no correlation.
    #pearsonCoeff = correlation / (stdDev1 * stdDev2)

    corrMatrix = np.corrcoef(valueList1, valueList2)
    refPearsonCoeff = corrMatrix[0, 1]

    ##refPearsonList = pearsonr(valueList1, valueList2)
    ##refPearsonCoeff2 = refPearsonList[0]
    ##refPValue = refPearsonList[1]

    #print("Derived pearsonCoeff=" + str(pearsonCoeff))
    #print("Reference pearsonCoeff=" + str(refPearsonCoeff))
    ##print("Reference pearsonCoeff2=" + str(refPearsonCoeff2))

    return refPearsonCoeff
# End - CalculatePearsonCorrelationForLists






#####################################################
#
# [CalculateSpearmanCorrelationForLists]
#
# Spearman correlation is just the Pearson correlation coefficient 
# between the rank variables
#####################################################
def CalculateSpearmanCorrelationForLists(valueList1, valueList2):
    listLength = len(valueList1)

    # Make a list of value indexes. 
    # These are the positions of a value in the original value-list.
    indexList1 = list(range(listLength))
    indexList2 = list(range(listLength))

    # Sort the indexes based on the actual values. 
    # This creates a list of value indexes, sorted in the order of the values themselves.
    # So, the first index references to the smallest value, and so on.
    # Because indexList is ordered, the position of an entry in indexList is also its rank.
    # So, the index stored at indexList[x] stores an index into valueList, but x (the index in indexList) is the rank.
    # This uses sort, so it takes O(N*logN) 
    indexList1.sort(key=lambda x: valueList1[x])
    indexList2.sort(key=lambda x: valueList2[x])

    # Now, arrange the ranks into the same order of the items in the original value list.
    # This means valueRanksList[N] stored the rank of the value stored at valueList1[N]
    # The index into indexList is the rank of the value stored in valueList1
    valueRanksList1 = [0] * listLength
    for indexListIndex, valueListIndex in enumerate(indexList1):
        valueRanksList1[valueListIndex] = indexListIndex

    valueRanksList2 = [0] * listLength
    for indexListIndex, valueListIndex in enumerate(indexList2):
        valueRanksList2[valueListIndex] = indexListIndex

    # scipy.stats.spearmanr will take care of computing the ranks for you, you simply have 
    # to give it the data in the correct order:
    refSpearmanCoeff, _ = spearmanr(valueList1, valueList2)

    #print("=================")
    #print("mySpearman=" + str(mySpearman))
    #mySpearman = CalculatePearsonCorrelationForLists(valueRanksList1, valueRanksList2)
    #print("refSpearmanCoeff=" + str(refSpearmanCoeff))

    return refSpearmanCoeff
# End - CalculateSpearmanCorrelationForLists






