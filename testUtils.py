#####################################################################################
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
# Some utility procedures for testing and debugging.
#####################################################################################
import time
from datetime import datetime

Test_AllLogLines = ""
Test_NumTestWarnings = 0
Test_NumTestErrors = 0

Test_NumModulesTested = 0
Test_NumTests = 0

Test_SubTestNestingLevel = 0
Test_NumHeartbeats = 0
Test_HeartbeatsBeforeProgressIndicator = 10

Test_AllTestsStartTimeInSeconds = time.time()
Test_StartModuleTime = datetime.now()
Test_StartTestTime = datetime.now()

Test_ModuleState = "UNINITIALIZED"

NEWLINE_STR = "\n"



#####################################################
#
# [StartAllTests]
#
#####################################################
def Test_StartAllTests(testType):
    global Test_AllLogLines
    global Test_NumTestWarnings
    global Test_NumTestErrors
    global Test_NumModulesTested
    global Test_NumTests
    global Test_SubTestNestingLevel
    global Test_NumHeartbeats
    global Test_HeartbeatsBeforeProgressIndicator
    global Test_AllTestsStartTimeInSeconds

    Test_AllTestsStartTimeInSeconds = time.time()
    Test_AllLogLines = ""

    Test_NumModulesTested = 0
    Test_NumTests = 0
    Test_SubTestNestingLevel = 0

    Test_NumTestErrors = 0
    Test_NumTestWarnings = 0

    Test_NumHeartbeats = 0
    Test_HeartbeatsBeforeProgressIndicator = 10

    Test_Log(testType)
    #Test_Log("OS = " + str(platform.platform()))
    #Test_Log("CPU = " + str(platform.processor()))
    #Test_Log("GPU = None")
# StartAllTests.






#####################################################
#
# [Test_EndAllTests]
#
#####################################################
def Test_EndAllTests():
    durationInSeconds = time.time() - Test_AllTestsStartTimeInSeconds
    durationInSeconds = round(durationInSeconds, 1)

    Test_Log("  ")
    Test_Log("  ")
    Test_Log("======================")
    Test_Log("Elapsed Seconnds: " + str(durationInSeconds))
    Test_Log("Number Modules: " + str(Test_NumModulesTested))
    Test_Log("Number Steps: " + str(Test_NumTests))
    Test_Log("Total Errors: " + str(Test_NumTestErrors))
    Test_Log("Total Warnings: " + str(Test_NumTestWarnings))
    Test_Log("======================")
    Test_Log("  ")
# Test_EndAllTests.





#####################################################
#
# [Test_StartModuleTest]
#
#####################################################
def Test_StartModuleTest(moduleName):
    global Test_NumModulesTested
    global Test_SubTestNestingLevel
    global Test_StartModuleTime

    Test_SubTestNestingLevel = 0
    Test_NumModulesTested += 1
    Test_StartModuleTime = time.time()

    # Print the message.
    Test_Log(" ")
    Test_Log(" ")
    Test_Log("===================================================")
    Test_Log("Module: " + moduleName)
    Test_Log("===================================================")
# Test_StartModuleTest.





#####################################################
#
# [Test_StartTest]
#
#####################################################
def Test_StartTest(testName):
    global Test_NumTests
    global Test_NumHeartbeats
    global Test_StartTestTime

    Test_StartTestTime = time.time()

    Test_Log("==> Testing: " + testName)

    Test_NumTests += 1
    Test_NumHeartbeats = 0
# Test_StartTest





#####################################################
#
# [Test_Error]
#
#####################################################
def Test_Error(message):
    global Test_NumTestErrors

    Test_NumTestErrors += 1
    Test_Log("ERROR: " + message)
# Test_Error





#####################################################
#
# [Test_Warning]
#
#####################################################
def Test_Warning(message):
    global Test_NumTestWarnings

    Test_NumTestWarnings += 1
    Test_Log("Warn: " + message)
# Test_Warning



        

#####################################################
#
# [Test_CheckString]
#
#####################################################
def Test_CheckString(val, expectedStr):
    if (val != expectedStr):
        message = "Expected: " + expectedStr + ", but instead got: " + val
        Test_Error(message)
# Test_CheckString



        

#####################################################
#
# [Test_CheckInt]
#
#####################################################
def Test_CheckInt(val, expectedInt):
    if (val != expectedInt):
        message = "Expected: " + str(expectedInt) + ", but instead got: " + str(val)
        Test_Error(message)
# Test_CheckInt






#####################################################
#
# [Test_StartSubTest]
#
#####################################################
def Test_StartSubTest(testName):
    global Test_NumHeartbeats
    global Test_SubTestNestingLevel

    Test_NumHeartbeats = 0
    Test_SubTestNestingLevel += 1

    # Print the message.
    padding = ""
    for _ in range(Test_SubTestNestingLevel):
        padding = padding + "   "
    Test_Log(padding + "==> Testing: " + testName)
# Test_StartSubTest






#####################################################
#
# [Test_EndSubTest]
#
#####################################################
def Test_EndSubTest():
    global Test_NumHeartbeats
    global Test_SubTestNestingLevel

    Test_NumHeartbeats = 0
    Test_SubTestNestingLevel = max(Test_SubTestNestingLevel - 1, 0)
# Test_EndSubTest





#####################################################
#
# [Test_ShowProgress]
#
#####################################################
def Test_ShowProgress():
    global Test_NumHeartbeats

    Test_NumHeartbeats += 1
    if (Test_NumHeartbeats >= Test_HeartbeatsBeforeProgressIndicator):
        Test_Log(".")
        Test_NumHeartbeats = 0
# Test_ShowProgress.





#####################################################
#
# [Test_Log]
#
#####################################################
def Test_Log(messageStr):
    global Test_AllLogLines

    print(messageStr)

    timeStr = ""
    #now = datetime.now()
    #timeStr = now.strftime("%Y-%m-%d %H:%M:%S")

    completeLogLine = timeStr + " " + messageStr + NEWLINE_STR
    Test_AllLogLines = Test_AllLogLines + completeLogLine
# End of Test_Log








#####################################################
#
# [Test_InitModuleState]
#
#####################################################
def Test_InitModuleState():
    global Test_ModuleState

    Test_ModuleState = "Running"
# End of Test_InitModuleState




#####################################################
#
# [Test_ShowModuleState]
#
#####################################################
def Test_ShowModuleState():
    print("Test_ModuleState=" + Test_ModuleState)
# End of Test_ShowModuleState





