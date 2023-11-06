#!/usr/bin/python3
################################################################################
# 
# Copyright (c) 2022-2023 Dawson Dean
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
# Graphing Utilities
#
################################################################################
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from sklearn.metrics import precision_recall_curve

# File ops
from os.path import isfile

import tdfTools as tdf
import dataShow as DataShow
import mlJob as mlJob
import mlEngine as mlEngine

NEWLINE_STR = "\n"
RESULT_SECTION_SEPARATOR_STR = "-------------------------"

MLJOB_CONSOLE_REPORT            = "MLJOB_CONSOLE_REPORT"
MLJOB_FILE_REPORT               = "MLJOB_FILE_REPORT"
MLJOB_LOG_REPORT                = "MLJOB_LOG_REPORT"
MLJOB_LEARNING_RATE_CSV_REPORT  = "MLJOB_LEARNING_RATE_CSV_REPORT"



#####################################################
#
# [JobShow_WriteReport]
#
#####################################################
def JobShow_WriteReport(job, fileType, filePathName):
    indentStr = "   "
    completeReportStr = ""
    csvLineReport = ""

    # Extract the results we will report.
    jobNameStr = job.GetTrainingParamStr("JobName", "")
    inputStr = job.GetNetworkInputVarNames()
    resultStr = job.GetNetworkOutputVarName()
    lrStr = job.GetTrainingParamStr("LearningRate", "0.1")
    jobStatus, errCode, errorMsg = job.GetJobStatus()

    avgLossStr = ""
    lossList = job.GetAvgLossPerEpochList()
    for avgLoss in lossList:
        avgLoss = round(avgLoss, 4)
        avgLossStr = avgLossStr + " " + str(avgLoss)

    trainResultGroupBucketsizeStr = ""
    if (job.GetNumSequencesTrainedPerEpoch() > 0):
        bucketNum = 0
        bucketStartValue = job.GetResultValMinValue()
        bucketStopValue = bucketStartValue + job.GetResultValBucketSize()
        for numItems in job.GetTrainNumItemsPerClass():
            bucketStartValue = round(bucketStartValue, 2)
            bucketStopValue = round(bucketStopValue, 2)

            trainResultGroupBucketsizeStr += indentStr + indentStr
            trainResultGroupBucketsizeStr += "[" + str(bucketStartValue) + " - " + str(bucketStopValue) + "]:    " 
            trainResultGroupBucketsizeStr += str(numItems) + NEWLINE_STR

            bucketNum += 1
            bucketStartValue += job.GetResultValBucketSize()
            bucketStopValue += job.GetResultValBucketSize()
        # End - for numItems in job.GetTrainNumItemsPerClass():
    # End - if (job.GetNumSequencesTrainedPerEpoch() > 0):

    csvLineReport = lrStr
    numSequencesTested = job.GetNumSequencesTested()
    testResults = job.GetTestResults()
    testNumItemsPerClass = job.GetTestNumItemsPerClass()


    #########################
    testResultStr = ""
    if (((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT)) 
            and (numSequencesTested > 0)):
        csvLineReport += ", " + str(numSequencesTested)

        percentAccurate = float(testResults["NumCorrectPredictions"]) / float(numSequencesTested)
        percentAccurate = percentAccurate * 100.0
        fractionInt = round(percentAccurate)
        testResultStr += "Exact Accuracy: " + str(fractionInt) + "%" + NEWLINE_STR
        csvLineReport += ", " + str(fractionInt)

        percentAccurate = float(testResults["NumPredictionsWithin2Percent"]) / float(numSequencesTested)
        percentAccurate = percentAccurate * 100.0
        fractionInt = round(percentAccurate)
        testResultStr += "Within 2 percent Accuracy: " + str(fractionInt) + "%" + NEWLINE_STR
        csvLineReport += ", " + str(fractionInt)

        percentAccurate = float(testResults["NumPredictionsWithin5Percent"]) / float(numSequencesTested)
        percentAccurate = percentAccurate * 100.0
        fractionInt = round(percentAccurate)
        testResultStr += "Within 5 percent Accuracy: " + str(fractionInt) + "%" + NEWLINE_STR
        csvLineReport += ", " + str(fractionInt)

        percentAccurate = float(testResults["NumPredictionsWithin10Percent"]) / float(numSequencesTested)
        percentAccurate = percentAccurate * 100.0
        fractionInt = round(percentAccurate)
        testResultStr += "Within 10 percent Accuracy: " + str(fractionInt) + "%" + NEWLINE_STR
        csvLineReport += ", " + str(fractionInt)

        percentAccurate = float(testResults["NumPredictionsWithin20Percent"]) / float(numSequencesTested)
        percentAccurate = percentAccurate * 100.0
        fractionInt = round(percentAccurate)
        testResultStr += "Within 20 percent Accuracy: " + str(fractionInt) + "%" + NEWLINE_STR
        csvLineReport += ", " + str(fractionInt)

        percentAccurate = float(testResults["NumPredictionsWithin50Percent"]) / float(numSequencesTested)
        percentAccurate = percentAccurate * 100.0
        fractionInt = round(percentAccurate)
        testResultStr += "Within 50 percent Accuracy: " + str(fractionInt) + "%" + NEWLINE_STR
        csvLineReport += ", " + str(fractionInt)

        percentAccurate = float(testResults["NumPredictionsWithin100Percent"]) / float(numSequencesTested)
        percentAccurate = percentAccurate * 100.0
        fractionInt = round(percentAccurate)
        testResultStr += "Within 100 percent Accuracy: " + str(fractionInt) + "%" + NEWLINE_STR
        csvLineReport += ", " + str(fractionInt)

    #########################
    elif ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS) and (numSequencesTested > 0)):
        totalNumItems = 0
        for classNum in range(tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES):
            totalNumItems += testNumItemsPerClass[classNum]
        # End - for classNum in range(tdf.TDF_NUM_FUTURE_EVENT_CATEGORIES):

        if (totalNumItems > 0):
            totalAcc = float(testResults["NumCorrectPredictions"]) / float(totalNumItems)
            totalCloseAcc = float(testResults["NumPredictionsWithin1Class"]) / float(totalNumItems)
        else:
            totalAcc = 0.0
            totalCloseAcc = 0.0

        totalAcc = totalAcc * 100.0
        totalAcc = round(totalAcc, 1)

        totalCloseAcc = totalCloseAcc * 100.0
        totalCloseAcc = round(totalCloseAcc, 1)

        testResultStr += NEWLINE_STR + "Total Cases: " + str(totalNumItems) + NEWLINE_STR
        testResultStr += "Total Correct: " + str(testResults["NumCorrectPredictions"]) + NEWLINE_STR
        testResultStr += "Total Within 1 Class: " + str(testResults["NumPredictionsWithin1Class"]) + NEWLINE_STR
        testResultStr += "Accurracy: " + str(totalAcc) + " percent" + NEWLINE_STR
        testResultStr += "Percent Within 1 Class: " + str(totalCloseAcc) + " percent" + NEWLINE_STR

        csvLineReport += ", " + str(totalNumItems) + ", " + str(totalAcc) + ", " + str(totalCloseAcc)

    #########################
    elif ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_BOOL) and (numSequencesTested > 0)):
        totalNumItems = testNumItemsPerClass[0] + testNumItemsPerClass[1]
        if (totalNumItems > 0):
            totalAcc = float(testResults["NumCorrectPredictions"]) / float(totalNumItems)
        else:
            totalAcc = 0.0
        totalAcc = totalAcc * 100.0
        totalAcc = round(totalAcc, 1)
        testResultStr += NEWLINE_STR + "Total Cases: " + str(totalNumItems) + NEWLINE_STR
        testResultStr += "Total Correct: " + str(testResults["NumCorrectPredictions"]) + NEWLINE_STR
        testResultStr += "Total Accurracy: " + str(totalAcc) + " percent" + NEWLINE_STR

        csvLineReport += ", " + str(totalNumItems) + ", " + str(totalAcc)

        if (job.GetROCAUC() > 0):
            roundedAUC = round(job.GetROCAUC(), 3)
            testResultStr += "ROC AUC: " + str(roundedAUC) + NEWLINE_STR
            csvLineReport += ", " + str(roundedAUC)
        else:
            csvLineReport += ", "

        if (job.GetAUPRC() > 0):
            roundedAUPRC = round(job.GetAUPRC(), 3)
            testResultStr += "AUPRC: " + str(roundedAUPRC) + NEWLINE_STR
            csvLineReport += ", " + str(roundedAUPRC)
        else:
            csvLineReport += ", "

        if (job.GetF1Score() > 0):
            roundedF1Score = round(job.GetF1Score(), 3)
            testResultStr += "F1Score: " + str(roundedF1Score) + NEWLINE_STR
            csvLineReport += ", " + str(roundedF1Score)
        else:
            csvLineReport += ", "
    # End - elif ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_BOOL) and (numSequencesTested > 0)):



    testResultStr += NEWLINE_STR
    testPredictionPerBucketStr = ""
    testActualAndCorrectPerBucketStr = ""
    testNumPredictionsPerClass = job.GetTestNumPredictionsPerClass()
    testNumCorrectPerClass = job.GetTestNumCorrectPerClass()
    if (numSequencesTested > 0):
        bucketStartValue = job.GetResultValMinValue()
        bucketStopValue = bucketStartValue + job.GetResultValBucketSize()
        numClasses = len(testNumItemsPerClass)
        for index in range(numClasses):
            numItems = testNumItemsPerClass[index]
            numPredictions = testNumPredictionsPerClass[index]
            numCorrectItems = testNumCorrectPerClass[index]

            bucketStartValue = round(bucketStartValue, 2)
            bucketStopValue = round(bucketStopValue, 2)

            testPredictionPerBucketStr += indentStr + indentStr + "[" + str(bucketStartValue) + " - " + str(bucketStopValue) + "]:    " 
            testPredictionPerBucketStr += str(numPredictions) + NEWLINE_STR

            testActualAndCorrectPerBucketStr += indentStr + indentStr + "[" + str(bucketStartValue) + " - " + str(bucketStopValue) + "]:    " 
            testActualAndCorrectPerBucketStr += str(numItems) + " (" + str(numCorrectItems) + " correct)" + NEWLINE_STR

            csvLineReport += ", " + str(numCorrectItems)

            bucketStartValue += job.GetResultValBucketSize()
            bucketStopValue += job.GetResultValBucketSize()
        # End - for numItems in job.GetTrainNumItemsPerClass():
    # End - if (numSequencesTested > 0):


    completeReportStr = NEWLINE_STR + NEWLINE_STR + "==========================================================" + NEWLINE_STR
    if (jobNameStr != ""):
        completeReportStr += jobNameStr + NEWLINE_STR
    completeReportStr += "Inputs: " + inputStr + NEWLINE_STR
    completeReportStr += "Result: " + resultStr + NEWLINE_STR
    completeReportStr += "Learning Rate: " + lrStr + NEWLINE_STR
    completeReportStr += NEWLINE_STR

    completeReportStr += "Training Results:" + NEWLINE_STR
    completeReportStr += RESULT_SECTION_SEPARATOR_STR + NEWLINE_STR
    completeReportStr += "Data Sequences per Epoch:  " + str(job.GetNumSequencesTrainedPerEpoch()) + NEWLINE_STR

    completeReportStr += "Patients Trained per Epoch: " + str(job.GetNumPatientsTrainedPerEpoch()) + NEWLINE_STR
    completeReportStr += "Patients Skipped per Epoch: " + str(job.GetNumPatientsSkippedPerEpoch()) + NEWLINE_STR

    if (job.GetNumSequencesTrainedPerEpoch() > 0):
        completeReportStr += "Average Losses Per Epoch: " + avgLossStr + NEWLINE_STR
        completeReportStr += "Num Items in Each Class:" + NEWLINE_STR + trainResultGroupBucketsizeStr + NEWLINE_STR

    completeReportStr += NEWLINE_STR + "Test Results:" + NEWLINE_STR 
    completeReportStr += RESULT_SECTION_SEPARATOR_STR + NEWLINE_STR
    completeReportStr += "Num Sequences Tested: " + str(numSequencesTested) + NEWLINE_STR

    if (numSequencesTested > 0):
        # Do not show the num predictions if this is a logistic.
        if (not job.GetIsLogisticNetwork()):
            completeReportStr += "Num Predictions for Each Class: " + NEWLINE_STR + testPredictionPerBucketStr 
        completeReportStr += "Num Items in Each Class: " + NEWLINE_STR + testActualAndCorrectPerBucketStr 
    # End - if (numSequencesTested > 0):

    completeReportStr += NEWLINE_STR + testResultStr + NEWLINE_STR

    completeReportStr += "Job Status: " + str(jobStatus) + NEWLINE_STR
    completeReportStr += "Err Code: " + str(errCode) + "  (" + str(errorMsg) + ")" + NEWLINE_STR
    completeReportStr += "Start Time: " + job.GetStartRequestTimeStr() + NEWLINE_STR
    completeReportStr += "Stop Time: " + job.GetStopRequestTimeStr() + NEWLINE_STR
    completeReportStr += "============================" + NEWLINE_STR


    ########################
    if (fileType == MLJOB_CONSOLE_REPORT):
        print(completeReportStr)
    ########################
    elif (fileType == MLJOB_FILE_REPORT):
        try:
            fileH = open(filePathName, "a+")
            fileH.write(completeReportStr)
            fileH.flush()
            fileH.close()
        except Exception:
            pass
    ########################
    elif (fileType == MLJOB_LOG_REPORT):
        try:
            fileH = open(filePathName, "a+")
            fileH.write(completeReportStr)
            fileH.flush()
            fileH.close()
        except Exception:
            pass 
    ########################
    elif (fileType == MLJOB_LEARNING_RATE_CSV_REPORT):
        fullLineStr = csvLineReport + NEWLINE_STR
        try:
            fileH = open(filePathName, "a+")
            fileH.write(fullLineStr)
            fileH.flush()
            fileH.close()
        except Exception:
            pass
