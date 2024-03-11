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
# TDF - Timeline Data Format - MEDICAL Vocabulary
#
#
#  <E C=className V=value T=ttt V=aaa/bbb/ccc D=detail />
#  Attributes:
#      T="ttt" is the timestamp for when the event happened
#
#      C = className where className is one of:
#           Admit
#           Discharge
#           Transfer
#           RapidResponse
#           RadImg
#           Proc    This is a procedure, including some GI procedures
#           Surg    This is a surgery
#           Med
#           Clinic
#
#      V = value   where value is:
#           There is no V attribute for Admit, Discharge, RapidResponse
#
#           For Transfer the value is one of:
#               Ward
#               Prog    Progressive Care, or Stepdown ICU or Intermediate ICU
#               ICU
#               Surgery
#               ICU/newUnit (where newUnit is one of CCU, MICU, TSICU, SICU, NICU, CSRU)
#           By default, a patient is in "Ward" after admission.
#           Note, that I combine ER with Ward. The real use of this is to decide whether a patient
#           will go to the ICU, so ER and Ward are practically similar. Moreover, hospital procedures
#           for ER Boarders may blur the distinction between ER and Ward.
#
#           For RadImg, value is a pathnames, with the format modality/bodyPart
#           modality is one of CT, CTA
#           bodyPart is one of Head, Chest, PE, Abd/Pel, Abdom, Pelvis
#
#           For Proc (procedures) the value is a pathname of the procedure
#           Some examples include:
#               proc/CardiacCath
#               proc/EGD
#               proc/ERCP
#               proc/PericardiacDrain
#               proc/Intubation
#               proc/CentralLine
#               proc/ArtLine
#               proc/PEG
#               proc/ChestTube
#               proc/Thoracentesis
#               proc/Paracentesis
#               proc/Paracentesis
#               proc/Colonoscopy
#               proc/Bronchoscopy
#               proc/LP
#               proc/Dialysis
#
#            For Surg (surgery) the value is a pathname of the procedure
#               {Major | Minor}/bodyPart
#            Major vs minor tries to follow the general Revised Cardiac Risk Index (RCRI)
#            grouping. Some examples include:
#                  Minor/IncisDrain
#                  Minor/FNA
#                  Minor/Skin
#                  Minor/Heme
#                  Minor/Ophtho
#                  Minor/ENT
#                  Minor/Other
#
#                  Major/Ortho
#                  Major/Thoracic
#                  Major/Cardiac
#                  Major/Cardiac/CABG
#                  Major/Thoracic
#                  Major/GI
#                  Major/GU
#                  Major/Repro
#                  Major/OBGyn
#                  Major/Endo
#                  Major/Neuro
#
#           For Med, the value is an abbreviation. The abbreviations and the corresponding
#           med name is listed below.
#             Vanc - Vancomycin
#             PipTaz - Pip/Tazo
#             Tob - Tobramycin
#             Vori - Voriconazole
#             Fluc - Fluconazole
#             Coum - Coumadin
#             Tac - Tacrolimus
#             Siro - Sirolimus
#             Gent - Gentamycin
#             MTX - Methotrexate
#             Ever - Everolimus
#             CsA - Cyclosporine
#             Furos - Furosemide (IV or PO)
#             Tors - Torsemide (IV or PO)
#             Bum - Bumetanide IV (not PO)
#
#       D - Detail 
#           For Proc and Surg, this is CPT code
#           For Medications, this is the dose, as a number
#           For Micro, this is the fluid type
################################################################################

TDF_DATA_TYPE_INT                   = 0
TDF_DATA_TYPE_FLOAT                 = 1
TDF_DATA_TYPE_BOOL                  = 2
TDF_DATA_TYPE_FUTURE_EVENT_CLASS    = 3
TDF_DATA_TYPE_STRING_LIST           = 4
TDF_DATA_TYPE_UNKNOWN               = -1

TDF_NUM_FUTURE_EVENT_CATEGORIES = 14
TDF_MAX_FUTURE_EVENT_CATEGORY = (TDF_NUM_FUTURE_EVENT_CATEGORIES - 1)

