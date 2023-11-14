################################################################################
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
################################################################################
#
# Utility Functions for local tool programs
#
# To import this into a tool program, include the following:
#
##################################
#from pathlib import Path
# Allow import to pull from the per-user lib directory.
#libDirPath = os.environ['DD_LIB_DIR']
#if libDirPath not in sys.path:
#    sys.path.insert(0, libDirPath)
#from ddToolsLib import *
#
################################################################################

import os
import sys
import shutil as shutil
from datetime import datetime

import xml.dom
import xml.dom.minidom
from xml.dom.minidom import parseString

import subprocess
from pathlib import Path
import psutil

# My own libraries
import xmlTools as dxml

#random.seed(3)
NEWLINE_STR = "\n"

g_LocalSecretsFilePathName = "/home/ddean/ddRoot/security/localSecrets.xml"
g_BackupLogFilePathName = "/home/ddean/ddRoot/logs/backupJobs.txt"
g_DataLogFilePathName = "/home/ddean/ddRoot/logs/dataTasks.txt"
g_AdminLogFilePathName = "/home/ddean/ddRoot/logs/adminTasks.txt"
g_PublishLogFilePathName = "/home/ddean/ddRoot/logs/publishTasks.txt"
g_DebugLogFilePathName = "/home/ddean/ddRoot/logs/debug.txt"
g_CodeLogFilePathName = "/home/ddean/ddRoot/logs/codeTasks.txt"
g_TasksLogFilePathName = "/home/ddean/ddRoot/logs/genTasks.txt"
g_LogFilePathName = g_BackupLogFilePathName
g_LogLinePrefix = ""
g_LogLineNum = 0
g_DebugLogResetInterval = -1
g_DebugMode = False





################################################################################
#
# [DDTools_Init]
#
################################################################################
def DDTools_Init(logPrefixStr, logFileID):
    global g_LogFilePathName
    global g_LogLinePrefix
    global g_DebugMode

    g_LogLinePrefix = logPrefixStr
    g_DebugMode = False

    # Set up the log file.
    logFileID = logFileID.lower()
    if (logFileID == "backup"):
        g_LogFilePathName = g_BackupLogFilePathName
    elif (logFileID == "admin"):
        g_LogFilePathName = g_AdminLogFilePathName
    elif (logFileID == "data"):
        g_LogFilePathName = g_DataLogFilePathName
    elif (logFileID == "publish"):
        g_LogFilePathName = g_PublishLogFilePathName
    elif (logFileID == "debug"):
        g_LogFilePathName = g_DebugLogFilePathName
        DDTools_InitDebug()
    elif (logFileID == "code"):
        g_LogFilePathName = g_CodeLogFilePathName
    elif (logFileID == "tasks"):
        g_LogFilePathName = g_TasksLogFilePathName
    else:
        g_LogFilePathName = g_BackupLogFilePathName
# End - DDTools_Init




################################################################################
#
# [DDTools_InitDebug]
#
################################################################################
def DDTools_InitDebug():
    global g_DebugMode
    g_DebugMode = True

    fileH = open(g_LogFilePathName, "w+")
    fileH.close()
# End - DDTools_InitDebug





################################################################################
#
# [DDTools_LogMemoryInfo]
#
################################################################################
def DDTools_LogMemoryInfo():
    #process = psutil.Process(os.getpid())
    textStr = str(psutil.virtual_memory())
    DDTools_Log(textStr)

    #textStr = str(psutil.swap_memory())
    #print("textStr=" + textStr)
# End - DDTools_LogMemoryInfo




################################################################################
#
# [DDTools_Log]
#
################################################################################
def DDTools_Log(message):
    global g_LogLineNum

    now = datetime.now()
    timeStr = now.strftime("%Y-%m-%d %H:%M:%S")
    textStr = timeStr + " " + g_LogLinePrefix + " " + message

    print(textStr)

    if ((g_DebugMode) and (g_DebugLogResetInterval > 0) and ((g_LogLineNum % g_DebugLogResetInterval) == 0)):
        fileH = open(g_LogFilePathName, "w+")
        fileH.write("Removed...." + NEWLINE_STR)
        fileH.close()
    g_LogLineNum += 1

    fileH = open(g_LogFilePathName, "a+")
    fileH.write(textStr + NEWLINE_STR)
    #fileH.flush()
    fileH.close()
# End - DDTools_Log