# End - JobShow_WriteReport







#####################################################
#
# [JobShow_DrawROCCurves]
# 
#####################################################
def JobShow_DrawROCCurves(job, fROC, fPRC, titleStr, showInGUI, filePath):
    logisticResultsTrueValueList = job.GetLogisticResultsTrueValueList()
    logisticResultsPredictedProbabilityList = job.GetLogisticResultsPredictedProbabilityList()

    ####################################
    # plot the precision-recall curves
    if (fPRC):
        PrecisionResults, RecallResults, _ = precision_recall_curve(logisticResultsTrueValueList, 
                                    logisticResultsPredictedProbabilityList)
        plt.plot(RecallResults, PrecisionResults, marker='.', label='Logistic')
        # axis labels
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.legend()
    ####################################
    # plot the roc curve for the model
    elif (fROC):
        falsePositiveRateCurve, truePositiveRateCurve, _ = roc_curve(logisticResultsTrueValueList, 
                                                    logisticResultsPredictedProbabilityList)
        plt.plot(falsePositiveRateCurve, truePositiveRateCurve, marker='.', label='Logistic')
        # axis labels
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        # show the legend
        plt.legend()

    if ((titleStr is not None) and (titleStr != "")):
        plt.title(titleStr)

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()
# End - JobShow_DrawROCCurves







