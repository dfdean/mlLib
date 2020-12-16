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
# TDF - Timeline Data Format
#
# The file is xml file format that is designed to store time-series of data for medical 
# applications. All Elements have close tags, and comments are standard XML comments.
#
# To read a TDF file, we typically iterate at several levels:
#   For each partition in the file
#       For each patient in the partition
#           For each event window in the patient
#               For each data entry in the current window
#
# You do not have to iterate over partitions, so you can instead just iterate over
#   all patients in the file. However, this allows you to have different worker processes
#   for a single file, and so avoid Python memory growth. That is important, because on very
#   large files, Python's heap can grow to consume all virtual memory and crash the process.
#
# You do not have to iterate over event windows, so you can instead just iterate over
#   all data for a single patient. This will be data for all admissions as one long sequence.
#
# So, in the simplest case:
#   For each patient in the file
#       For each data entry in the current patient
#
##########################################
# XML Syntax
# ------------
#  <TDF>
#  Parent Element: None (document root)
#  Child Elements: Head, PatientList
#  Text Contents: None
#  Attributes: None
#
#  <Head>
#  Parent Element: TDF
#  Child Elements: Description, Created, DataSource, Events, DataValues
#  Text Contents: None
#  Attributes: None
#
#  <Vocab>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: One of the element vocabularies. Current supported values are:
#           Medicine
#  Attributes: None
#
#  <Description>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: A human readable string that describes this data.
#  Attributes: None
#
#  <DataType>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: A human readable string that describes what this data is. For medical data, this includes "Patient", "Derived"
#  Attributes: None
#
#  <DataSource>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: A human readable string that describes where this data was extracted from
#  Attributes: None
#
#  <Created>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: Contains the time and data that the file was generated
#  Attributes: None
#
#  <Keywords>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: Contains a comma-separated list of Keywords
#  Attributes: None
#
#  <Events>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: Contains a comma-separated list of events
#  Attributes: None
#
#  <DataValues>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: Contains a comma-separated list of events
#  Attributes: None
#
#  <PatientList>
#  Parent Element: TDF
#  Child Elements: A list of <Patient> elements
#  Text Contents: None
#  Attributes: None
#
#
#  <Patient id=nnn gender=male race=c>
#  Parent Element: PatientList
#  Child Elements:
#     This contains all data and events for a single patient. This related
#     data is stored as nested elements below the Patient element.
#  Text Contents: None
#  Attributes: 
#       id = nnn
#           A unique id within this file. It is de-identified, so it is not
#           related to any actual MRN.
#
#       gender = "aaa" where aaa is one of:
#           M - Male
#           F - Female
#
#       race = "aaa" where aaa is one of:
#           ? - Unknown
#           W - white, caucasian
#           Af - African, African American
#           L - Latin, Hispanic
#           A - Asian
#           I - Asian Indian
#           AI - American Indian, Alaskan
#           ME - Middle Eastern
#
#       
#
#  <E C=className V=value T=ttt V=aaa/bbb/ccc D=detail />
#  Parent Element: Patient
#  Child Elements: None
#  Text Contents:
#     This element describes one or more events that happened at a time.
#     The events are a comma-separated list of words in the text of the element.
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
#               Tele
#               Prog    Progressive Care, or Stepdown ICU or Intermediate ICU
#               ICU
#               ICU/newUnit (where newUnit is one of CCU, MICU, TSICU, SICU, NICU, CSRU)
#           By default, a patient is in "Ward" after admission.
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
#             Dapto - Daptomycin
#             Mero - Meropenem
#             Cefep - Cefepime
#             Aztr - Aztreonam
#             Amik - Amikacin
#             Tob - Tobramycin
#             Vori - Voriconazole
#             Fluc - Fluconazole
#             Epi - Epinephrine
#             Norepi - Norepinephrine
#             Dop - Dopamine
#             Dobu - Dobutamine
#             Vaso - Vasopressin
#             Oct - Octreotide
#             Mido - Midodrine
#             Alb - Albumin
#             Nicar - Nicardipine
#             HyCor - Hydrocortisone
#             Pred - Prednisone
#             Dex - Dexamethasone
#             Nicar - Nicardipine
#             Amio - amiodarone
#             Coum - Coumadin
#             Apix - Apixaban
#             Riva - Rivaroxiban
#             Clop - clopidogrel
#             Ticag - ticagrelor
#             Dab - Dabigatran
#             Tac - Tacrolimus
#             Siro - Sirolimus
#             Gent - Gentamycin
#             MTX - Methotrexate
#             Ever - Everolimus
#             CsA - Cyclosporine
#             MMF - Mycophenolate
#             Myf - Mycophenolic
#             Azi - Azithromycin
#             PantopIV = IV Pantoprazole (scheduled or drip)
#             HepIV - IV Heparin (not subcu)
#             InsulIV - Insulin drip (not subcu)
#             DiltIV - IV Diltiazem (not PO)
#             FurosIV - IV furosemide (not PO)
#             BumIV - Bumetanide IV (not PO)
#             NTGIV - Nitroglycerin drip
#
#       P = Priority. This is only used for RadImg
#           The values are:
#               ROUTINE
#               ASAP
#               STAT
#
#       D - Detail 
#           For Proc and Surg, this is CPT code
#           For Medications, this is the dose, as a number
#           For Micro, this is the fluid type
#
# Optional Attributes - These may be included in some Events of class "Admit"
#       DiedInpt = T/F  Died During the Admission
#       DiedIn12Mos = T/F
#       Readmit30D = T/F Readmit In 30 Days
#
#
#
#  <OC scope=xxx>  name=value, name=value, name=value   </OC>
#       OC is short for "Outcomes" and this element contains a text list of outcomes either during 
#       a single admission or for the patient after all admissions. 
#       If the scope attribute is "Admit" then this applies just to the admission
#       If the scope attribute is "All" then this applies to the patient after all admissions.
#
#       In the text contents, name is one of:
#           DiedInpt - The value is "T" or "F". Died During the Admission
#           DiedIn12Mos - The value is "T" or "F"
#           ReadmitIn30Days - The value is "T" or "F"
#
#
#
#  <D C=className T=ttt>  name=value, name=value, name=value   </D>
#  Parent Element: Parient
#  Child Elements: None
#  Text Contents:
#   This element contains all data that is sampled at a single time.
#   An example is a Basic Metabolic Panel, which has 7 lab values, and all are
#   drawn from the same blood sample at the same time.    
#   The data values are stored as a text string of name=value pairs.
#             Na=131,K=3.7
#  Attributes:
#      T="ttt" is the timestamp for when the event happened
#
#      C = className  where className is one of:
#           L - Labs
#           V - Vitals
#           D - Diagnoses
#
#       V - A series of name value pairs, in the form:
#           name1=val1,name2=valw,name3=val3
#           The values are numbers except in a few specific cases below.
#
#
# For Vitals, the values are:
#       TF - Temperature in Faranheit
#       SBP - Systolic Blood Pressure
#       DBP - Diastolic Blood Pressure
#       HR - Heart Rate
#       SPO2 - Pulse Oximetry SpO2
#       WtKg - Weight in kg
#       BMI - BMI
#
#
#  For Labs, the values are:
#       CBC Labs
#       Hgb - Hemoglobin
#       WBC - WBC Count
#       Plt - Platelet Count
#
#       Basic Metabolic Panel Labs
#       Na - Sodium
#       K - Potassium
#       Cl - Chloride
#       CO2 - Bicarbonate
#       BUN - Urea Nitrogen Blood
#       Cr - Creatinine
#       Glc - Glucose
#       Ca - Calcium
#       iCal - Ionized Calcium
#       Phos - Phosphorus
#
#       Hepatic Function Panel
#       ALT - Alanine Aminotransferase
#       AST - AST
#       ALP - Alkaline Phosphatase
#       Tbili - Total Bilirubin
#       TProt - Total Protein
#       Alb - Albumin
#
#       Multiple Myeloma Workup
#       FLCKappa - Kappa Quantitative Free Light Chains
#       FLCLambda - Lambda Quantitative Free Light Chains
#       UPEPAlb - AlbuminElecUrine
#       UPEPTProt - Total Urine Protein Per Day UPEP
#       UPEPTProt2 - Total Urine Protein Per Day UPEP
#       UCr24hr - Total Urine Creatinine Urine Per Day
#       UUN24hr - Total Urea Nitrogen Urine Per Day
#       UPEPInterp - A quoted string
#       SPEPInterp - A quoted string
#
#       Blood Gas (both venous and arterial)
#       PO2 - PO2 (Arterial or Venous)
#       PCO2 - PCO2 (Arterial or Venous)
#       BGSpO2 - O2 SAT
#
#       Drug Doses
#       WarfarinDose - Warfarin dose (once daily)
#       CycDose - Cyclosporine for daily dose
#       CycDoseAM - Cyclosporine for AM dose
#       CycDosePM - Cyclosporine for PM dose
#       MTXDose - Daily dose, but may be given once weekly
#       TacroDoseAM - Tacrolimus AM dose
#       TacroDosePM - Tacrolimus PM dose
#       TobraDose - Tobramycin total daily dose
#       VancDose - Vancomycin total daily dose
#       VoriDose - Vori total daily dose
#
#       Drug Levels
#       VancLvl - Vancomycin Level Trough or Random
#       TacLvl - Tacrolimus Level
#       SiroLvl - Sirolimus Level
#       GentLvl - (Random, Peak, Trough)
#       TobLvl - Tobramycin Level (Random, Peak, Trough)
#       AmikLvl - Amikacin Level (Random, Peak, Trough)
#       CycLvl - Cyclosporine Level
#       MTXLvl - Methotrexate Level
#       EveroLvl - Everolimus Level
#       DigLvl - Digoxin Level
#       VoriLvl - Voriconazole level
#       GabapLvl - Gabapentin level
#
#       Random Urine Electrolytes
#       UNa - Sodium Urine
#       UUN - Urea Nitrogen Urine Random
#       UCr - Creatinine Urine Random
#       UCl - Chloride Urine Random
#       UK - Potassium Urine Random
#       UCO2 - CO2 Urine Random
#       UAlb - Albumin Urine
#       UProt - Protein Urine Random
#       UPCR - Urine Protein Creatinine Ratio
#
#       Miscellaneous Labs
#       Lac - Lactic Acid (Arterial or Venous)
#       PT - Prothrombin Time
#       PTT - PTT
#       TropHS - Troponin High Sensitivity
#       Trop - Troponin T  (CTNT)
#       INR - INR
#       Procal - Procalcitonin
#       A1c - Hemoglobin A1c
#       CRP - C-Reactive Protein
#       NTBNP - NT-proBNP
#       Lipase - Lipase
#       BNP - B-Natriuretic Peptide
#
# Derived values that are computed at runtime
#       GFR
#       BaselineGFR
#       BaselineCr
#       BaselineMELD
#       inAKI
#       UPCR
#       UACR
#       FENa
#       FEUrea
#       AdjustCa
#       ProtGap
#       AnionGap
#       UrineAnionGap
#       KappaLambdaRatio
#       MELD
#       CKDStage
#
#       Patient Characteristice
#       IsCaucasian - The value is 0 or 1
#       IsMale - The value is 0 or 1
#       WtKg
#
#       Time Values
#       AgeInYrs - Age of the patient at each time
#       AgeInDays
#
#
# Future Event Categories
# You cannot do "TimeUntil_xxx" because that cannot express the idea that the event "xxx" may
# never happen. Instead, use categories, like "xxx will happen", "xxxx will not happen" or
# time-bound categories like "xxx will happen in 3mos"
#
# Each "Future_XXX" variable is a category:
#       0 = EVENT is happening now or has previously happened
#       1 = EVENT will happen in 1 day
#       2 = EVENT will happen in 3 days
#       3 = EVENT will happen in 7 days
#       4 = EVENT will happen in 14 days
#       5 = EVENT will happen in 30 days
#       6 = EVENT will happen in 90 days
#       7 = EVENT will happen in 180 days
#       8 = EVENT will happen in 365 days
#       9 = EVENT will happen in 730 days (2yrs, some ESRD models use this)
#       10 = EVENT will happen in 1095 days (3yrs)
#       11 = EVENT will happen in 1825 days (5yrs, some ESRD models use this)
#       12 = EVENT will happen in 3650 days (10yrs, Framingham uses this)
#       13 = EVENT will not happen in the next 10yrs
#
#       Future_AKI
#       Future_AKIResolution
#       Future_CKD5
#       Future_CKD4
#       Future_CKD3
#       Future_Death
#       Future_Admission
#       Future_Discharge
#       Future_RapidResponse
#       Future_TransferIntoICU
#       Future_TransferOutOfICU
#       Future_Dialysis
#       Future_Intubation
#       Future_MELD10
#       Future_MELD20
#       Future_MELD30
#       Future_MELD40
#       Future_Cirrhosis
#       Future_ESLD
#       LengthOfStay
#
#   Outcomes
#       DiedInpt - The value is 0 or 1. Died During the Admission
#       DiedIn12Mos - The value is 0 or 1
#       ReadmitIn30Days - The value is 0 or 1
#       PreexistingMyeloma - The value is 0 or 1
#       DiagMyeloma - The value is 0 or 1
#
#       Status Values
#       InHospital - The value is 0 or 1
#       InICU - The value is 0 or 1
#
#
#
#  For Diagnoses, the values are:
#       Hepatitis
#       Cirrhosis
#       ESLD
#
#
#
#
#
#
#  <DiagPOA T=xxxx diag=value>
#  Attributes:
#      T="ttt" is the timestamp for when the event happened
#      diag = xxxxx
#
#
#
#  <Diag T=xxxx diag=value>
#  Attributes:
#      T="ttt" is the timestamp for when the event happened
#      diag = xxxxx
#
#
#  <Text T=ttt C=nnn>  some-text   </Text>
#  Parent Element: Patient
#  Child Elements: None
#  Text Contents:
#     This is a free text note or report 
#  Attributes:
#      T="ttt" is the timestamp for when the procedure was reported.
#      C="nnn" where nnn is one of:
#           Note
#
#
##########################################
#
# TimeStamps are a formatted string that is the time code. Each TimeStamp has the
# format:   
#          dd:hh:mm
# or:
#          dd:hh:mm:ss
#
# where:
#   dd is the number of days. 
#       The number may be positive or negative depending on whether the timecode
#       is before or after the indexEvent of the timeline.
#   hh is the number of hours. 
#   mm is the number of minutes. 
#   ss is the number of seconds. This is optional and not used for medical data.
#
# All numbers are 2 or more digits. They are padded with a leading 0 if the 
# number is < 10.
#
# Days are the day in your lifetime, so 365 is the 1st birthday, 3650 is the tenth birthday and
# 36500 is the 100th birthday. This representation has several advantages:
# 1. It is deidentified. It has no relation to the calendar date
# 2. It is easy to compute time intervals, like whether 2 dates are within 30 days of each other.
# 3. The same timestamp tells you when something happened in relation to all other events, and also
#   exactly how old the patient is at each event.
# 
#
##########################################
#
# The Reader API allows clients to iterate over several levels of detail:
# 1. A client can iterate over patients. 
# 2. Within a patient, a client can iterate over "windows".
# A window is all data recordings and events between a start and stop time.
# Each window is contained within a single patient record. 
# By default, there is a single window for each patient, so this contains all data 
# recordings and events for that patient. This may be useful, for example, if we want
# to track progression of a chronic disease in a single patient, and we want to follow
# the disease state across many different hospitalizations and clinic visits.
# Alternatively, a client may specify criteria that divide all data recordings and events
# into several windows. The criteria specify when a window starts and stops.
# Some example criteria include:
#     - Everything between admission and discharge to the hospital. This makes each hospital admission
#     a separate window.
#     - All events between a surgery and discharge. This looks at post-operative complications.
#     - All events between dialysis and 1 day later. This looks at post-dialysis complications.
# 3. Within a window, a client can iterate over data recordings and events.
#
#
#
#
##########################################
# DEPRECATED FEATURES:
#
#  <Preexisting> name=value   </Preexisting>
#  ***** DEPRECATED ***** (Used only in Myeloma)
#  Parent Element: Patient
#  Child Elements: None
#  Text Contents:
#   This is a comma-separated list of pre-existing conditions. 
#   These exist before any timed values.
#   Name is a condition, and the value is T or F
#  Attributes: None
#
#  <FinalDiag>  name=value   </FinalDiag>
#  ***** DEPRECATED ***** (Used only in Myeloma)
#  Parent Element: Patient
#  Child Elements: None
#  Text Contents:
#   This is a comma-separated list of final conditions
#   Name is a condition, and the value is T or F
#  Attributes:
#      T="ttt" is the timestamp for when the event happened
#
#      diag = xxxxx
################################################################################

import os
import sys
import math
import random
import statistics
from scipy.stats import spearmanr, kendalltau, pearsonr
import numpy as np
import time
import unicodedata
import string
import xml.dom
import xml.dom.minidom
from xml.dom import minidom
from xml.dom.minidom import parse, parseString
from datetime import datetime

import torch
from torch.utils.data import Dataset

# Normally we have to set the search path to load these.
# But, this .py file is always in the same directories as these imported modules.
from xmlTools import *

random.seed(3)
torch.manual_seed(1)

ANY_EVENT_OR_VALUE = "ANY"
NEWLINE_STR = "\n"

# This is 0-based, so January is 0
g_DaysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

TDF_DATA_TYPE_INT                   = 0
TDF_DATA_TYPE_FLOAT                 = 1
TDF_DATA_TYPE_BOOL                  = 2
TDF_DATA_TYPE_FUTURE_EVENT_CLASS    = 3
TDF_DATA_TYPE_UNKNOWN               = -1

# These are the values for a future event variable.
TDF_FUTURE_EVENT_NOW_OR_PAST    = 0
TDF_FUTURE_EVENT_IN_1_DAY       = 1
TDF_FUTURE_EVENT_IN_3_DAYS      = 2
TDF_FUTURE_EVENT_IN_7_DAYS      = 3
TDF_FUTURE_EVENT_IN_14_DAYS     = 4
TDF_FUTURE_EVENT_IN_30_DAYS     = 5
TDF_FUTURE_EVENT_IN_90_DAYS     = 6
TDF_FUTURE_EVENT_IN_180_DAYS    = 7
TDF_FUTURE_EVENT_IN_365_DAYS    = 8
TDF_FUTURE_EVENT_IN_730_DAYS    = 9
TDF_FUTURE_EVENT_IN_1095_DAYS   = 10
TDF_FUTURE_EVENT_IN_1825_DAYS   = 11
TDF_FUTURE_EVENT_IN_3650_DAYS   = 12
TDF_FUTURE_EVENT_NOT_IN_10YRS   = 13

TDF_NUM_CATEGORIES_IN_FUTURE_VAL = 14
TDF_MAX_FUTURE_VAL = (TDF_NUM_CATEGORIES_IN_FUTURE_VAL - 1)

MAX_PREVIOUS_LAB_EXTRA_PREVIOUS = 365
MAX_PREVIOUS_LAB_EXTRA_FUTURE   = 60

VARIABLE_START_OFFSET_MARKER    = "["
VARIABLE_STOP_OFFSET_MARKER     = "]"



################################################################################
                # CBC