################################################################################
#
# [DDTools_RunProgram]
#
# commandStr has the format "ls -l"
################################################################################
def DDTools_RunProgram(commandStr):
    # commandArgStrList has the format ["ls", "-l"]
    commandArgStrList = [commandStr]

    try:
        # shell=True - run in a shell, so has all environment variables set
        # check=True - raise an exception if the return code is not 0
        # capture_output=True - Save stdOut and stderr in processResult.stdout and processResult.stderr
        #   Leave this as false. If you run a program from the shell prompt, this will print an
        #   error or user prompt, where you can see it during debugging. Otherwise, this
        #   gets silently tucked away and a command may hang.
        subprocess.run(commandArgStrList, capture_output=False, check=False, shell=True)
    except subprocess.CalledProcessError:  # as err:
        message = "DDTools_RunProgram Error: " + str(commandStr)
        DDTools_Log(message)
        return
    except subprocess.SubprocessError:  # as err:
        message = "DDTools_RunProgram Subprocess error: " + str(commandStr)
        DDTools_Log(message)
        return
    except OSError:  # as err:
        message = "DDTools_RunProgram OS error: " + str(commandStr)
        DDTools_Log(message)
        return
    except Exception:
        message = "DDTools_RunProgram. Unknown error cmd: " + str(commandStr)
        DDTools_Log(message)
        return
# End - DDTools_RunProgram






################################################################################
#
# [DDTools_ConvertSizeIntToStr]
#
################################################################################
def DDTools_ConvertSizeIntToStr(resultInt):
    if (resultInt > 1000000000):
        resultFloat = float(resultInt) / 1000000000.0
        suffix = " GB"
    elif (resultInt > 1000000):
        resultFloat = float(resultInt) / 1000000.0
        suffix = " MB"
    elif (resultInt > 1000):
        resultFloat = float(resultInt) / 1000.0
        suffix = " KB"
    else:
        resultFloat = float(resultInt)
        suffix = ""

    resultFloat = round(resultFloat, 1)
    result = str(resultFloat) + suffix

    return(result)
# End - DDTools_ConvertSizeIntToStr





################################################################################
#
# [DDTools_GetFileSizeAsStr]
#
################################################################################
def DDTools_GetFileSizeAsStr(filePath):
    resultInt = Path(filePath).stat().st_size
    result = DDTools_ConvertSizeIntToStr(resultInt)
    return(result)
# End - DDTools_GetFileSizeAsStr





################################################################################
#
# [DDTools_GetDirSizeAsInt]
#
################################################################################
def DDTools_GetDirSizeAsInt(folder):
    totalSize = os.path.getsize(folder)

    for fileName in os.listdir(folder):
        filePath = os.path.join(folder, fileName)

        if os.path.isfile(filePath):
            totalSize += os.path.getsize(filePath)
        elif os.path.isdir(filePath):
            totalSize += DDTools_GetDirSizeAsInt(filePath)

    return totalSize
# End - DDTools_GetDirSizeAsInt





################################################################################
#
# [DDTools_GetDirSizeAsStr]
#
################################################################################
def DDTools_GetDirSizeAsStr(folder):
    totalSize = DDTools_GetDirSizeAsInt(folder)
    totalSizeStr = DDTools_ConvertSizeIntToStr(totalSize)
    return totalSizeStr
# End - DDTools_GetDirSizeAsStr





################################################################################
#
################################################################################
def DDTools_DeleteDirContents(dirPathName):
    if ((dirPathName is None) or (dirPathName == "")):
        return
    if not os.path.exists(dirPathName):
        return

    for filename in os.listdir(dirPathName):
        filePathName = os.path.join(dirPathName, filename)
        try:
            if os.path.isfile(filePathName) or os.path.islink(filePathName):
                os.unlink(filePathName)
            elif os.path.isdir(filePathName):
                shutil.rmtree(filePathName)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (filePathName, e))
# End - DDTools_DeleteDirContents