################################################################################
#
# [GetJobValue]
#
# Value Types (case IN-sensitive)
# ===============================
#   NetworkType
#   LearningRate
#   FinalLoss
#   NumSequencesTrainedPerEpoch
#   NumSequencesTested
#   PercentAccurate 
#        with index 1, 2, 5, 10, 20, 50, 100 for types INT or FLOAT
#        any index for results of type for TDF_DATA_TYPE_FUTURE_EVENT_CLASS or TDF_DATA_TYPE_BOOL
#   PercentClose - only for results of type TDF_DATA_TYPE_FUTURE_EVENT_CLASS
#   Accuracy - only for results of type for TDF_DATA_TYPE_BOOL
#   AUC - only for results of type for TDF_DATA_TYPE_BOOL
#   AUPRC - only for results of type for TDF_DATA_TYPE_BOOL
#   F1 - only for results of type for TDF_DATA_TYPE_BOOL
#   NumSequencesTestedPerClass - with valueIndex 0-1 for bool, 0-13 for class, 0-19 for int and float
#   PercentCorrectPerClass - with valueIndex 0-1 for bool, 0-13 for class, 0-19 for int and float
#   NumCorrectPerClass - with valueIndex 0-1 for bool, 0-13 for class, 0-19 for int and float
#   NumTestedPerClass - with valueIndex 0-1 for bool, 0-13 for class, 0-19 for int and float
#
################################################################################
def GetJobValue(job, valueName, valueIndex):
    fDebug = False
    resultValue = None

    numSequencesTested = job.GetNumSequencesTested()
    testResults = job.GetTestResults()
    if (fDebug):
        print("valueName = " + str(valueName))
        print("numSequencesTested = " + str(numSequencesTested))
        print("job.GetResultValueType() = " + str(job.GetResultValueType()))
        print("job.GetROCAUC() = " + str(job.GetROCAUC()))


    valueName = valueName.lower()
    #########################
    if (valueName == "networktype"):
        return job.GetNetworkType()
    #########################
    elif (valueName == "inputnames"):
        return job.GetNetworkInputVarNames()
    #########################
    elif (valueName == "outputnames"):
        return job.GetNetworkOutputVarName()
    #########################
    elif (valueName == "learningrate"):
        lrStr = job.GetTrainingParamStr("LearningRate", "0.1")
        return float(lrStr)
    #########################
    elif (valueName == "numsequencestrainedperepoch"):
        return job.GetNumSequencesTrainedPerEpoch()
    #########################
    elif (valueName == "numsequencestested"):
        return numSequencesTested
    #########################
    elif (valueName == "finalloss"):
        lossList = job.GetAvgLossPerEpochList()
        lastLoss = lossList[len(lossList) - 1]
        return round(lastLoss, 4)
    #########################
    elif ((valueName == "accuracy") and (job.GetResultValueType() == tdf.TDF_DATA_TYPE_BOOL) 
            and (numSequencesTested > 0)):
        if (numSequencesTested <= 0):
            return(0.0)
        totalAcc = float(testResults["NumCorrectPredictions"]) / float(numSequencesTested)
        return round((totalAcc * 100.0), 1)
    #########################
    elif ((valueName == "auc") and (job.GetResultValueType() == tdf.TDF_DATA_TYPE_BOOL) 
            and (numSequencesTested > 0) and (job.GetROCAUC() > 0)):
        return round(job.GetROCAUC(), 3)
    #########################
    elif ((valueName == "auprc") and (job.GetResultValueType() == tdf.TDF_DATA_TYPE_BOOL) 
            and (numSequencesTested > 0) and (job.GetAUPRC() > 0)):
        return round(job.GetAUPRC(), 3)
    #########################
    elif ((valueName == "f1") and (job.GetResultValueType() == tdf.TDF_DATA_TYPE_BOOL) 
            and (numSequencesTested > 0) and (job.GetF1Score() > 0)):
        return round(job.GetF1Score(), 3)
    #########################
    elif ((valueName == "accurratewithin5percent")
            and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
                or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)

        totalCorrect = float(testResults["NumCorrectPredictions"])
        totalCorrect += float(testResults["NumPredictionsWithin2Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin5Percent"])
        resultValue = totalCorrect / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "accurratewithin10percent")
            and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
                or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)

        totalCorrect = float(testResults["NumCorrectPredictions"])
        totalCorrect += float(testResults["NumPredictionsWithin2Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin5Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin10Percent"])
        resultValue = totalCorrect / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "accurratewithin20percent")
            and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
                or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)

        totalCorrect = float(testResults["NumCorrectPredictions"])
        totalCorrect += float(testResults["NumPredictionsWithin2Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin5Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin10Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin20Percent"])
        resultValue = totalCorrect / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "accurratewithin50percent")
            and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
                or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)

        totalCorrect = float(testResults["NumCorrectPredictions"])
        totalCorrect += float(testResults["NumPredictionsWithin2Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin5Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin10Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin20Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin50Percent"])
        resultValue = totalCorrect / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "accurratewithin100percent")
            and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
                or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)

        totalCorrect = float(testResults["NumCorrectPredictions"])
        totalCorrect += float(testResults["NumPredictionsWithin2Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin5Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin10Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin20Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin50Percent"])
        totalCorrect += float(testResults["NumPredictionsWithin100Percent"])
        resultValue = totalCorrect / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "percentaccurate") and (valueIndex == 1)
            and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
                or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)
        resultValue = float(testResults["NumCorrectPredictions"]) / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "percentaccurate") and (valueIndex == 2) 
        and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
            or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)
        resultValue = float(testResults["NumPredictionsWithin2Percent"]) / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "percentaccurate") and (valueIndex == 5) 
        and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
            or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)
        resultValue = float(testResults["NumPredictionsWithin5Percent"]) / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "percentaccurate") and (valueIndex == 10) 
        and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
            or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (("NumPredictionsWithin10Percent" in testResults) and (numSequencesTested > 0)):
            resultValue = float(testResults["NumPredictionsWithin10Percent"]) / float(numSequencesTested)
        else:
            resultValue = 0
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "percentaccurate") and (valueIndex == 20) 
        and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
            or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)
        resultValue = float(testResults["NumPredictionsWithin20Percent"]) / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "percentaccurate") and (valueIndex == 50) 
        and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
            or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)
        resultValue = float(testResults["NumPredictionsWithin50Percent"]) / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "percentaccurate") and (valueIndex == 100) 
        and ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_INT) 
            or (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FLOAT))):
        if (numSequencesTested <= 0):
            return(0.0)
        resultValue = float(testResults["NumPredictionsWithin100Percent"]) / float(numSequencesTested)
        return round(resultValue * 100.0)
    #########################
    elif ((valueName == "percentaccurate")
               and (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS) 
               and (numSequencesTested > 0)):
        if (numSequencesTested <= 0):
            return(0.0)
        totalAcc = float(testResults["NumCorrectPredictions"]) / float(numSequencesTested)
        return round((totalAcc * 100.0), 1)
    #########################
    elif ((valueName == "percentclose")
               and (job.GetResultValueType() == tdf.TDF_DATA_TYPE_FUTURE_EVENT_CLASS) 
               and (numSequencesTested > 0)):
        if (numSequencesTested <= 0):
            return(0.0)
        totalCloseAcc = float(testResults["NumPredictionsWithin1Class"]) / float(numSequencesTested)
        return round((totalCloseAcc * 100.0), 1)
    #########################
    elif ((valueName == "percentaccurate") 
            and (job.GetResultValueType() == tdf.TDF_DATA_TYPE_BOOL) 
            and (numSequencesTested > 0)):
        if (numSequencesTested <= 0):
            return(0.0)
        totalAcc = float(testResults["NumCorrectPredictions"]) / float(numSequencesTested)
        return round((totalAcc * 100.0), 1)

    return None
