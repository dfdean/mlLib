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
# Elixhauser Tools
#
# This uses the Elixhauser tables from the Healthcare Cost and Utilization Project 
# (HCUP, pronounced H-Cup), by the Agency for Healthcare Research and Quality (AHRQ).
#
# The ICD-10 Excel file is:
#    https://www.hcup-us.ahrq.gov/toolssoftware/comorbidityicd10/CMR-Reference-File-v2022-1.xlsx
#
# ICD-9 Tables are from:
#    https://www.hcup-us.ahrq.gov/toolssoftware/comorbidity/comformat2012-2015.txt  
################################################################################
import sys
import re

g_ICD9ToComorbiditiesDict = {}
g_ICD10ToComorbiditiesDict = {}

# This separaters different diagnoses
DIAGNOSIS_SEPARATOR_CHARACTER = "/"


g_ComorbidityToICD9Dict = {
    "AIDS": "042-044.9",   # HIV and AIDS
    "ALCOHOL": "291.0-291.3,291.5,291.8,291.81,291.82,291.89,291.9,303.00-303.93,305.00-305.03",   # Alcohol abuse
    "ANEMDEF": "280.1-281.9,285.21-285.29,285.9",   # Deficiency anemias
    "AUTOIMMUNE": "701.0,710.0-710.9,714.0-714.9,720.0-720.9,725",   # Rheumatoid arthritis
    "BLDLOSS": "280.0,648.20-648.24",   # Blood loss anemia
    "CANCER_LEUK": "",   # Leukemia ????
    "CANCER_LYMPH": "200.00-202.38,202.50-203.01,203.02-203.82,203.8-203.81,238.6,273.3",
    "CANCER_METS": "196.0-199.1,209.70,209.71,209.72,209.73,209.74,209.75,209.79,789.51",    # Metastatic cancer
    "CANCER_NSITU": "",   # ???
    "CANCER_SOLID": "140.0-172.9,174.0-175.9,179-195.8,209.00-209.24,209.25-209.3,209.30-209.36,258.01-258.03",   # Solid tumor without mets
    "CBVD_POA": "",   # CVA PoA???
    "CBVD_SQLA": "",   # CVA Sequela????
    "COAG": "286.0-286.9,287.1,287.3-287.5,289.84,649.30-649.34",  # Coagulation deficiency
    "DEMENTIA": "",   # ???
    "DEPRESS": "300.4,301.12,309.0,309.1,311",   # Depression
    "DIAB_CX": "249.40-249.91,250.40-250.93,775.1",   # Diabetes w/ chronic complications
    "DIAB_UNCX": "249.00-249.31,250.00-250.33,648.00-648.04",  # Diabetes w/o chronic complications
    "DRUG_ABUSE": "292.0,292.82-292.89,292.9,304.00-304.93,305.20-305.93,648.30-648.34",  # Drug abuse
    "HF": "398.91,402.01,402.11,402.91,404.01,404.03,404.11,404.13,404.91,404.93,428.0,428.1,428.2,428.3,428.4,428.5,428.6,428.7,428.8,428.9",   # Heart failure
    "HTN_CX": "401.0,402.00-405.99,437.2,642.10-642.24,642.70-642.94",    # Hypertension,complicated
    "HTN_UNCX": "401.1,401.9,642.00-642.04",  # Hypertension,uncomplicated
    "LIVER_MLD": "070.22,070.23,070.32,070.33,070.44,070.54,456.0,456.1,456.20,456.21,571.0,571.2,571.3,571.40-571.49,571.5,571.6,571.8,571.9,572.3,572.8,573.5,V42.7",   # Liver disease
    "LIVER_SEV": "",   # ?????
    "LUNG_CHRONIC": "490-492.8,493.00-493.92,494-494.1,495.0-505,506.4",   # Chronic pulmonary disease     
    "NEURO_MOVT": "",   # ?????
    "NEURO_OTH": "330.1-331.9,332.0,333.4,333.5,333.71,333.72,333.79,333.85,333.94,334.0-335.9,338.0,340,341.1-341.9,345.00-345.11,345.2-345.3,345.40-345.91,347.00-347.01,347.10-347.11,649.40-649.44,768.7,768.70,768.71,768.72,780.3,780.31,780.32,780.33,780.39,780.97,784.3",   # Other neurological
    "NEURO_SEIZ": "",   # ?????
    "OBESE": "278.0,278.00,278.01,278.03,649.10-649.14,793.91,V85.30-V85.39,V85.41-V85.45,V85.54",   # Obesity
    "PARALYSIS": "342.0-344.9,438.20-438.53,780.72",   # Paralysis
    "PERIVASC": "440-440.9,441.00-441.9,442.0-442.9,443.1-443.9,444.21-444.22,447.1,449,557.1,557.9,V43.4",   # Peripheral vascular disorder ????
    "PSYCHOSES": "295.00-298.9,299.10,299.11",   # Psychoses
    "PULMCIRC": "415.11-415.19,416.0-416.9,417.9",   # Pulmonary circulation disorder     
    "RENLFL_MOD": "403.01,403.11,403.91,404.02,404.03,404.12,404.13,404.92,404.93,585.3,585.4,585.5,585.6,585.9,586,V42.0,V45.1,V45.11,V45.12,V56.0-V56.32,V56.8",   # Renal failure
    "RENLFL_SEV": "",
    "THYROID_HYPO": "243-244.2,244.8,244.9",   # Hypothyroidism
    "THYROID_OTH": "",
    "ULCER_PEPTIC": "531.41,531.51,531.61,531.70,531.71,531.91,532.41,532.51,532.61,532.70,532.71,532.91,533.41,533.51,533.61,533.70,533.71,533.91,534.41,534.51,534.61,534.70,534.71,534.91",  # Chronic Peptic ulcer disease
    "VALVE": "093.20,093.21,093.22,093.23,093.24,394.0-397.1,397.9,424.0-424.99,746.3-746.6,V42.2,V43.3",  # Valvular disease
    "WGHTLOSS": "260-263.9,783.21,783.22"   # Weight loss
    #  "FLUIDS_LYTES": "276.0-276.9",   # ????
}  # g_ComorbidityToICD9Dict



