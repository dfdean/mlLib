#!/usr/bin/python3
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
# Graphing Utilities
#
################################################################################

import numpy as np
import matplotlib.pyplot as plt

NEWLINE_STR = "\n"

# print(plt.style.available)
# 'seaborn-whitegrid'
WHITE_BACKGROUND_STYLE = 'seaborn-v0_8-whitegrid'



################################################################################
#
# [DrawPredictedVsActualValues]
#
# X-axis is predicted, Y is actual. 45-degree line is perfect
################################################################################
def DrawPredictedVsActualValues(titleStr, predictedValueList, actualValueList, showInGUI, filePath):
    # Discard any previous plots
    plt.clf()
    plt.cla()
    plt.style.use('seaborn-whitegrid')

    # Add 45-degree line
    plt.axline([0, 0], [1, 1])

    # X-axis is actual value, Y-axis is predicted value
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.scatter(actualValueList, predictedValueList)

    if ((titleStr is not None) and (titleStr != "")):
        plt.title(titleStr)

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()

    plt.close()
# DrawPredictedVsActualValues






################################################################################
#
# [DrawBarGraph]
#
################################################################################
def DrawBarGraph(titleStr, xLabelStr, xAxisNameList, yLabelStr, yValueList, 
                showInGUI, filePath):
    fDebug = False
    if (fDebug):
        print("DrawBarGraph. titleStr = " + str(titleStr))
        print("DrawBarGraph. xLabelStr = " + str(xLabelStr))
        print("DrawBarGraph. xAxisNameList = " + str(xAxisNameList))
        print("DrawBarGraph. yLabelStr = " + str(yLabelStr))
        print("DrawBarGraph. yValueList = " + str(yValueList))
        print("DrawBarGraph. showInGUI = " + str(showInGUI))
        print("DrawBarGraph. filePath = " + str(filePath))

    xLabelLocations = np.arange(len(xAxisNameList))
    barWidth = 0.36

    # Discard any previous plots
    plt.clf()
    plt.cla()
    plt.style.use(WHITE_BACKGROUND_STYLE)

    fig, ax = plt.subplots()
    rects1 = ax.bar(xLabelLocations, yValueList, barWidth, label=' ')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if ((yLabelStr is not None) and (yLabelStr != "")):
        ax.set_ylabel(yLabelStr)
    if ((xLabelStr is not None) and (xLabelStr != "")):
        ax.set_xlabel(xLabelStr)
    if ((titleStr is not None) and (titleStr != "")):
        ax.set_title(titleStr)
    ax.set_xticks(xLabelLocations)
    ax.set_xticklabels(xAxisNameList)

    ax.bar_label(rects1, padding=3)
    fig.tight_layout()

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()

    plt.close()
# DrawBarGraph







################################################################################
#
# [DrawHorizontalBarGraph]
#
################################################################################
def DrawHorizontalBarGraph(titleStr, yAxisNameList, xLabelStr, xAxisValueList, 
                showInGUI, filePath):
    fDebug = False
    if (fDebug):
        print("DrawHorizontalBarGraph. titleStr = " + str(titleStr))
        print("DrawHorizontalBarGraph. xLabelStr = " + str(xLabelStr))
        print("DrawHorizontalBarGraph. xAxisValueList = " + str(xAxisValueList))
        print("DrawHorizontalBarGraph. yAxisNameList = " + str(yAxisNameList))
        print("DrawHorizontalBarGraph. showInGUI = " + str(showInGUI))
        print("DrawHorizontalBarGraph. filePath = " + str(filePath))

    # Discard any previous plots
    plt.clf()
    plt.cla()
    plt.style.use(WHITE_BACKGROUND_STYLE)

    #plt.rcdefaults()
    _, ax = plt.subplots()

    yLabelLocations = np.arange(len(yAxisNameList))
    ax.barh(yLabelLocations, xAxisValueList, align='center')
    ax.set_yticks(yLabelLocations, labels=yAxisNameList)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if ((xLabelStr is not None) and (xLabelStr != "")):
        ax.set_xlabel(xLabelStr)
    if ((titleStr is not None) and (titleStr != "")):
        ax.set_title(titleStr)

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()

    plt.close()
# DrawHorizontalBarGraph