# End - GetJobValue





################################################################################
#
# [JobShowGetLinearUnitInputWeights]
#
################################################################################
def JobShowGetLinearUnitInputWeights(job):
    fDebug = False
    
    networkType = job.GetNetworkType().lower()
    if (networkType == "simplenet"):
        linearUnitName = "inputToOutput"
    elif (networkType == "multilevelnet"):
        linearUnitName = "Vec0To1"
    else:
        print("Error. JobShowGetLinearUnitInputWeights cannot process network type: " + networkType)
        return None

    fFoundIt, weightMatrix, biasVector = job.GetLinearUnitMatrices(linearUnitName)
    if (not fFoundIt):
        print("Error. JobShowGetLinearUnitInputWeights cannot find linear unit: " + linearUnitName)
        return None

    if (fDebug):
        print("JobShowGetLinearUnitInputWeights. networkType=" + str(networkType))
        print("JobShowGetLinearUnitInputWeights. linearUnitName=" + str(linearUnitName))
        print("JobShowGetLinearUnitInputWeights. weightMatrix.shape=" + str(weightMatrix.shape))
        print("JobShowGetLinearUnitInputWeights. biasVector.shape=" + str(biasVector.shape))

    totalWeightsVector = np.sum(weightMatrix, axis=0)
    if (fDebug):
        print("JobShowGetLinearUnitInputWeights. totalWeightsVector.shape="
                    + str(totalWeightsVector.shape))
        print("JobShowGetLinearUnitInputWeights. totalWeightsVector="
                    + str(totalWeightsVector))
    
    return totalWeightsVector