g_ddean_ICD9_AKIList = ["584.9", "583.6", "584.6", "584.8", "959.9", "583.9", "646.2", "669.3", "584.7", "583.7", "584.5", "958.5"]

g_ddean_ICD10_AKIList = ["N17", "N17.0", "N17.1", "N17.2", "N17.8", "N17.9", "N00", "N00.0", "N00.1", "N00.2", "N00.3", "N00.4", "N00.5", "N00.6", "N00.7", "N00.8", "N00.9", "N01", "N01.0", "N01.1", "N01.2", "N01.3", "N01.4", "N01.5", "N01.6", "N01.7", "N01.8", "N01.9", "N10", "N15.1", "T79.5"]

g_ddean_ICD9_CKDList = ["586", "585.9", "997.5", "403.90", "403.91", "593.9", "585.1", "585.2", "585.3", "585.4", "585.5", "753.10", "753.19", "753.11", "753.12", "753.1.3", "753.14", "274.10", "753.19", "581.9", "581.81", "446.21", "583.81", "250.4", "249.4", "446.21", "710.0", "583.89", "583.9", "588.0", "095.4", "404.02", "404.0.3", "404.12", "404.1.3", "404.92", "404.9.3", "958.5", "277.39", "249.4", "446.21"]

g_ddean_ICD10_CKDList = ["N18", "N18.1", "N18.2", "N18.3", "N18.4", "N18.5", "N18.6", "N18.9", "N02", "N02.0", "N02.1", "N02.2", "N02.3", "N02.4", "N02.5", "N02.6", "N02.7", "N02.8", "N02.9", "N0.3", "N03.0", "N03.1", "N03.2", "N03.3", "N03.4", "N03.5", "N03.6", "N03.7", "N03.8", "N03.9", "N04", "N04.0", "N04.1", "N04.2", "N04.3", "N04.4", "N04.5", "N04.6", "N04.7", "N04.8", "N04.9", "N05", "N05.0", "N05.1", "N05.2", "N05.3", "N05.4", "N05.5", "N05.6", "N05.7", "N05.8", "N05.9", "N06", "N06.0", "N06.1", "N06.2", "N06.3", "N06.4", "N06.5", "N06.6", "N06.7", "N06.8", "N06.9", "N07", "N07.0", "N07.1", "N07.2", "N07.3", "N07.4", "N07.5", "N07.6", "N07.7", "N07.8", "N07.9", "N11", "N11.0", "N11.1", "N11.8", "N11.9", "N12", "N14", "N14.0", "N14.1", "N14.2", "N14.3", "N14.4", "N16", "N15.0", "N15.8", "N15.9", "R39.2", "N28.9", "E08.22", "E09.22", "E10.22", "E11.22", "E13.22", "I12", "I13"]