g_LabValueInfo = {'Hgb': {'minVal': 2.0, 'maxVal': 17.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'WBC': {'minVal': 1.0, 'maxVal': 25.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Plt': {'minVal': 30.0, 'maxVal': 500.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MCV': {'minVal': 60.0, 'maxVal': 110.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # BMP
                'Na': {'minVal': 115.0, 'maxVal': 155.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'K': {'minVal': 2.0, 'maxVal': 7.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Cl': {'minVal': 80.0, 'maxVal': 120.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'CO2': {'minVal': 10.0, 'maxVal': 35.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'BUN': {'minVal': 5.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Cr': {'minVal': 0.3, 'maxVal': 8.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Glc': {'minVal': 50.0, 'maxVal': 300.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Ca': {'minVal': 6.0, 'maxVal': 13.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'iCal': {'minVal': 1.0, 'maxVal': 6.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Phos': {'minVal': 1.0, 'maxVal': 8.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Mg': {'minVal': 1.0, 'maxVal': 3.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # LFT
                'ALT': {'minVal': 10.0, 'maxVal': 150.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'AST': {'minVal': 10.0, 'maxVal': 150.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'ALP': {'minVal': 30.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Tbili': {'minVal': 0.5, 'maxVal': 20.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'TProt': {'minVal': 1.0, 'maxVal': 8.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Alb': {'minVal': 1.0, 'maxVal': 5.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Random Urine
                'UProt': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UAlb': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UNa': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UUN': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UCr': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UCl': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UK': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UCO2': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UAlb': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UProt': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # 24hr Urine
                'UPEPAlb': {'minVal': 1.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UPEPTProt': {'minVal': 1.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UCr24hr': {'minVal': 1.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UNa24hr': {'minVal': 1.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UCl24hr': {'minVal': 1.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UK24hr': {'minVal': 1.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UUN24hr': {'minVal': 1.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Myeloma workup
                'FLCKappa': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'FLCLambda': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UPEPAlb': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UPEPTProt': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UPEPTProt2': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UCr24hr': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UUN24hr': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Misc
                'Lac': {'minVal': 0.1, 'maxVal': 10.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'PT': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'PTT': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'INR': {'minVal': 1.0, 'maxVal': 7.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'TropHS': {'minVal': 1.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Trop': {'minVal': 0.1, 'maxVal': 10.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'NTBNP': {'minVal': 50.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'BNP': {'minVal': 50.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'A1c': {'minVal': 5.0, 'maxVal': 15.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Procal': {'minVal': 0.01, 'maxVal': 2.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'CRP': {'minVal': 1.0, 'maxVal': 20.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Lipase': {'minVal': 1.0, 'maxVal': 50.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # ABG and VBG
                'PO2': {'minVal': 20.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'PCO2': {'minVal': 20.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'BGSpO2': {'minVal': 50.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Drug levels
                'VancLvl': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'TacLvl': {'minVal': 0.1, 'maxVal': 52.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'Sirolimus': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'GentLvl': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'TobLvl': {'minVal': 0.1, 'maxVal': 30.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'AmikLvl': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'CycLvl': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MTXLvl': {'minVal': 0.5, 'maxVal': 26.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'EveroLvl': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'DigLvl': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'VoriLvl': {'minVal': 0.1, 'maxVal': 12.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'GabapLvl': {'minVal': 0.1, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Derived values
                'GFR': {'minVal': 1.0, 'maxVal': 90.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UPCR': {'minVal': 0.1, 'maxVal': 10.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UACR': {'minVal': 0.01, 'maxVal': 5.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'FENa': {'minVal': 0.01, 'maxVal': 2.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'FEUrea': {'minVal': 5.0, 'maxVal': 50.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'AdjustCa': {'minVal': 6.0, 'maxVal': 13.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'ProtGap': {'minVal': 1.0, 'maxVal': 7.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'AnionGap': {'minVal': 5.0, 'maxVal': 20.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UrineAnionGap': {'minVal': -10.0, 'maxVal': 10.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'KappaLambdaRatio': {'minVal': 0.1, 'maxVal': 8.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'UPEPInterp': {'minVal': 1.0, 'maxVal': 10.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'SPEPInterp': {'minVal': 1.0, 'maxVal': 10.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Chronic Disease States
                'MELD': {'minVal': 1.0, 'maxVal': 50.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'CKDStage': {'minVal': 1.0, 'maxVal': 5.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'BaselineCr': {'minVal': 0.3, 'maxVal': 8.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'BaselineGFR': {'minVal': 1.0, 'maxVal': 90.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'BaselineMELD': {'minVal': 1.0, 'maxVal': 90.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'inAKI': {'minVal': 0, 'maxVal': 1.0, 'derived': 1, 'dataType': "Boolean", 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Vitals
                'TF': {'minVal': 95.0, 'maxVal': 105.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'SBP': {'minVal': 50.0, 'maxVal': 180.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'DBP': {'minVal': 30.0, 'maxVal': 120.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'HR': {'minVal': 30.0, 'maxVal': 160.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'SPO2': {'minVal': 70.0, 'maxVal': 100.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'WtKg': {'minVal': 30.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'BMI': {'minVal': 15.0, 'maxVal': 50.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Med Doses
                'WarfarinDose': {'minVal': 1.0, 'maxVal': 9.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'CycDose': {'minVal': 50.0, 'maxVal': 750.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'CycDoseAM': {'minVal': 50.0, 'maxVal': 750.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'CycDosePM': {'minVal': 50.0, 'maxVal': 750.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MTXDose': {'minVal': 5.0, 'maxVal': 50.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'TacroDoseAM': {'minVal': 1.0, 'maxVal': 10.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'TacroDosePM': {'minVal': 1.0, 'maxVal': 10.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'VancDose': {'minVal': 150.0, 'maxVal': 2000.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'TobraDose': {'minVal': 50.0, 'maxVal': 200.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'VoriDose': {'minVal': 100.0, 'maxVal': 600.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_FLOAT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Outcomes
                'DiedInpt': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'DiedIn12Mos': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 60, 'FuturePredictedValue':""},
                'ReadmitIn30Days': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 30, 'FuturePredictedValue':""},
                'PreexistingMyeloma': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'DiagMyeloma': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'InHospital': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'InICU': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Patient Characteristice
                'IsMale': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'IsCaucasian': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # Future Events
                'Future_Death': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 90, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_Admission': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 90, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_Discharge': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 7, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_RapidResponse': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 14, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_TransferIntoICU': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 14, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_TransferOutOfICU': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 14, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_Dialysis': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 60, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_Intubation': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 10, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_CKD5': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 180, 'FuturePredictedValue':"CKDStage"},
                'Future_CKD4': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 180, 'FuturePredictedValue':"CKDStage"},
                'Future_CKD3': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 180, 'FuturePredictedValue':"CKDStage"},
                'Future_MELD10': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 180, 'FuturePredictedValue':"MELD"},
                'Future_MELD20': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 180, 'FuturePredictedValue':"MELD"},
                'Future_MELD30': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 180, 'FuturePredictedValue':"MELD"},
                'Future_MELD40': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 180, 'FuturePredictedValue':"MELD"},
                'Future_Cirrhosis': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 180, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_ESLD': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': -1, 'FuturePredictedValue':ANY_EVENT_OR_VALUE},
                'Future_AKI': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': -1, 'FuturePredictedValue':"Cr"},
                'Future_AKIResolution': {'minVal': 0.0, 'maxVal': TDF_MAX_FUTURE_VAL, 'derived': 1, 'dataType': TDF_DATA_TYPE_FUTURE_EVENT_CLASS, 'numFutureDaysNeeded': 60, 'FuturePredictedValue':"Cr"},


                # Time
                'AgeInYrs': {'minVal': 18.0, 'maxVal': 90.0, 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'AgeInDays': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'DaysSinceDialysis': {'minVal': -1.0, 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': -1, 'FuturePredictedValue':""},
                'LengthOfStay': {'minVal': 0.0, 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': -1, 'FuturePredictedValue':""},
                'DaysSinceStart': {'minVal': 0.0, 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'DaysUntilStop': {'minVal': 0.0, 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': -1, 'FuturePredictedValue':""},


                # Events
                'MostRecentDialysisDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MostRecentCardiacCathDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MostRecentIntubationDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MostRecentPEGDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MostRecentCABGDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MostRecentMajorSurgeryDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},
                'MostRecentRapidResponseDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'derived': 1, 'dataType': TDF_DATA_TYPE_INT, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""},

                # MetaData
                'NewLabs': {'minVal': 0.0, 'maxVal': 1.0, 'derived': 0, 'dataType': TDF_DATA_TYPE_BOOL, 'numFutureDaysNeeded': 0, 'FuturePredictedValue':""}
}




g_TDF_Log_Buffer = ""


################################################################################
#
# [TDF_ClearLog]
#
################################################################################
def TDF_ClearLog():
    global g_TDF_Log_Buffer
    g_TDF_Log_Buffer = ""
# End - TDF_ClearLog




################################################################################
#
# [TDF_Log]
#
################################################################################
def TDF_Log(message):
    global g_TDF_Log_Buffer
    g_TDF_Log_Buffer = g_TDF_Log_Buffer + "TDF: " + message + "\n"
# End - TDF_Log




################################################################################
#
# [TDF_GetLog]
#
################################################################################
def TDF_GetLog():
    global g_TDF_Log_Buffer
    return(g_TDF_Log_Buffer)
# End - TDF_GetLog





################################################################################
# 
# This creates a formatted string that is the time code. Each timecode has the
# format:
#          dd:hh:mm
# or:
#          dd:hh:mm:ss
#
# where:
#   dd is the number of days. 
#       The number may be positive or negative depending on whether the timecode
#       is before or after the indexEvent of the timeline.
#   hh is the number of hours. 
#   mm is the number of minutes. 
#   ss is the number of seconds. This is optional and not used for medical data.
#
# All numbers are 2 or more digits. They are padded with a leading 0 if the 
# number is < 10.
################################################################################
def TDF_MakeTimeStamp(days, hours, minutes):
    result = "{0:0>2d}:{1:0>2d}:{2:0>2d}".format(days, hours, minutes)
    #print("\nresult=" + result)
    return result
# End - TDF_MakeTimeStamp




################################################################################
# 
################################################################################
def TDF_MakeTimeStampWithSeconds(days, hours, minutes, seconds):
    if (seconds >= 0):
        result = "{0:0>2d}:{1:0>2d}:{2:0>2d}:{3:0>2d}".format(days, hours, minutes, seconds)
    else:
        result = "{0:0>2d}:{1:0>2d}:{2:0>2d}".format(days, hours, minutes)

    #print("\nresult=" + result)
    return result
# End - TDF_MakeTimeStampWithSeconds





################################################################################
# 
# This parses a formatted string that is a time code and converts it to the
# number of seconds. Each timecode has the format:   nn:nn:nn:nn
# where:
#
#   nn is the number of days
#   nn is the number of hours
#   nn is the number of minutes 
#   nn is the number of seconds 
#
# All numbers are 2 or more digits. They are padded with a leading 0 if the 
# number is < 10.
#  
################################################################################
def TDF_ConvertTimeStampToInt(timeCode):
    result = 0
    words = timeCode.split(':')

    # Add days in seconds
    valStr = words[0]
    result = result + (int(valStr) * 24 * 60 * 60)

    # Add hours in seconds
    valStr = words[1]
    result = result + (int(valStr) * 60 * 60)

    # Add minutes in seconds
    valStr = words[2]
    result = result + (int(valStr) * 60)

    # Add seconds if they are present - these are optional
    if (len(words) >= 4):
        valStr = words[3]
        result = result + int(valStr)

    return(result)
# End - TDF_ConvertTimeStampToInt





################################################################################
# 
# This parses a formatted string that is a time code and converts it to separate 
# integers
#  
################################################################################
def TDF_ParseTimeStamp(timeCode):
    if (timeCode == ""):
        print("Error. TDF_ParseTimeStamp invalid str: " + timeCode)
        sys.exit(0)
        return 0,0,0
    words = timeCode.split(':')

    days = int(words[0])
    hours = int(words[1])
    min = int(words[2])

    return days, hours, min
# End - TDF_ParseTimeStamp




################################################################################
# 
# This parses a formatted string that is a time code and converts it to separate 
# integers
#  
################################################################################
def TDF_ParseTimeStampWithSecs(timeCode):
    if (timeCode == ""):
        print("Error. TDF_ParseTimeStampWithSecs invalid str: " + timeCode)
        sys.exit(0)
        return 0,0,0,0
    words = timeCode.split(':')

    days = int(words[0])
    hours = int(words[1])
    min = int(words[2])
    sec = -1
    if (len(words) >= 4):
        sec = int(words[3])

    return days, hours, min, sec
# End - TDF_ParseTimeStampWithSecs






################################################################################
#
# This is used only for writing a TDF File. Typically, it is used when importing 
# data from some other format into TDF.
#
# BUGBUG FIXME - The TDF writer seems to emit text with < or > for some lab values.
#
# BUGBUG FIXME - The TDF writer seems to accidentally add the same drug several times.
################################################################################
class TDFFileWriter():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        return
    # End -  __init__


    #####################################################
    #
    # [TDFFileWriter::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return
    # End of destructor


    #####################################################
    #
    # [TDFFileWriter::SaveAndClose]
    #
    # Called to explicitly release resources
    #####################################################
    def SaveAndClose(self):
        self.outputFileH.flush()
        self.outputFileH.close()
    # End of SaveAndClose




    #####################################################
    #
    # [TDFFileWriter::__SetFileOutputFileHandle__
    # 
    #####################################################
    def __SetFileOutputFileHandle__(self, fileH):
        self.outputFileH = fileH
    # End -  __SetFileOutputFileHandle__



    #####################################################
    #
    # [TDFFileWriter::WriteHeader]
    #
    #####################################################
    def WriteHeader(self, comment, dataSourceStr, keywordStr):
        self.outputFileH.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + NEWLINE_STR)    
        self.outputFileH.write("<TDF version=\"1.0\">" + NEWLINE_STR)
        self.outputFileH.write(NEWLINE_STR)
        self.outputFileH.write("<Head>" + NEWLINE_STR)
        self.outputFileH.write("    <Vocab>Medicine</Vocab>" + NEWLINE_STR)
        self.outputFileH.write("    <Description>" + comment + "</Description>" + NEWLINE_STR)        
        self.outputFileH.write("    <DataSource>" + dataSourceStr + "</DataSource>" + NEWLINE_STR)
        self.outputFileH.write("    <Created>" + datetime.today().strftime('%b-%d-%Y') + " " 
                + datetime.today().strftime('%H:%M') + "</Created>" + NEWLINE_STR)
        self.outputFileH.write("    <Keywords>" + keywordStr + "</Keywords>" + NEWLINE_STR)        
        self.outputFileH.write("</Head>" + NEWLINE_STR)    
        self.outputFileH.write(NEWLINE_STR)
        self.outputFileH.write("<PatientList>" + NEWLINE_STR)    
    # End of WriteHeader




    #####################################################
    #
    # [TDFFileWriter::WriteFooter]
    #
    #####################################################
    def WriteFooter(self):
        self.outputFileH.write(NEWLINE_STR + "</PatientList>" + NEWLINE_STR)    
        self.outputFileH.write(NEWLINE_STR + "</TDF>" + NEWLINE_STR)
        self.outputFileH.write(NEWLINE_STR + NEWLINE_STR)
    # End of WriteFooter




    #####################################################
    #
    # [TDFFileWriter::WriteXMLNode]
    #
    #####################################################
    def WriteXMLNode(self, xmlNode):
        #print("Starting WriteXMLNode")
        bytesStr = xmlNode.toprettyxml(indent='  ', newl='', encoding="utf-8")
        textStr = bytesStr.decode("utf-8", "strict")  

        self.outputFileH.write(NEWLINE_STR + NEWLINE_STR)
        self.outputFileH.write(textStr)
    # End of WriteXMLNode




    ################################################################################
    # 
    # [TDFFileWriter::StartPatientNode]
    #
    ################################################################################
    def StartPatientNode(self, patientID, gender, race):
        textStr = NEWLINE_STR + NEWLINE_STR + "<Patient"
        textStr = textStr + " id=\"" + str(patientID) + "\""

        if ((gender != None) and (gender != "")):
            textStr = textStr + " gender=\"" + gender + "\""

        if ((race != None) and (race != "")):
            textStr = textStr + " race=\"" + race + "\""

        textStr = textStr + ">" + NEWLINE_STR

        self.outputFileH.write(textStr)
    # End - StartPatientNode




    ################################################################################
    # 
    # [TDFFileWriter::FinishPatientNode]
    #
    ################################################################################
    def FinishPatientNode(self):
        self.outputFileH.write("</Patient>" + NEWLINE_STR)
    # End - FinishPatientNode




    ################################################################################
    # 
    # [TDFFileWriter::WriteOutcomesNode]
    #
    ################################################################################
    def WriteOutcomesNode(self, diedDuringAdmission, diedIn12MonthsStr, readmit30D, 
                        akiStr, ckdStr, esrdStr, hepatitisStr, cirrhosisStr, esldStr):

        textStr = "    <OC scope=\"Admit\">" 
        if ((diedDuringAdmission != None) and (diedDuringAdmission != "")):
            textStr = textStr + "DiedInpt=\"" + diedDuringAdmission + "\""
        if ((diedIn12MonthsStr != None) and (diedIn12MonthsStr != "")):
            textStr = textStr + " DiedIn12Mos=\"" + diedIn12MonthsStr + "\"" 
        if ((readmit30D != None) and (readmit30D != "")):
            textStr = textStr + " Readmit30D=\"" + readmit30D + "\"" 
        if ((akiStr != None) and (akiStr != "")):
            textStr = textStr + " AKI=\"" + akiStr + "\""
        if ((ckdStr != None) and (ckdStr != "")):
            textStr = textStr + " CKD=\"" + ckdStr + "\""
        if ((esrdStr != None) and (esrdStr != "")):
            textStr = textStr + " ESRD=\"" + esrdStr + "\"" 
        if ((hepatitisStr != None) and (hepatitisStr != "")):
            textStr = textStr + " Hepatitis=\"" + hepatitisStr + "\""
        if ((cirrhosisStr != None) and (cirrhosisStr != "")):
            textStr = textStr + " Cirrhosis=\"" + cirrhosisStr + "\"" 
        if ((esldStr != None) and (esldStr != "")):
            textStr = textStr + " ESLD=\"" + esldStr + "\""
        textStr = textStr + "</OC>" + NEWLINE_STR

        self.outputFileH.write(textStr)
    # End - WriteOutcomesNode




    ################################################################################
    # 
    # [TDFFileWriter::WriteDataNode]
    #
    ################################################################################
    def WriteDataNode(self, classStr, timeStampStr, calendarTimeStr, valueStr):
        str = "    <D C=\"" + classStr + "\" T=\"" + timeStampStr + "\""

        if ((calendarTimeStr != None) and (calendarTimeStr != "")):
            # Remove characters that would create an invalid XML file.
            calendarTimeStr = calendarTimeStr.replace('>', '') 
            calendarTimeStr = calendarTimeStr.replace('<', '') 
            calendarTimeStr = calendarTimeStr.replace("=", "")
            calendarTimeStr = calendarTimeStr.replace("+", "")
            calendarTimeStr = calendarTimeStr.replace("-", "")
            calendarTimeStr = calendarTimeStr.replace(" ", "")
            str = str + " CT=\"" + calendarTimeStr + "\""

        valueStr = valueStr.replace('>', '')
        valueStr = valueStr.replace('<', '')
        valueStr = valueStr.replace("+", "")
        valueStr = valueStr.replace("-", "")
        valueStr = valueStr.replace(" ", "")

        str = str + ">" + valueStr + "</D>" + NEWLINE_STR
        self.outputFileH.write(str)
    # End - WriteDataNode





    ################################################################################
    # 
    # [TDFFileWriter::WriteEventNode]
    #
    ################################################################################
    def WriteEventNode(self, eventType, timeStampStr, calendarTimeStr, valueStr, detailStr):
        str = "    <E C=\"" + eventType + "\" T=\"" + timeStampStr + "\""

        if ((calendarTimeStr != None) and (calendarTimeStr != "")):
            # Remove characters that would create an invalid XML file.
            calendarTimeStr = calendarTimeStr.replace('>', '') 
            calendarTimeStr = calendarTimeStr.replace('<', '') 
            calendarTimeStr = calendarTimeStr.replace("=>", "")
            str = str + " CT=\"" + calendarTimeStr + "\""

        if ((valueStr != None) and (valueStr != "")):
            # Remove characters that would create an invalid XML file.
            valueStr = valueStr.replace('>', '') 
            valueStr = valueStr.replace('<', '') 
            str = str + " V=\"" + valueStr + "\""

        if ((detailStr != None) and (detailStr != "")):
            # Remove characters that would create an invalid XML file.
            detailStr = detailStr.replace('>', '') 
            detailStr = detailStr.replace('<', '') 
            str = str + " D=\"" + detailStr + "\""

        str = str + " />" + NEWLINE_STR

        self.outputFileH.write(str)
    # End - WriteEventNode




    ################################################################################
    # 
    # [TDFFileWriter::WriteTextNode]
    #
    ################################################################################
    def WriteTextNode(self, textType, extraAttributeName, extraAttributeValue, textStr):
        # Remove characters that would create an invalid XML file.
        textStr = textStr.replace('>', '') 
        textStr = textStr.replace('<', '') 
        textStr = textStr.replace("=<", "")
        textStr = textStr.replace("=", "")
        textStr = textStr.replace("=>", "")

        str = "    <Text C=\"" + textType + "\""
        if ((extraAttributeName != "") and (extraAttributeValue != "")):
            str = str + " " + extraAttributeName + "=\"" + extraAttributeValue + "\""
        str = str + ">"

        str = str + textStr + "</Text>" + NEWLINE_STR

        self.outputFileH.write(str)
    # End - WriteTextNode




    ################################################################################
    # 
    # [TDFFileWriter::AppendNameValuePairToStr]
    #
    # isinstance(test_string, str)
    ################################################################################
    def AppendNameValuePairToStr(self, totalStr, name, valueStr):
        saveName = name
        saveValueStr = valueStr
        saveTotalStr = totalStr

        if ((name == None) or (valueStr == None)):
            print("Error. AppendNameValuePairToStr discarding NONE name or value str")
            return(totalStr)

        #name = name.lstrip()
        #valueStr = valueStr.lstrip()
        valueStr = valueStr.replace('>', '') 
        valueStr = valueStr.replace('<', '') 
        valueStr = valueStr.replace("=", "")
        valueStr = valueStr.replace("+", "")
        valueStr = valueStr.replace("-", "")
        valueStr = valueStr.replace(" ", "")

        if (name == ""):
            print("Error. AppendNameValuePairToStr discarding empty name str")
            return(totalStr)    

        if (valueStr == ""):
            print("Error. AppendNameValuePairToStr discarding empty value str")
            return(totalStr)    

        try:
            floatVal = float(valueStr)
        except:
            print("Error. AppendNameValuePairToStr discarding non-numeric valueStr: " + str(valueStr))
            return(totalStr)    

        totalStr = totalStr + name + "=" + valueStr + ","

        return(totalStr)
    # End - AppendNameValuePairToStr


# End - class TDFFileWriter








################################################################################
#
# This is used to read a TDF file. It is read-only, and is designed to be called
# by a Neural Net or similar program.
################################################################################
class TDFFileReader(Dataset):

    #####################################################
    #
    # [TDFFileReader::__init__]
    #
    # Constructor
    #####################################################
    def __init__(self, tdfFilePathName):
        #print("TDFFileReader.__init__. Pathname = " + tdfFilePathName)
        super(TDFFileReader, self).__init__()
        self.m_DebugMode = False
        self.m_DebugLevel = 0

        ###################
        # Open the file.
        self.tdfFilePathName = tdfFilePathName
        # Opening in binary mode is important. I do seek's to arbitrary positions
        # and that is only allowed when a file is opened in binary.
        try:
            self.fileHandle = open(self.tdfFilePathName, 'rb') 
        except:
            print("Error from opening TDF file. File=" + self.tdfFilePathName)
            print("Exiting process...")
            sys.exit(0)
            return
        self.lineNum = 0

  
        ####################
        # Read the file header as a series of text lines and create a single
        # large text string for just the header. Stop at the body, which may
        # be quite large, and may not fit in in memory all at once.
        self.fileHeaderStr = ""        
        while True: 
            # Get next line from file 
            try:
                binaryLine = self.fileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. lineNum=" + str(self.lineNum))
                print("err=" + str(err))
                continue
            except:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue
            self.lineNum += 1

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. lineNum=" + str(self.lineNum))
                print("err=" + str(err))
                continue
            except:
                print("Error from converting string. lineNum=" + str(self.lineNum))
                continue

            self.fileHeaderStr += currentLine

            # Remove whitespace, including the trailing newline.
            currentLine = currentLine.rstrip()
            currentLine = currentLine.lstrip()
            if (currentLine == "</Head>"):
                break;
        # End - Read the file header

        # Add a closing element to make the header string into a complete XML string, 
        # and then we can parse it into XML
        self.fileHeaderStr += "</TDF>"
        #print("__init__. Header str=" + self.fileHeaderStr)
        try:
            self.headerXMLDOM = parseString(self.fileHeaderStr)
        except xml.parsers.expat.ExpatError as err:
            print("TDFFileReader::__init__. Error from parsing string:")
            #print("[" + self.fileHeaderStr + "]")
            print("ExpatError:" + str(err))
            sys.exit(0)
        except:
            print("TDFFileReader::__init__. Error from parsing string:")
            #print("[" + self.fileHeaderStr + "]")
            print("Unexpected error:", sys.exc_info()[0])
            sys.exit(0)


        self.headerNode = self.headerXMLDOM.getElementsByTagName("Head")[0]

        # Initalize the iterator to start at the beginning.
        self.currentPatientNodeStr = ""
        self.startNodeInCurrentWindow = None
        self.lastNodeInCurrentWindow = None
        self.LastTimeLineIndex = -1
        #self.GotoFirstPatient()
    # End -  __init__




    #####################################################
    #
    # [TDFFileReader::__del__]
    #
    # Destructor. This method is part of any class
    #####################################################
    def __del__(self):
        self.Shutdown()
    # End of destructor



    #####################################################
    #
    # [TDFFileReader::Shutdown]
    # Public Procedure
    #
    # Called to explicitly release resources
    #####################################################
    def Shutdown(self):
        try:
            self.fileHandle.close()
        except:
            pass
    # End of Shutdown




    #####################################################
    #
    # [TDFFileReader::SetDebugMode]
    # Public Procedure
    #
    #####################################################
    def SetDebugMode(self, newMode):
        self.m_DebugMode = newMode
    # End of SetDebugMode




    #####################################################
    #
    # [TDFFileReader::GetRawXMLStrForHeader]
    # Public Procedure
    #
    # This is used by the TDF writer class when making
    # a derived TDF file from an original source.
    #####################################################
    def GetRawXMLStrForHeader(self):
        resultStr = self.fileHeaderStr

        # Remove the </TDF> we added to make it parseable.
        resultStr = resultStr[:-6]

        # Add the PatientList element.
        resultStr = resultStr + "<PatientList>"

        return(resultStr)
    # End of GetRawXMLStrForHeader



    #####################################################
    #
    # [TDFFileReader::GetRawXMLStrForFooter]
    # Public Procedure
    #
    # This is used by the TDF writer class when making
    # a derived TDF file from an original source.
    #####################################################
    def GetRawXMLStrForFooter(self):
        footerStr = "\n\n</PatientList>\n</TDF>\n\n"
        return(footerStr)
    # End of GetRawXMLStrForFooter



    #####################################################
    #
    # [TDFFileReader::GetRawXMLStrForFirstPatient]
    # Public Procedure
    #
    # Returns True/False. 
    #   It returns True if it found a valid patient entry.
    #
    # This is used by the TDF writer class when making
    # a derived TDF file from an original source.
    #####################################################
    def GetRawXMLStrForFirstPatient(self):
        return self.currentPatientNodeStr
    # End - GetRawXMLStrForFirstPatient(self)




    #####################################################
    #
    # [TDFFileReader::GetRawXMLStrForNextPatient]
    # Public Procedure
    #
    # Returns True/False. 
    #   It returns True if it found a valid patient entry.
    #
    # This is used by the TDF writer class when making
    # a derived TDF file from an original source.
    #####################################################
    def GetRawXMLStrForNextPatient(self):
        #TDF_Log("GetRawXMLStrForNextPatient")

        fFoundPatient, fEOF = self.ReadNextPatientXMLStrImpl(-1)
        if ((not fFoundPatient) or (fEOF)):
            return(None)

        return self.currentPatientNodeStr
    # End - GetRawXMLStrForNextPatient(self)





    #####################################################
    #
    # [TDFFileReader::GetXMLNodeForCurrentPatient]
    # Public Procedure
    #
    #####################################################
    def GetXMLNodeForCurrentPatient(self):
        return self.currentPatientNode
    # End - GetXMLNodeForCurrentPatient(self)




    #####################################################
    #
    # [TDFFileReader::GetFileDescriptionStr]
    # Public Procedure
    #
    # valueName may be any property in the header.
    #####################################################
    def GetFileDescriptionStr(self, valueName):
        commentNode = XMLTools_GetChildNode(self.headerNode, valueName)
        if (commentNode == None):
            return("")

        str = XMLTools_GetTextContents(commentNode)
        if (str == None):
            return("")

        return(str)
    # End of GetFileDescriptionStr






    #####################################################
    #
    # [TDFFileReader::GotoFirstPatient]
    # Public Procedure
    #
    # Returns a single boolean fFoundPatient
    #   This is True iff the procedure found a valid patient entry.
    #   This is False if it hit the end of the file
    #
    #####################################################
    def GotoFirstPatient(self):
        #print("GotoFirstPatient.")
        self.fileHandle.seek(0, 0)

        # Advance in the file to the start of the patient list
        while True: 
            # Get next line from file 
            try:
                binaryLine = self.fileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. lineNum=" + str(self.lineNum))
                print("err=" + str(err))
                continue
            except:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue
            self.lineNum += 1

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. lineNum=" + str(self.lineNum))
                print("err=" + str(err))
                continue
            except:
                print("Error from converting string. lineNum=" + str(self.lineNum))
                continue

            # If we hit the end of the file, then we did not find a next patient.
            if (currentLine == ""):
                return(False)

            # Remove whitespace, including the trailing newline.
            currentLine = currentLine.rstrip()
            currentLine = currentLine.lstrip()
            #TDF_Log("GotoFirstPatient. currentLine=" + currentLine)
            if (currentLine == "<PatientList>"):
                break;
        # End - Advance to the first patient

        # Now, go to the first patient
        fFoundPatient = self.GotoNextPatient()
        TDF_Log("GotoFirstPatient. fFoundPatient=" + str(fFoundPatient))
        return(fFoundPatient)
    # End - GotoFirstPatient






    #####################################################
    #
    # [TDFFileReader::GotoNextPatient]
    # Public Procedure
    #
    # Returns a single boolean fFoundPatient
    #   This is True iff the procedure found a valid patient entry.
    #   This is False if it hit the end of the file
    #
    #####################################################
    def GotoNextPatient(self):
        fFoundPatient, fEOF = self.ReadNextPatientXMLStrImpl(-1)
        if ((not fFoundPatient) or (fEOF)):
            return(False)

        fFoundPatient = self.ParseCurrentPatientImpl()

        return fFoundPatient
    # End - GotoNextPatient(self)






    #####################################################
    #
    # [TDFFileReader::GotoFirstPatientInPartition]
    # Public Procedure
    #
    # This returns two values: fFoundPatient, fEOF
    #   fFoundPatient - True if we read a complete patient
    #   fEOF - True if we hit the end of the file
    #
    # This will find the next patient that starts within the
    # current partition. The selected patient may extend beyond
    # the end of the partition, which is OK. 
    #####################################################
    def GotoFirstPatientInPartition(self, startPartition, stopPartition):
        #TDF_Log("GotoFirstPatientInPartition. startPartition=" + str(startPartition) + 
        #            ", stopPartition=" + str(stopPartition))
        fFoundPatient = False
        fEOF = False

        # If this is the beginning of the file, then skip over the header.
        if (startPartition == 0):
            fFoundPatient = self.GotoFirstPatient()
            if (not fFoundPatient):
                fEOF = True
            #TDF_Log("GotoFirstPatientInPartition. fFoundPatient=" + str(fFoundPatient))
            return fFoundPatient, fEOF

        # Otherwise, jump to the partition starting position. 
        # Note, the partition boundaries are arbitrary byte positions, so
        # this may jump to the middle of a line of text. That is OK, since
        # we will still advance until we see a valid start of a patient element.
        self.fileHandle.seek(startPartition, 0)

        # Now, go to the first patient
        fFoundPatient, fEOF = self.GotoNextPatientInPartition(stopPartition)
        #TDF_Log("GotoFirstPatientInPartition. fFoundPatient=" + str(fFoundPatient))

        return fFoundPatient, fEOF
    # End - GotoFirstPatientInPartition






    #####################################################
    #
    # [TDFFileReader::GotoNextPatientInPartition]
    # Public Procedure
    #
    # This returns two values: fFoundPatient, fEOF
    #   fFoundPatient - True if we read a complete patient
    #   fEOF - True if we hit the end of the file
    #
    # This will find the next patient that starts within the
    # current partition. The selected patient may extend beyond
    # the end of the partition, which is OK. 
    #####################################################
    def GotoNextPatientInPartition(self, stopPartition):
        #print("GotoNextPatientInPartition. stopPartition=" + str(stopPartition))

        fFoundPatient, fEOF = self.ReadNextPatientXMLStrImpl(stopPartition)
        if ((not fFoundPatient) or (fEOF)):
            #print("GotoNextPatientInPartition. fFoundPatient=" + str(fFoundPatient) + ", fEOF=" + str(fEOF))
            return fFoundPatient, fEOF

        fFoundPatient = self.ParseCurrentPatientImpl()

        return fFoundPatient, fEOF
    # End - GotoNextPatientInPartition(self)





    #####################################################
    #
    # [TDFFileReader::ReadNextPatientXMLStrImpl]
    # Public Procedure
    #
    # This returns two values: fFoundPatient, fEOF
    #   fFoundPatient - True if we read a complete patient
    #   fEOF - True if we hit the end of the file
    #
    # It is OK to start a patient before the end of the partition and 
    # then read it past the end. So, we may read a patient that 
    # stretches past the end of the partition. But, it is NOT OK
    # to start a patient after the end of the partition.
    #    
    #####################################################
    def ReadNextPatientXMLStrImpl(self, stopPartition):
        #print("ReadNextPatientXMLStrImpl. stopPartition=" + str(stopPartition))
        fFoundPatient = False
        fEOF = False

        ####################
        # Read the next patient node as a text string
        # This ASSUMES we are about to read the <Patient> opening tag for the next patient.
        # We start just before the first patient when opening a file.
        # We stop just before the next patient when we read one patient.
        self.currentPatientNodeStr = ""
        fStartedPatientSection = False
        while True: 
            # Check if we have run past the end of the partition
            # It is OK to start a patient before the end of the partition and then read it past the end.
            # But, it is NOT OK to start a patient after the end of the partition.
            if ((stopPartition > 0) and (not fStartedPatientSection)):
                currentPositon = self.fileHandle.tell()
                #print("ReadNextPatientXMLStrImpl. currentPositon=" + str(currentPositon))
                if (currentPositon >= stopPartition):
                    #print("ReadNextPatientXMLStrImpl. End of Partition")
                    fFoundPatient = False
                    fEOF = False
                    return fFoundPatient, fEOF

            # Get next line from file 
            try:
                binaryLine = self.fileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. lineNum=" + str(self.lineNum))
                print("err=" + str(err))
                continue
            except:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue
            self.lineNum += 1

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. lineNum=" + str(self.lineNum))
                print("err=" + str(err))
                continue
            except:
                print("Error from converting string. lineNum=" + str(self.lineNum))
                continue

            # If we hit the end of the file, then we did not find a next patient.
            if (currentLine == ""):
                #print("ReadNextPatientXMLStrImpl. Hit end of file")
                fEOF = True
                return fFoundPatient, fEOF

            # Before we decide to save the line, remove whitespace for comparisons.
            # Gotcha 1: Do this to a temp copy, but save the original line with the whitespace
            # Gotcha 2: Do this before we decide we are in the patient. Don't save text before the patient starts.
            #print("ReadNextPatientXMLStrImpl. currentLine=" + currentLine)
            lineTokenText = currentLine.lstrip()
            lineTokenText = lineTokenText.rstrip()
            lineTokenText = lineTokenText.lower()

            # Now, check if this is the start of a patient element
            # Notice the patient element may contain attributes, so don't compare 
            # with "<patient>"
            if ((not fStartedPatientSection) and (lineTokenText.startswith("<patient"))):
                #print("ReadNextPatientXMLStrImpl. Started a patient section")
                fStartedPatientSection = True

            if (fStartedPatientSection):
                # <> BUGBUG FIXME - Move this str.replace() into the code
                # that generates a TDF from the source data. Maybe in TDFWriter.
                currentLine = currentLine.replace("=<", "")
                # <> End of FIXME
                self.currentPatientNodeStr += currentLine

            # Stop when we have read the entire patient.
            if ((fStartedPatientSection) and (lineTokenText == "</patient>")):
                #print("ReadNextPatientXMLStrImpl. <<< Found end of patient")
                #print("ReadNextPatientXMLStrImpl. Last lineTokenText=[" + lineTokenText + "]")
                break;
        # End - Read the file header

        #print("ReadNextPatientXMLStrImpl. Found patient")
        #print("ReadNextPatientXMLStrImpl. Patient Text XML=[" + self.currentPatientNodeStr + "]")
        fFoundPatient = True
        return fFoundPatient, fEOF
    # End - ReadNextPatientXMLStrImpl(self)






    #####################################################
    #
    # [TDFFileReader::ParseCurrentPatientImpl]
    # Public Procedure
    #
    # Returns True/False. 
    #   It returns True if it found a valid patient entry.
    #
    #####################################################
    def ParseCurrentPatientImpl(self):
        #print("ParseCurrentPatientImpl")

        # Parse the text string into am XML DOM
        try:
            self.currentPatientXMLDOM = parseString(self.currentPatientNodeStr)
        except xml.parsers.expat.ExpatError as err:
            print("ParseCurrentPatientImpl. Error from parsing string:")
            #print("[" + self.currentPatientNodeStr + "]")
            print("ExpatError:" + str(err))
            sys.exit(0)
        except:
            print("ParseCurrentPatientImpl. Error from parsing string:")
            #print("[" + self.currentPatientNodeStr + "]")
            print("Unexpected error:", sys.exc_info()[0])
            sys.exit(0)
        self.currentPatientNode = self.currentPatientXMLDOM.getElementsByTagName("Patient")[0]

        # Get some properties from the patient. These apply to all windows and
        # data entries within this patient.
        genderStr = self.currentPatientNode.getAttribute("gender")
        if (genderStr == "M"):
            self.CurrentIsMale = 1
        else:
            self.CurrentIsMale = 0
        self.CurrentRaceStr = self.currentPatientNode.getAttribute("race")
        if (self.CurrentRaceStr == ""):
            self.CurrentRaceStr = "C"

        self.CurrentWtInKg = -1
        wtInKgStr = self.currentPatientNode.getAttribute("wt")
        if ((wtInKgStr) and (wtInKgStr != "")):
            self.CurrentWtInKg = float(wtInKgStr)
        #print("TDFFileReader.ParseCurrentPatientImpl self.CurrentIsMale: " + str(self.CurrentIsMale))
        #print("TDFFileReader.ParseCurrentPatientImpl CurrentRaceStr: " + str(self.CurrentRaceStr))
        #print("TDFFileReader.ParseCurrentPatientImpl CurrentWtInKg: " + str(self.CurrentWtInKg))

        # Initially, we do not have any result data
        self.inputVectorIsComplete = False
        self.LatestLabsFromCurrentOrEarlierTimes = {}

        # Generate a timeline of actual and derived data values.
        # This covers the entire patient.
        self.CompilePatientTimelineImpl()

        # By default, there is a single window for each patient, so this contains all data 
        # recordings and events for that patient.
        self.ResetWindowBoundariesInPatient()

        return True
    # End - ParseCurrentPatientImpl(self)





    #####################################################
    #
    # [TDFFileReader::ResetWindowBoundariesInPatient]
    # Public Procedure
    #
    #####################################################
    def ResetWindowBoundariesInPatient(self):
        #print("ResetWindowBoundariesInPatient")

        self.WindowStartEventClass = "any"
        self.WindowStartEventValueList = []
        self.WindowStartTimelineID = 0
        self.WindowStopEventClass = "any"
        self.WindowStopEventValueList = []
        self.WindowStopTimelineID = len(self.CompiledTimeline)

        self.SetWindowBoundariesImpl(XMLTools_GetFirstChildNode(self.currentPatientNode), 
                                    XMLTools_GetLastChildNode(self.currentPatientNode))
    # End - ResetWindowBoundariesInPatient





    ################################################################################
    #
    # [TDFFileReader::SetWindowBoundariesImpl]
    #
    ################################################################################
    def SetWindowBoundariesImpl(self, firstNode, lastNode):
        #print("SetWindowBoundariesImpl")

        self.startNodeInCurrentWindow = firstNode
        self.lastNodeInCurrentWindow = lastNode

        xidStr = firstNode.getAttribute("xID")
        if ((xidStr != "") and (xidStr != None)):
            self.startTimeLineIDInCurrentWindow = int(xidStr)
        else:
            self.startTimeLineIDInCurrentWindow = -1

        xidStr = lastNode.getAttribute("xID")
        if ((xidStr != "") and (xidStr != None)):
            self.lastTimeLineIDInCurrentWindow = int(xidStr)
        else:
            self.lastTimeLineIDInCurrentWindow = -1

        #print("self.startTimeLineIDInCurrentWindow=" + str(self.startTimeLineIDInCurrentWindow))
        #print("self.lastTimeLineIDInCurrentWindow=" + str(self.lastTimeLineIDInCurrentWindow))
            
        # This is an UPPER BOUND ONLY on the number of data entries.
        # Not every timeline point may be a useful data entry.
        self.numDataEntriesInCurrentWindow = (self.lastTimeLineIDInCurrentWindow - self.startTimeLineIDInCurrentWindow) + 1
        #print("SetWindowBoundariesImpl. self.numDataEntriesInCurrentWindow=" + str(self.numDataEntriesInCurrentWindow))
    # End - SetWindowBoundariesImpl






    ################################################################################
    #
    # [TDFFileReader::SetFirstDataWindow]
    # Public procedure
    #
    # Returns True/False. 
    #   It returns True if it found a valid window
    #
    ################################################################################
    def SetFirstDataWindow(self, WindowStartEventClass, WindowStartEventValueList, 
                            WindowStopEventClass, WindowStopEventValueList):
        # Save the values so we can later advance to the next window.
        self.WindowStartEventClass = WindowStartEventClass
        self.WindowStartEventValueList = []
        for valueName in WindowStartEventValueList:
            valueName = valueName.lower()
            self.WindowStartEventValueList.append(valueName)

        self.WindowStopEventClass = WindowStopEventClass
        self.WindowStopEventValueList = []
        for valueName in WindowStopEventValueList:
            valueName = valueName.lower()
            self.WindowStopEventValueList.append(valueName)

        #####################
        # Find where the first window starts.
        firstNodeInPatient = XMLTools_GetFirstChildNode(self.currentPatientNode)
        if ((self.WindowStartEventClass.lower() == "any") or (self.WindowStartEventClass == "")):
            firstNode = firstNodeInPatient
        else:
            firstNode = self.FindNextNodeMatchingCriteriaImpl(firstNodeInPatient, self.WindowStartEventClass, 
                                                                self.WindowStartEventValueList)
        if (firstNode == None):
            print("SetFirstDataWindow. Found no first node.")
            return(False)

        #####################
        # Find where the first window stops.
        if ((self.WindowStopEventClass.lower() == "any") or (self.WindowStopEventClass == "")):
            lastNode = XMLTools_GetLastChildNode(self.currentPatientNode)
        else:
            lastNode = self.FindNextNodeMatchingCriteriaImpl(firstNode, self.WindowStopEventClass, 
                                                            self.WindowStopEventValueList)
        if (lastNode == None):
            print("SetFirstDataWindow. Found no last node.")
            return(False)


        self.SetWindowBoundariesImpl(firstNode, lastNode)
        return(True)
    # End - SetFirstDataWindow






    ################################################################################
    #
    # [TDFFileReader::SetNextDataWindow]
    # Public procedure
    #
    # Returns True/False. 
    #   It returns True if it found a valid window
    #
    ################################################################################
    def SetNextDataWindow(self):
        # If the first window stretches to the end of the patient, then there is 
        # no next window.
        if ((self.WindowStopEventClass.lower() == "any") or (self.WindowStopEventClass == "")):
            return(False)

        # Find where the next window starts.
        # The next window may overlap the current window, but it cannot be identical.
        nextPossibleFirstNode = XMLTools_GetAnyPeerNode(self.startNodeInCurrentWindow)
        firstNode = self.FindNextNodeMatchingCriteriaImpl(nextPossibleFirstNode, self.WindowStartEventClass, 
                                                        self.WindowStartEventValueList)
        if (firstNode == None):
            #print("SetNextDataWindow. Found no first node.")
            return(False)

        # Find where the next window stops.
        # The next window may overlap the current window, but it cannot be identical.
        nextPossibleLastNode = XMLTools_GetAnyPeerNode(self.lastNodeInCurrentWindow)
        lastNode = self.FindNextNodeMatchingCriteriaImpl(nextPossibleLastNode, self.WindowStopEventClass, 
                                                    self.WindowStopEventValueList)
        if (lastNode == None):
            #print("SetNextDataWindow. Found no lastNode.")
            return(False)

        self.SetWindowBoundariesImpl(firstNode, lastNode)
        return(True)
    # End - SetNextDataWindow





    ################################################################################
    #
    # [TDFFileReader::FindNextNodeMatchingCriteriaImpl]
    #
    ################################################################################
    def FindNextNodeMatchingCriteriaImpl(self, startNode, requiredEventClass, requiredEventValueList):
        #print("FindNextNodeMatchingCriteriaImpl")

        requiredEventClass = requiredEventClass.lower()
        if ((requiredEventClass == "") or (requiredEventClass == "any")):
            return(startNode)
        #print("FindNextNodeMatchingCriteriaImpl. requiredEventClass=" + str(requiredEventClass))

        currentNode = startNode
        while (currentNode):
            nodeMatchesCriteria = True
            nodeName = XMLTools_GetElementName(currentNode)
            #print("FindNextNodeMatchingCriteriaImpl. Check one node. nodeName=" + str(nodeName))

            ###########################
            if (nodeName == "E"):
                try:
                    currentEventClass = currentNode.getAttribute("C")
                    currentEventValue = currentNode.getAttribute("V")
                except:
                    currentEventClass = ""
                    eventData = ""

                currentEventClass = currentEventClass.lower()
                #print("FindNextNodeMatchingCriteriaImpl. currentEventClass=" + str(currentEventClass))

                if (("any" != requiredEventClass) and (currentEventClass != requiredEventClass)):
                    nodeMatchesCriteria = False

                currentEventValue = currentEventValue.lower()
                if ((len(requiredEventValueList) > 0) and (not (currentEventValue in requiredEventValueList))):
                    nodeMatchesCriteria = False
            ###########################
            elif (nodeName == "D"):
                # <>Later I should also use a data node with some value as a window boundary.
                nodeMatchesCriteria = False
            ###########################
            else:
                nodeMatchesCriteria = False

            if (nodeMatchesCriteria):
                #print("Found node. currentNode=" + str(currentNode))
                return(currentNode)

            currentNode = XMLTools_GetAnyPeerNode(currentNode)
        # End - while (currentNode):

        #print("Found NO matching node")
        return None
    # End - FindNextNodeMatchingCriteriaImpl






    #####################################################
    #
    # [TDFFileReader::ParseSingleVariable]
    #
    #####################################################
    def ParseSingleVariable(self, valueName):
        nameStem = valueName
        valueOffset = 0
        if (VARIABLE_START_OFFSET_MARKER in valueName):
            nameParts = valueName.split(VARIABLE_START_OFFSET_MARKER, 1)
            nameStem = nameParts[0]
            valueOffsetStr = nameParts[1]
            valueOffsetStr = valueOffsetStr.split(VARIABLE_STOP_OFFSET_MARKER, 1)[0]
            valueOffsetStr = valueOffsetStr.lower()
            valueOffset = int(valueOffsetStr)
        #print("nameStem = " + nameStem)
        #print("valueOffset = " + str(valueOffset))

        if (not (nameStem in g_LabValueInfo)):
            print("nameStem(" + nameStem + ") not in g_LabValueInfo")
            return None, None, 0
        labInfo = g_LabValueInfo[nameStem]

        return labInfo, nameStem, valueOffset
    # End - ParseSingleVariable





    #####################################################
    #
    # [TDFFileReader::ParseVariables]
    #
    #####################################################
    def ParseVariables(self, inputValueNameList, numValsInEachInputVector, resultValueName):
        # Get information about the result
        resultLabInfo, resultValueStem, resultValueOffset = self.ParseSingleVariable(resultValueName)
        if (resultLabInfo == None):
            print("resultValueStem(" + resultValueStem + ") not in g_LabValueInfo")
            return None, None, None, None, None

        inputValueOffsets = [0] * numValsInEachInputVector

        # A single name may have the form "foo" or "foo[n]" where n is an offset.
        # Split the names into name stems and optional offsets
        earliestOffset = 0
        for valueIndex, valueName in enumerate(inputValueNameList):
            #print("valueName = " + valueName)
            #print("valueIndex = " + str(valueIndex))
            if (VARIABLE_START_OFFSET_MARKER in valueName):
                valueNameStem = valueName.split(VARIABLE_START_OFFSET_MARKER, 1)[0]
                valueNameIndexStr = valueName.split(VARIABLE_START_OFFSET_MARKER, 1)[1]
                valueNameIndexStr = valueNameIndexStr.split(VARIABLE_STOP_OFFSET_MARKER, 1)[0]
                offset = int(valueNameIndexStr)
                if (offset < earliestOffset):
                    earliestOffset = offset
                inputValueNameList[valueIndex] = valueNameStem
                inputValueOffsets[valueIndex] = offset
                #print("valueNameStem = " + valueNameStem)
                #print("valueNameIndexStr = " + valueNameIndexStr)
        # End - for valueIndex, valueName in enumerate(inputValueNameList):

        #print("Show Offsets to Value Names")
        #for valueIndex, valueName in enumerate(inputValueNameList):
        #    #print("valueIndex = " + str(valueIndex))
        #    print("valueName = " + valueName)
        #    print("valueOffset = " + str(inputValueOffsets[valueIndex]))
        # End - for valueIndex, valueName in enumerate(inputValueNameList):
        #print("earliestOffset = " + str(earliestOffset))

        return inputValueNameList, inputValueOffsets, resultLabInfo, resultValueStem, resultValueOffset
    # End - ParseVariables






    #####################################################
    #
    # [TDFFileReader::GetBoundsForDataFetch]
    #
    #####################################################
    def GetBoundsForDataFetch(self, resultLabInfo):
        # By default, we will read the entire window.
        firstTimelineID = self.startTimeLineIDInCurrentWindow
        lastTimelineID = self.lastTimeLineIDInCurrentWindow

        # If this result assumes that we will know a future outcome (most results do), then 
        # make sure we only include data points that know whether the future outcome happened.
        # Clip the data window so we only include data points that have enough future information.
        # If we need to predict a result N days in the future, then do not return data that cannot
        # accurately know that in the future.
        # This loop will iterate over each step in the timeline.
        NameOfFutureLabValue = resultLabInfo['FuturePredictedValue']
        if (NameOfFutureLabValue != ""):
            numFutureDaysNeeded = int(resultLabInfo['numFutureDaysNeeded'])
            #print("Clipping. NameOfFutureLabValue=" + NameOfFutureLabValue)
            #print("Clipping. numFutureDaysNeeded=" + str(numFutureDaysNeeded))

            # First, find the latest day with the required lab values.
            # This is the value we want to predict, so we will stop *before* this day.
            latestTimeLineIndex = len(self.CompiledTimeline) - 1
            futureDayNum = -1
            while (latestTimeLineIndex >= firstTimelineID):
                #print("Look at future data. latestTimeLineIndex=" + str(latestTimeLineIndex))
                timelineEntry = self.CompiledTimeline[latestTimeLineIndex]
                futureDataValues = timelineEntry['data']
                if (NameOfFutureLabValue in futureDataValues):
                    futureDayNum = timelineEntry['TimeDays']
                    #print("Found future date with the info. futureDayNum=" + str(futureDayNum))
                    break
                latestTimeLineIndex = latestTimeLineIndex - 1
            # End - while (latestTimeLineIndex >= firstTimelineID)

            if (futureDayNum < 0):
                return -1, -1
    
            # Clip to a date that can predict sufficiently far ahead.        
            while (lastTimelineID >= firstTimelineID):
                timelineEntry = self.CompiledTimeline[lastTimelineID]
                currentDayNum = timelineEntry['TimeDays']
                #print("Look at possible days. currentDayNum=" + str(currentDayNum))
                if (futureDayNum >= (currentDayNum + numFutureDaysNeeded)):
                    #print("Found new max day. currentDayNum=" + str(currentDayNum))
                    break
                lastTimelineID = lastTimelineID - 1
            # End - while (lastTimelineID >= firstTimelineID):

            if (lastTimelineID < firstTimelineID):
                return -1, -1   
        # End - if (NameOfFutureLabValues != ""):

        return firstTimelineID, lastTimelineID
    # End - GetBoundsForDataFetch






    #####################################################
    #
    # [TDFFileReader::GetNamedValueFromTimeline]
    #
    # BUGUG FIXME <> If this is called with several different offsets, 
    # like -1, then -3, then -5, it may return the *same* past timepoint
    # for all of them. 
    #####################################################
    def GetNamedValueFromTimeline(self, valueName, offset, timeLineIndex, timelineEntry, currentDayNum):
        ############################
        # This is the simple case, we want a value from the current position in the timeline
        if (offset == 0):
            try:
                latestValues = timelineEntry['data']
                result = latestValues[valueName]
                #print("latestValues = " + str(latestValues))
                #print("result = " + str(result))
                return True, result
            except:
                return False, -1
        # End - if (offset == 0):

        
        targetDayNum = currentDayNum + offset
        #print("GetNamedValueFromTimeline. targetDayNum=" + str(targetDayNum) + ", currentDayNum=" + str(currentDayNum))

        ############################
        # If offset<0, then we want a value from a previous position in the timeline.
        if (offset < 0):
            # We may search to before the current window. That is ok.
            # The point of a past lab value is to get a trend, or baseline, and
            # that should not be clipped to a single event, like one hospital admission.
            pastTimeLineIndex = timeLineIndex
            while (pastTimeLineIndex >= 0):
                pastTimelineEntry = self.CompiledTimeline[pastTimeLineIndex]
                pastDayNum = pastTimelineEntry['TimeDays']
                #print("GetNamedValueFromTimeline. pastDayNum=" + str(pastDayNum))
                if (pastDayNum <= targetDayNum):
                    # Don't do anything if we are too far back. If I want a lab from
                    # 30 days before now, don't confuse this with a lab 6 years ago.
                    if ((targetDayNum - pastDayNum) >= MAX_PREVIOUS_LAB_EXTRA_PREVIOUS):
                        #print("GetNamedValueFromTimeline. Too far back. pastDayNum=" + str(pastDayNum))
                        return False, -1

                    pastLabValues = pastTimelineEntry['data']
                    if (valueName in pastLabValues):
                        #print("GetNamedValueFromTimeline. valueName is in prevDay. pastDayNum=" + str(pastDayNum))
                        result = pastLabValues[valueName]
                        return True, result
                # End - if (pastDayNum <= targetDayNum):

                pastTimeLineIndex = pastTimeLineIndex - 1
            # End - while (pastTimeLineIndex >= 0):
        # End - if (offset < 0):


        ############################
        # If offset>0, then we want a value from a future position in the timeline.
        if (offset > 0):
            # We may search past the current window. That is ok.
            futureTimeLineIndex = timeLineIndex

            while (futureTimeLineIndex <= self.LastTimeLineIndex):
                futureTimelineEntry = self.CompiledTimeline[futureTimeLineIndex]
                futureDayNum = futureTimelineEntry['TimeDays']
                #print("GetNamedValueFromTimeline. futureDayNum=" + str(futureDayNum))

                if (futureDayNum >= targetDayNum):
                    # Don't do anything if we are too far ahead. If I want a lab from
                    # 3 days after now, don't confuse this with a lab 6 years in the future
                    if ((futureDayNum - targetDayNum) >= MAX_PREVIOUS_LAB_EXTRA_FUTURE):
                        #print("GetNamedValueFromTimeline. Too far ahead. futureDayNum=" + str(futureDayNum))
                        return False, -1

                    futureLabValues = futureTimelineEntry['data']
                    if (valueName in futureLabValues):
                        #print("GetNamedValueFromTimeline. valueName is in future. futureDayNum=" + str(futureDayNum))
                        result = futureLabValues[valueName]
                        return True, result
                # End - if (futureDayNum >= targetDayNum):

                futureTimeLineIndex = futureTimeLineIndex + 1
            # End - while (futureTimeLineIndex <= self.lastTimeLineIDInCurrentWindow):
        # End - if (offset > 0):


        return False, -1
    # End - GetNamedValueFromTimeline







    #####################################################
    #####################################################
    def CheckIfCurrentTimeMeetsCriteria(self, numProperties, 
                                            propertyRelationList, 
                                            propertyNameList, 
                                            propertyValueList, 
                                            timeLineIndex,
                                            timelineEntry,
                                            currentDayNum):
        for propNum in range(numProperties):
            valueOffset = 0
            #print("CheckIfCurrentTimeMeetsCriteria: valueName=" + str(propertyNameList[propNum]))
            valueName = propertyNameList[propNum]
            targetVal = float(propertyValueList[propNum])

            try:
               labInfo = g_LabValueInfo[valueName]
            except:
                print("Error! CheckIfCurrentTimeMeetsCriteria found undefined lab name: " + valueName)
                return(False)

            foundIt, actualVal = self.GetNamedValueFromTimeline(valueName, valueOffset, timeLineIndex, timelineEntry, currentDayNum)
            if (not foundIt):
                return(False)
            #print("CheckIfCurrentTimeMeetsCriteria: targetVal=" + str(targetVal))
            #print("CheckIfCurrentTimeMeetsCriteria: actualVal=" + str(actualVal))
            #print("CheckIfCurrentTimeMeetsCriteria: foundIt=" + str(foundIt))
            dataTypeName = labInfo['dataType']
            #print("CheckIfCurrentTimeMeetsCriteria: dataTypeName=" + str(dataTypeName))

            ###############
            if (propertyRelationList[propNum] == "="):
                if (dataTypeName == TDF_DATA_TYPE_FLOAT):
                    if (float(actualVal) != float(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
                elif ((dataTypeName == TDF_DATA_TYPE_INT) or (dataTypeName == TDF_DATA_TYPE_FUTURE_EVENT_CLASS)):
                    if (int(actualVal) != int(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
            ###############
            elif (propertyRelationList[propNum] == "!="):
                if (dataTypeName == TDF_DATA_TYPE_FLOAT):
                    if (float(actualVal) == float(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
                elif ((dataTypeName == TDF_DATA_TYPE_INT) or (dataTypeName == TDF_DATA_TYPE_FUTURE_EVENT_CLASS)):
                    if (int(actualVal) == int(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
            ###############
            elif (propertyRelationList[propNum] == ".LT."):
                if (dataTypeName == TDF_DATA_TYPE_FLOAT):
                    if (float(actualVal) >= float(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
                elif ((dataTypeName == TDF_DATA_TYPE_INT) or (dataTypeName == TDF_DATA_TYPE_FUTURE_EVENT_CLASS)):
                    if (int(actualVal) >= int(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
            ###############
            elif (propertyRelationList[propNum] == ".LTE."):
                if (dataTypeName == TDF_DATA_TYPE_FLOAT):
                    if (float(actualVal) > float(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
                elif ((dataTypeName == TDF_DATA_TYPE_INT) or (dataTypeName == TDF_DATA_TYPE_FUTURE_EVENT_CLASS)):
                    if (int(actualVal) > int(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
            ###############
            elif (propertyRelationList[propNum] == ".GT."):
                if (dataTypeName == TDF_DATA_TYPE_FLOAT):
                    if (float(actualVal) <= float(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
                elif ((dataTypeName == TDF_DATA_TYPE_INT) or (dataTypeName == TDF_DATA_TYPE_FUTURE_EVENT_CLASS)):
                    if (int(actualVal) <= int(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
            ###############
            elif (propertyRelationList[propNum] == ".GTE."):
                if (dataTypeName == TDF_DATA_TYPE_FLOAT):
                    if (float(actualVal) < float(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
                elif ((dataTypeName == TDF_DATA_TYPE_INT) or (dataTypeName == TDF_DATA_TYPE_FUTURE_EVENT_CLASS)):
                    if (int(actualVal) < int(targetVal)):
                        #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                        return(False)
            ###############
            else:
                #print("CheckIfCurrentTimeMeetsCriteria: targetVal does not match required value")
                return(False)

            #print("CheckIfCurrentTimeMeetsCriteria: targetVal does indeed match required value")
        # End - for propNum in range(numProperties):

        return(True)
    # End - CheckIfCurrentTimeMeetsCriteria







    #####################################################
    #
    # [TDFFileReader::GetDataFromCurrentWindow]
    #
    # This returns two tensors:
    #   - The first is a tensor of inputs. This is an NxM array
    #           Each column is 1 timestep, and each array is one input variable.
    #
    #   - The second is an array of results. This is an Nx1 array.
    #           It is the result at each time step
    #
    # This method is NOT part of DataSet - it is a special iterator
    # Notice, we iterate over BOTH patients and dataNodes within a patient.
    #
    #
    # dataTypeName has values:
    #   "NormFraction" 
    #   "NormInt0-100"
    #
    #####################################################
    def GetDataFromCurrentWindow(self, 
                                inputValueFormatStr, 
                                resultValueName, 
                                resultDataTypeName, 
                                numRequireProperties,
                                requirePropertyRelationList,
                                requirePropertyNameList,
                                requirePropertyValueList,
                                minIntervalInHours):
        #print("====================================GetDataFromCurrentWindow, start")
        TDF_Log("Enter GetDataFromCurrentWindow")
        #TDF_LogMemoryInfo()

        # Parse the value name list. These are the elements of each tensor
        inputValueNameList = inputValueFormatStr.split(',')
        numValsInEachInputVector = len(inputValueNameList)      

        # Get information about the requested variables. This splits
        # complicated name values like "eGFR[-30]" into a name and an 
        # offset, like "eGFR" and "-30"
        inputValueNameList, inputValueOffsets, resultLabInfo, resultName, resultValueOffset = self.ParseVariables(inputValueNameList, 
                                                                        numValsInEachInputVector, 
                                                                        resultValueName)
        if (None == resultLabInfo):
            return 0, None, None

        # Find where we will look for the data. We may not consider data values
        # that run right up to the end.        
        firstTimelineID, lastTimelineID = self.GetBoundsForDataFetch(resultLabInfo)
        if (firstTimelineID < 0):
            return 0, None, None

        # Count the max possible number of complete data nodes.
        # We will return less than this, but this lets us allocate result storage.
        maxNumCompleteLabSets = (lastTimelineID - firstTimelineID) + 1
        if (maxNumCompleteLabSets <= 0):
            #TDF_Log("GetDataFromCurrentWindow, No data")
            return 0, None, None

        # Make a vector big enough to hold all possible labs.
        # We will likely not need all of this space, but there is enough
        # room for the most extreme case.
        inputTensor = torch.zeros(maxNumCompleteLabSets, 1, numValsInEachInputVector, requires_grad=True)
        resultTensor = torch.zeros(maxNumCompleteLabSets, 1, 1, requires_grad=True)
        self.inputVectorIsComplete = False

        # This loop will iterate over each step in the timeline.
        timeLineIndex = firstTimelineID
        numReturnedDataSets = 0
        lastHourReturned = -1
        inputValueTimelineIndexes = [-1] * numValsInEachInputVector
        inputValueDayNums = [-1] * numValsInEachInputVector
        while (timeLineIndex <= lastTimelineID):
            timelineEntry = self.CompiledTimeline[timeLineIndex]
            currentDayNum = timelineEntry['TimeDays']
            currentHour = timelineEntry['TimeHours']
            #print("GetDataFromCurrentWindow. timeLineIndex=" + str(timeLineIndex))
            #print("GetDataFromCurrentWindow. timelineEntry=" + str(timelineEntry))
            #print("GetDataFromCurrentWindow. latestValues=" + str(latestValues))

            # We may keep high frequency data, like vitals, along with low frequency data
            # like Cr. If a value is missing, we always use the most recent past value, which
            # can make low frequency data like Cr still return a series like high frequency data.
            # We want to avoid that, so skip values that happen more frequently than we want.
            # HOWEVER. We take the latest value in each bucket, so the latest lab value in that
            # day. This prevents a vitals recorded at just after midnight (with still the previous days labs)
            # from blocking more recent labs drawn later in the day (like on morning lab draws).
            fOverwriteLatestLabs = False
            if ((lastHourReturned > 0) and (minIntervalInHours > 0) 
                    and (((currentDayNum * 24) + currentHour) < (lastHourReturned + minIntervalInHours))):
                #print("GetDataFromCurrentWindow. Overwrite. lastHourReturned=" + str(lastHourReturned))
                #print("GetDataFromCurrentWindow. Overwrite. currentDayNum=" + str(currentDayNum))
                #print("GetDataFromCurrentWindow. Overwrite. currentHour=" + str(currentHour))
                #print("GetDataFromCurrentWindow. Overwrite. minIntervalInHours=" + str(minIntervalInHours))
                fOverwriteLatestLabs = True

            # Find the labs we are looking for.
            # There are often lots of labs, but this only return labs that are relevant.
            foundAllInputs = True
            for valueIndex, valueName in enumerate(inputValueNameList):
                # Get the lab value itself.
                #print("GetDataFromCurrentWindow. Look for valueName=" + valueName)
                foundIt, result = self.GetNamedValueFromTimeline(valueName, inputValueOffsets[valueIndex],
                                                                timeLineIndex, timelineEntry, currentDayNum)
                if (not foundIt):
                    foundAllInputs = False
                    break

                # Get information about the lab.
                try:
                   labInfo = g_LabValueInfo[valueName]
                except:
                    print("Error! GetDataFromCurrentWindow found undefined lab name: " + valueName)
                    foundAllInputs = False
                    break
                labMinVal = float(labInfo['minVal'])
                labMaxVal = float(labInfo['maxVal'])
                dataTypeName = labInfo['dataType']
                #print("GetDataFromCurrentWindow. Found value valueName: " + valueName)
                # Normalize the lab value so all values range between 0.0 and 1.0
                normValue = TDF_NormalizeLabValue(result, labMinVal, labMaxVal, dataTypeName)
                #print("GetDataFromCurrentWindow. valueName=" + valueName + ", result=" + str(result))
                #print("GetDataFromCurrentWindow. valueName=" + valueName + ", normValue=" + str(normValue))
                #print("GetDataFromCurrentWindow. valueName=" + valueName + ", fOverwriteLatestLabs=" + str(fOverwriteLatestLabs))
                #intValue = round(100 * floatValue)
                #TDF_Log("Read and normalized one value")
                #TDF_Log("numReturnedDataSets=" + str(numReturnedDataSets) + ", valueIndex=" + str(valueIndex))

                #TDF_Log("maxNumCompleteLabSets=" + str(maxNumCompleteLabSets) + ", numValsInEachInputVector=" + str(numValsInEachInputVector))
                if (fOverwriteLatestLabs):
                    inputTensor[numReturnedDataSets - 1][0][valueIndex] = normValue
                else:
                    inputTensor[numReturnedDataSets][0][valueIndex] = normValue
                #print("GetDataFromCurrentWindow. NON-normalized=" + str(result))
                #print("GetDataFromCurrentWindow. normValue=" + str(normValue))
                #print("GetDataFromCurrentWindow. valueName=" + valueName + ", index=" + str(valueIndex) + ", value=" + str(normValue))
                #TDF_Log("Saved one value to result")
            # End - for valueIndex, valueName in enumerate(inputValueNameList):


            # Check if there are additional requirements for a timeline entry.
            if (foundAllInputs and (numRequireProperties > 0)):
                #print("Check required properties. numRequireProperties=" + str(numRequireProperties))
                #print("Check required properties. requirePropertyRelationList=" + str(requirePropertyRelationList))
                #print("Check required properties. requirePropertyNameList=" + str(requirePropertyNameList))
                #print("Check required properties. requirePropertyValueList=" + str(requirePropertyValueList))
                fMeetsCriteria = self.CheckIfCurrentTimeMeetsCriteria(numRequireProperties,
                                                requirePropertyRelationList,
                                                requirePropertyNameList,
                                                requirePropertyValueList,
                                                timeLineIndex, 
                                                timelineEntry, 
                                                currentDayNum)
                if (not fMeetsCriteria):
                    foundAllInputs = False
                #print(">foundAllInputs = " + str(foundAllInputs))
                #sys.exit(0)

            # If we did not find all of the Input values here, move on and try to them 
            # in the next timeline position.
            if (not foundAllInputs):
                timeLineIndex += 1
                continue
                
            # Now, try to get the result for this time step.
            # Note, this is NOT normalized. That is a category ID, or exact value like INR, 
            # so we want the actual numeric value, not a normalized version.            
            foundIt, result = self.GetNamedValueFromTimeline(resultName, resultValueOffset,
                                                             timeLineIndex, timelineEntry, currentDayNum)

            # If we found all values, then assemble the next vector of results.
            if (foundIt):
                #print("GetDataFromCurrentWindow. found resultValueName: " + str(resultValueName))
                if (fOverwriteLatestLabs):
                    resultTensor[numReturnedDataSets - 1][0][0] = result
                else:
                    resultTensor[numReturnedDataSets][0][0] = result
                    #TDF_Log("Advance numReturnedDataSets")
                    #print("GetDataFromCurrentWindow. foundAllInputs=1. Count this as complete")
                    numReturnedDataSets += 1
                    if (numReturnedDataSets >= maxNumCompleteLabSets):
                        break
                    lastHourReturned = (currentDayNum * 24) + currentHour
                # End - if (foundAllInputs):

            timeLineIndex += 1
        # End - while (timeLineIndex <= lastTimelineID)

        if (numReturnedDataSets <= 0):
            return numReturnedDataSets, None, None

        #print("GetDataFromCurrentWindow. numReturnedDataSets=" + str(numReturnedDataSets))
        if (numReturnedDataSets > maxNumCompleteLabSets):
            TDF_Log("ERROR!. numReturnedDataSets != numCompleteLabSets")
            numReturnedDataSets = maxNumCompleteLabSets
        
        # Discard any previous compute graph.
        # tensor.detach() creates a tensor that shares storage with tensor that does not require grad. It detaches
        inputTensor = inputTensor.detach()
        resultTensor = resultTensor.detach()

        # The client expects that the returned tensors will be the exact size.
        # We have to return a full tensor, without any unused rows.
        # This will reallocate the working tensors.
        newInputTensor = inputTensor[:numReturnedDataSets,:1,:numValsInEachInputVector]
        newResultTensor = resultTensor[:numReturnedDataSets,:1,:1]
        
        #print("GetDataFromCurrentWindow. numValsInEachInputVector=" + str(numValsInEachInputVector))
        #print("newInputTensor.dim() = " + str(newInputTensor.dim()))
        #print("newInputTensor.size() = " + str(newInputTensor.size()))
        #print("newResultTensor.dim() = " + str(newResultTensor.dim()))
        #print("newResultTensor.size() = " + str(newResultTensor.size()))
        #for dataSetNum in range(numReturnedDataSets):
        #    for inputNum in range(numValsInEachInputVector):
        #        if (newInputTensor[dataSetNum][0][inputNum] != inputTensor[dataSetNum][0][inputNum]):
        #            print("ERROR!")
        #    # End - for inputNum in range(numValsInEachInputVector):
        #    if (newResultTensor[dataSetNum][0][0] != resultTensor[dataSetNum][0][0]):
        #        print("ERROR!")
        ## End - for dataSetNum in range(numReturnedDataSets)


        # If we did not return with success in the above loop, then tell the caller
        # there is no more data left.
        #TDF_Log("GetDataFromCurrentWindow finished")
        return numReturnedDataSets, newInputTensor, newResultTensor
    # End - GetDataFromCurrentWindow()








    #####################################################
    #
    # [TDFFileReader::GetListOfValsForCurrentPatient]
    #
    # This returns two lists of values.
    #####################################################
    def GetListOfValsForCurrentPatient(self, 
                                    valueName1, 
                                    valueList1,
                                    valueName2,
                                    valueList2,
                                    numRequireProperties,
                                    requirePropertyRelationList,
                                    requirePropertyNameList,
                                    requirePropertyValueList):
        #print("====================================GetListOfValsForCurrentPatient, start")
        #TDF_Log("Enter GetListOfValsForCurrentPatient")
        #TDF_LogMemoryInfo()
        foundPrevValues = False
        prevValue1 = -1
        prevValue2 = -1

        # Get information about the requested variables. This splits
        # complicated name values like "eGFR[-30]" into a name and an 
        # offset, like "eGFR" and "-30"
        labInfo1, nameStem1, valueOffset1 = self.ParseSingleVariable(valueName1)
        if (None == labInfo1):
            print("!!Error!!")
            return None, None
        labInfo2, nameStem2, valueOffset2 = self.ParseSingleVariable(valueName2)
        if (None == labInfo2):
            print("!!Error!!")
            return None, None

        # Find where we will look for the data
        firstTimelineID = self.startTimeLineIDInCurrentWindow
        lastTimelineID = self.lastTimeLineIDInCurrentWindow

        # This loop will iterate over each step in the timeline.
        timeLineIndex = firstTimelineID
        while (timeLineIndex <= lastTimelineID):
            timelineEntry = self.CompiledTimeline[timeLineIndex]
            currentDayNum = timelineEntry['TimeDays']
            currentHour = timelineEntry['TimeHours']
            #print("GetListOfValsForCurrentPatient. timeLineIndex=" + str(timeLineIndex))
            #print("GetListOfValsForCurrentPatient. timelineEntry=" + str(timelineEntry))
            #print("GetListOfValsForCurrentPatient. latestValues=" + str(latestValues))

            # Find the labs we are looking for.
            foundNewValue, value1 = self.GetNamedValueFromTimeline(nameStem1, valueOffset1,
                                                             timeLineIndex, timelineEntry, currentDayNum)
            if (foundNewValue):
                foundNewValue, value2 = self.GetNamedValueFromTimeline(nameStem2, valueOffset2,
                                                               timeLineIndex, timelineEntry, currentDayNum)

            # If we found both values, make sure this is not a repeat.
            # We may carry past values forward every time there is new data, like
            # new vital signs. As a result, a slower changing lab may be repeated many 
            # times until a true new value appears.
            # We use the fact that both values are identical to indicate this is a repeat.
            # This may rarely miss a true case of identical values at different times, but
            # that is rare.
            if ((foundNewValue) and (foundPrevValues) and (prevValue1 == value1) and (prevValue2 == value2)):
                foundNewValue = False
            if (foundNewValue):
                foundPrevValues = True
                prevValue1 = value1
                prevValue2 = value2

            # If we found both values, then normalize them
            if (foundNewValue):
                labMinVal = float(labInfo1['minVal'])
                labMaxVal = float(labInfo1['maxVal'])
                #dataTypeName = labInfo1['dataType']
                if (value1 < float(labMinVal)):
                    value1 = float(labMinVal)
                if (value1 > float(labMaxVal)):
                    value1 = float(labMaxVal)
                valueList1.append(value1)

                labMinVal = float(labInfo2['minVal'])
                labMaxVal = float(labInfo2['maxVal'])
                #dataTypeName = labInfo2['dataType']
                if (value2 < float(labMinVal)):
                    value2 = float(labMinVal)
                if (value2 > float(labMaxVal)):
                    value2 = float(labMaxVal)
                valueList2.append(value2)

            timeLineIndex += 1
        # End - while (timeLineIndex <= lastTimelineID)

        return valueList1, valueList2
    # End - GetListOfValsForCurrentPatient()






    #####################################################
    #
    # [TDFFileReader::GetStatsForList]
    #
    # This returns two lists of values.
    #####################################################
    def GetStatsForList(self, valueList):
        # Compute the mean, which is the average of the values.
        # Make sure to treat these as floats to avoid truncation or rounding errors.
        avgValue = 0
        refAvgValue = 0
        listLen = len(valueList)
        if (listLen > 0):
            avgValue = float(sum(valueList)) / listLen
            refAvgValue = statistics.mean(valueList)  # 20.11111111111111
        #print("Derived avgValue=" + str(avgValue))
        #print("Reference avgValue=" + str(refAvgValue))

        # Next, compute the variance.
        # This is a measure of how far spread out the numbers are.
        # Intuitively, this is the average distance from members of the set and the mean.
        # This uses the "Sample Variance" where avgValue is the sample mean, not the
        # mean of some superset "population" from which the sample is drawn.
        # As a result, we divide by listLen-1, but if we used the "population mean" then
        # we would divide by listLen
        variance = sum((x - avgValue) ** 2 for x in valueList) / listLen
        refVariance = np.var(valueList)
        #print("Derived variance=" + str(variance))
        #print("Reference variance=" + str(refVariance))

        # Standard deviation is simply the sqrt of the Variance
        stdDev = math.sqrt(variance)
        refStdDev = np.std(valueList)
        #print("Derived stdDev=" + str(stdDev))
        #print("Reference stdDev=" + str(refStdDev))

        return listLen, refAvgValue, refVariance, refStdDev
    # End - GetStatsForList






    #####################################################
    #
    # [TDFFileReader::CalculatePearsonCovarianceForLists]
    #
    # This returns two lists of values.
    #####################################################
    def CalculatePearsonCovarianceForLists(self, valueList1, valueList2):
        length1, meanVal1, variance1, stdDev1 = self.GetStatsForList(valueList1)
        length2, meanVal2, variance2, stdDev2 = self.GetStatsForList(valueList2)

        # Compute the covariance. 
        # This is the tendency for the variables to have a linear relationship.
        # ???It is the slope of the regression line.???
        # It is computed by the average of the products of distances from each list element and the list mean.
        #
        # If a list is sorted in increasing order, then the difference between list elements and the list mean will
        # start with a negative number (the smallest value, so farthest below the mean) and end with a positive number
        # (the largest value, so farthest greater than the mean). 
        # Each value in the list will have a difference to the mean that lays somewhere in the middle.
        # The two lists are covariant if small values in one list correspond to small values in the other list, and
        # large values in one list correspond to large values in the other list. In other words, the two corresponding
        # values will have distances with the same sign, either both positive or both negative. In either case, their
        # product is a positive value.
        # If the two lists are not covariant, then a number above average in one list will be associated with a
        # number below average in the other list. when they are very different, then their differences to the respective 
        # means will have different polarity, one is positice and one is negative. The product is a negative number.
        # The sum of all of these will be a mix of positive and negative products.
        covariance = 0
        for i in range(0, length1):
            covariance += ((valueList1[i] - meanVal1) * (valueList2[i] - meanVal2))
        # This is the sample covariance, so we should use length-1 to compute the mean.
        # However, the Python library seems to use the population variance, so uses length to compute the mean
        covariance = covariance / length1 # (length1 - 1)
        refCovariance = np.cov(valueList1, valueList2)[0][1]
        #print("Derived covariance=" + str(covariance))
        #print("Reference covariance=" + str(refCovariance))

        # The absolute value of the covariance can be any number, from -infinity to +infinity.
        # Its absolute value does not tell you anything about how well the lists are correlated.
        # So, normalize the covariance by the variability of the data. This essentially normalizes
        # the covariance by some measure of the range of values (largest - smallest). Now, why don't
        # we normalize the the products of the two ranges like (largest - smallest of set 1) * (largest - smallest of set2)
        # Not sure.
        # Pearson assumes a Gaussian distribution of the data, because it uses the mean value of each list
        # in its calculation.
        # It has values between -1 (negative correlation) and 1 (positive correlation). 0 means no correlation.
        pearsonCoeff = covariance / (stdDev1 * stdDev2)

        corrMatrix = np.corrcoef(valueList1, valueList2)
        refPearsonCoeff = corrMatrix[0, 1]

        ##refPearsonList = pearsonr(valueList1, valueList2)
        ##refPearsonCoeff2 = refPearsonList[0]
        ##refPValue = refPearsonList[1]

        #print("Derived pearsonCoeff=" + str(pearsonCoeff))
        #print("Reference pearsonCoeff=" + str(refPearsonCoeff))
        ##print("Reference pearsonCoeff2=" + str(refPearsonCoeff2))

        return refPearsonCoeff
    # End - CalculatePearsonCovarianceForLists






    #####################################################
    #
    # [TDFFileReader::CalculateSpearmanCovarianceForLists]
    #
    # Spearman correlation is just the Pearson correlation coefficient 
    # between the rank variables
    #####################################################
    def CalculateSpearmanCovarianceForLists(self, valueList1, valueList2):
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

        #print("=================")
        #print("valueList1=" + str(valueList1))
        #print("=================")
        #print("indexList=" + str(indexList))
        #print("=================")
        #print("valueRanksList=" + str(valueRanksList))
        
        mySpearman = self.CalculatePearsonCovarianceForLists(valueRanksList1, valueRanksList2)

        #scipy.stats.spearmanr will take care of computing the ranks for you, you simply have to give it the data in the correct order:
        refSpearmanCoeff, pValue = spearmanr(valueList1, valueList2)

        #print("=================")
        #print("mySpearman=" + str(mySpearman))
        #print("refSpearmanCoeff=" + str(refSpearmanCoeff))

        return refSpearmanCoeff
    # End - CalculateSpearmanCovarianceForLists





    #####################################################
    #
    # [TDFFileReader::GetCovariance]
    #
    #####################################################
    def GetCovariance(self, varName1, varName2):
        # Iterate over every patient
        numpatients = 0
        list1 = []
        list2 = []
        fFoundPatient = self.GotoFirstPatient()
        while (fFoundPatient):
            list1, list2 = self.GetListOfValsForCurrentPatient(varName1, list1, varName2, list2, 0, None, None, None)
    
            numpatients += 1
            if ((False) and (numpatients >= 10)):
                break
            fFoundPatient = self.GotoNextPatient()
        # End - while (patientNode):

        pearson = 0
        spearman = 0

        pearson = self.CalculatePearsonCovarianceForLists(list1, list2)
        #spearman = self.CalculateSpearmanCovarianceForLists(list1, list2)

        return pearson, spearman
    # End - GetCovariance






    #####################################################
    #
    # [TDFFileReader::FindCovariantInputs]
    #
    #####################################################
    def FindCovariantInputs(self, resultVarName, inputNameListStr):
        print("\nCovariance with " + resultVarName + "\n===============================")

        inputNameList = inputNameListStr.split(',')  
        for valueIndex, inputName in enumerate(inputNameList):
            pearson, spearman = self.GetCovariance(resultVarName, inputName)
            pearson = round(pearson, 4)
            spearman = round(spearman, 4)
            print(inputName + ": " + str(pearson))
    # End - FindCovariantInputs





    #####################################################
    #
    # [TDFFileReader::TestGetRawTimelineData]
    #
    #####################################################
    def TestGetRawTimelineData(self, timeLineIndex):
        if ((timeLineIndex < 0) or (timeLineIndex >= len(self.CompiledTimeline))):
            return False, 0, 0, {}

        timelineEntry = self.CompiledTimeline[timeLineIndex]
        currentDayNum = timelineEntry['TimeDays']
        currentHour = timelineEntry['TimeHours']
        currentMin = timelineEntry['TimeMin']
        
        #timeStamp = TDF_MakeTimeStamp(currentDayNum, currentHour, currentMin)
        dataDict = timelineEntry['data']

        timeStampAsInt = 0
        timeStampAsInt = timeStampAsInt + (currentDayNum * 24 * 60 * 60)
        # Add hours in seconds
        timeStampAsInt = timeStampAsInt + (currentHour * 60 * 60)
        # Add minutes in seconds
        timeStampAsInt = timeStampAsInt + (currentMin * 60)

        return True, timeStampAsInt, currentDayNum, dataDict
    # End - TestGetRawTimelineData






    #####################################################
    #
    # [TDFFileReader::CompilePatientTimelineImpl]
    #
    #####################################################
    def CompilePatientTimelineImpl(self):
        #print("CompilePatientTimelineImpl, start")

        if (self.m_DebugMode):
            print("CompilePatientTimelineImpl, start Debugging")

        self.CompiledTimeline = []
        # At any given time, self.LatestLabsFromCurrentOrEarlierTimes has the most recent
        # value for each lab.
        self.LatestLabsFromCurrentOrEarlierTimes = {}
        self.TimesOfFutureEvents = {}
        self.latestTimeLineEntryTimeDays = -1
        self.latestTimeLineEntryTimeHours = -1
        self.latestTimeLineEntryTimeMins = -1
        self.latestTimeLineEntry = None

        # Initialize the latest labs with a few special values that don't change.
        self.LatestLabsFromCurrentOrEarlierTimes['IsMale'] = int(self.CurrentIsMale)
        self.LatestLabsFromCurrentOrEarlierTimes['WtKg'] = int(self.CurrentWtInKg)
        if (self.CurrentRaceStr == "C"):
            self.LatestLabsFromCurrentOrEarlierTimes['IsCaucasian'] = 1
        else:
            self.LatestLabsFromCurrentOrEarlierTimes['IsCaucasian'] = 0

        # Initially, all outcomes are false for this patient. 
        # This will change as we move forward through the timeline.
        self.LatestLabsFromCurrentOrEarlierTimes['DiedInpt'] = 0
        self.LatestLabsFromCurrentOrEarlierTimes['DiedIn12Mos'] = 0
        self.LatestLabsFromCurrentOrEarlierTimes['ReadmitIn30Days'] = 0
        self.LatestLabsFromCurrentOrEarlierTimes['PreexistingMyeloma'] = 0
        self.LatestLabsFromCurrentOrEarlierTimes['DiagMyeloma'] = 0

        # This is the list of recent values and the current baseline
        self.numPastDaysForBaselineCr = 2
        self.BaselineGFR = -1
        self.BaselineCr = -1
        self.BaselineMELD = -1
        self.DateOfLatestCKD5 = -1

        # Initialize the daily med list for the forward pass.            
        self.DailyMeds = dict()
        self.NewMedsForCurrentDay = dict()
        self.NewMedHoursForCurrentDay = dict()
        self.DailyMeds["WarfarinDose"] = 0.0
        self.DailyMeds["MTXDose"] = 0.0
        self.DailyMeds["TacroDoseAM"] = 0.0
        self.DailyMeds["TacroDosePM"] = 0.0
        self.DailyMeds["VoriDose"] = 0.0


        ######################################
        # FORWARD PASS
        # Keep a running list of the latest values for all lab values. This includes
        # all lab values.
        #print("=======================================================")
        #print("Start Forward Pass")
        currentNode = XMLTools_GetFirstChildNode(self.currentPatientNode)
        currentTimelinePointID = -1
        self.CurrentAdmitDay = -1
        while (currentNode):
            nodeType = XMLTools_GetElementName(currentNode).lower()
            #print("Forward Pass. NodeType: " + nodeType)

            # Get the timestamp for this XML node.
            labDateDays = 0
            labDateHours = 0
            labDateMins = 0
            # Data and Events
            if ((nodeType == "e") or (nodeType == "d")):
                timeStampStr = currentNode.getAttribute("T")
                labDateDays, labDateHours, labDateMins = TDF_ParseTimeStamp(timeStampStr)

                if (self.m_DebugMode):
                    if ((labDateDays >= 18506) and (labDateDays <= 18574)):
                        #print("FORWARD PASS. labDateDays=" + str(labDateDays) + ", timeStampStr=" + str(timeStampStr))
                        pass

                dataClass = currentNode.getAttribute("C").lower()
            else:
                currentNode = XMLTools_GetAnyPeerNode(currentNode)
                continue

            # Find where we store the data from this XML node in the runtime timeline.
            # There may be separate XML nodes for labs, vitals and events that all map to the same
            # point in time. Collapse all lab and vitals data from the same time to a single data point.
            reuseLatestData = False
            if ((self.latestTimeLineEntryTimeDays == labDateDays)
                    and (self.latestTimeLineEntryTimeHours == labDateHours)
                    and (self.latestTimeLineEntryTimeMins == labDateMins)):
                reuseLatestData = True
            # Outcome dates are sloppy. However, do not overuse too much
            # because that allows a later diagnosis to overwrite the date of a much
            # earlier data point.
            elif ((nodeType == "oc")
                    and (self.latestTimeLineEntryTimeDays == labDateDays)
                    and (self.latestTimeLineEntryTimeHours >= labDateHours)):
                reuseLatestData = True
            # Diagnosis dates are sloppy. However, do not overuse too much
            # because that allows a later diagnosis to overwrite the date of a much
            # earlier data point.
            elif ((nodeType == "d") and (dataClass == "d")
                    and (self.latestTimeLineEntryTimeDays == labDateDays)
                    and (self.latestTimeLineEntryTimeHours >= labDateHours)):
                reuseLatestData = True
            # Events reuse the most recent data point if it is in the same day and hour
            elif ((nodeType == "e")
                    and (self.latestTimeLineEntryTimeDays == labDateDays)
                    and (self.latestTimeLineEntryTimeHours >= labDateHours)):
                reuseLatestData = True



            if (self.m_DebugMode):
                if ((labDateDays >= 18506) and (labDateDays <= 18574)):
                    print("FORWARD PASS. labDateDays=" + str(labDateDays) + ", timeStampStr=" + str(timeStampStr))
                    print("    reuseLatestData=" + str(reuseLatestData) + ", currentTimelinePointID=" + str(currentTimelinePointID))
                    print("    self.latestTimeLineEntryTimeDays=" + str(self.latestTimeLineEntryTimeDays))
                    print("    nodeType=" + str(nodeType))



            # Get the actual list of data values for this time.
            # This will create a new timeline entry if necessary.
            if ((reuseLatestData) and (self.latestTimeLineEntry != None)):
                #print("Reuse existing timeline entry")
                timelineEntry = self.latestTimeLineEntry
            else:
                #print("Create new timeline entry")
                currentTimelinePointID += 1

                timelineEntry = {}
                timelineEntry['TimeDays'] = labDateDays
                timelineEntry['TimeHours'] = labDateHours
                timelineEntry['TimeMin'] = labDateMins
                timelineEntry['timelinePointID'] = currentTimelinePointID

                self.CompiledTimeline.append(timelineEntry)
                self.latestTimeLineEntry = timelineEntry
    
                # Each timeline node needs a private copy of the latest labs.
                # Make a copy of the most recent labs, so we inherit any labs up to this point.
                # This node may overwrite any of the labs that change.
                privateCopy = self.LatestLabsFromCurrentOrEarlierTimes.copy()

                timelineEntry['data'] = privateCopy
                self.LatestLabsFromCurrentOrEarlierTimes = privateCopy

                # At the start of each day, we update the list of medications.
                if ((self.latestTimeLineEntryTimeDays < 0) or (labDateDays != self.latestTimeLineEntryTimeDays)):
                    # Overwrite the daily meds with any changes from the previous day.
                    for index, (medName, medDose) in enumerate(self.NewMedsForCurrentDay.items()):
                        self.DailyMeds[medName] = medDose

                    # Copy the daily med lists to each day's meds.
                    # Drug events happen when a drug is ordered, not each time it is given.
                    # As a result, we keep a list of daily meds, and apply it to each day.
                    # We update the list of daily meds any time a new order.
                    #
                    # BUG BUGBUG FIXME
                    # Note, this does NOT record when a med is stopped, so once it starts
                    # and is added to the daily list, then it continues.
                    #
                    # BUG BUGBUG FIXME
                    # If a drug is ordered for day N, it will be added to the daily med list
                    # at the end of the day, and only show up on the next day. This may be close
                    # to what happens on the wards, so actually may be correct.
                    for index, (medName, medDose) in enumerate(self.DailyMeds.items()):
                        self.LatestLabsFromCurrentOrEarlierTimes[medName] = medDose

                    # Reset the list of new med additions for the new day we are about to start.
                    self.NewMedsForCurrentDay = dict()
                    self.NewMedHoursForCurrentDay = dict()
                    # Some counters are added over the course of a day. Initialize them.
                    self.NewMedsForCurrentDay["VancDose"] = 0.0
                    self.NewMedsForCurrentDay["TobraDose"] = 0.0
                    self.NewMedsForCurrentDay["VoriDose"] = 0.0
                    self.NewMedsForCurrentDay["CycDose"] = 0.0
                # End - Update med lists at the start of each new day.

                self.latestTimeLineEntryTimeDays = labDateDays
                self.latestTimeLineEntryTimeHours = labDateHours
                self.latestTimeLineEntryTimeMins = labDateMins

            # We always set the timeline ID each XML node is associated with
            currentNode.setAttribute("xID", str(currentTimelinePointID))


            # Read the contents of this XML node into the runtime timeline data structures.
            # Outcomes
            if (nodeType == "oc"):
                self.ProcessOutcomeNodeForwardImpl(currentNode)
            ###################
            # Events
            elif (nodeType == "e"):
                self.ProcessEventNodeForwardImpl(currentNode, labDateDays, labDateHours, labDateMins)
            ###################
            # Data
            elif (nodeType == "d"):
                self.ProcessDataNodeForwardImpl(currentNode, labDateDays, labDateHours, labDateMins)

            # Count the days since the last dialysis or ESRD event.
            daysSinceCKD5 = -1
            if (("CKDStage" in self.LatestLabsFromCurrentOrEarlierTimes) 
                    and (self.LatestLabsFromCurrentOrEarlierTimes["CKDStage"] >= 5)):
                self.DateOfLatestCKD5 = labDateDays
            if (self.DateOfLatestCKD5 > 0):
                daysSinceCKD5 = labDateDays - self.DateOfLatestCKD5
            self.LatestLabsFromCurrentOrEarlierTimes["DaysSinceDialysis"] = daysSinceCKD5
            

            currentNode = XMLTools_GetAnyPeerNode(currentNode)
        # End - while (currentNode):

        self.LastTimelinePointID = currentTimelinePointID


        ######################################
        # REVERSE PASS
        # Keep a running list of the next occurrence of each event.
        #print("=======================================================")
        #print("Start Reverse Pass")
        self.CurrentLengthOfStay = -1
        self.TimesOfFutureEvents['NextAKIDate'] = -1
        self.TimesOfFutureEvents['NextBaselineCrDate'] = -1
        currentNode = XMLTools_GetLastChildNode(self.currentPatientNode)
        while (currentNode):
            nodeType = XMLTools_GetElementName(currentNode)
            nodeType = nodeType.lower()
            #print("nodeType: " + str(nodeType))

            # Skip anything that is not a data or event node.
            # We don't do anything with nodes like outcomes.
            if ((nodeType != "e") and (nodeType != "d")):
                currentNode = XMLTools_GetAnyPrevPeerNode(currentNode)
                continue

            timeStampStr = currentNode.getAttribute("T")
            # Some nodes, like outcomes, do not have timestamps.
            if (timeStampStr != ""):
                labDateDays, labDateHours, labDateMins = TDF_ParseTimeStamp(timeStampStr)
            else:
                labDateDays = 0
                labDateHours = 0
                labDateMins = 0

            timelinePointIDStr = currentNode.getAttribute("xID")
            #print("Reverse timelinePointIDStr = " + str(timelinePointIDStr))
            #print("Reverse (before update) HR = " + str(self.CompiledTimeline[int(timelinePointIDStr)]['data']['HR']))
            timelineIndex = int(timelinePointIDStr)
            timelineEntry = self.CompiledTimeline[timelineIndex]

            if (self.m_DebugMode):
                self.m_DebugLevel = 0
                if ((labDateDays >= 18506) and (labDateDays <= 18574)):
                    print("REVERSE PASS. labDateDays=" + str(labDateDays) + ", timeStampStr=" + str(timeStampStr))
                    print("      timelinePointIDStr=" + str(timelinePointIDStr) + ", timelineIndex=" + str(timelineIndex))
                    print("      nodeType: " + str(nodeType) + ", labDateDay = " + str(labDateDays))
                    self.m_DebugLevel = 1

            # Get a reference to the data collected up to this point in FORWARD order.
            # This was compiled in the previous loop, which did the forward pass.
            self.LatestLabsFromCurrentOrEarlierTimes = timelineEntry['data']

            # Now, update the events at this node using data pulled from the future in REVERSE order.
            # Events
            if (nodeType == "e"):
                self.ProcessEventNodeInReverseImpl(currentNode, labDateDays, labDateHours, labDateMins)
            # Data
            elif (nodeType == "d"):
                self.ProcessDataNodeInReverseImpl(currentNode, labDateDays, labDateHours, labDateMins)

            currentNode = XMLTools_GetAnyPrevPeerNode(currentNode)
        # End - while (currentNode):



        self.LastTimeLineIndex = len(self.CompiledTimeline) - 1
    # End - CompilePatientTimelineImpl(self)





    ################################################################################
    #
    # [TDFFileReader::ProcessEventNodeForwardImpl]
    #
    # This processes any EVENT node as we move forward in the the timeline. 
    # It updates self.LatestLabsFromCurrentOrEarlierTimes, possibly overwriting earlier outcomes.
    ################################################################################
    def ProcessEventNodeForwardImpl(self, eventNode, eventDateDays, eventDateHours, eventDateMins):
        #print("ProcessEventNodeForwardImpl")

        eventClass = eventNode.getAttribute("C")
        eventValue = eventNode.getAttribute("V")
        #print("ProcessEventNodeForwardImpl. Class=" + eventClass)
        #print("ProcessEventNodeForwardImpl. Value=" + eventValue)

        ############################################
        if (eventClass == "Admit"):
            self.LatestLabsFromCurrentOrEarlierTimes['InHospital'] = 1
            self.CurrentAdmitDay = eventDateDays
        ############################################
        elif (eventClass == "Discharge"):
            self.LatestLabsFromCurrentOrEarlierTimes['InHospital'] = 0
            eventNode.setAttribute("AdmitDate", str(self.CurrentAdmitDay))
            self.CurrentAdmitDay = -1
            # Reset all outcomes until the next admission.
            self.LatestLabsFromCurrentOrEarlierTimes['DiedInpt'] = 0
            self.LatestLabsFromCurrentOrEarlierTimes['DiedIn12Mos'] = 0
            self.LatestLabsFromCurrentOrEarlierTimes['ReadmitIn30Days'] = 0
            self.LatestLabsFromCurrentOrEarlierTimes['DiagMyeloma'] = 0
        ############################################
        elif (eventClass == "Transfer"):
            if (eventValue.startswith("ICU")):
                self.LatestLabsFromCurrentOrEarlierTimes['InICU'] = 1
            else:
                self.LatestLabsFromCurrentOrEarlierTimes['InICU'] = 0
        ############################################
        elif (eventClass == "RapidResponse"):
            self.LatestLabsFromCurrentOrEarlierTimes['MostRecentRapidResponseDate'] = eventDateDays
        ############################################
        elif (eventClass == "Proc"):
            if (eventValue == "proc/Dialysis"):
                self.LatestLabsFromCurrentOrEarlierTimes['MostRecentDialysisDate'] = eventDateDays
                self.DateOfLatestCKD5 = eventDateDays
            elif (eventValue == "proc/CardiacCath"):
                self.LatestLabsFromCurrentOrEarlierTimes['MostRecentCardiacCathDate'] = eventDateDays
            elif (eventValue == "proc/Intubation"):
                self.LatestLabsFromCurrentOrEarlierTimes['MostRecentIntubationDate'] = eventDateDays
            elif (eventValue == "proc/PEG"):
                self.LatestLabsFromCurrentOrEarlierTimes['MostRecentPEGDate'] = eventDateDays
        ############################################
        elif (eventClass == "Surg"):
            if (eventValue == "Major/Cardiac/CABG"):
                self.LatestLabsFromCurrentOrEarlierTimes['MostRecentCABGDate'] = eventDateDays
            elif (eventValue.startswith("Major")):
                self.LatestLabsFromCurrentOrEarlierTimes['MostRecentMajorSurgeryDate'] = eventDateDays
        ############################################
        elif (eventClass == "Med"):
            doseStr = eventNode.getAttribute("D")
            eventValue = eventValue.lower()
            ###########
            if ((eventValue == "warfarin") or (eventValue == "coumadin") or (eventValue == "coum")):
                doseStr = doseStr.lstrip()
                # Be careful. Some orders, are "Pharmacist to dose" and do not have a dose.
                if (doseStr != ""):
                    #print("WarfarinDose=" + doseStr)
                    self.NewMedsForCurrentDay["WarfarinDose"] = float(doseStr)
                    # This takes effect on the next day. Coumadin is usually given in the evenings, and INR
                    # is not checked until the next morning.
                    # self.LatestLabsFromCurrentOrEarlierTimes["WarfarinDose"] = float(doseStr)
                # End - if (doseStr != ""):
            ###########
            elif ((eventValue == "mtx") or (eventValue == "methotrexate")):
                doseStr = doseStr.lstrip()
                # Be careful. Some orders, are "Pharmacist to dose" and do not have a dose.
                if (doseStr != ""):
                    #print("MTXDose=" + doseStr)
                    self.NewMedsForCurrentDay["MTXDose"] = float(doseStr)
                # End - if (doseStr != ""):
            ###########
            elif ((eventValue == "tac") or (eventValue == "tacrolimus")):
                doseStr = doseStr.lstrip()
                # Be careful. Some orders, are "Pharmacist to dose" and do not have a dose.
                if (doseStr != ""):
                    # Record the separate AM and PM doses
                    if ((eventDateHours >= 0) and (eventDateHours <= 12)):
                        #print("Tacrolimus. AM. Day=" + str(eventDateDays) + ", hour=" + str(eventDateHours) + ", min=" + str(eventDateMins) + ", dose="+ doseStr)
                        self.NewMedsForCurrentDay["TacroDoseAM"] = float(doseStr)
                    else:
                        #print("Tacrolimus. PM. Day=" + str(eventDateDays) + ", dose="+ doseStr)
                        self.NewMedsForCurrentDay["TacroDosePM"] = float(doseStr)
                # End - if (doseStr != ""):
            ###########
            elif ((eventValue == "vanc") or (eventValue == "vancomycin")):
                doseStr = doseStr.lstrip()
                # Be careful. Some orders, are "Pharmacist to dose" and do not have a dose.
                if (doseStr != ""):
                    # Make sure this is a new dose.
                    # BUGBUG FIXME - The TDF writer seems to accidentally add the same drug several times.
                    if ((not ("VancDose" in self.NewMedHoursForCurrentDay)) or (self.NewMedHoursForCurrentDay["VancDose"] < eventDateHours)):
                        self.NewMedHoursForCurrentDay["VancDose"] = eventDateHours
                        #print("VancDose=" + doseStr)
                        # Add this to the daily total. Vanc may be given daily, or Q12h or Q8h. We use the 
                        # total daily dose for each day.
                        self.NewMedsForCurrentDay["VancDose"] += float(doseStr)
                # End - if (doseStr != ""):
            ###########
            elif ((eventValue == "vori") or (eventValue == "voriconazole")):
                doseStr = doseStr.lstrip()
                # Be careful. Some orders, are "Pharmacist to dose" and do not have a dose.
                if (doseStr != ""):
                    # Make sure this is a new dose.
                    # BUGBUG FIXME - The TDF writer seems to accidentally add the same drug several times.
                    if ((not ("VoriDose" in self.NewMedHoursForCurrentDay)) or (self.NewMedHoursForCurrentDay["VoriDose"] < eventDateHours)):
                        self.NewMedHoursForCurrentDay["VoriDose"] = eventDateHours
                        #print("VoriDose=" + doseStr)
                        # Add this to the daily total.
                        self.NewMedsForCurrentDay["VoriDose"] += float(doseStr)
                # End - if (doseStr != ""):
            ###########
            elif ((eventValue == "tob") or (eventValue == "tobramycin")):
                doseStr = doseStr.lstrip()
                # Be careful. Some orders, are "Pharmacist to dose" and do not have a dose.
                if (doseStr != ""):
                    # Make sure this is a new dose.
                    # BUGBUG FIXME - The TDF writer seems to accidentally add the same drug several times.
                    if ((not ("TobraDose" in self.NewMedHoursForCurrentDay)) or (self.NewMedHoursForCurrentDay["TobraDose"] < eventDateHours)):
                        self.NewMedHoursForCurrentDay["TobraDose"] = eventDateHours
                        #print("VoriDose=" + doseStr)
                        # Add this to the daily total.
                        self.NewMedsForCurrentDay["TobraDose"] += float(doseStr)
                # End - if (doseStr != ""):
            ###########
            elif ((eventValue == "csa") or (eventValue == "cyclosporine")):
                doseStr = doseStr.lstrip()
                # Be careful. Some orders, are "Pharmacist to dose" and do not have a dose.
                if (doseStr != ""):
                    #print("CycDose=" + doseStr)
                    # Add this to the daily total.
                    if ((not ("CycDose" in self.NewMedHoursForCurrentDay)) or (self.NewMedHoursForCurrentDay["CycDose"] < eventDateHours)):
                        self.NewMedHoursForCurrentDay["CycDose"] = eventDateHours
                        #print("VoriDose=" + doseStr)
                        # Add this to the daily total.
                        self.NewMedsForCurrentDay["CycDose"] += float(doseStr)

                    # Record the separate AM and PM doses
                    if ((eventDateHours >= 0) and (eventDateHours <= 12)):
                        self.NewMedsForCurrentDay["CycDoseAM"] = float(doseStr)
                    else:
                        self.NewMedsForCurrentDay["CycDosePM"] = float(doseStr)
                # End - if (doseStr != ""):
        ############################################
        elif (eventClass == "Clinic"):
            pass
    # End - ProcessEventNodeForwardImpl







    ################################################################################
    #
    # [TDFFileReader::ProcessDataNodeForwardImpl]
    #
    # This processes any DATA node as we move forward in the the timeline. 
    # It updates self.LatestLabsFromCurrentOrEarlierTimes, possibly overwriting earlier outcomes.
    ################################################################################
    def ProcessDataNodeForwardImpl(self, dataNode, labDateDays, labDateHours, labDateMins):
        #print("ProcessDataNodeForwardImpl")
        dataClass = dataNode.getAttribute("C")
        labTextStr = str(XMLTools_GetTextContents(dataNode))

        ###################################
        # Diagnosis Node
        # Record the first time we have a diagnosis. That is why we do this on a
        # forward, not reverse, pass.
        if (dataClass == "D"): 
            diagnosisList = labTextStr.split(',')
            for diagnosisVal in diagnosisList:
                attrName = "Diagnose_" + diagnosisVal
                if (not (attrName in self.TimesOfFutureEvents)):
                    self.TimesOfFutureEvents[attrName] = labDateDays
        ###################################
        # Labs and Vitals
        # Copy all labs and vitals into the accumulator
        elif ((dataClass == "L") or (dataClass == "V")):
            assignmentList = labTextStr.split(',')
            for assignment in assignmentList:
                #print("ProcessDataNodeForwardImpl. assignment=" + assignment)        
                assignmentParts = assignment.split('=')
                if (len(assignmentParts) < 2):
                    continue
                labName = assignmentParts[0]
                labvalueStr = assignmentParts[1]
                labValueFloat = -1.0
                foundValidLab = False
                #print("ProcessDataNodeForwardImpl. labName=" + labName)        
                #print("ProcessDataNodeForwardImpl. labvalueStr=" + labvalueStr)        
                if ((labName != "") and (labvalueStr != "")):
                    foundValidLab = True
                    try:
                        labValueFloat = float(labvalueStr)
                    except:
                        # Replace invalid characters.
                        labvalueStr = labvalueStr.replace('>', '') 
                        labvalueStr = labvalueStr.replace('<', '') 
                        try:
                            labValueFloat = float(labvalueStr)
                        except:
                            foundValidLab = False
                # End - if ((labName != "") and (labValue != "")):


                if (foundValidLab):
                    try:
                        labInfo = g_LabValueInfo[labName]
                        labMinVal = float(labInfo['minVal'])
                        labMaxVal = float(labInfo['maxVal'])
                    except:
                        foundValidLab = False

                # Rule out ridiculous values. Often, vitals will be entered incorrectly
                # or similar things. This won't catch all invalid entries, but will catch
                # some.
                if (foundValidLab):
                    if ((labValueFloat < 0) or (labValueFloat >= (2 * labMaxVal))):
                        foundValidLab = False

                if (foundValidLab):
                    # Now, clip the value to the 
                    if (labValueFloat < float(labMinVal)):
                        labValueFloat = float(labMinVal)
                    if (labValueFloat > float(labMaxVal)):
                        labValueFloat = float(labMaxVal)
                    self.LatestLabsFromCurrentOrEarlierTimes[labName] = labValueFloat
                # End - if (foundValidLab)
            # End - for assignment in assignmentList
        # End - if ((dataClass == "L") or (dataClass == "V")):


        ###################################
        # Compute all derived values
        #######################
        valueName = "AgeInYrs"
        result = int(labDateDays / 365)
        self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "AgeInDays"
        result = int(labDateDays)
        self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "GFR"
        foundValidLab = False
        try:
            ageInYrs = self.LatestLabsFromCurrentOrEarlierTimes['AgeInYrs']
            serumCr = self.LatestLabsFromCurrentOrEarlierTimes['Cr']
            foundValidLab = True
        except:
            foundValidLab = False
        if ((foundValidLab) and (ageInYrs >= 0) and (serumCr >= 0)):
            # Weights are not that reliable. If we get a Cr, then try to use
            # it, even if we have to guess the weight.
            wtInKg = self.CurrentWtInKg
            if (wtInKg <= 0):
                wtInKg = 70

            result = ((140.0 - ageInYrs) * wtInKg) / (serumCr * 72.0)
            if (self.CurrentIsMale <= 0):
                result = result * 0.85
            result = round(result, 2)
            #print("GFR=" + str(result))
            if (result < 2):
                foundValidLab = False
                print("ERROR. GFR < 0")
                print("ERROR. ageInYrs=" + str(ageInYrs))
                print("ERROR. serumCr=" + str(serumCr))
                print("ERROR. wtInKg=" + str(wtInKg))
        if (foundValidLab):
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "AnionGap"
        foundValidLab = False
        try:
            serumNa = self.LatestLabsFromCurrentOrEarlierTimes['Na']
            serumCl = self.LatestLabsFromCurrentOrEarlierTimes['Cl']
            serumCO2 = self.LatestLabsFromCurrentOrEarlierTimes['CO2']
            foundValidLab = True
        except:
            foundValidLab = False
        if ((foundValidLab) and (serumNa >= 0) and (serumCl >= 0) and (serumCO2 >= 0)):
            result = serumNa - (serumCl + serumCO2)
            #print("AnionGap=" + str(result))
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "UrineAnionGap"
        foundValidLab = False
        try:
            urineNa = self.LatestLabsFromCurrentOrEarlierTimes['UNa']
            urineK = self.LatestLabsFromCurrentOrEarlierTimes['UK']
            urineCl = self.LatestLabsFromCurrentOrEarlierTimes['UCl']
            foundValidLab = True
        except:
            foundValidLab = False
        if ((foundValidLab) and (urineNa >= 0) and (urineK >= 0) and (urineCl >= 0)):
            result = (serumNa + urineK) - urineCl
            print("UrineAnionGap=" + str(result))
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "UACR"
        foundValidLab = False
        try:
            result = self.LatestLabsFromCurrentOrEarlierTimes['UPEPAlb']
            if (result >= 0):
                foundValidLab = True
        except:
            foundValidLab = False

        if (not foundValidLab):
            try:
                urineAlb = self.LatestLabsFromCurrentOrEarlierTimes['UAlb']
                urineCr = self.LatestLabsFromCurrentOrEarlierTimes['UCr']
                if ((urineAlb >= 0) and (urineCr >= 0)):
                    foundValidLab = True
            except:
                foundValidLab = False        
            if (foundValidLab):
                result = urineAlb / urineCr
                #print("UACR=" + str(result))
                self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "FENa"
        foundValidLab = False
        try:
            serumCr = self.LatestLabsFromCurrentOrEarlierTimes['Cr']
            serumNa = self.LatestLabsFromCurrentOrEarlierTimes['Na']
            urineCr = self.LatestLabsFromCurrentOrEarlierTimes['UCr']
            urineNa = self.LatestLabsFromCurrentOrEarlierTimes['UNa']
            if ((serumCr >= 0) and (serumNa >= 0) and (urineCr >= 0) and (urineNa >= 0)):
                foundValidLab = True
        except:
            foundValidLab = False
        if (foundValidLab):
            result = 100 * (serumCr * urineNa) / (serumNa * urineCr)
            result = round(result, 1)
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
            #print("FENa=" + str(result))
        #######################
        valueName = "FEUrea"
        foundValidLab = False
        try:
            serumCr = self.LatestLabsFromCurrentOrEarlierTimes['Cr']
            serumBUN = self.LatestLabsFromCurrentOrEarlierTimes['BUN']
            urineCr = self.LatestLabsFromCurrentOrEarlierTimes['UCr']
            urineUUN = self.LatestLabsFromCurrentOrEarlierTimes['UUN']
            if ((serumCr >= 0) and (serumBUN >= 0) and (urineCr >= 0) and (urineUUN >= 0)):
                foundValidLab = True
        except:
            foundValidLab = False
        if (foundValidLab):
            result = 100 * (serumCr * urineUUN) / (serumBUN * urineCr)
            result = round(result, 1)
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
            #print("FEUrea=" + str(result))
        #######################
        valueName = "AdjustCa"
        foundValidLab = False
        try:
            tCal = self.LatestLabsFromCurrentOrEarlierTimes['Ca']
            alb = self.LatestLabsFromCurrentOrEarlierTimes['alb']
            if ((tCal >= 0) and (alb >= 0)):
                foundValidLab = True
        except:
            foundValidLab = False
        if (foundValidLab):
            result = tCal + (0.8 * (4.0 - alb))
            result = round(result, 1)
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
            #print("AdjustCa=" + str(result))
        else:
            try:
                tCal = self.LatestLabsFromCurrentOrEarlierTimes['Ca']
                if (tCal >= 0):
                    foundValidLab = True
            except:
                foundValidLab = False
            if (foundValidLab):
                self.LatestLabsFromCurrentOrEarlierTimes[valueName] = tCal
                #print("AdjustCa=" + str(result))
        #######################
        valueName = "UPCR"
        foundValidLab = False
        try:
            result = self.LatestLabsFromCurrentOrEarlierTimes['UPEPTProt']
            if (result >= 0):
                foundValidLab = True
        except:
            foundValidLab = False
        if (not foundValidLab):
            try:
                result = self.LatestLabsFromCurrentOrEarlierTimes['UPCR']
                if (result >= 0):
                    foundValidLab = True
            except:
                foundValidLab = False
        if (not foundValidLab):
            try:
                urineProt = self.LatestLabsFromCurrentOrEarlierTimes['UProt']
                urineCr = self.LatestLabsFromCurrentOrEarlierTimes['UCr']
                result = urineAlb / urineCr
                if ((urineProt >= 0) and (urineCr >= 0) and (result >= 0)):
                    foundValidLab = True
            except:
                foundValidLab = False
        if (foundValidLab):
            #print("urineProt / urineCr=" + str(result))
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "ProtGap"
        foundValidLab = False
        try:
            serumTProt = self.LatestLabsFromCurrentOrEarlierTimes['TProt']
            serumAlb = self.LatestLabsFromCurrentOrEarlierTimes['Alb']
            if ((serumTProt >= 0) and (serumAlb >= 0)):
                foundValidLab = True
        except:
            foundValidLab = False
        if (foundValidLab):
            result = serumTProt - serumAlb
            #print("ProtGap=" + str(result))
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "KappaLambdaRatio"
        foundValidLab = False
        try:
            kappaVal = self.LatestLabsFromCurrentOrEarlierTimes['FLCKappa']
            lambdaVal = self.LatestLabsFromCurrentOrEarlierTimes['FLCLambda']
            if ((kappaVal >= 0) and (lambdaVal >= 0)):
                foundValidLab = True
        except:
            foundValidLab = False
        if (foundValidLab):
            result = kappaVal / lambdaVal
            print("ProtGap=" + str(result))
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
        #######################
        valueName = "MELD"
        foundValidLab = False
        try:
            serumCr = self.LatestLabsFromCurrentOrEarlierTimes['Cr']
            tBili = self.LatestLabsFromCurrentOrEarlierTimes['Tbili']
            inr = self.LatestLabsFromCurrentOrEarlierTimes['INR']
            if ((serumCr > 0) and (tBili > 0) and (inr > 0)):
                foundValidLab = True
        except:
            foundValidLab = False
        if (foundValidLab):
            # If the base is not passed as a second parameter, then math.log() returns natural log.
            lnCr = math.log(float(serumCr))
            lntBili = math.log(float(tBili))
            #print(">>> inr=" + str(inr))
            lnINR = math.log(float(inr))
            result = 10 * ((0.957 * lnCr) + (0.378 * lntBili) + (1.12 * lnINR)) + 6.43
            self.LatestLabsFromCurrentOrEarlierTimes[valueName] = result
    # End - ProcessDataNodeForwardImpl





    ################################################################################
    #
    # [TDFFileReader::ProcessOutcomeNodeForwardImpl]
    #
    # This processes any OUTCOME (OC) node as we move forward in the the timeline. 
    # It updates self.LatestLabsFromCurrentOrEarlierTimes, possibly overwriting earlier outcomes.
    ################################################################################
    def ProcessOutcomeNodeForwardImpl(self, outcomesNode):
        #print("ProcessOutcomeNodeForwardImpl")
        try:
            outcomeStr = outcomesNode.getAttribute("DiedInpt")
            if (outcomeStr == "T"):
                self.LatestLabsFromCurrentOrEarlierTimes['DiedInpt'] = 1
        except:
            pass
        try:
            outcomeStr = outcomesNode.getAttribute("DiedIn12Mos")
            if (outcomeStr == "T"):
                self.LatestLabsFromCurrentOrEarlierTimes['DiedIn12Mos'] = 1
        except:
            pass
        try:
            outcomeStr = outcomesNode.getAttribute("ReadmitIn30Days")
            if (outcomeStr == "T"):
                self.LatestLabsFromCurrentOrEarlierTimes['ReadmitIn30Days'] = 1
        except:
            pass
        try:
            outcomeStr = outcomesNode.getAttribute("PreexistingMyeloma")
            if (outcomeStr == "T"):
                self.LatestLabsFromCurrentOrEarlierTimes['PreexistingMyeloma'] = 1
        except:
            pass
        try:
            outcomeStr = outcomesNode.getAttribute("DiagMyeloma")
            if (outcomeStr == "T"):
                self.LatestLabsFromCurrentOrEarlierTimes['DiagMyeloma'] = 1
        except:
            pass
    # End - ProcessOutcomeNodeForwardImpl





    ################################################################################
    #
    # [TDFFileReader::ProcessEventNodeInReverseImpl]
    #
    # This processes any EVENT node as we move REVERSE in the the timeline. 
    # It updates self.LatestLabsFromCurrentOrEarlierTimes, possibly overwriting later outcomes.
    # It also propagates values backward in time. This lets nodes record the time until 
    # some future event. 
    ################################################################################
    def ProcessEventNodeInReverseImpl(self, eventNode, eventDateDays, eventDateHours, eventDateMins):
        eventClass = eventNode.getAttribute("C")
        eventValue = eventNode.getAttribute("V")
        #print("ProcessEventNodeInReverseImpl")
        #print("eventClass=" + str(eventClass) + ", eventValue=" + str(eventValue))

        if (self.m_DebugLevel >= 1):
            print("ProcessEventNodeInReverseImpl. eventClass=" + str(eventClass) + ", eventValue=" + str(eventValue))

        #####################
        if (eventClass == "Admit"):
            self.TimesOfFutureEvents['NextAdmissionDate'] = eventDateDays
            self.CurrentLengthOfStay = -1
        #####################
        elif (eventClass == "Discharge"):
            self.TimesOfFutureEvents['NextDischargeDate'] = eventDateDays

            try:
                currentAdmitDay = int(eventNode.getAttribute("AdmitDate"))
            except:
                currentAdmitDay = -1
            if (currentAdmitDay > 0):
                self.CurrentLengthOfStay = eventDateDays - currentAdmitDay

            try:
                diedInpt = eventNode.getAttribute("DiedInpt")
            except:
                diedInpt = "F"
            diedInpt = diedInpt.lower()
            if (diedInpt == "t"):
                self.TimesOfFutureEvents['DeathDate'] = eventDateDays
        #####################
        elif (eventClass == "Transfer"):
            if ((eventValue == "Ward") or (eventValue == "Prog")):
                self.TimesOfFutureEvents['NextTransferToWardDate'] = eventDateDays
            elif (eventValue.startswith("ICU")):
                self.TimesOfFutureEvents['NextTransferToICUDate'] = eventDateDays
        #####################
        elif (eventClass == "RapidResponse"):
            self.TimesOfFutureEvents['NextRapidResponseDate'] = eventDateDays
        #####################
        elif (eventClass == "Proc"):
            if (eventValue == "proc/Dialysis"):
                self.TimesOfFutureEvents['NextDialysisDate'] = eventDateDays
                self.DateOfLatestCKD5 = eventDateDays
            elif (eventValue == "proc/Intubation"):
                self.TimesOfFutureEvents['NextIntubationDate'] = eventDateDays
        #####################
        elif (eventClass == "Surg"):
            pass
        #####################
        elif (eventClass == "Med"):
            pass
        #####################
        elif (eventClass == "Clinic"):
            pass
    # End - ProcessEventNodeInReverseImpl







    ################################################################################
    #
    # [TDFFileReader::ProcessDataNodeInReverseImpl]
    #
    # This processes any DATA node as we move REVERSE in the the timeline. 
    # It updates self.LatestLabsFromCurrentOrEarlierTimes, possibly overwriting later outcomes.
    # It also propagates values backward in time. This lets nodes record the time until 
    # some future event. 
    ################################################################################
    def ProcessDataNodeInReverseImpl(self, dataNode, labDateDays, labDateHours, labDateMins):
        #print("ProcessDataNodeInReverseImpl")
        dataClass = dataNode.getAttribute("C")

        # Compute the baseline GFR
        # ------------------------
        # GFR can only decrease as time moves forward. So, it should only increase as we
        # go in REVERSE.
        #
        # If a future GFR (one we previously saw in the reverse direction) is
        # GREATER than the current GFR, then the current GFR reflects an AKI, not baseline.
        # In this case, just copy the future baseline back to this point.
        #
        # Alternatively, if this current GFR is greater than the future baseline, 
        # then this may be the new baseline when going forward to this point in time,
        # and it will decline in the future with progression of CKD.
        currentGFR = -1
        if ("GFR" in self.LatestLabsFromCurrentOrEarlierTimes):
            currentGFR = self.LatestLabsFromCurrentOrEarlierTimes["GFR"]
        if (currentGFR > 0):
            if ((self.BaselineGFR < 0) or (currentGFR > self.BaselineGFR)):
                self.BaselineGFR = currentGFR
        self.LatestLabsFromCurrentOrEarlierTimes["BaselineGFR"] = self.BaselineGFR


        # Compute the baseline Cr
        # ------------------------
        # Opposite to GFR, Cr can only increase as time moves forward. So, it should only
        # decrease as we go in REVERSE.
        # 
        # If a future Cr (one we previously saw in the reverse direction) is
        # LESS than the current Cr, then the current Cr reflects an AKI, not baseline.
        # In this case, just copy the future baseline back to this point.
        # Otherwise, update the Cr.
        currentCr = -1
        if ("Cr" in self.LatestLabsFromCurrentOrEarlierTimes):
            currentCr = self.LatestLabsFromCurrentOrEarlierTimes["Cr"]
        if (currentCr > 0):
            if ((self.BaselineCr < 0) or (currentCr < self.BaselineCr)):
                self.BaselineCr = currentCr
        self.LatestLabsFromCurrentOrEarlierTimes["BaselineCr"] = self.BaselineCr


        # Now, use the baseline GFR to compute the current CKD stage.
        if ((self.BaselineGFR >= 60) or (self.BaselineGFR <= 0)):
            currentCKDStage = 1
        elif (self.BaselineGFR >= 30):
            currentCKDStage = 3
        elif (self.BaselineGFR >= 15):
            currentCKDStage = 4
        else:
            currentCKDStage = 5        
        self.LatestLabsFromCurrentOrEarlierTimes["CKDStage"] = currentCKDStage


        # Now we know the baselines, we can decide whether we are in an AKI.
        # <> FIXME - Currently, I use 0.3 as the threshold.
        # But, really, this should depend on the CKD. A variation of 0.3
        # when the baseline GFR is 20 and Cr is 2.5, is probably not a real AKI.
        # Still, this is what the guidelines say.
        inAKI = False
        if ((self.BaselineCr > 0) and (currentCr > 0)):
            deltaCr = currentCr - self.BaselineCr
            if (deltaCr > 0.3):
                inAKI = True
        self.LatestLabsFromCurrentOrEarlierTimes["inAKI"] = inAKI


        # Compute the ABSOLUTE time until the next AKI or Recovery
        if (inAKI):
            self.TimesOfFutureEvents['NextAKIDate'] = labDateDays
        elif (not inAKI):
            self.TimesOfFutureEvents['NextBaselineCrDate'] = labDateDays


        # Compute the category for the next AKI at this time.
        self.LatestLabsFromCurrentOrEarlierTimes["Future_AKI"] = self.ComputeOutcomeCategory(labDateDays, self.TimesOfFutureEvents['NextAKIDate'])
        self.LatestLabsFromCurrentOrEarlierTimes["Future_AKIResolution"] = self.ComputeOutcomeCategory(labDateDays, self.TimesOfFutureEvents['NextBaselineCrDate'])


        # Compute the ABSOLUTE time when the next CKD stage happens
        # We check above that CKD stage is always increasing, so this will not be affected
        # by AKI's.
        if (currentCKDStage == 5):
            self.TimesOfFutureEvents['NextCKD5Date'] = labDateDays
        elif (currentCKDStage == 4):
            self.TimesOfFutureEvents['NextCKD4Date'] = labDateDays
        elif (currentCKDStage == 3):
            self.TimesOfFutureEvents['NextCKD3Date'] = labDateDays
        elif (currentCKDStage == 1):
            self.TimesOfFutureEvents['NextCKD1Date'] = labDateDays


        # Compute the Relative time until the next CKD stage.
        # Do this for all nodes, whether we have CKD yet or not. If we don't now,
        # we still may in the future.
        # We check above that CKD stage is always increasing, so this will not be affected
        # by AKI's.
        futureDate = -1
        if ("NextCKD5Date" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextCKD5Date"]

        if (self.m_DebugLevel >= 1):
            print("ProcessDataNodeInReverseImpl. labDateDays = " + str(labDateDays) + ", futureDate = " + str(futureDate))
            print("ProcessDataNodeInReverseImpl. deltaTime = " + str((futureDate - labDateDays)))
            print("ProcessDataNodeInReverseImpl. FutureCategory = " + str(self.ComputeOutcomeCategory(labDateDays, futureDate)))
        self.LatestLabsFromCurrentOrEarlierTimes["Future_CKD5"] = self.ComputeOutcomeCategory(labDateDays, futureDate)


        futureDate = -1
        if ("NextCKD4Date" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextCKD4Date"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_CKD4"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextCKD3Date" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextCKD3Date"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_CKD3"] = self.ComputeOutcomeCategory(labDateDays, futureDate)


        # Compute the baseline MELD
        # ------------------------
        # MELD can only go up as time moves forward. So, it should only decrease as we
        # go in REVERSE.
        # 
        # If a future MELD (one we previously saw in the reverse direction) is
        # LESS than the current MELD, then the current MELD reflects an acute change
        # (like an AKI), not baseline. In this case, just copy the future baseline 
        # value back to this point.
        #
        # Alternatively, if this current MELD is less than the future baseline, 
        # then this may be the new baseline when going forward to this point in time, and it will 
        # increase in the future with progression of disease
        currentMELD = -1
        if ("MELD" in self.LatestLabsFromCurrentOrEarlierTimes):
            currentMELD = self.LatestLabsFromCurrentOrEarlierTimes["MELD"]
            if (currentMELD > 0):
                if ((self.BaselineMELD < 0) or (currentMELD < self.BaselineCr)):
                    self.BaselineMELD = currentMELD
        self.LatestLabsFromCurrentOrEarlierTimes["BaselineMELD"] = self.BaselineMELD


        # Compute the ABSOLUTE time until the next MELD stage
        if (currentMELD > 0):
            if (currentMELD >= 40):
                self.TimesOfFutureEvents['NextMELD40Date'] = labDateDays
            elif (currentMELD >= 30):
                self.TimesOfFutureEvents['NextMELD30Date'] = labDateDays
            elif (currentMELD >= 20):
                self.TimesOfFutureEvents['NextMELD20Date'] = labDateDays
            elif (currentMELD >= 10):
                self.TimesOfFutureEvents['NextMELD10Date'] = labDateDays
        # End - if (currentMELD > 0):


        # Update the RELATIVE time until the next MELD stage.
        # Do this for all nodes, whether the patient has Cirrhosis yet or not.
        futureDate = -1
        if ("NextMELD40Date" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextMELD40Date"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_MELD40"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextMELD30Date" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextMELD30Date"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_MELD30"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextMELD20Date" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextMELD20Date"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_MELD20"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextMELD10Date" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextMELD10Date"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_MELD10"] = self.ComputeOutcomeCategory(labDateDays, futureDate)


        # Update the RELATIVE time until the next event
        futureDate = -1
        if ("NextAdmissionDate" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextAdmissionDate"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_Admission"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextDischargeDate" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextDischargeDate"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_Discharge"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("DeathDate" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["DeathDate"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_Death"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextTransferToWardDate" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextTransferToWardDate"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_TransferOutOfICU"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextTransferToICUDate" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextTransferToICUDate"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_TransferIntoICU"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextRapidResponseDate" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextRapidResponseDate"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_RapidResponse"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextDialysisDate" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextDialysisDate"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_Dialysis"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("NextIntubationDate" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["NextIntubationDate"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_Intubation"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        # Record RELATIVE time until a diagnosis.
        # These times were filled on the forward pass, so it is the very first time an event
        # was seen, not the next time.
        futureDate = -1
        if ("Diagnose_Cirrhosis" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["Diagnose_Cirrhosis"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_Cirrhosis"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        futureDate = -1
        if ("Diagnose_ESLD" in self.TimesOfFutureEvents):
            futureDate = self.TimesOfFutureEvents["Diagnose_ESLD"]
        self.LatestLabsFromCurrentOrEarlierTimes["Future_ESLD"] = self.ComputeOutcomeCategory(labDateDays, futureDate)

        if (self.CurrentLengthOfStay > 0):
            self.LatestLabsFromCurrentOrEarlierTimes['LengthOfStay'] = self.CurrentLengthOfStay
    # End - ProcessDataNodeInReverseImpl





    ################################################################################
    #
    # [TDFFileReader::ComputeOutcomeCategory]
    #
    # You cannot do "TimeUntil_xxx" because that cannot express the idea that the event "xxx" may
    # never happen. Instead, use categories, like "xxx will happen", "xxxx will not happen" or
    # time-bound categories like "xxx will happen in 3mos"
    # Each "Outcome_XXX" variable is a category:
    ################################################################################
    def ComputeOutcomeCategory(self, currentDate, outcomeDate):
        # 13 = EVENT will NOT happen in the next 10yrs
        if (outcomeDate < 0):
            return(TDF_FUTURE_EVENT_NOT_IN_10YRS)

        # 0 = EVENT is happening now or has previously happened
        daysUntilOutcome = outcomeDate - currentDate
        if (daysUntilOutcome <= 0):
            return(TDF_FUTURE_EVENT_NOW_OR_PAST)

        # 1 = EVENT will happen in 1 day
        if (daysUntilOutcome <= 1):
            return(TDF_FUTURE_EVENT_IN_1_DAY)

        # 2 = EVENT will happen in 3 days
        if (daysUntilOutcome <= 3):
            return(TDF_FUTURE_EVENT_IN_3_DAYS)

        # 3 = EVENT will happen in 7 days
        if (daysUntilOutcome <= 7):
            return(TDF_FUTURE_EVENT_IN_7_DAYS)

        # 4 = EVENT will happen in 14 days
        if (daysUntilOutcome <= 14):
            return(TDF_FUTURE_EVENT_IN_14_DAYS)

        # 5 = EVENT will happen in 30 days
        if (daysUntilOutcome <= 30):
            return(TDF_FUTURE_EVENT_IN_30_DAYS)

        # 6 = EVENT will happen in 90 days
        if (daysUntilOutcome <= 90):
            return(TDF_FUTURE_EVENT_IN_90_DAYS)

        # 7 = EVENT will happen in 180 days
        if (daysUntilOutcome <= 180):
            return(TDF_FUTURE_EVENT_IN_180_DAYS)

        # 8 = EVENT will happen in 365 days
        if (daysUntilOutcome <= 365):
            return(TDF_FUTURE_EVENT_IN_365_DAYS)

        # 9 = EVENT will happen in 730 days
        if (daysUntilOutcome <= 730):
            return(TDF_FUTURE_EVENT_IN_730_DAYS)

        # 10 = EVENT will happen in 1095 days (3yrs)
        if (daysUntilOutcome <= 1095):
            return(TDF_FUTURE_EVENT_IN_1095_DAYS)

        # 11 = EVENT will happen in 1825 days (5yrs) (some ESRD models use this)
        if (daysUntilOutcome <= 1825):
            return(TDF_FUTURE_EVENT_IN_1825_DAYS)

        # 12 = EVENT will happen in 3650 days (10yrs)  (10yrs, Framingham uses this)
        if (daysUntilOutcome <= 3650):
            return(TDF_FUTURE_EVENT_IN_3650_DAYS)

        # 13 = EVENT will NOT happen in the next 10yrs
        return(TDF_FUTURE_EVENT_NOT_IN_10YRS)
    # End - ComputeOutcomeCategory






    #####################################################
    #
    # [TDFFileReader::DoesPatientHaveNCompleteLabSets]
    # This method is NOT part of DataSet - it is a special iterator
    # Notice, we iterate over BOTH patients and dataNodes within a patient.
    #
    # This returns one sample of data
    #####################################################
    def DoesPatientHaveNCompleteLabSets(self, minThreshold):
        print("DoesPatientHaveNCompleteLabSets, start")
        if (self.numDataEntriesInCurrentWindow >= minThreshold):
            return True

        return False
    # End - DoesPatientHaveNCompleteLabSets(self)



    #####################################################
    #
    # [TDFFileReader::GetNumValuesInCurrentWindow]
    #
    # Return the total number of data samples
    # This method is NOT inherited from DataSet
    #####################################################
    def GetNumValuesInCurrentWindow(self):
        return(self.numDataEntriesInCurrentWindow)
    # End - GetNumValuesInCurrentWindow(self)

# End - class TDFFileReader








################################################################################
# A public procedure.
################################################################################
def TDF_GetVariableType(valueName):
    if (VARIABLE_START_OFFSET_MARKER in valueName):
        valueName = valueName.split(VARIABLE_START_OFFSET_MARKER, 1)[0]
        #print("Clipped name. valueName = " + valueName)

    # Get information about the lab.
    try:
        labInfo = g_LabValueInfo[valueName]
    except:
        print("Error! TDF_GetVariableType found undefined lab name: " + valueName)
        return(TDF_DATA_TYPE_UNKNOWN)

    dataType = labInfo['dataType']
    return(dataType)
# End - TDF_GetVariableType




################################################################################
# A public procedure.
################################################################################
def TDF_GetMinMaxValuesForVariable(valueName):
    #print("TDF_GetMinMaxValuesForVariable. valueName = " + valueName)
    if (VARIABLE_START_OFFSET_MARKER in valueName):
        valueName = valueName.split(VARIABLE_START_OFFSET_MARKER, 1)[0]
        #print("Clipped name. valueName = " + valueName)

    # Get information about the lab.
    try:
        labInfo = g_LabValueInfo[valueName]
    except:
        print("Error! TDF_GetMinMaxValuesForVariable found undefined lab name: " + valueName)
        return -1,-1

    labMinVal = float(labInfo['minVal'])
    labMaxVal = float(labInfo['maxVal'])
    return labMinVal, labMaxVal
# End - TDF_GetMinMaxValuesForVariable




################################################################################
# A public procedure.
################################################################################
def TDF_GetNumClassesForVariable(valueName):
    #print("TDF_GetNumClassesForVariable. valueName = " + valueName)
    if (VARIABLE_START_OFFSET_MARKER in valueName):
        valueName = valueName.split(VARIABLE_START_OFFSET_MARKER, 1)[0]
        #print("Clipped name. valueName = " + valueName)

    # Get information about the lab.
    try:
        labInfo = g_LabValueInfo[valueName]
    except:
        print("Error! TDF_GetNumClassesForVariable found undefined lab name: " + valueName)
        return(1)

    if (labInfo['dataType'] == TDF_DATA_TYPE_BOOL):
        numVals = 2
    elif (labInfo['dataType'] == TDF_DATA_TYPE_FUTURE_EVENT_CLASS):
        return(TDF_NUM_CATEGORIES_IN_FUTURE_VAL)
    else:
        numVals = 1

    return(numVals)
# End - TDF_GetNumClassesForVariable




################################################################################
#
# [TDF_NormalizeLabValue]
#
# dataTypeName has values:
#   "NormFraction" 
#   "NormInt0-100"
################################################################################
def TDF_NormalizeLabValue(labValue, minVal, maxVal, dataTypeName):
    #print("TDF_NormalizeLabValue. labValue=" + str(labValue))
    #print("TDF_NormalizeLabValue. minVal=" + str(minVal))
    #print("TDF_NormalizeLabValue. maxVal=" + str(maxVal))

    # Clip the value to within the min and max.
    # Some patients can have *really* odd values, like a patient who refuses 
    # transfusion can have a Hgb around 3.0.
    if (labValue < float(minVal)):
        labValue = float(minVal)
    if (labValue > float(maxVal)):
        labValue = float(maxVal)

    # Normalize the value to a number between 0..1 for where this
    # value lands in the range of possible values.
    range = float(maxVal) - float(minVal)
    #print("NormalizeLabValueImpl. range=" + str(range))

    offset = float(labValue) - float(minVal)
    #print("NormalizeLabValueImpl. offset=" + str(offset))

    if (range > 0):
        normalFloatValue = float(offset /  range)
    else:
        normalFloatValue = 0.0

    if (dataTypeName == "NormInt0-100"):
        resultVal = int(round(normalFloatValue))
    elif (dataTypeName == "NormFraction"):
        resultVal = round(normalFloatValue, 2)
    else:
        resultVal = round(normalFloatValue, 2)

    #print("TDF_NormalizeLabValue. normalValue=" + str(normalValue))
    return(resultVal)
# End - TDF_NormalizeLabValue





################################################################################
#
# [TDF_ParseUserRequestDataString]
#
# A public procedure.
# This is used to parse the data passed in a HTTP request to a web server into
# a tensor of input values.
################################################################################
def TDF_ParseUserRequestDataString(inputNameListStr, userProvidedInputvalueStr):
    # Parse the input names into a list.
    # Leave the offsets on the names, as those offsets willremain on the name for both
    # the variables and the values.
    inputValueNameList = inputNameListStr.split(',')
    numValsInEachInputVector = len(inputValueNameList)      

    # Make a vector big enough to hold the labs.
    inputTensor = torch.zeros(1, 1, numValsInEachInputVector, requires_grad=True)

    # Parse the named data values into a list.
    # Leave the offsets on the names, as those offsets willremain on the name for both
    # the variables and the values.
    userProvidedInputValueList = userProvidedInputvalueStr.split(',')
    numUserProvidedInputValues = len(userProvidedInputValueList)      
    userProvidedInputNames = [" "] * numUserProvidedInputValues
    userProvidedInputData = [0] * numUserProvidedInputValues
    for valueIndex, valueStr in enumerate(userProvidedInputValueList):
        partsList = valueStr.split('=')
        userProvidedInputNames[valueIndex] = partsList[0]
        userProvidedInputData[valueIndex] = float(partsList[1])
        #print("userProvidedInputNames[n]=" + str(userProvidedInputNames[valueIndex]))
        #print("userProvidedInputData[n]=" + str(userProvidedInputData[valueIndex]))


    # Find the labs we are looking for.
    # This will leave offsets on the variables, like Cr[-3]. 
    # The userdata will also include these offsets, so we exactly match the entire string.
    foundAllInputs = True
    for nameIndex, nameStr in enumerate(inputValueNameList):
        foundCurrentValue = False
        for valueNameIndex, valueNameStr in enumerate(userProvidedInputNames):
            #print("Look for nameStr=" + str(nameStr))
            if (nameStr == valueNameStr):
                valueNameStem = valueNameStr
                if (VARIABLE_START_OFFSET_MARKER in valueNameStem):
                    valueNameStem = valueNameStem.split(VARIABLE_START_OFFSET_MARKER, 1)[0]
    
                # Get information about the lab.
                try:
                   labInfo = g_LabValueInfo[valueNameStem]
                except:
                    break

                labMinVal = float(labInfo['minVal'])
                labMaxVal = float(labInfo['maxVal'])
                dataTypeName = labInfo['dataType']
                #print("Found nameStr=" + str(nameStr))
                #print("Found nameStr labInfo=" + str(labInfo))

                # Normalize the lab value so all values range between 0.0 and 1.0
                normValue = TDF_NormalizeLabValue(userProvidedInputData[valueNameIndex], 
                                                    labMinVal, labMaxVal, dataTypeName)

                inputTensor[0][0][nameIndex] = normValue
                foundCurrentValue = True
                break
            # End - if (nameStr == valueNameStr):
        # End - for valueNameIndex, valueNameStr in enumerate(userProvidedInputNames):        

        if (not foundCurrentValue):
            TDF_Log("TDF_ParseUserRequestDataString. Failed to find " + nameStr)
            foundAllInputs = False
            break
    # End - for nameIndex, nameStr in enumerate(inputValueNameList):

    if (not foundAllInputs):
        return False, None

    # tensor.detach() creates a tensor that shares storage with tensor that does not require grad. It detaches
    inputTensor = inputTensor.detach()

    # The client expects that the returned tensors will be the exact size.
    # We have to return a full tensor, without any unused rows.
    # This will reallocate the working tensors.
    newInputTensor = inputTensor[:1,:1,:numValsInEachInputVector]

    return True, newInputTensor
# End - TDF_ParseUserRequestDataString





################################################################################
# A public procedure.
################################################################################
def TDF_GetFutureTimeHorizonForVariable(valueName):
    if (VARIABLE_START_OFFSET_MARKER in valueName):
        valueName = valueName.split(VARIABLE_START_OFFSET_MARKER, 1)[0]
        #print("Clipped name. valueName = " + valueName)

    # Get information about the lab.
    try:
        labInfo = g_LabValueInfo[valueName]
    except:
        print("Error! TDF_GetFutureTimeHorizonForVariable found undefined lab name: " + valueName)
        return(0)

    numFutureDaysNeeded = int(labInfo['numFutureDaysNeeded'])
    return(numFutureDaysNeeded)
# End - TDF_GetFutureTimeHorizonForVariable





################################################################################
# A public procedure to create the DataLoader
################################################################################
def TDF_CreateTDFFileReader(tdfFilePathName):
    reader = TDFFileReader(tdfFilePathName)
    return reader
# End - TDF_CreateTDFFileReader




################################################################################
# 
################################################################################
def TDF_CreateNewFileWriterEx(filePathName):
    try:
        os.remove(filePathName) 
    except:
        pass

    fileH = open(filePathName,"w+")

    writer = TDFFileWriter()
    writer.__SetFileOutputFileHandle__(fileH)

    return writer
# End - TDF_CreateNewFileWriterEx




################################################################################
# 
################################################################################
def TDF_CreateNewFileWriter(fileH):
    writer = TDFFileWriter()
    writer.__SetFileOutputFileHandle__(fileH)

    return writer
# End - TDF_CreateNewFileWriter





    # To read a TDF file, we typically iterate at several levels:
    #   For each partition in the file
    #       For each patient in the partition
    #           For each event window in the patient
    #               For each data entry in the current window
    #