# End - JobShowGetLinearUnitInputWeights






################################################################################
#
# [JobShowGetXGBoostInputWeights]
#
################################################################################
def JobShowGetXGBoostInputWeights(job):
    fDebug = False
    
    # Restore the network matrices
    localNeuralNet = mlEngine.MLEngine_XGBoostModel(job)
    localNeuralNet.RestoreNetState(job)

    inputWtArray = localNeuralNet.GetInputWeights()
    if (fDebug):
        print("JobShowGetXGBoostInputWeights. inputWtArray=" + str(inputWtArray))

    return inputWtArray
# End - JobShowGetXGBoostInputWeights





################################################################################
#
# [JobShow_ShowInputWeights]
#
################################################################################
def JobShow_ShowInputWeights(jobFilePathName, graphFilePath, reportFilePathName):
    fDebug = False
    
    err, job = mlJob.MLJob_ReadExistingMLJob(jobFilePathName)
    if (job is None):
        print("Error. JobShow_ShowInputWeights cannot open the file: " + jobFilePathName)
        return

    inputNameListStr = job.GetNetworkInputVarNames()
    inputNameList = inputNameListStr.split(tdf.VARIABLE_LIST_SEPARATOR)
    numInputVars = len(inputNameList)
    if (fDebug):
        print("JobShow_ShowInputWeights. jobFilePathName=" + str(jobFilePathName))
        print("JobShow_ShowInputWeights. inputNameListStr=" + str(inputNameListStr))
        print("JobShow_ShowInputWeights. numInputVars=" + str(numInputVars))

    networkType = job.GetNetworkType().lower()
    if (networkType in ("simplenet", "multilevelnet")):
        inputWtArray = JobShowGetLinearUnitInputWeights(job)
    elif (networkType == "xgboost"):
        inputWtArray = JobShowGetXGBoostInputWeights(job)
    elif (networkType == "lstm"):
        print("Error. JobShow_ShowInputWeights cannot process network type: " + networkType)
        return
    else:
        print("Error. JobShow_ShowInputWeights cannot process network type: " + networkType)
        return


    # Get the absolute value of all inputs
    polarity = [1] * numInputVars
    varInfoList = []
    for inputNum in range(numInputVars):
        if (inputWtArray[inputNum] < 0):
            polarity[inputNum] = -1
            inputWtArray[inputNum] = - inputWtArray[inputNum]

        newDict = {"name": inputNameList[inputNum], "pol": polarity[inputNum], "rawWt": inputWtArray[inputNum]}
        varInfoList.append(newDict)
    # End - for inputNum in range(numInputVars):

    if (fDebug):
        print("JobShow_ShowInputWeights. polarity=" + str(polarity))
        print("JobShow_ShowInputWeights. positive inputWtArray=" + str(inputWtArray))

    sumOfAllWeights = np.sum(inputWtArray)
    inputWtArray /= sumOfAllWeights
    if (fDebug):
        print("JobShow_ShowInputWeights. sumOfAllWeights=" + str(sumOfAllWeights))
        print("JobShow_ShowInputWeights. SCALED inputWtArray=" + str(inputWtArray))

    for inputNum in range(numInputVars):
        varInfoList[inputNum]["wt"] = inputWtArray[inputNum]
    # End - for inputNum in range(numInputVars):

    varInfoList = sorted(varInfoList, reverse=True, key=lambda entry: entry['wt'])
    listOfWts = [round((100.0 * x['wt']), 1) for x in varInfoList]
    listOfNames = [x['name'] for x in varInfoList]

    sumOfAllFractions = np.sum(inputWtArray)
    if (fDebug):
        print("JobShow_ShowInputWeights. sumOfAllFractions=" + str(sumOfAllFractions))
        print("JobShow_ShowInputWeights. varInfoList=" + str(varInfoList))
        print("JobShow_ShowInputWeights. listOfWts=" + str(listOfWts))
        print("JobShow_ShowInputWeights. listOfNames=" + str(listOfNames))

    if ((graphFilePath is not None) and (graphFilePath != "")):
        DataShow.DrawBarGraph("Title", "Input", listOfNames, "Weight", listOfWts, False, graphFilePath)

    if ((reportFilePathName is not None) and (reportFilePathName != "")):
        DataShow.WriteReportToExcelFile(reportFilePathName, "Input,Weight", [listOfNames, listOfWts])