g_ddean_ICD9_ESRDList = ["586", "403.91", "402", "404.9.3", "404.12", "404.1.3", "404.02", "404.0.3", "484.5", "585.6", "585.9"]

g_ddean_ICD10_ESRDList = ["N19", "N18.6", "Z99.2", "N28.9"]

g_ddean_ICD9_HepatitisList = ["573.3", "573.1", "573.8", "573.9", "571.1", "571.3", "571.40", "571.41", "571.42", "571.49", "571.9", "570", "070.0", "070.1", "070.20", "070.21", "070.22", "070.2.3", "070.30", "070.31", "070.32", "070.3.3", "070.41", "070.42", "070.4.3", "070.44", "070.49", "070.5", "070.51", "070.54", "070.59", "070.6", "070.70", "070.9", "751.62", "V12.09", "V02.61", "V02.62", "070.52", "070.53"]

g_ddean_ICD10_HepatitisList = ["B17.9", "K75.9", "B15.9", "B19.9", "B25.1", "B00.81", "D86.89", "B58.1", "A18.83", "K70", "K70.0", "K70.1", "K70.10", "K70.11", "K70.2", "K70.3", "K70.30", "K70.31", "K70.4", "K70.40", "K70.41", "K70.9", "K71", "K71.0", "K71.1", "K71.10", "K71.11", "K71.2", "K71.3", "K71.4", "K71.5", "K71.50", "K71.51", "K71.6", "K71.7", "K71.8", "K71.9", "K72.0", "K72.01", "K72.00", "K7.3", "K73.0", "K73.1", "K73.2", "K73.8", "K73.9", "K75", "K75.0", "K75.1", "K75.2", "K75.3", "K75.4", "K75.8", "K75.81", "K75.89", "K75.9", "K76.0", "K76", "K76.2", "K76.3", "K76.4", "K76.5", "K76.6", "K76.7", "K76.8", "K76.81", "K76.89", "K76.9"]

g_ddean_ICD9_CirrhosisList = ["571.0", "571.2", "571.5", "571.6", "571.8", "570", "577.8", "646.7", "639.8", "674.8", "275.01", "275.0.3", "275.1", "277.00", "272.2", "587", "515", "573.8", "535.4"]

g_ddean_ICD10_CirrhosisList = ["K74", "K74.0", "K74.1", "K74.2", "K74.3", "K74.4", "K74.5", "K74.66", "K74.60", "K74.69", "K70.31", "K74.5", "B66.1", "K76.1", "E83.01", "K76.0", "K70.0", "K70.30"]
 
g_ddean_ICD9_ESLDList = ["572.8", "571.0", "571.1", "571.3", "571.8", "571.9", "573.3", "573.8", "573.9", "781.3", "277.39", "751.62", "570", "573.9"]

g_ddean_ICD10_ESLDList = ["K72.90", "K72.00", "K71.10", "K71.11", "K72.01", "K70.40", "K70.41", "K72.10", "K71.10", "K71.11", "K72.11", "K91.82", "K72.91", "K76.7", "K72.1", "K72.10", "K72.11", "K72.9", "K72.90", "K72.91"]




##############################
# DO NOT CHANGE THIS!!!!
# These are in a VERY specific order - they match the columns in the Elixhauser data file that defines 
# comorbidities for ICD-10 from the definitions file.
g_ComordityNames = ["AIDS", "ALCOHOL", "ANEMDEF", "AUTOIMMUNE", "BLDLOSS", 
                      "CANCER_LEUK", "CANCER_LYMPH", "CANCER_METS", "CANCER_NSITU", "CANCER_SOLID", 
                      "CBVD_POA", "CBVD_SQLA", "COAG", "DEMENTIA", "DEPRESS", "DIAB_CX", "DIAB_UNCX",
                      "DRUG_ABUSE", "HF", "HTN_CX", "HTN_UNCX", "LIVER_MLD", "LIVER_SEV", "LUNG_CHRONIC", 
                      "NEURO_MOVT", "NEURO_OTH", "NEURO_SEIZ", "OBESE", "PARALYSIS", "PERIVASC", 
                      "PSYCHOSES", "PULMCIRC", "RENLFL_MOD", "RENLFL_SEV", "THYROID_HYPO", "THYROID_OTH",
                      "ULCER_PEPTIC", "VALVE", "WGHTLOSS"]