################################################################################
#
# [DrawDoubleBarGraph]
#
################################################################################
def DrawDoubleBarGraph(titleStr, xLabelStr, xAxisNameList, yLabelStr, 
                        y1LabelStr, y1AxisValueList, 
                        y2LabelStr, y2AxisValueList, 
                        showInGUI, filePath):
    xLabelLocations = np.arange(len(xAxisNameList))
    barWidth = 0.36

    # Discard any previous plots
    plt.clf()
    plt.cla()
    plt.style.use(WHITE_BACKGROUND_STYLE)

    fig, ax = plt.subplots()
    rects1 = ax.bar(xLabelLocations - (barWidth / 2), y1AxisValueList, barWidth, label=y1LabelStr)
    rects2 = ax.bar(xLabelLocations + (barWidth / 2), y2AxisValueList, barWidth, label=y2LabelStr)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if ((yLabelStr is not None) and (yLabelStr != "")):
        ax.set_ylabel(yLabelStr)
    if ((xLabelStr is not None) and (xLabelStr != "")):
        ax.set_xlabel(xLabelStr)
    if ((titleStr is not None) and (titleStr != "")):
        ax.set_title(titleStr)
    ax.set_xticks(xLabelLocations)
    ax.set_xticklabels(xAxisNameList)

    # Add a legend box to correlate the colors with the group
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    fig.tight_layout()

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()

    plt.close()
# DrawDoubleBarGraph






################################################################################
#
# [DrawTripleBarGraph]
#
################################################################################
def DrawTripleBarGraph(titleStr, xLabelStr, xAxisNameList, yLabelStr, 
                        y1LabelStr, y1AxisValueList, y1Color,
                        y2LabelStr, y2AxisValueList, y2Color,
                        y3LabelStr, y3AxisValueList, y3Color,
                        showInGUI, filePath):
    xLabelLocations = np.arange(len(xAxisNameList))
    barWidth = 0.26

    # Discard any previous plots
    plt.clf()
    plt.cla()
    plt.style.use(WHITE_BACKGROUND_STYLE)

    fig, ax = plt.subplots()
    rects1 = ax.bar(xLabelLocations - barWidth, y1AxisValueList, barWidth, label=y1LabelStr, color=y1Color)
    rects2 = ax.bar(xLabelLocations, y2AxisValueList, barWidth, label=y2LabelStr, color=y2Color)
    rects3 = ax.bar(xLabelLocations + barWidth, y3AxisValueList, barWidth, label=y3LabelStr, color=y3Color)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if ((yLabelStr is not None) and (yLabelStr != "")):
        ax.set_ylabel(yLabelStr)
    if ((xLabelStr is not None) and (xLabelStr != "")):
        ax.set_xlabel(xLabelStr)
    if ((titleStr is not None) and (titleStr != "")):
        ax.set_title(titleStr)
    ax.set_xticks(xLabelLocations)
    ax.set_xticklabels(xAxisNameList)

    # Add a legend box to correlate the colors with the group
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)
    fig.tight_layout()

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()

    plt.close()
# DrawTripleBarGraph




################################################################################
#
# [ShowFourHistogramsOnOneGraph]
#
################################################################################
def ShowFourHistogramsOnOneGraph(titleStr, xLabelStr, yLabelStr,
                                histogram1, label1Str, color1, 
                                histogram2, label2Str, color2, 
                                histogram3, label3Str, color3, 
                                histogram4, label4Str, color4, 
                                showInGUI, filePath):
    xValueList = list(range(0, histogram1.GetNumBuckets()))

    # You cannot do ".-o" because "o" is a style marker, not a color.
    formatStrList = [".-g", ".-c", ".-y", ".-r"]
    yNamesList = [label1Str, label2Str, label3Str, label4Str]
    ySequencesList = [histogram1.GetBucketsAsPercentages(),
                        histogram2.GetBucketsAsPercentages(),
                        histogram3.GetBucketsAsPercentages(),
                        histogram4.GetBucketsAsPercentages()]

    DrawMultiLineGraphEx(titleStr, xLabelStr, xValueList, 
                         yLabelStr, yNamesList, ySequencesList, formatStrList,
                         showInGUI, filePath)
# End - ShowFourHistogramsOnOneGraph