################################################################################
#
#
################################################################################
def CopyAllFiles(srcDirPathName, destDirPathName):
    fDebug = False

    try:
        os.mkdir(destDirPathName)
    except Exception:
        pass
    try:
        os.chmod(destDirPathName, 0o777)
    except Exception:
        pass

    DDTools_DeleteDirContents(destDirPathName)


    if (os.path.isfile(srcDirPathName)):
        srcFilePathName = srcDirPathName
        fileName = os.path.basename(srcFilePathName)
        destFilePathName = os.path.join(destDirPathName, fileName)
        shutil.copy(srcFilePathName, destFilePathName)
    # End - if (os.path.isfile(srcDirPathName)):


    fileNameList = os.listdir(srcDirPathName)
    for fileName in fileNameList:
        srcFilePathName = os.path.join(srcDirPathName, fileName)
        destFilePathName = os.path.join(destDirPathName, fileName)
        if (fDebug):
            print("CheckPythonFilesInDir. fileName = " + fileName + ", srcFilePathName = " + srcFilePathName)

        if (os.path.isfile(srcFilePathName)):
            shutil.copy(srcFilePathName, destFilePathName)
        else:
            CopyAllFiles(srcFilePathName, destFilePathName)
        # End - if (fOKToCopyFile):
    # End - for fileName in fileNameList:
# End - CopyAllFiles







################################################################################
#
################################################################################
def DeleteFilesWithSuffix(dirPathName, fileSuffix):
    fileSuffix = fileSuffix.lower()

    if ((dirPathName is None) or (dirPathName == "") or (not os.path.exists(dirPathName))):
        return

    for filename in os.listdir(dirPathName):
        filePathName = os.path.join(dirPathName, filename)
        try:
            if (filename.lower().endswith(fileSuffix)):
                if os.path.isfile(filePathName) or os.path.islink(filePathName):
                    os.unlink(filePathName)
                elif os.path.isdir(filePathName):
                    shutil.rmtree(filePathName)
            # End - if (filename.lower().endswith(fileSuffix)):
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (filePathName, e))
# End - DeleteFilesWithSuffix





################################################################################
#
#
################################################################################
def CopyFilesWithSuffix(srcDirPathName, destDirPathName, fileSuffix):
    fDebug = False
    fileSuffix = fileSuffix.lower()

    try:
        os.mkdir(destDirPathName)
    except Exception:
        pass
    try:
        os.chmod(destDirPathName, 0o777)
    except Exception:
        pass

    DeleteFilesWithSuffix(destDirPathName, fileSuffix)


    if (os.path.isfile(srcDirPathName)):
        srcFilePathName = srcDirPathName
        fileName = os.path.basename(srcFilePathName)
        if ((fileName.lower().endswith(fileSuffix))):
            destFilePathName = os.path.join(destDirPathName, fileName)
            shutil.copy(srcFilePathName, destFilePathName)
        # End - if (fOKToCopyFile):
    # End - if (os.path.isfile(srcDirPathName)):


    fileNameList = os.listdir(srcDirPathName)
    for fileName in fileNameList:
        srcFilePathName = os.path.join(srcDirPathName, fileName)
        destFilePathName = os.path.join(destDirPathName, fileName)
        if (fDebug):
            print("CheckPythonFilesInDir. fileName = " + fileName + ", srcFilePathName = " + srcFilePathName)

        if ((os.path.isfile(srcFilePathName)) and (fileName.lower().endswith(fileSuffix))):
            shutil.copy(srcFilePathName, destFilePathName)
        # End - if (fOKToCopyFile):
    # End - for fileName in fileNameList:
# End - CopyFilesWithSuffix









################################################################################
#
# [DDTools_GetLocalSecret]
#
################################################################################
def DDTools_GetLocalSecret(secretName):
    fDebug = False

    # Read the file to a string.
    fileH = open(g_LocalSecretsFilePathName, "r")
    contentsText = fileH.read()
    fileH.close()
    if (fDebug):
        print("g_LocalSecretsFilePathName = " + g_LocalSecretsFilePathName)
        print("File contents = [" + contentsText + "]")

    # Parse the text string into am XML DOM
    try:
        xmlDOMObj = parseString(contentsText)
    except xml.parsers.expat.ExpatError as err:
        print("DDTools_GetLocalSecret. Error from parsing string:")
        print("ExpatError:" + str(err))
        print("contentsText=[" + contentsText + "]")
        return ""
    except Exception:
        print("DDTools_GetLocalSecret. Error from parsing string:")
        print("contentsText=[" + contentsText + "]")
        print("Unexpected error:", sys.exc_info()[0])
        return ""

    try:
        rootXMLNode = xmlDOMObj.getElementsByTagName("LocalSecrets")[0]
    except Exception:
        print("DDTools_GetLocalSecret. Required elements are missing: [" + contentsText + "]")
        return ""

    valueNode = dxml.XMLTools_GetChildNode(rootXMLNode, secretName)
    if (valueNode is None):
        return ""

    resultStr = dxml.XMLTools_GetTextContents(valueNode)
    return(resultStr)
# End - DDTools_GetLocalSecret