g_ComordityDescriptiveStrings = ["AIDS", "Alcohol", "Deficiency Anemia", "Autoimmune Disorders", "Blood Loss Anemia", 
                      "Leukemia", "Lymphoma", "Metastatic Cancer", "In-Situ Cancer", "Solid Cancer", 
                      "Cerebral Vascular Disease (POA)", "Cerebral Vascular Disease Sequela", 
                            "Coagulopathy", "Dementia", "Depression", "Diabetes (complicated)", "Diabeles (uncomplicated)",
                      "Drug Abuse", "Heart Failure", "Hypertension (complicated)", "Hypertension (uncomplicated)", 
                            "Liver Disease (mild)", "Liver Disease (severe)", "Lung Disease", 
                      "Neuro Movement Disorders", "Neuro Disorders", "Seizures", "Obese", "Paralysis", "Perivascular Disease", 
                      "Psychosis", "Pulmonary circulation", "Renal failure (moderate)", "Renal failure (severe)", 
                      "Hypothyroid", "Thyroid Disease", "Peptic Ulcer", "Valvular Cardiomyopathy", "Weight Loss"]
##############################





################################################################################
#
# [ElixhauserLoadICD9Library]
#
################################################################################
def ElixhauserLoadICD9Library():
    global g_ICD9ToComorbiditiesDict
    fDebug = False

    g_ICD9ToComorbiditiesDict = {}
    for comorbidity, idc9StrList in g_ComorbidityToICD9Dict.items():
        if (fDebug):
            print("Comorbidity: " + comorbidity + ", ICDList=" + idc9StrList)

        icd9ListItems = idc9StrList.split(",")
        for icdItem in icd9ListItems:
            if (fDebug):
                print("icdItem=" + icdItem)

            numLeadingZeros = 0
            while (icdItem.startswith("0")):
                icdItem = icdItem[1:]
                numLeadingZeros += 1
            if (fDebug):
                print("icdItem=" + icdItem + ", numLeadingZeros=" + str(numLeadingZeros))

            leadingChar = ""
            if ("V" in icdItem):
                icdItem = icdItem.replace("V", "")
                leadingChar = "V"

            if ("-" in icdItem):
                icdItemParts = icdItem.split("-")
                if (len(icdItemParts) >= 2):
                    try:
                        startICDCodeStr = icdItemParts[0]
                        stopICDCodeStr = icdItemParts[1]
                        startICDCodeFloat = float(startICDCodeStr)
                        stopICDCodeFloat = float(stopICDCodeStr)
                    except Exception:
                        print("Error. Cannot convert ICDs to string: " + icdItem)
                        continue

                    codeIncrement = 1
                    if ("." in startICDCodeStr):
                        partsList = startICDCodeStr.split(".")
                        decimalSuffix = partsList[1]
                        if (len(decimalSuffix) == 1):
                            codeIncrement = 0.1
                        else:
                            codeIncrement = 0.01
                    
                    if (fDebug):
                        print("startICDCodeStr = " + startICDCodeStr + ", stopICDCodeStr = " + stopICDCodeStr
                            + ", startICDCodeFloat = " + str(startICDCodeFloat) 
                            + ", stopICDCodeFloat = " + str(stopICDCodeFloat))

                    currentICDCodeFloat = startICDCodeFloat
                    # You cannot use floats in a Python range operation. So, it is ok
                    # stylistically to use the old C-style for this loop.
                    while (currentICDCodeFloat <= stopICDCodeFloat):
                        currentICDCodeStr = str(currentICDCodeFloat)
                        for index in range(numLeadingZeros):
                            currentICDCodeStr = "0" + currentICDCodeStr
                        currentICDCodeStr = leadingChar + currentICDCodeStr

                        if (fDebug):
                            print("Register (from a range) currentICDCodeStr = " + currentICDCodeStr)
                        if currentICDCodeStr not in g_ICD9ToComorbiditiesDict:
                            g_ICD9ToComorbiditiesDict[currentICDCodeStr] = comorbidity
                        elif (comorbidity not in g_ICD9ToComorbiditiesDict[currentICDCodeStr]):
                            g_ICD9ToComorbiditiesDict[currentICDCodeStr] += (DIAGNOSIS_SEPARATOR_CHARACTER + comorbidity)

                        currentICDCodeFloat = round((currentICDCodeFloat + codeIncrement), 2)
                    # End - for icdCodeInt in range(startICDCode, stopICDCode + 1):
                # End - if (len(icdItemParts) >= 2):
            # if ("-" in icdItem):
            elif ("" == icdItem):
                continue
            else:
                try:
                    currentICDCodeFloat = float(icdItem)
                except Exception:
                    print("Error. Cannot convert ICDs to string: " + icdItem)
                    continue

                currentICDCodeStr = icdItem
                if (fDebug):
                    print("currentICDCodeFloat=" + str(currentICDCodeFloat))

                for index in range(numLeadingZeros):
                    currentICDCodeStr = "0" + currentICDCodeStr
                currentICDCodeStr = leadingChar + currentICDCodeStr

                if (fDebug):
                    print("Register currentICDCodeStr = " + currentICDCodeStr)
                if currentICDCodeStr not in g_ICD9ToComorbiditiesDict:
                    g_ICD9ToComorbiditiesDict[currentICDCodeStr] = comorbidity
                elif (comorbidity not in g_ICD9ToComorbiditiesDict[currentICDCodeStr]):
                    g_ICD9ToComorbiditiesDict[currentICDCodeStr] += (DIAGNOSIS_SEPARATOR_CHARACTER + comorbidity)
            # elif ("-" not in icdItem):
        # End - for icdItem in icd9ListItems:
    # End - for key, patientInfo in g_ComorbidityToICD9Dict.items():

    if (fDebug):
        print("\n\n\ng_ICD9ToComorbiditiesDict=" + str(g_ICD9ToComorbiditiesDict))