################################################################################
#
# [DrawLineGraph]
#
################################################################################
def DrawLineGraph(titleStr, xLabelStr, xValueList, yLabelStr, yValueList, showInGUI, filePath):
    fDebug = False
    if (fDebug):
        print("DrawLineGraph. titleStr = " + str(titleStr))
        print("DrawLineGraph. xLabelStr = " + str(xLabelStr))
        print("DrawLineGraph. xValueList = " + str(xValueList))
        print("DrawLineGraph. yLabelStr = " + str(yLabelStr))
        print("DrawLineGraph. yValueList = " + str(yValueList))
        print("DrawLineGraph. showInGUI = " + str(showInGUI))
        print("DrawLineGraph. filePath = " + str(filePath))

    # Discard any previous plots
    plt.clf()
    plt.cla()
    plt.style.use(WHITE_BACKGROUND_STYLE)

    # The format string is 3 chars:
    # Marker
    # Line Style
    # Color
    plt.plot(xValueList, yValueList, ".-b", label="")
    #plt.plot(x*0.1, y, 'o-', color='lightgrey', label='No mask')

    if ((yLabelStr is not None) and (yLabelStr != "")):
        plt.ylabel(yLabelStr)
    if ((xLabelStr is not None) and (xLabelStr != "")):
        plt.xlabel(xLabelStr)
    if ((titleStr is not None) and (titleStr != "")):
        plt.title(titleStr)

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()

    plt.close()
# DrawLineGraph






################################################################################
#
# [DrawMultiLineGraph]
#
################################################################################
def DrawMultiLineGraph(titleStr, xLabelStr, xValueList, 
                        yLabelStr, yNamesList, ySequencesList, 
                        showInGUI, filePath):
    # The format string is 3 chars:
    # Marker: "." dit, "o" circle
    # Line Style: "-" solid, "--" dashed
    # Color: b=blue, r=red, g=green, y=yellow, k=black, m=magenta, c=cyan
    formatStrList = [".-b", ".-r", ".-g", ".-y", ".-k", ".-m", ".-c",
                    "o--b", "o--r", "o--g", "o--y", "o--k", "o--m", "o--c"
                     ]

    DrawMultiLineGraphEx(titleStr, xLabelStr, xValueList, 
                        yLabelStr, yNamesList, ySequencesList, formatStrList,
                        showInGUI, filePath)
# DrawMultiLineGraph





################################################################################
#
# [DrawMultiLineGraphEx]
#
################################################################################
def DrawMultiLineGraphEx(titleStr, xLabelStr, xValueList, 
                        yLabelStr, yNamesList, ySequencesList, lineColorsList,
                        showInGUI, filePath):
    fDebug = False
    if (fDebug):
        print("lineColorsList = " + str(lineColorsList))

    # Discard any previous plots
    plt.clf()
    plt.cla()
    plt.style.use(WHITE_BACKGROUND_STYLE)

    lineList = []
    numLines = len(ySequencesList)
    for index in range(numLines):
        if (fDebug):
            print("xValueList = " + xValueList)
            print("ySequencesList[index] = " + ySequencesList[index])
            print("lineColorsList[index] = " + lineColorsList[index])
            print("yNamesList[index] = " + yNamesList[index])
        currentLine = plt.plot(xValueList, ySequencesList[index], lineColorsList[index], label=yNamesList[index])
        lineList.append(currentLine)
    # End - for index in range(numLines):


    if ((yLabelStr is not None) and (yLabelStr != "")):
        plt.ylabel(yLabelStr)
    if ((xLabelStr is not None) and (xLabelStr != "")):
        plt.xlabel(xLabelStr)
    if ((titleStr is not None) and (titleStr != "")):
        plt.title(titleStr)

    numXPts = len(xValueList)
    xTickLabels = []
    for index in range(numXPts):
        xTickLabels.append(str(xValueList[index]))
    plt.xticks(xValueList, xTickLabels)

    # Add a legend box to correlate the colors with the group
    plt.legend()

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()

    plt.close()
# DrawMultiLineGraphEx