ANY_EVENT_OR_VALUE = "ANY"


################################################################################
g_FunctionInfo = {'delta': {'resultDataType': TDF_DATA_TYPE_UNKNOWN},
    'rate': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate7': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate14': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate30': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate60': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate90': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate180': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'accel': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'faster7Than30': {'resultDataType': TDF_DATA_TYPE_BOOL},
    'runavg': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'bollup': {'resultDataType': TDF_DATA_TYPE_BOOL},
    'bolllow': {'resultDataType': TDF_DATA_TYPE_BOOL},
    'range': {'resultDataType': TDF_DATA_TYPE_UNKNOWN},
    'relrange': {'resultDataType': TDF_DATA_TYPE_UNKNOWN}
}  # g_FunctionInfo



################################################################################
# CBC
g_LabValueInfo = {'Hgb': {'minVal': 3.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbAlone': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbCBC': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbCBCDiff': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbABG': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbPathology': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    'WBC': {'minVal': 1.0, 'maxVal': 25.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Plt': {'minVal': 30.0, 'maxVal': 500.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'AbsNeutrophils': {'minVal': 0.1, 'maxVal': 25.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'AbsLymphs': {'minVal': 0.1, 'maxVal': 25.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    'MCV': {'minVal': 60.0, 'maxVal': 110.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Basic Metabolic Function Panel
    'Na': {'minVal': 115.0, 'maxVal': 155.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'K': {'minVal': 2.0, 'maxVal': 7.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Cl': {'minVal': 80.0, 'maxVal': 120.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'CO2': {'minVal': 10.0, 'maxVal': 35.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'BUN': {'minVal': 5.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Cr': {'minVal': 0.5, 'maxVal': 6.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Glc': {'minVal': 50.0, 'maxVal': 300.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Ca': {'minVal': 6.0, 'maxVal': 13.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'iCal': {'minVal': 1.0, 'maxVal': 6.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Phos': {'minVal': 1.0, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Mg': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Hepatic Function Panel
    'ALT': {'minVal': 10.0, 'maxVal': 150.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'AST': {'minVal': 10.0, 'maxVal': 150.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'ALP': {'minVal': 30.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Tbili': {'minVal': 0.5, 'maxVal': 20.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'TProt': {'minVal': 1.0, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Alb': {'minVal': 1.0, 'maxVal': 5.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Random Urine
    'UProt': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UAlb': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UNa': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UUN': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UCr': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UCl': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UK': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UCO2': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # 24hr Urine
    'UCr24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UProt24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UNa24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UCl24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UK24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UUN24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Misc
    'Lac': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'PT': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'PTT': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'INR': {'minVal': 1.0, 'maxVal': 7.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'DDimer': {'minVal': 0.1, 'maxVal': 5.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Fibrinogen': {'minVal': 0, 'maxVal': 2000, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Haptoglobin': {'minVal': 0, 'maxVal': 2000, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'FreeHgb': {'minVal': 0, 'maxVal': 2000, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'LDH': {'minVal': 0, 'maxVal': 2000, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'TropHS': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Trop': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'NTBNP': {'minVal': 50.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'BNP': {'minVal': 50.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'A1c': {'minVal': 5.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'PTH': {'minVal': 1.0, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'CK': {'minVal': 1.0, 'maxVal': 2000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Procal': {'minVal': 0.01, 'maxVal': 2.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'CRP': {'minVal': 1.0, 'maxVal': 20.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Lipase': {'minVal': 1.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'CystatinC': {'minVal': 1.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    'Transferrin': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'TransferrinSat': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Iron': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'TIBC': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Iron;TransferrinSat;Transferrin"},
    'Ferritin': {'minVal': 10.0, 'maxVal': 400.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # ABG and VBG
    'PO2': {'minVal': 20.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'PCO2': {'minVal': 20.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'BGSpO2': {'minVal': 50.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Drug levels
    'VancLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'TacLvl': {'minVal': 0.1, 'maxVal': 52.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'SiroLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'GentLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'TobLvl': {'minVal': 0.1, 'maxVal': 30.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'AmikLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'CycLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'MTXLvl': {'minVal': 0.5, 'maxVal': 26.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'EveroLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'DigLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'VoriLvl': {'minVal': 0.1, 'maxVal': 12.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'GabapLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'DaptoLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Derived values
    'GFR': {'minVal': 5.0, 'maxVal': 60.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "WtKg;AgeInYrs;Cr;IsMale"},
    'UPCR': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "UPEPTProt;UPCR;UProt;UCr"},
    'UACR': {'minVal': 0.01, 'maxVal': 5.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "UPEPAlb;UAlb;UCr"},
    'FENa': {'minVal': 0.01, 'maxVal': 2.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Cr;Na;UCr;UNa"},
    'FEUrea': {'minVal': 5.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Cr;BUN;UCr;UUN"},
    'AdjustCa': {'minVal': 6.0, 'maxVal': 13.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Ca;Alb"},
    'ProtGap': {'minVal': 1.0, 'maxVal': 7.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "TProt;Alb"},
    'AnionGap': {'minVal': 5.0, 'maxVal': 20.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Na;Cl;CO2"},
    'UrineAnionGap': {'minVal': -10.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "UNa;UK;UCl"},
    'BUNCrRatio': {'minVal': 1.0, 'maxVal': 30.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "BUN;Cr"},
    'NeutLymphRatio': {'minVal': -10.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "AbsNeutrophils;AbsLymphs"},
    'MELD': {'minVal': 1.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Cr;Na;Tbili;INR"},
    'BaselineCr': {'minVal': 0.3, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr"},
    'BaselineGFR': {'minVal': 10.0, 'maxVal': 60.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "WtKg;AgeInYrs;BaselineCr;IsMale"},
    'InAKI': {'minVal': 0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;BaselineCr"},

    ##############################
    # Myeloma workup
    'FLCKappa': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'FLCLambda': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UPEPAlb': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UPEPTProt': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UPEPTProt2': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'KappaLambdaRatio': {'minVal': 0.1, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "FLCKappa;FLCLambda"},
    'UPEPInterp': {'minVal': 1.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'SPEPInterp': {'minVal': 1.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Vitals
    'TF': {'minVal': 95.0, 'maxVal': 105.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'SBP': {'minVal': 50.0, 'maxVal': 180.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'DBP': {'minVal': 30.0, 'maxVal': 120.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HR': {'minVal': 30.0, 'maxVal': 160.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'SPO2': {'minVal': 70.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'WtKg': {'minVal': 30.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'BMI': {'minVal': 15.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Med Doses
    'VancDose': {'minVal': 150.0, 'maxVal': 2000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'CoumDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'EnoxDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'HeparinDripDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'ClopidogrelDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'PrasugrelDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'ApixDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'DabigDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'FurosIVDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'FurosDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'TorsDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'BumetDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'SpiroDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'ChlorthalDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'LisinDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'LosarDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'ValsarDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'EnalaprilDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'TacroDose': {'minVal': 1.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'CycDose': {'minVal': 50.0, 'maxVal': 750.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'MTXDose': {'minVal': 5.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'TobraDose': {'minVal': 50.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'VoriDose': {'minVal': 100.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'SiroDose': {'minVal': 10.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'GentDose': {'minVal': 10.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'AmikDose': {'minVal': 10.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'EveroDose': {'minVal': 10.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'DigDose': {'minVal': 10.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'GabaDose': {'minVal': 10.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'DaptoDose': {'minVal': 50.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'PipTazoDose': {'minVal': 1.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'MeroDose': {'minVal': 1.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'ErtaDose': {'minVal': 1.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'MetroDose': {'minVal': 1.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'CefepimeDose': {'minVal': 1.0, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'CeftriaxoneDose': {'minVal': 1.0, 'maxVal': 4.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'Dapto': {'minVal': 50.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'IbupDose': {'minVal': 1.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'KetorDose': {'minVal': 1.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'NaproxDose': {'minVal': 1.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'DiclofDose': {'minVal': 1.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},

    # Transfusions
    'TransRBC': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "inval", 'Calculated': False, 'VariableDependencies': ""},
    'TransPlts': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "inval", 'Calculated': False, 'VariableDependencies': ""},
    'TransFFP': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "inval", 'Calculated': False, 'VariableDependencies': ""},
    'TransCryo': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "inval", 'Calculated': False, 'VariableDependencies': ""},

    # Surgeries and Procedures
    'MajorSurgeries': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'GIProcedures': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Outcomes
    'DiedThisAdmission': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'DiedIn12Mos': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 60, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'ReadmitIn30Days': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    'HospitalDay': {'minVal': 0.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital"},
    'InHospital': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'InICU': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital"},

    ##############################
    # Patient Characteristice
    'IsMale': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'IsCaucasian': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Future Disease Stages by Boolean
    'Future_Boolean_Death': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "EventualDeathDate;InHospital;DiedThisAdmission"},
    'Future_Boolean_RapidResponse': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "NextFutureRapidResponseDate;InHospital"},
    'Future_Boolean_TransferIntoICU': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InICU;NextFutureTransferToICUDate;InHospital"},
    'Future_Boolean_TransferOutOfICU': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InICU;NextFutureTransferToWardDate;InHospital"},
    'Future_Boolean_CKD5': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_Boolean_CKD4': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_Boolean_CKD3b': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_Boolean_CKD3a': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},
    'Future_Boolean_MELD10': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD10Date"},
    'Future_Boolean_MELD20': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD20Date"},
    'Future_Boolean_MELD30': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD30Date"},
    'Future_Boolean_MELD40': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD40Date"},

    'Future_CKD5_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_CKD4_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_CKD3b_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_CKD3a_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},
    'Future_MELD10_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD10Date"},
    'Future_MELD20_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD20Date"},
    'Future_MELD30_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD30Date"},
    'Future_MELD40_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD40Date"},

    'Future_CKD5_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_CKD4_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_CKD3b_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_CKD3a_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},
    'Future_MELD10_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD10Date"},
    'Future_MELD20_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD20Date"},
    'Future_MELD30_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD30Date"},
    'Future_MELD40_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD40Date"},


    ##############################
    # Future Disease Stages by Number of Days
    'Future_Days_Until_Death': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "HospitalAdmitDate;EventualDeathDate;InHospital;DiedThisAdmission"},
    'Future_Days_Until_Discharge': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "HospitalAdmitDate;NextFutureDischargeDate;InHospital"},
    'Future_Days_Until_RapidResponse': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "NextFutureRapidResponseDate;InHospital"},
    'Future_Days_Until_TransferIntoICU': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InICU;NextFutureTransferToICUDate;InHospital"},
    'Future_Days_Until_TransferOutOfICU': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InICU;NextFutureTransferToWardDate;InHospital"},
    'Future_Days_Until_CKD5': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_Days_Until_CKD4': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_Days_Until_CKD3b': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_Days_Until_CKD3a': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},
    'Future_Days_Until_MELD10': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD10Date"},
    'Future_Days_Until_MELD20': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD20Date"},
    'Future_Days_Until_MELD30': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD30Date"},
    'Future_Days_Until_MELD40': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD40Date"},
    'Future_Days_Until_AKI': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;InAKI;NextAKIDate"},
    'Future_Days_Until_AKIResolution': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;InAKI;NextCrAtBaselineDate"},

    ##############################
    # Future Disease Stages by Time Category
    # Events, like death, rapid response, or discharge do not need any number of future days to predict.
    # If they do not happen in the remaining time inpatient, then they willnot happen.
    'Future_Category_Death': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': ANY_EVENT_OR_VALUE, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "EventualDeathDate;InHospital;DiedThisAdmission"},
    'Future_Category_Discharge': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': ANY_EVENT_OR_VALUE, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "HospitalAdmitDate;NextFutureDischargeDate;InHospital"},
    'Future_Category_RapidResponse': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': ANY_EVENT_OR_VALUE, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "NextFutureRapidResponseDate;InHospital"},
    'Future_Category_TransferIntoICU': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': ANY_EVENT_OR_VALUE, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InICU;NextFutureTransferToICUDate;InHospital"},
    'Future_Category_TransferOutOfICU': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': ANY_EVENT_OR_VALUE, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InICU;NextFutureTransferToWardDate;InHospital"},
    'Future_Category_CKD5': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "GFR", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_Category_CKD4': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "GFR", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_Category_CKD3b': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "GFR", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_Category_CKD3a': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "GFR", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},
    'Future_Category_MELD10': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "MELD", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD10Date"},
    'Future_Category_MELD20': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "MELD", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD20Date"},
    'Future_Category_MELD30': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "MELD", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD30Date"},
    'Future_Category_MELD40': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "MELD", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD;StartMELD40Date"},
    'Future_Category_AKI': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "Cr", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;InAKI;NextAKIDate"},
    'Future_Category_AKIResolution': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_EVENT_CATEGORY, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 30, 'FuturePredictedValue': "Cr", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;InAKI;NextCrAtBaselineDate"},

    ##############################
    # Time
    'AgeInYrs': {'minVal': 18.0, 'maxVal': 80.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': ""},
    'LengthOfStay': {'minVal': 0.0, 'maxVal': 90.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital;HospitalAdmitDate;HospitalAdmitDate"},

    ##############################
    # Events
    'HadDialysis': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MostRecentDialysisDate"},
    'HadSurgery': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MostRecentMajorSurgeryDate"},
    'Procedure': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_STRING_LIST, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "none", 'Calculated': False, 'VariableDependencies': ""},
    'Surgery': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_STRING_LIST, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "none", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Medical History
    'MedHxDiabetes': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyDiagnosis': {'minVal': 0.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Renal Biopsy Results - These were defined for the IU Renal Biopsy Study
    'BiopsyPercentObsGloms': {'minVal': 0.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'BiopsyPercentIFTA': {'minVal': 0.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyNumGloms': {'minVal': 0.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyIFTAScore': {'minVal': 0.0, 'maxVal': 5.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyArtHyalinizationScore': {'minVal': 0.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyCrescents': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyNodular': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyDiabetes': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyHypertension': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyATN': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyAIN': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyChronicTIN': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyTransplant': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyAcuteCellRejectionGrade': {'minVal': 0.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyXPlantAntibodyRejection': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyXPlantAcuteCellRejectionGrade': {'minVal': 0.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyXPlantC4d': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyXPlantTransplantGN': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyCancer': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyChronicVascRejection': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyBK': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyIgA': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyMembranous': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyLupusGrade': {'minVal': 0.0, 'maxVal': 6.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyLupus1': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyLupus2': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyLupus3': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyLupus4': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyLupus5': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyFSGS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyMCD': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyPodocyteEfface': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyANCA': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyPIGN': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyC3GN': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyFibrillary': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyAmyloid': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyMultMyeloma': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyCryos': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyMPGN': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyAntiTubularBM': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyTMA': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyTTPHUS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyAntiGBM': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyOxalate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyElecDenseDep': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyIgGStain': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyIgAStain': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyIgMStain': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyC3Stain': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyC1qGStain': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyKappaStain': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'RenalBiopsyLambdaStain': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},



    ##############################
    # INTERNAL USE ONLY
    # These are only used when compiling timeline events.
    'EventualDeathDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "DiedThisAdmission"},

    'StartCKD5Date': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR"},
    'StartCKD4Date': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR"},
    'StartCKD3bDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR"},
    'StartCKD3aDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR"},

    'StartMELD10Date': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD"},
    'StartMELD20Date': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD"},
    'StartMELD30Date': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD"},
    'StartMELD40Date': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MELD"},

    'NextCrAtBaselineDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;BaselineCr"},

    'NextAKIDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;InAKI;BaselineCr"},
    'Flag_HospitalAdmission': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'Flag_HospitalDischarge': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},

    'HospitalAdmitDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital"},
    'NextFutureDischargeDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "HospitalAdmitDate;NextFutureDischargeDate;InHospital"},
    'NextFutureRapidResponseDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital"},
    'NextFutureTransferToICUDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital;InICU"},
    'NextFutureTransferToWardDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ";InICU"},

    'MostRecentDialysisDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'MostRecentMajorSurgeryDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital"},

    'NewLabs': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue': "", 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""}
}  # g_LabValueInfo