# End - ElixhauserLoadICD9Library







################################################################################
#
# [Elixhauser_LoadLibrary]
#
################################################################################
def Elixhauser_LoadLibrary(csvFilePathname):
    global g_ICD10ToComorbiditiesDict
    fDebug = False

    # Load the ICD-9 Library
    ElixhauserLoadICD9Library()

    ###################
    # Open the file.
    try:
        fileHandle = open(csvFilePathname, 'rb') 
    except Exception:
        print("Error from opening Lab file. File=" + csvFilePathname)
        return
    # Skip the first line of the file. This is just column headers.
    try:
        binaryLine = fileHandle.readline() 
    except Exception:
        pass
    lineNum = 1

    ############################################################
    # Read each line of the file.
    # I read them with a loop, so I do not load more than 1 line of text into
    # a variable at a time. These files are quite large, so I prefer the old-fashioned
    # C-style.
    while True: 
        # Get next line from file 
        try:
            binaryLine = fileHandle.readline() 
        except UnicodeDecodeError as err:
            print("Unicode Error from reading Lab file. lineNum=" + str(lineNum) + ", err=" + str(err))
            continue
        except Exception:
            print("Error from reading Lab file. lineNum=" + str(lineNum))
            continue

        # Convert the text from Unicode to ASCII. 
        try:
            line = binaryLine.decode("ascii", "ignore")
        except UnicodeDecodeError as err:
            print("Unicode Error from converting string. lineNum=" + str(lineNum) + ", err=" + str(err))
            continue
        except Exception:
            print("Error from converting string. lineNum=" + str(lineNum))
            continue

        #Remove whitespace including the trailing newline.
        line = line.rstrip()
  
        # if line is empty, end of file is reached 
        if not line: 
            break
        lineNum += 1

        # Skip the first 2 lines
        if (lineNum <= 2):
            continue

        if (fDebug):
            print("Elixhauser_LoadLibrary. Line = " + line)

        ############################################################
        # Read each field in the current line
        ############################################################
        # Remove comas within quotes, because we use the commas between quoted 
        # strings to separate the columns.
        line = re.sub(',(?=[^"]*"[^"]*(?:"[^"]*"[^"]*)*$)', "", line)
        words = line.split(",")
        # Strip quotes off the ends.
        for index in range(len(words)):
            currentWord = words[index]
            currentWord = currentWord.replace('"', '')
            currentWord = currentWord.replace("\'", '')
            words[index] = currentWord

        #ICD-10-CM Diagnosis,ICD-10-CM Code Description,NumComorbidities,AIDS,ALCOHOL,ANEMDEF,AUTOIMMUNE,BLDLOSS,CANCER_LEUK,CANCER_LYMPH,CANCER_METS,CANCER_NSITU,CANCER_SOLID,CBVD_POA,CBVD_SQLA,COAG,DEMENTIA,DEPRESS,DIAB_CX,DIAB_UNCX,DRUG_ABUSE,HF,HTN_CX,HTN_UNCX,LIVER_MLD,LIVER_SEV,LUNG_CHRONIC,NEURO_MOVT,NEURO_OTH,NEURO_SEIZ,OBESE,PARALYSIS,PERIVASC,PSYCHOSES,PULMCIRC,RENLFL_MOD,RENLFL_SEV,THYROID_HYPO,THYROID_OTH,ULCER_PEPTIC,VALVE,WGHTLOSS

        ######################
        try:
            icd10Code = words[0]
        except Exception:
            print("Error parsing icd10Code. line=" + line)
            sys.exit(0)
            continue
        ######################
        # icdCodeDescription = words[1]
        ######################
        try:
            numComorbidityStr = words[2]
        except Exception:
            print("Error parsing numComorbidityStr. line=" + line)
            sys.exit(0)
            continue

        ############################################################
        # Parse fields
        ############################################################
        comorbidityIndexList = []
        numComorboditiesToRead = int(numComorbidityStr)
        totalNumComorboditiesToRead = numComorboditiesToRead
        currentIndex = 3
        numWords = len(words)
        while ((numComorboditiesToRead > 0) and (currentIndex < numWords)):
            try:
                flagStr = words[currentIndex]
            except Exception:
                print("Error parsing flagStr. line=" + line)
                sys.exit(0)
                continue

            if (flagStr == "0"):
                pass
            elif (flagStr == "1"):
                comorbidityID = currentIndex - 3
                comorbidityIndexList.append(comorbidityID)
                numComorboditiesToRead = numComorboditiesToRead - 1
            else:
                print("Unrecognized flag: " + flagStr)

            currentIndex += 1
        # End - while (numComorboditiesToRead > 0):

        g_ICD10ToComorbiditiesDict[icd10Code] = comorbidityIndexList

        if (fDebug):
            print("icd10Code " + icd10Code + ": " + str(comorbidityIndexList))
        if (len(comorbidityIndexList) != totalNumComorboditiesToRead):
            print("ERROR! Did not read all comorbidities")
            print("Line=" + line)
            sys.exit(0)

        # End of parsing a single line
    # End - while True:

    fileHandle.close()