################################################################################
#
# [DrawPieChart]
#
# Pie chart, where the slices will be ordered and plotted counter-clockwise:
# labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
# sizes = [15, 30, 45, 10]
#explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
################################################################################
def DrawPieChart(titleStr, labelList, sizeList, showInGUI, filePath):
    # Discard any previous plots
    plt.clf()
    plt.cla()
    plt.style.use(WHITE_BACKGROUND_STYLE)

    _, ax = plt.subplots()
    #ax.pie(sizeList, explode=explodeList, labels=labelList, autopct='%1.1f%%', shadow=True, startangle=90)
    ax.pie(sizeList, labels=labelList, autopct='%1.1f%%', shadow=True, startangle=90)

    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.axis('equal')

    if ((titleStr is not None) and (titleStr != "")):
        ax.set_title(titleStr)

    if ((filePath is not None) and (filePath != "")):
        plt.savefig(filePath)

    if (showInGUI):
        plt.show()

    plt.close()
# DrawPieChart





#####################################################
#
# [WriteReportToExcelFile
#
#####################################################
def WriteReportToExcelFile(filePathName, columnHeaderStr, listOfColmns):
    fDebug = False
    numColumns = len(listOfColmns)
    numRows = len(listOfColmns[0])

    if (fDebug):
        print("WriteReportToExcelFile. filePathName = " + str(filePathName))
        print("WriteReportToExcelFile. columnHeaderStr = " + str(columnHeaderStr))
        print("WriteReportToExcelFile. listOfColmns = " + str(listOfColmns))
        print("WriteReportToExcelFile. numColumns = " + str(numColumns))
        print("WriteReportToExcelFile. numRows = " + str(numRows))

    try:
        fileH = open(filePathName, "w+")
        fileH.write(columnHeaderStr + NEWLINE_STR)
    except Exception:
        print("WriteReportToExcelFile Error!!  Cannot open file: " + str(filePathName))
        return


    for rowNum in range(numRows):
        reportLine = ""
        for colNum in range(numColumns):
            if (fDebug):
                print(">>> rowNum=" + str(rowNum) + ", colNum=" + str(colNum))
            reportLine += str(listOfColmns[colNum][rowNum])
            reportLine += ","
        # End - for colNum in range(numColumns)

        # Strip off the last comma
        reportLine = reportLine[:-1]
        reportLine += NEWLINE_STR

        if (fDebug):
            print(">>> reportLine = " + reportLine)
        fileH.write(reportLine)
    # End - for rowNum in range(numRows)

    fileH.flush()
    fileH.close()
# End - WriteReportToExcelFile





#####################################################
#
# [StartExcelFile
#
#####################################################
def StartExcelFile(filePathName, columnHeaderStr):
    try:
        fileH = open(filePathName, "w+")
        fileH.write(columnHeaderStr + NEWLINE_STR)
        fileH.flush()
    except Exception:
        print("WriteReportToExcelFile Error!!  Cannot open file: " + str(filePathName))
        return None

    return fileH
# End - StartExcelFile



#####################################################
#
# [WriteOneLineToExcelFile]
#
#####################################################
def WriteOneLineToExcelFile(fileH, reportLine):
    fileH.write(reportLine + NEWLINE_STR)
# End - WriteOneLineToExcelFile



#####################################################
#
# [FinishExcelFile
#
#####################################################
def FinishExcelFile(fileH):
    fileH.flush()
    fileH.close()
# End - FinishExcelFile








################################################################################
#
# DataShowHistogram
#
################################################################################
class DataShowHistogram():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, minVal, maxVal, numCLasses):
        self.minVal = minVal
        self.maxVal = maxVal
        self.numClasses = numCLasses

        valRange = float(self.maxVal - self.minVal)
        self.bucketSize = float(valRange) / float(self.numClasses)

        self.numVals = 0
        self.totalVal = 0 
        self.histogramBuckets = [0] * self.numClasses        
    # End -  __init__


    #####################################################
    # [DataShowHistogram::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    # [DataShowHistogram::GetNumBuckets
    #####################################################
    def GetNumBuckets(self):
        return self.numClasses

    #####################################################
    # [DataShowHistogram::GetBucketSize
    #####################################################
    def GetBucketSize(self):
        return self.bucketSize

    #####################################################
    # [DataShowHistogram::GetBuckets
    #####################################################
    def GetBuckets(self):
        return self.histogramBuckets


    #####################################################
    #
    # [DataShowHistogram::AddValue]
    #
    #####################################################
    def AddValue(self, value):
        # Ignore values of 0
        if (value <= 0):
            return

        if (value < self.minVal):
            value = self.minVal
        offset = value - self.minVal

        bucketNum = round(offset / self.bucketSize)
        if (bucketNum >= self.numClasses):
            bucketNum = self.numClasses - 1

        self.numVals += 1
        self.totalVal += value 
        self.histogramBuckets[bucketNum] += 1
    # End - AddValue


    #####################################################
    #
    # [DataShowHistogram::ShowHistogram]
    #
    #####################################################
    def ShowHistogram(self, titleStr, xLabelStr, yLabelStr, filePath):
        bucketNameList = []
        for index in range(self.numClasses):
            labelStr = ""
            if (index % 2) == 1:
                labelStr = "\n"            
            labelStr += str(index * self.bucketSize)
            bucketNameList.append(labelStr)
        # End - for index in range(self.numClasses):

        DrawBarGraph(titleStr, 
                    xLabelStr, bucketNameList, 
                    yLabelStr, self.histogramBuckets, 
                    False, filePath)
    # End - ShowHistogram