# End - JobShow_ShowInputWeights






################################################################################
#
# [JobShow_MakeBarGraphFromDir]
#
################################################################################
def JobShow_MakeBarGraphFromDir(jobFileDirPathName, 
                                graphTitleStr, 
                                xLabelStr, xValueName, 
                                yLabelStr, yValueName,
                                graphFilePathName):
    fDebug = False
    xValueList = []
    yValueList = []

    if (fDebug):
        print("JobShow_MakeBarGraphFromDir. jobFileDirPathName = " + jobFileDirPathName)
        print("JobShow_MakeBarGraphFromDir. xValueName = " + xValueName)
        print("JobShow_MakeBarGraphFromDir. yValueName = " + yValueName)

    fileNameList = os.listdir(jobFileDirPathName)
    for fileName in fileNameList:
        jobFilePathname = os.path.join(jobFileDirPathName, fileName)
        if (fDebug):
            print("JobShow_MakeBarGraphFromDir. fileName = " + fileName + ", jobFilePathname = " + jobFilePathname)

        if (not isfile(jobFilePathname)):
            continue

        # Skip any image files left over from past analysis runs
        if ((jobFilePathname.endswith(".jpg")) 
                or (jobFilePathname.endswith(".JPG"))
                or (jobFilePathname.endswith(".png")) 
                or (jobFilePathname.endswith(".PNG"))):
            continue

        # Read the job
        jobErr, job = mlJob.MLJob_ReadExistingMLJob(jobFilePathname)
        if (mlJob.JOB_E_NO_ERROR != jobErr):
            print("JobShow_MakeBarGraphFromDir. Error for fileName = " + fileName + ", Err=" + str(jobErr))
            continue

        valueIndex = 0
        xVal = GetJobValue(job, xValueName, valueIndex)
        yVal = GetJobValue(job, yValueName, valueIndex)
        if (fDebug):
            print("JobShow_MakeBarGraphFromDir. xVal=" + str(xVal) + ", yVal=" + str(yVal))
        if ((xVal is not None) and (yVal is not None)):
            xValueList.append(xVal)
            yValueList.append(yVal)
            if (fDebug):
                print("JobShow_MakeBarGraphFromDir. xVal=" + str(xVal) + ", yVal=" + str(yVal))
        # End - for fileName in fileNameList:

    if (fDebug):
        print("JobShow_MakeBarGraphFromDir. xValueList=" + str(xValueList))
        print("JobShow_MakeBarGraphFromDir. yValueList=" + str(yValueList))

    if ((len(xValueList) > 0) and (len(yValueList) > 0)):
        DataShow.DrawBarGraph(graphTitleStr, 
                            xLabelStr, xValueList, 
                            yLabelStr, yValueList,
                            False, graphFilePathName)
    else:
        if os.path.exists(graphFilePathName):
            os.remove(graphFilePathName)