# Elixhauser_LoadLibrary






################################################################################
#
# [Elixhauser_ConvertICDToComorbidities]
#
# This is used when we import TDF files. 
################################################################################
def Elixhauser_ConvertICDToComorbidities(icdStr):
    global g_ICD10ToComorbiditiesDict
    fDebug = False

    comorbidityList = ""

    # ICD-10
    if (icdStr in g_ICD10ToComorbiditiesDict):
        if (fDebug):
            print("icdStr = " + icdStr)

        comorbidityIndexList = g_ICD10ToComorbiditiesDict[icdStr]
        if (fDebug):
            print("comorbidityIndexList = " + str(comorbidityIndexList))

        for comorbidityID in comorbidityIndexList:
            if (fDebug):
                print("comorbidityID = " + str(comorbidityID))
                print("g_ComordityNames[comorbidityID] = " + str(g_ComordityNames[comorbidityID]))
            comorbidityList = comorbidityList + g_ComordityNames[comorbidityID] + DIAGNOSIS_SEPARATOR_CHARACTER + icdStr + ","
            if (fDebug):
                print("comorbidityList = " + str(comorbidityList))
        # End - for comorbidityID in comorbidityIndexList
    # End - if (icdStr in g_ICD10ToComorbiditiesDict):

    # ICD-9
    icd9Str = icdStr      
    if (icd9Str in g_ICD9ToComorbiditiesDict):
        comorbidityIndexList = g_ICD9ToComorbiditiesDict[icd9Str]
        if (fDebug):
            print("comorbidityIndexList = " + str(comorbidityIndexList))

        comorbidityIndexListItems = comorbidityIndexList.split(DIAGNOSIS_SEPARATOR_CHARACTER)
        if (fDebug):
            print("comorbidityIndexListItems = " + str(comorbidityIndexListItems))

        for comorbidityID in comorbidityIndexListItems:
            if (fDebug):
                print("comorbidityID = " + str(comorbidityID))
            comorbidityList = comorbidityList + comorbidityID + DIAGNOSIS_SEPARATOR_CHARACTER + icdStr + ","
            if (fDebug):
                print("comorbidityList = " + str(comorbidityList))
        # End - for comorbidityID in comorbidityIndexList
    # End - if (icd9Str in g_ICD9ToComorbiditiesDict):

    
    if (comorbidityList == ""):
        comorbidityList = "U" + DIAGNOSIS_SEPARATOR_CHARACTER + icdStr
    else:
        comorbidityList = comorbidityList[:-1]

    if (fDebug):
        print("Final comorbidityList = " + comorbidityList)

    return comorbidityList