# End - class DataShowHistogram





################################################################################
#
# [DrawMultipleHistograms]
#
################################################################################
def DrawMultipleHistograms(titleStr, xLabelStr, yLabelStr, 
                            y1LabelStr, hist1,
                            y2LabelStr, hist2,
                            y3LabelStr, hist3,
                            filePath):
    # Color: b=blue, r=red, g=green, y=yellow, k=black, m=magenta, c=cyan
    colorList = ["b", "r", "g", "y", "k", "m", "c"]

    numClasses = hist1.GetNumBuckets()
    bucketSize = hist1.GetBucketSize()

    bucketNameList = []
    for index in range(numClasses):
        labelStr = ""
        if (index % 2) == 1:
            labelStr = "\n"            
        labelStr += str(index * bucketSize)
        bucketNameList.append(labelStr)
    # End - for index in range(self.numClasses):

    DrawTripleBarGraph(titleStr, xLabelStr, bucketNameList, yLabelStr, 
                        y1LabelStr, hist1.GetBuckets(), colorList[0],
                        y2LabelStr, hist2.GetBuckets(), colorList[1],
                        y3LabelStr, hist3.GetBuckets(), colorList[2],
                        False, filePath)
# End - DrawMultipleHistograms








################################################################################
#
# EventTimeline
#
# This makes a timeline graph, which shows values over time, and also special
# events.
#
################################################################################
class EventTimeline():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.eventList = []
        self.recordEveryNthValues = 1
        self.numValuesConsidered = 0
    # End -  __init__


    #####################################################
    # [EventTimeline::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    # [EventTimeline::RecordOnlyNthValue
    #####################################################
    def RecordOnlyNthValue(self, numValues):
        self.recordEveryNthValues = numValues
    # End - def RecordOnlyNthValue(numValues):


    #####################################################
    # [EventTimeline::
    #####################################################
    def AddValue(self, name, value):
        self.numValuesConsidered += 1
        if (self.numValuesConsidered < self.recordEveryNthValues):
            return

        self.numValuesConsidered = 0
        newEventDict = {'t': 'd', 'n': name, 'v': value}
        self.eventList.append(newEventDict)
    # End - AddValue


    #####################################################
    # [EventTimeline::
    # Typical events: epoch, process, loss, ....
    #####################################################
    def AddEvent(self, name):
        newEventDict = {'t': 'e', 'n': name, 'v': 0.0}
        self.eventList.append(newEventDict)
    # End - AddEvent


    #####################################################
    # [EventTimeline::SerializeToString
    #####################################################
    def SerializeToString(self):
        serialStr = ""
        for eventDict in self.eventList:
            serialStr += "t=" + str(eventDict['t']) + ",n=" + str(eventDict['n']) + ",v=" + str(eventDict['v']) + ";"
        # End - for eventDict in eventDictList:

        # Remove the trailing semicolon
        serialStr = serialStr[:-1]

        return serialStr
    # End - SerializeToString


    #####################################################
    # [EventTimeline::DeserializeFromString
    #####################################################
    def DeserializeFromString(self, eventListStr):
        fDebug = False
        if (fDebug):
            print("DeserializeFromString. eventListStr = " + eventListStr)

        self.eventList = []
        eventStrArray = eventListStr.split(";")
        for singleEventStr in eventStrArray:
            if (fDebug):
                print("DeserializeFromString. singleEventStr = " + singleEventStr)

            newEventDict = {}
            eventPairList = singleEventStr.split(',')
            for eventPairStr in eventPairList:
                if (fDebug):
                    print("DeserializeFromString. eventPairStr = " + eventPairStr)
                partsList = eventPairStr.split('=')
                if (fDebug):
                    print("DeserializeFromString. partsList = " + str(partsList))
                    print("DeserializeFromString. partsList[0] = " + str(partsList[0]))
                    print("DeserializeFromString. partsList[1] = " + str(partsList[1]))
                if (partsList[0] == 'v'):
                    newEventDict[partsList[0]] = float(partsList[1])
                else:
                    newEventDict[partsList[0]] = partsList[1]
            # End - for eventPairStr in eventPairList:

            self.eventList.append(newEventDict)
        # End - for eventStr in eventStrArray:
    # End - DeserializeFromString



    #####################################################
    # [EventTimeline::DrawTimeline
    #####################################################
    def DrawTimeline(self, titleStr, 
                        xLabelStr, 
                        yLabelStr,
                        desiredEventNameList, 
                        vertLineDict,
                        filePath):
        fDebug = True
        if (fDebug):
            print("DrawTimeline. desiredEventNameList=" + str(desiredEventNameList))

        # Discard any previous plots
        plt.clf()
        plt.cla()
        plt.style.use(WHITE_BACKGROUND_STYLE)

        # Make empty lists
        numEvents = len(desiredEventNameList)
        xValueListList = [[] for i in range(numEvents)]
        yValueListList = [[] for i in range(numEvents)]
        vertLineXList = []
        vertLineColorList = []
        vertLineNameList = []

        # Build up lists of values
        eventIndex = 0
        for event in self.eventList:
            if ((event['t'] == 'd') and (event['n'] in desiredEventNameList)):
                #print("DrawTimeline. Name=" + event['n'] + ", desiredEventNameList=" + str(desiredEventNameList))
                lineNumber = desiredEventNameList.index(event['n'])
                xValueList = xValueListList[lineNumber]
                yValueList = yValueListList[lineNumber]
                xValueList.append(eventIndex)
                yValueList.append(event['v'])
                eventIndex += 1
            elif ((event['t'] == 'e') and (event['n'] in vertLineDict)):
                vertLineXList.append(eventIndex)
                vertLineColorList.append(vertLineDict[event['n']])
                if (event['n'] not in vertLineNameList):
                    vertLineNameList.append(event['n'])
                else:
                    vertLineNameList.append(" ")
                eventIndex += 1
        # End - for event in self.eventList:

        # Now, draw each list
        # The format string is 3 chars:
        # Marker: "." dit, "o" circle
        # Line Style: "-" solid, "--" dashed
        # Color: b=blue, r=red, g=green, y=yellow, k=black, m=magenta, c=cyan
        formatStrList = [".-b", ".-r", ".-g", ".-y", ".-k", ".-m", ".-c",
                        "o--b", "o--r", "o--g", "o--y", "o--k", "o--m", "o--c"
                         ]
        lineList = []
        for index in range(numEvents):
            currentLine = plt.plot(xValueListList[index], yValueListList[index], formatStrList[index], 
                                    label=desiredEventNameList[index])
            lineList.append(currentLine)
        # End - for index in range(numLines):

        for name, xPos, colorStr in zip(vertLineNameList, vertLineXList, vertLineColorList):
            if (name != " "):
                plt.axvline(x=xPos, color=colorStr, label=name)
            else:
                plt.axvline(x=xPos, color=colorStr)
        # End - for xPos, color in zip(vertLineXList, vertLineColorList):

        # Add a legend box to correlate the colors with the group
        plt.legend()

        # Add labels
        if ((yLabelStr is not None) and (yLabelStr != "")):
            plt.ylabel(yLabelStr)
        if ((xLabelStr is not None) and (xLabelStr != "")):
            pass
            #plt.xlabel(xLabelStr)
        if ((titleStr is not None) and (titleStr != "")):
            plt.title(titleStr)

        # Hide the x-axis. The absolute values are not important, only their
        # relation to the events.
        plt.xticks([])

        if ((filePath is not None) and (filePath != "")):
            plt.savefig(filePath)
        #if (showInGUI): plt.show()

        plt.close()
    # End - DrawTimeline


# End - class EventTimeline