# End - JobShow_MakeBarGraphFromDir






################################################################################
#
# [GetMatchingJobsInDir]
#
################################################################################
def GetMatchingJobsInDir(srcDirPathName, resultVarName, fIsLogistic):
    fDebug = False
    resultJobList = []

    fileNameList = os.listdir(srcDirPathName)
    for fileName in fileNameList:
        if (fileName.endswith(".xgboost")):
            continue

        srcFilePathName = os.path.join(srcDirPathName, fileName)
        if (isfile(srcFilePathName)):
            if (fDebug):
                print("GetMatchingJobsInDir. file: " + srcFilePathName)

            jobErr, job = mlJob.MLJob_ReadExistingMLJob(srcFilePathName)
            if (mlJob.JOB_E_NO_ERROR != jobErr):
                print("Error. Invalid job found in the list of Done jobs")
                continue

            jobStatus, _, _ = job.GetJobStatus()
            if (mlJob.MLJOB_STATUS_DONE == jobStatus):
                pass
                #print("Error. Incomplete job found in the list of Done jobs")
                #continue

            if (resultVarName != job.GetNetworkOutputVarName()):
                continue
            if (fDebug):
                print("GetMatchingJobsInDir. Found job with desired output: " + resultVarName)

            if ((job.GetResultValueType() == tdf.TDF_DATA_TYPE_BOOL)
                    and (fIsLogistic != job.GetIsLogisticNetwork())):
                continue

            resultJobList.append(job)
        # End - if (isfile(srcFilePathName)):
    # End - for fileName in fileNameList:

    if (fDebug):
        print("resultJobList = " + str(resultJobList))

    return resultJobList
# End - GetMatchingJobsInDir






################################################################################
# 
# [ShowBoolVsLogistic]
# 
################################################################################
def ShowBoolVsLogistic(jobDirName, titleStr, compareProperty,
                        listOfOutputVars, reportFilePathName):
    boolResList = []
    logisticResultList = []
    varNameList = []

    for outputVarName in listOfOutputVars:
        logisticJobList = GetMatchingJobsInDir(jobDirName, outputVarName, True)
        boolJobList = GetMatchingJobsInDir(jobDirName, outputVarName, False)
        if ((len(logisticJobList) != 1) or (len(boolJobList) != 1)):
            continue

        # Value Types (case IN-sensitive)
        # ===============================
        #   FinalLoss
        #   PercentAccurate 
        #        with index 1, 2, 5, 10, 20, 50, 100 for types INT or FLOAT
        #        any index for results of type for TDF_DATA_TYPE_FUTURE_EVENT_CLASS or TDF_DATA_TYPE_BOOL
        #   Accuracy - only for results of type for TDF_DATA_TYPE_BOOL
        #   AUC - only for results of type for TDF_DATA_TYPE_BOOL
        #   AUPRC - only for results of type for TDF_DATA_TYPE_BOOL
        #   F1 - only for results of type for TDF_DATA_TYPE_BOOL
        logisticAccuracyFloat = float(GetJobValue(logisticJobList[0], compareProperty, 10))
        boolAccuracyFloat = float(GetJobValue(boolJobList[0], compareProperty, 10))

        logisticResultList.append(logisticAccuracyFloat)
        boolResList.append(boolAccuracyFloat)
        if ((len(outputVarName) % 2) == 1):
            varNameList.append("\n" + outputVarName)
        else:
            varNameList.append(outputVarName)
    # End - for outputVarName in listOfOutputVars

    DataShow.DrawDoubleBarGraph(titleStr, 
                        "", varNameList, 
                        compareProperty,  #yLabelStr, 
                        "Boolean", boolJobList, "Logistic", logisticJobList, 
                        False, reportFilePathName)