# End - Elixhauser_ConvertICDToComorbidities






################################################################################
#
#
################################################################################
class ElixhauserGroup():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.numPatients = 0
        self.fTrackAKI = False
        self.fTrackCKD = False
        self.fTrackAnemia = False
        self.NumPatientsWithAKI = 0
        self.NumPatientsWithAKIExtended = 0
        self.NumPatientsWithCKD = 0
        self.NumPatientsWithAnemia = 0

        self.Comorbidities = {}
        for comorbidity in g_ComordityNames:
            self.Comorbidities[comorbidity] = 0
    # End -  __init__


    #####################################################
    # [ElixhauserGroup::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #
    # [ElixhauserGroup::TrackAdditionalComorbidity]
    #
    #####################################################
    def TrackAdditionalComorbidity(self, comorbidityName):
        comorbidityName = comorbidityName.lower()
        if (comorbidityName == "aki"):
            self.fTrackAKI = True
        elif (comorbidityName == "ckd"):
            self.fTrackCKD = True
        elif (comorbidityName == "anemia"):
            print(">>>>> Track anemia")
            self.fTrackAnemia = True
    # End - TrackAdditionalComorbidity



    #####################################################
    #
    # [ElixhauserGroup::AddDiagnosisList]
    #
    #####################################################
    def AddDiagnosisList(self, diagnosisList):
        fDebug = False
        if (fDebug):
            print("AddDiagnosisList. diagnosisList=" + str(diagnosisList))

        if (diagnosisList is None):
            return

        self.numPatients += 1
        numAKIPatients = 0
        numCKDPatients = 0
        numAnemiaPatients = 0
        numAKIExtendedPatients = 0

        # Look at every ICD code for this patient
        for patientICDCodeStr in diagnosisList:
            if (fDebug):
                print("AddDiagnosisList. Look at patientICDCodeStr=" + patientICDCodeStr)

            if ((patientICDCodeStr in g_ddean_ICD10_AKIList) or (patientICDCodeStr in g_ddean_ICD9_AKIList)):
                numAKIExtendedPatients = 1
            if ((patientICDCodeStr in g_ddean_ICD10_CKDList) or (patientICDCodeStr is g_ddean_ICD9_CKDList)):
                numCKDPatients = 1

            if patientICDCodeStr in g_ICD10ToComorbiditiesDict:
                currentComorbidityList = g_ICD10ToComorbiditiesDict[patientICDCodeStr]
                if (fDebug):
                    print("Found an ICD10 code: " + patientICDCodeStr + ", currentComorbidityList=" 
                        + str(currentComorbidityList))
                for currentComorbidityInt in currentComorbidityList:
                    currentComorbidityName = g_ComordityNames[currentComorbidityInt]
                    self.Comorbidities[currentComorbidityName] += 1

                    #########################################
                    # We may also track some special comorbidities, outside the typical Elixhauser groups.
                    # Only count this once per patient
                    if ((currentComorbidityName == "RENLFL_MOD") or (currentComorbidityName == "RENLFL_SEV")):
                        numAKIPatients = 1
                    if ((currentComorbidityName == "ANEMDEF") or (currentComorbidityName == "BLDLOSS")):
                        numAnemiaPatients = 1

                    if (fDebug):
                        print("AddDiagnosisList. currentICDCodeStr Matches ICD10. currentComorbidityInt=" + str(currentComorbidityInt))
                        print("AddDiagnosisList. currentICDCodeStr Matches ICD10. currentComorbidityName=" + str(currentComorbidityName))
                # End - for currentComorbidityInt in currentComorbidityList:
            # End - if patientICDCodeStr in g_ICD10ToComorbiditiesDict:
            elif patientICDCodeStr in g_ICD9ToComorbiditiesDict:
                currentComorbidityList = g_ICD9ToComorbiditiesDict[patientICDCodeStr]
                namesArray = currentComorbidityList.split(DIAGNOSIS_SEPARATOR_CHARACTER)
                if (fDebug):
                    print("Found an ICD9 code: " + patientICDCodeStr + ", currentComorbidityList=" 
                            + str(currentComorbidityList))

                for comorbidityName in namesArray:
                    self.Comorbidities[comorbidityName] += 1

                    #########################################
                    # We may also track some special comorbidities, outside the typical Elixhauser groups.
                    # Only count this once per patient
                    if ((comorbidityName == "RENLFL_MOD") or (comorbidityName == "RENLFL_SEV")):
                        numAKIPatients = 1
                    if ((comorbidityName == "ANEMDEF") or (comorbidityName == "BLDLOSS")):
                        numAnemiaPatients = 1

                    if (fDebug):
                        print("AddDiagnosisList. currentICDCodeStr Matches ICD9. comorbidityName=" + str(comorbidityName))
                # End - for comorbidityName in namesArray:
            # End - elif patientICDCodeStr in g_ICD9ToComorbiditiesDict:
        # End - for patientICDCodeStr in diagnosisList:


        self.NumPatientsWithAKI += numAKIPatients
        self.NumPatientsWithAKIExtended += numAKIExtendedPatients
        self.NumPatientsWithCKD += numCKDPatients
        self.NumPatientsWithAnemia += numAnemiaPatients
    # End - AddDiagnosisList






    #####################################################
    #
    # [ElixhauserGroup::GetPatientsWithComorbidity]
    #
    #####################################################
    def GetPatientsWithComorbidity(self, comorbidityIndex):
        numPts = self.Comorbidities[comorbidityIndex]
        if (self.numPatients > 0):
            fractionPts = round((numPts / self.numPatients), 2)
        else:
            fractionPts = 0.0

        return fractionPts, numPts
    # End - GetPatientsWithComorbidity




    #####################################################
    #
    # [ElixhauserGroup::GetFractionPatientsWithComorbidity]
    #
    #####################################################
    def GetFractionPatientsWithComorbidity(self, comorbidityName):
        comorbidityName = comorbidityName.lower()
        fractionPts = 0

        if (comorbidityName == "aki"):
            fractionPts = round((self.NumPatientsWithAKI / self.numPatients), 2)
        elif (comorbidityName == "akiex"):
            fractionPts = round((self.NumPatientsWithAKIExtended / self.numPatients), 2)
        elif (comorbidityName == "ckd"):
            fractionPts = round((self.NumPatientsWithCKD / self.numPatients), 2)
        elif (comorbidityName == "anemia"):
            fractionPts = round((self.NumPatientsWithAnemia / self.numPatients), 2)

        return(fractionPts)
    # End - GetFractionPatientsWithComorbidity
 
# End - class ElixhauserGroup




################################################################################
#
# [PrintStatsForGroups]
#
################################################################################
def PrintStatsForGroups(title, groupList, nameStrList, filePathName):
    columnSpacer = ", "
    NEWLINE_STR = "\n"

    # Make the column headers at the top;
    textStr = NEWLINE_STR + " " + columnSpacer
    for nameStr in nameStrList:
        textStr = textStr + nameStr + " " + columnSpacer
    textStr += NEWLINE_STR

    # Write a row for each comorbidity
    numComorbities = len(g_ComordityNames)
    for index in range(numComorbities):
        textStr = textStr + g_ComordityDescriptiveStrings[index] + columnSpacer
        for group in groupList:
            fractionPts, numPts = group.GetPatientsWithComorbidity(g_ComordityNames[index])
            fractionPts = fractionPts * 100.0
            textStr = textStr + str(fractionPts) + "% (" + str(numPts) + ")" + columnSpacer
        # End - for group in groupList:

        textStr += NEWLINE_STR
    # End - for comorbidity in g_ComordityNames:

    print(textStr)
    if ((filePathName is not None) and (filePathName != "")):
        fileH = open(filePathName, "w+")
        fileH.write(textStr)
        fileH.close()
# End - PrintStatsForGroups