# End - ShowBoolVsLogistic





################################################################################
# 
# [ShowResultVsLearningRate]
# 
################################################################################
def ShowResultVsLearningRate(jobDirName, titleStr, compareProperty,
                        outputVarName, isLogistic, reportFilePathName):
    fDebug = False

    # Value Types (case IN-sensitive)
    # ===============================
    #   FinalLoss
    #   PercentAccurate 
    #        with index 1, 2, 5, 10, 20, 50, 100 for types INT or FLOAT
    #        any index for results of type for TDF_DATA_TYPE_FUTURE_EVENT_CLASS or TDF_DATA_TYPE_BOOL
    #   Accuracy - only for results of type for TDF_DATA_TYPE_BOOL
    #   AUC - only for results of type for TDF_DATA_TYPE_BOOL
    #   AUPRC - only for results of type for TDF_DATA_TYPE_BOOL
    #   F1 - only for results of type for TDF_DATA_TYPE_BOOL
    outputVarType = tdf.TDF_GetVariableType(outputVarName)
    if ((outputVarType == tdf.TDF_DATA_TYPE_BOOL) and (isLogistic)):
        compareProperty = "AUC"
    else:
        compareProperty = "PercentAccurate"

    jobList = GetMatchingJobsInDir(jobDirName, outputVarName, isLogistic)

    xyPairList = []
    for currentJob in jobList:
        try:
            lr = float(currentJob.GetTrainingParamStr("LearningRate", "0.1"))
        except Exception:
            print("ShowResultVsLearningRate. Cannot parse learningRate =" + str(currentJob.GetTrainingParamStr("LearningRate", "0.1")))
            continue

        # Value Types (case IN-sensitive)
        # ===============================
        #   FinalLoss
        #   PercentAccurate 
        #        with index 1, 2, 5, 10, 20, 50, 100 for types INT or FLOAT
        #        any index for results of type for TDF_DATA_TYPE_FUTURE_EVENT_CLASS or TDF_DATA_TYPE_BOOL
        #   Accuracy - only for results of type for TDF_DATA_TYPE_BOOL
        #   AUC - only for results of type for TDF_DATA_TYPE_BOOL
        #   AUPRC - only for results of type for TDF_DATA_TYPE_BOOL
        #   F1 - only for results of type for TDF_DATA_TYPE_BOOL
        accuracyFloat = float(GetJobValue(currentJob, compareProperty, 10))

        newDictEntry = {'x': lr, 'y': accuracyFloat}
        xyPairList.append(newDictEntry)
    # End - for currentJob in jobList:
    sortedXYPairList = sorted(xyPairList, key=lambda k: k['x'])
    if (fDebug):
        print("ShowResultVsLearningRate. sortedXYPairList =" + str(sortedXYPairList))

    xValueList = []
    yValueList = []
    for xyPair in xyPairList:
        xValueList.append(xyPair['x'])
        yValueList.append(xyPair['y'])

    if (fDebug):
        print("ShowResultVsLearningRate. xValueList =" + str(xValueList))
        print("ShowResultVsLearningRate. yValueList =" + str(yValueList))

    # Do a bar graph, not a line graph. The LR values may span a wide range (from 0.0001 to 1.0) and
    # a line graph will scale them so they bunch up at the bottom of the range.
    DataShow.DrawBarGraph(titleStr, 
                "Learning Rate", xValueList, 
                compareProperty, yValueList, 
                False, reportFilePathName)
# End - ShowResultVsLearningRate






################################################################################
# 
# [ShowAvgLossPerEpoch]
# 
################################################################################
def ShowAvgLossPerEpoch(jobDirName, titleStr,
                        outputVarName, isLogistic, reportFilePathName):
    MAX_EPOCHS = 20
    curveNamesList = []
    lossSequencesList = []

    jobList = GetMatchingJobsInDir(jobDirName, outputVarName, isLogistic)
    for currentJob in jobList:
        lrStr = currentJob.GetTrainingParamStr("LearningRate", "0.1")
        curveNamesList.append("LR=" + lrStr)

        avgLossList = currentJob.GetAvgLossPerEpochList()
        newLossSequence = [0] * MAX_EPOCHS
        epochNum = 0
        for avgLoss in avgLossList:
            newLossSequence[epochNum] = avgLoss
            epochNum += 1
        lossSequencesList.append(newLossSequence)
    # End - for currentJob in jobList:

    epochNames = []
    for epochNum in range(MAX_EPOCHS):
        epochNames.append(str(epochNum))

    DataShow.DrawMultiLineGraph(titleStr, 
                        "Epoch", epochNames, 
                        "Loss", curveNamesList, 
                        lossSequencesList, 
                        False, reportFilePathName)
# End - ShowAvgLossPerEpoch



