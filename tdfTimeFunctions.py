#####################################################################################
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
#####################################################################################
#
# Time-Based Derived Values - Make derived values from existing values across time
#
# Each of these is a state-ful object that takes a time ordered sequence of input
# values and outputs a computed value.
# It ASSUMES inputs are passed in in increasing time order, so pass in the values 
# at time t-1 before time t.
#
# The functions are identified by Case-INsensitive names:
#
# "delta" - Returns a float, the delta between current and most recent previous value
# It also allows you to specify how long a timespan to use for the rate:
#       delta - the current value and the most recent previous value
#       delta3 - the current value and a previous value from 3 days before
#       delta7 - the current value and a previous value from 7 days before
#       delta14 - the current value and a previous value from 14 days before
#       delta30 - the current value and a previous value from 30 days before
#       delta60 - the current value and a previous value from 60 days before
#       delta90 - the current value and a previous value from 90 days before
#       delta180 - the current value and a previous value from 180 days before
#
# "rate" - Returns a float, the rate over time between current and most recent previous value. 
# This is "delta" divided by the number of days between the two values.
# It also allows you to specify how long a timespan to use for the rate:
#       rate - the current value and the most recent previous value
#       rate3 - the current value and a previous value from 3 days before
#       rate7 - the current value and a previous value from 7 days before
#       rate14 - the current value and a previous value from 14 days before
#       rate30 - the current value and a previous value from 30 days before
#       rate60 - the current value and a previous value from 60 days before
#       rate90 - the current value and a previous value from 90 days before
#       rate180 - the current value and a previous value from 180 days before
#
# "accel" - Returns a float, the accelleration over time across the current and 2 most recent 
# previous values. This is "rate" divided by the number of days between the two values.
# It also allows you to specify how long a timespan to use for the accelleration:
#       accel - the current value and the most recent previous value
#       accel3 - the current value and a previous value from 3 days before
#       accel7 - the current value and a previous value from 7 days before
#       accel14 - the current value and a previous value from 14 days before
#       accel30 - the current value and a previous value from 30 days before
#       accel60 - the current value and a previous value from 60 days before
#       accel90 - the current value and a previous value from 90 days before
#       accel180 - the current value and a previous value from 180 days before
#
# "percentchange" - Returns a float, the relative change between current and most recent 
# previous value. This is ((newVal - oldValue) / oldValue)
# It also allows you to specify how long a timespan to use for the rate:
#       percentchange - the current value and the most recent previous value
#       percentchange7 - the current value and a previous value from 7 days before
#       percentchange14 - the current value and a previous value from 14 days before
#       percentchange30 - the current value and a previous value from 30 days before
#       percentchange60 - the current value and a previous value from 60 days before
#       percentchange90 - the current value and a previous value from 90 days before
#       percentchange180 - the current value and a previous value from 180 days before
#
# "isstable" - Returns a boolean that describes whether all values in the last time
# period have been within a range of 0.3
# It also allows you to specify how long a timespan to use
#       isstable - the current value and the most recent previous value
#       isstable7 - the current value and all previous values from the past 7 days
#       isstable14 - the current value and all previous values from the past 14 days
#       isstable30 - the current value and all previous values from the past 30 days
#       isstable60 - the current value and all previous values from the past 60 days
#       isstable90 - the current value and all previous values from the past 90 days
#       isstable180 - the current value and all previous values from the past 180 days
#
# "runavg" - Returns a float, the running average of all recent values within the past N days
#   By default N is 60    
#
# "bollup" - Returns a bool, whether the current value is >= the upper Bollinger band.
#   Bollinger band computed with all values in past N days. By default N is 60    
#
# "bolllow" - Returns a bool, whether the current value is <= the lower Bollinger band.
#   Bollinger band computed with all values in past N days. By default N is 60    
#
# "range" - Returns a float, the range between min and max recent values within the past N days
# It also allows you to specify how long a timespan to use
#       range - the current value and all previous values from the past 3 days
#       range7 - the current value and all previous values from the past 7 days
#       range14 - the current value and all previous values from the past 14 days
#       range30 - the current value and all previous values from the past 30 days
#       range60 - the current value and all previous values from the past 60 days
#       range90 - the current value and all previous values from the past 90 days
#       range180 - the current value and all previous values from the past 180 days
#
# "relrange" - Returns a float, the relative range between min and max recent values within the past N days
# This is similar to "percentchange", except it uses the min and max values of the time period, rather
# than the earliest and latest values. This is ((maxVal - minValue) / minValue)
# It also allows you to specify how long a timespan to use for the rate:
#       relrange - the current value and all previous values from the past 3 days
#       relrange7 - the current value and all previous values from the past 7 days
#       relrange14 - the current value and all previous values from the past 14 days
#       relrange30 - the current value and all previous values from the past 30 days
#       relrange60 - the current value and all previous values from the past 60 days
#       relrange90 - the current value and all previous values from the past 90 days
#       relrange180 - the current value and all previous values from the past 180 days
#
# "faster30than90" - Returns a Bool, the rate of change over the past 30 days is faster than
# that over the past 90 days.

################################################################################

from collections import deque
import statistics

import tdfTools as tdf


################################################################################
# This is used for computing Baselines
################################################################################
class CTimeSeries():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, maxHistoryInDays):
        self.ValueQueue = deque()

        self.maxHistoryInDays = maxHistoryInDays
        self.lowestValue = -1

        self.MostRecentValue = -1.0
        self.MostRecentDay = -1
        self.MostRecentHour = -1
        self.MostRecentMin = -1

        self.OldestDay = -1
        self.OldestHour = -1
        self.OldestMin = -1
    # End -  __init__



    #####################################################
    #
    # [CTimeSeries::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return
    # End of destructor



    #####################################################
    #
    # [CTimeSeries::AddNewValue]
    #
    #####################################################
    def AddNewValue(self, value, timeInDays, timeMin):
        fDebug = False
        if (fDebug):
            print("Inside AddNewValue")
        fNeedToFindLowestValue = False

        newQueueEntry = {'v': value, 'd': timeInDays, 'm': timeMin}
        self.ValueQueue.append(newQueueEntry)
        if (fDebug):
            print("AddNewValue. newQueueEntry = " + str(newQueueEntry))
            print("AddNewValue. self.ValueQueue = " + str(self.ValueQueue))

        self.MostRecentValue = round(float(value), 2)
        self.MostRecentDay = timeInDays
        self.MostRecentMin = timeMin

        if ((self.lowestValue == -1) or (value < self.lowestValue)):
            self.lowestValue = value

        if ((self.OldestDay == -1) and (self.OldestMin == -1)):
            self.OldestDay = timeInDays
            self.OldestMin = timeMin
        else:
            deltaDays = timeInDays - self.OldestDay
            while (deltaDays > self.maxHistoryInDays):
                removedValue = self.ValueQueue[0]
                self.ValueQueue.popleft()

                if (fDebug):
                    print("AddNewValue. Trim Queue. removedValue = " + str(removedValue))
                    print("AddNewValue. Trim Queue. self.ValueQueue = " + str(self.ValueQueue))

                # If we removed the smallest value, then we need to search through
                # the list for a new smallest value
                if (round(removedValue['v'], 2) == round(self.lowestValue, 2)):
                    fNeedToFindLowestValue = True

                oldestValue = self.ValueQueue[0]
                self.OldestDay = oldestValue['d']
                self.OldestHour = oldestValue['h']
                self.OldestMin = oldestValue['m']

                deltaDays = timeInDays - self.OldestDay
            # End - while (deltaDays > self.maxHistoryInDays):

            if (fNeedToFindLowestValue):
                if (fDebug):
                    print("AddNewValue. fNeedToFindLowestValue = " + str(fNeedToFindLowestValue))
                # iterate over the deque's elements
                self.lowestValue = -1
                for elem in self.ValueQueue:
                    currentVal = round(elem['v'], 2)
                    if (fDebug):
                        print("AddNewValue. currentVal = " + str(currentVal))
                    if ((self.lowestValue == -1) or (currentVal < self.lowestValue)):
                        self.lowestValue = currentVal
                # End - for elem in self.ValueQueue:
            # End - if (fNeedToFindLowestValue):
        # else               
    # End of AddNewValue



    #####################################################
    #
    # [CTimeSeries::GetLowestValue]
    #
    #####################################################
    def GetLowestValue(self):
        fDebug = False
        if (fDebug):
            print("GetLowestValue MostRecentValue = " + str(self.MostRecentValue) 
                + ", self.lowestValue = " + str(self.lowestValue))

        if (self.MostRecentValue == -1):
            return None

        return self.lowestValue
    # End of GetLowestValue



    #####################################################
    #
    # [CTimeSeries::ValueHasIncreased]
    #
    #####################################################
    def ValueHasIncreased(self, deltaValue):
        fDebug = False
        if (fDebug):
            print("ValueHasIncreased MostRecentValue = " + str(self.MostRecentValue) 
                + ", deltaValue = " + str(deltaValue) 
                + ", self.lowestValue = " + str(self.lowestValue))

        if (self.MostRecentValue == -1):
            return False

        if (fDebug):
            print("ValueHasIncreased self.lowestValue + deltaValue = " + str(self.lowestValue + deltaValue))
        if (self.MostRecentValue >= round((self.lowestValue + deltaValue), 2)):
            return True

        return False
    # End of ValueHasIncreased

# End - class CTimeSeries








################################################################################
#
#
################################################################################
class CGenericTimeValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.CurrentValue = None
        self.PrevValue = None
    # End -  Reset


    #####################################################
    #
    # [CGenericTimeValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        newValInfo = {'v': value, 'd': dayNum, 'm': timeMin}
        self.PrevValue = self.CurrentValue
        self.CurrentValue = newValInfo
        if (self.PrevValue is None):
            return tdf.TDF_INVALID_VALUE

        deltaValue = newValInfo['v'] - self.PrevValue['v']
        deltaDays = newValInfo['d'] - self.PrevValue['d']
        if (deltaDays <= 0):
            return tdf.TDF_INVALID_VALUE

        rate = float(deltaValue / deltaDays)
        return rate
    # End of ComputeNewValue

# End - class CGenericTimeValue






################################################################################
#
#
################################################################################
class CAccelerationValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numDays):
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CAccelerationValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                self.ValueQueue.popleft()
                if (fDebug):
                    print("CAccelerationValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Compute the current rate. This will then be used to later
        # compute the accelleration.
        deltaValue = -1
        deltaDays = -1
        for entry in self.ValueQueue:
            if (fDebug):
                print("CAccelerationValue::ComputeNewValue. Examine entry=" + str(entry))
            currentDeltaValue = value - entry['v']
            if (currentDeltaValue < 0):
                currentDeltaValue = -currentDeltaValue

            if ((deltaValue == -1) or (currentDeltaValue > deltaValue)):
                deltaValue = currentDeltaValue
                deltaDays = dayNum - entry['d']
        # End - for elem in self.ValueQueue:

        # <> Use the full time span, even though the range may be in a subset
        newRate = 0.0
        if (len(self.ValueQueue) >= 1):
            deltaDays = dayNum - self.ValueQueue[0]['d']
            if (deltaDays > 0):
                newRate = float(deltaValue / deltaDays)
                if (newRate < 0):
                    newRate = -newRate
        # End - if (len(self.ValueQueue) >= 1):
        
        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin, 'r': newRate})
        if (fDebug):
            print("CAccelerationValue::ComputeNewValue. Value=" + str(value) + ", newRate=" + str(newRate))

        # A list with only 2 items cannot have an accelleration.
        if (len(self.ValueQueue) <= 2):
            return tdf.TDF_INVALID_VALUE    

        # Get the oldest and newest rates.
        # We are NOT looking for the min and max rates, but rather the rates at the
        # beginning and end of the sliding window. We are using increasing sizes in
        # the sliding window to moderate the effect of a big change in rate.
        deltaDays = dayNum - self.ValueQueue[0]['d']
        deltaRate = newRate - self.ValueQueue[0]['r'] 
        if (fDebug):
            print("CAccelerationValue::ComputeNewValue. deltaDays=" + str(deltaDays) + ", deltaRate=" + str(deltaRate))

        if (deltaDays <= 0):
            return tdf.TDF_INVALID_VALUE

        acceleration = float(deltaRate / deltaDays)
        if (acceleration < 0):
            acceleration = -acceleration

        return acceleration
    # End of ComputeNewValue

# End - class CAccelerationValue





################################################################################
#
#
################################################################################
class CDeltaValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numDays, varName):
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return

    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CDeltaValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        # Pop any values that are older than we need.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                self.ValueQueue.popleft()
                if (fDebug):
                    print("CDeltaValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (len(self.ValueQueue) > 2):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})
        if (fDebug):
            print("CDeltaValue::ComputeNewValue. self.ValueQueue=" + str(self.ValueQueue))
           
        # A list with only 1 items cannot have a delta
        if (len(self.ValueQueue) <= 1):
            return tdf.TDF_INVALID_VALUE    

        # Normally, this is an old entry, but it may also be the entry
        # we just added if the queue is just starting up.
        oldestEntry = self.ValueQueue[0]
        if (fDebug):
            print("CDeltaValue::ComputeNewValue. oldestEntry=" + str(oldestEntry))
            print("CDeltaValue::ComputeNewValue. (dayNum - oldestEntry['d'])=" + str((dayNum - oldestEntry['d'])))

        if ((dayNum - oldestEntry['d']) < 1):
            if (fDebug):
                print("CDeltaValue::ComputeNewValue. oldestEntry is still too young")
            return tdf.TDF_INVALID_VALUE

        deltaValue = float(value - oldestEntry['v'])
        if (fDebug):
            print("CDeltaValue::ComputeNewValue. deltaValue=" + str(deltaValue) + ", self.MaxDaysInQueue=" + str(self.MaxDaysInQueue))

        return deltaValue
    # End of ComputeNewValue

# End - class CDeltaValue






################################################################################
#
#
################################################################################
class CSum():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numDays, varName):
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.TotalValue = 0
    # End -  Reset


    #####################################################
    #
    # [CRunningAvgValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                self.TotalValue = self.TotalValue - self.ValueQueue[0]['v']
                self.ValueQueue.popleft()
                if (fDebug):
                    print("CRunningAvgValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})
        self.TotalValue += value
        if (fDebug):
            print("CRunningAvgValue::ComputeNewValue. self.ValueQueue=" + str(self.ValueQueue))

        if (len(self.ValueQueue) > 0):
            sumVal = float(self.TotalValue)
        else:
            sumVal = tdf.TDF_INVALID_VALUE

        if (fDebug):
            print("CRunningAvgValue::ComputeNewValue. sumVal=" + str(sumVal))

        return sumVal
    # End of ComputeNewValue

# End - class CSum







################################################################################
#
#
################################################################################
class CRunningAvgValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numDays):
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.TotalValue = 0
    # End -  Reset


    #####################################################
    #
    # [CRunningAvgValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                self.TotalValue = self.TotalValue - self.ValueQueue[0]['v']
                self.ValueQueue.popleft()
                if (fDebug):
                    print("CRunningAvgValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})
        self.TotalValue += value
        if (fDebug):
            print("CRunningAvgValue::ComputeNewValue. self.ValueQueue=" + str(self.ValueQueue))

        if (len(self.ValueQueue) > 0):
            avgValue = float(self.TotalValue / len(self.ValueQueue))
        else:
            avgValue = tdf.TDF_INVALID_VALUE

        if (fDebug):
            print("CRunningAvgValue::ComputeNewValue. avgValue=" + str(avgValue))

        return avgValue
    # End of ComputeNewValue

# End - class CRunningAvgValue








################################################################################
#
#
################################################################################
class CRateValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numDays):
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CRateValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                self.ValueQueue.popleft()
                if (fDebug):
                    print("CRateValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})
        if (fDebug):
            print("CRateValue::ComputeNewValue. self.ValueQueue=" + str(self.ValueQueue))

        # A list with only 1 item cannot have a range.
        if (len(self.ValueQueue) <= 1):
            return tdf.TDF_INVALID_VALUE    

        deltaValue = -1
        deltaDays = -1
        for entry in self.ValueQueue:
            if (fDebug):
                print("CRateValue::ComputeNewValue. Examine entry=" + str(entry))

            currentDeltaValue = value - entry['v']
            if (currentDeltaValue < 0):
                currentDeltaValue = -currentDeltaValue

            if ((deltaValue == -1) or (currentDeltaValue > deltaValue)):
                deltaValue = currentDeltaValue
                deltaDays = dayNum - entry['d']
        # End - for elem in self.ValueQueue:

        # <> Use the full time span, even though the range may be in a subset
        deltaDays = dayNum - self.ValueQueue[0]['d']

        if (deltaDays <= 0):
            return tdf.TDF_INVALID_VALUE

        rate = float(deltaValue / deltaDays)
        if (fDebug):
            print("CRateValue::ComputeNewValue. deltaDays=" + str(deltaDays))
            print("CRateValue::ComputeNewValue. rate=" + str(rate))

        return rate
    # End of ComputeNewValue

# End - class CRateValue









################################################################################
#
#
################################################################################
class CRateCrossValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, shortNumDays, longNumDays, varName):
        self.shortRate = CRateValue(shortNumDays)
        self.longRate = CRateValue(longNumDays)

        self.fDetectFasterRate = True
        self.fFuzzinessMargin = 1.1

        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.shortRate.Reset()
        self.longRate.Reset()
    # End -  Reset


    #####################################################
    #
    # [CRateCrossValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False
        if (fDebug):
            print("CRateCrossValue::ComputeNewValue. value=" + str(value))

        shortRateVal = self.shortRate.ComputeNewValue(value, dayNum, timeMin)
        longRateVal = self.longRate.ComputeNewValue(value, dayNum, timeMin)
        if ((shortRateVal == tdf.TDF_INVALID_VALUE) or (longRateVal == tdf.TDF_INVALID_VALUE)):
            return tdf.TDF_INVALID_VALUE

        if (fDebug):
            print("CRateCrossValue::ComputeNewValue. shortRateVal=" + str(shortRateVal))
            print("CRateCrossValue::ComputeNewValue. longRateVal=" + str(longRateVal))
            print("CRateCrossValue::ComputeNewValue. self.fFuzzinessMargin=" + str(self.fFuzzinessMargin))
            print("CRateCrossValue::ComputeNewValue. self.fFuzzinessMargin * longRateVal=" + str(self.fFuzzinessMargin * longRateVal))

        if ((self.fDetectFasterRate) and (shortRateVal >= (self.fFuzzinessMargin * longRateVal))):
            return(1)

        return(0)
    # End of ComputeNewValue

# End - class CRateCrossValue






################################################################################
#
#
################################################################################
class CBollingerValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, fUpperBollinger, numDays):
        self.fUpperBollinger = fUpperBollinger
        self.MaxDaysInQueue = numDays

        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.TotalValue = 0
    # End -  Reset


    #####################################################
    #
    # [CBollingerValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False
        if (fDebug):
            print("CBollingerValue::ComputeNewValue. value=" + str(value))

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                self.TotalValue = self.TotalValue - self.ValueQueue[0]['v']
                self.ValueQueue.popleft()
                if (fDebug):
                    print("CBollingerValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})
        self.TotalValue += value
        if (fDebug):
            print("CBollingerValue::ComputeNewValue. self.ValueQueue=" + str(self.ValueQueue))
            print("CBollingerValue::ComputeNewValue. self.TotalValue=" + str(self.TotalValue))

        numValues = len(self.ValueQueue)
        if (numValues < 2):
            return tdf.TDF_INVALID_VALUE
        avgValue = float(self.TotalValue / numValues)
        if (fDebug):
            print("CBollingerValue::ComputeNewValue. avgValue=" + str(avgValue))

        # Get the total of deviations, or the difference between each value and the mean
        listOfValues = [entry['v'] for entry in self.ValueQueue]
        listStdDev = statistics.stdev(listOfValues)
        if (self.fUpperBollinger):
            bandVal = avgValue + listStdDev
            result = (value >= bandVal)
        else:
            bandVal = avgValue - listStdDev
            result = (value <= bandVal)

        if (fDebug):
            print("CBollingerValue::ComputeNewValue. listOfValues=" + str(listOfValues))
            print("CBollingerValue::ComputeNewValue. listStdDev=" + str(listStdDev))
            print("CBollingerValue::ComputeNewValue. bandVal=" + str(bandVal))
            print("CBollingerValue::ComputeNewValue. result=" + str(result))

        return result
    # End of ComputeNewValue

# End - class CBollingerValue








################################################################################
#
#
################################################################################
class CRangeValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, fAbsolute, numDays):
        self.fAbsolute = fAbsolute
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End - __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.MaxValue = tdf.TDF_INVALID_VALUE
        self.MinValue = tdf.TDF_INVALID_VALUE
    # End -  Reset


    #####################################################
    #
    # [CRangeValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                if ((self.MinValue == self.ValueQueue[0]['v']) or (self.MaxValue == self.ValueQueue[0]['v'])):
                    self.MaxValue = tdf.TDF_INVALID_VALUE
                    self.MinValue = tdf.TDF_INVALID_VALUE

                self.ValueQueue.popleft()
                if (fDebug):
                    print("CRangeValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})

        if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (self.MinValue == tdf.TDF_INVALID_VALUE)):
            self.MinValue = tdf.TDF_INVALID_VALUE
            self.MaxValue = tdf.TDF_INVALID_VALUE

            for entry in self.ValueQueue:
                if (fDebug):
                    print("CRangeValue::ComputeNewValue. Examine entry=" + str(entry))

                if ((self.MinValue == tdf.TDF_INVALID_VALUE) or (entry['v'] <= self.MinValue)):
                    self.MinValue = entry['v']
                if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (entry['v'] >= self.MaxValue)):
                    self.MaxValue = entry['v']
            # End - for entry in self.ValueQueue:

            if (fDebug):
                print("CRangeValue::ComputeNewValue. End of recompute loop. MinValue=" + str(self.MinValue) 
                            + ", MaxValue=" + str(self.MaxValue))
        # End - if (fRecomputeMinMax):
        else:  # if (not fRecomputeMinMax):
            if ((self.MinValue == tdf.TDF_INVALID_VALUE) or (value <= self.MinValue)):
                self.MinValue = value
            if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (value >= self.MaxValue)):
                self.MaxValue = value

            if (fDebug):
                print("CRangeValue::ComputeNewValue. End of adding enw entry. MinValue=" + str(self.MinValue) 
                            + ", MaxValue=" + str(self.MaxValue))
        # End - if (not fRecomputeMinMax):

        if ((self.MinValue == tdf.TDF_INVALID_VALUE) 
                or (self.MaxValue == tdf.TDF_INVALID_VALUE)
                or (len(self.ValueQueue) <= 1)):
            if (fDebug):
                print("CRangeValue::ComputeNewValue. Small queue. Return Invalid")
            return tdf.TDF_INVALID_VALUE

        result = float(self.MaxValue - self.MinValue)
        if (fDebug):
            print("CRangeValue::ComputeNewValue. Computed value=" + str(result))

        if ((not self.fAbsolute) and (self.MinValue != 0)):
            if (self.MinValue == 0):
                result = 0
            else:
                result = float(result / self.MinValue)
            if (fDebug):
                print("CRangeValue::ComputeNewValue. Computed value=" + str(result))

        if (fDebug):
            print("CRangeValue::ComputeNewValue. result=" + str(result))

        return result
    # End of ComputeNewValue

# End - class CRangeValue




################################################################################
#
#
################################################################################
class CPercentChangeValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numDays):
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.lowestValue = tdf.TDF_INVALID_VALUE
    # End -  Reset


    #####################################################
    #
    # [CPercentChangeValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                if (self.lowestValue == self.ValueQueue[0]['v']):
                    self.lowestValue = tdf.TDF_INVALID_VALUE

                self.ValueQueue.popleft()
                if (fDebug):
                    print("CPercentChangeValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})
        if (fDebug):
            print("CPercentChangeValue::ComputeNewValue. self.ValueQueue=" + str(self.ValueQueue))

        # Find the lowest value in the queue.
        # This may not be the oldest, we may have initially decreased then risen again.
        if (self.lowestValue == tdf.TDF_INVALID_VALUE):
            for elem in self.ValueQueue:
                if (fDebug):
                    print("AddNewValue. Find lowest value. elem = " + str(elem))

                if ((self.lowestValue == tdf.TDF_INVALID_VALUE) or (elem['v'] < self.lowestValue)):
                    self.lowestValue = elem['v']
            # End - for elem in self.ValueQueue:
        # End - if (self.lowestValue == tdf.TDF_INVALID_VALUE):

        if ((self.lowestValue == tdf.TDF_INVALID_VALUE) or (len(self.ValueQueue) < 2)):
            return tdf.TDF_INVALID_VALUE

        if (self.lowestValue == 0):
            result = 0
        else:
            result = float((value - self.lowestValue) / self.lowestValue)
        if (fDebug):
            print("CPercentChangeValue::ComputeNewValue. result=" + str(result))

        return result
    # End of ComputeNewValue

# End - class CPercentChangeValue









################################################################################
#
#
################################################################################
class CThresholdValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, fAbove, thresholdVal, numDays):
        self.fAbove = fAbove
        self.thresholdVal = thresholdVal
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End - __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.MaxValue = tdf.TDF_INVALID_VALUE
        self.MinValue = tdf.TDF_INVALID_VALUE
    # End -  Reset


    #####################################################
    #
    # [CThresholdValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                if ((self.MinValue == self.ValueQueue[0]['v']) or (self.MaxValue == self.ValueQueue[0]['v'])):
                    self.MaxValue = tdf.TDF_INVALID_VALUE
                    self.MinValue = tdf.TDF_INVALID_VALUE

                self.ValueQueue.popleft()
                if (fDebug):
                    print("CThresholdValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})

        if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (self.MinValue == tdf.TDF_INVALID_VALUE)):
            self.MinValue = tdf.TDF_INVALID_VALUE
            self.MaxValue = tdf.TDF_INVALID_VALUE

            for entry in self.ValueQueue:
                if (fDebug):
                    print("CThresholdValue::ComputeNewValue. Examine entry=" + str(entry))

                if ((self.MinValue == tdf.TDF_INVALID_VALUE) or (entry['v'] <= self.MinValue)):
                    self.MinValue = entry['v']
                if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (entry['v'] >= self.MaxValue)):
                    self.MaxValue = entry['v']
            # End - for entry in self.ValueQueue:

            if (fDebug):
                print("CThresholdValue::ComputeNewValue. End of recompute loop. MinValue=" + str(self.MinValue) 
                            + ", MaxValue=" + str(self.MaxValue))
        # End - if (fRecomputeMinMax):
        else:  # if (not fRecomputeMinMax):
            if ((self.MinValue == tdf.TDF_INVALID_VALUE) or (value <= self.MinValue)):
                self.MinValue = value
            if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (value >= self.MaxValue)):
                self.MaxValue = value

            if (fDebug):
                print("CRangeValue::CThresholdValue. End of adding enw entry. MinValue=" + str(self.MinValue) 
                            + ", MaxValue=" + str(self.MaxValue))
        # End - if (not fRecomputeMinMax):


        if ((not self.fAbove) and (self.thresholdVal > 0) and (self.MaxValue <= self.thresholdVal)):
            if (fDebug):
                print("CThresholdValue::ComputeNewValue. result=True (1)")
            return 1

        if ((self.fAbove) and (self.thresholdVal > 0) and (self.MinValue >= self.thresholdVal)):
            if (fDebug):
                print("CThresholdValue::ComputeNewValue. result=True (2)")
            return 1


        if (fDebug):
            print("CThresholdValue::ComputeNewValue. result=False")
        return 0
    # End of ComputeNewValue

# End - class CThresholdValue










################################################################################
#
#
################################################################################
class CVolatilityValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numDays):
        self.MaxDaysInQueue = numDays
        self.Reset()
    # End - __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CVolatilityValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        fDebug = False

        if (fDebug):
            print("CVolatilityValue::ComputeNewValue. >>>>>>>>>")

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((dayNum - self.ValueQueue[0]['d']) > self.MaxDaysInQueue):
                #if ((self.MinValue == self.ValueQueue[0]['v']) or (self.MaxValue == self.ValueQueue[0]['v'])):
                self.ValueQueue.popleft()
                if (fDebug):
                    print("CVolatilityValue::ComputeNewValue. Popped. New self.ValueQueue=" + str(self.ValueQueue))
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 'd': dayNum, 'm': timeMin})

        totalChange = 0
        prevValue = tdf.TDF_INVALID_VALUE
        for entry in self.ValueQueue:
            if (fDebug):
                print("CThresholdValue::ComputeNewValue. Examine entry=" + str(entry))
            currentValue = entry['v']

            if (prevValue != tdf.TDF_INVALID_VALUE):
                currentChange = currentValue - prevValue
                if (currentChange < 0):
                    currentChange = -currentChange

                totalChange += currentChange
            # End - if (prevValue != tdf.TDF_INVALID_VALUE):

            prevValue = currentValue
        # End - for entry in self.ValueQueue:

        if (fDebug):
            print("CVolatilityValue::ComputeNewValue. totalChange=" + str(totalChange) + " <<<<<<<<<<<<<<<<<<<<<<<<<<")

        return totalChange
    # End of ComputeNewValue

# End - class CVolatilityValue









################################################################################
#
#
################################################################################
class CIsStableValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numDays, varName, threshold):
        self.RangeVar = CRangeValue(True, numDays)
        self.threshold = threshold

        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.RangeVar.Reset()
    # End -  Reset


    #####################################################
    #
    # [CIsStableValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, dayNum, timeMin):
        range = self.RangeVar.ComputeNewValue(value, dayNum, timeMin)
        if (range == tdf.TDF_INVALID_VALUE):
            return tdf.TDF_INVALID_VALUE

        if (range > self.threshold):
            return 0

        return 1
    # End of ComputeNewValue

# End - class CIsStableValue









#####################################################################################
#
#####################################################################################
def CreateTimeValueFunction(functionNameStr, varName):
    functionNameStr = functionNameStr.lower()
    ###############################################
    if (functionNameStr == "generic"):
        return CGenericTimeValue()

    ###############################################
    elif (functionNameStr == "delta"):
        return CDeltaValue(1, varName)
    elif (functionNameStr == "delta3"):
        return CDeltaValue(3, varName)
    elif (functionNameStr == "delta7"):
        return CDeltaValue(7, varName)
    elif (functionNameStr == "delta14"):
        return CDeltaValue(14, varName)
    elif (functionNameStr == "delta30"):
        return CDeltaValue(30, varName)
    elif (functionNameStr == "delta60"):
        return CDeltaValue(60, varName)
    elif (functionNameStr == "delta90"):
        return CDeltaValue(90, varName)
    elif (functionNameStr == "delta180"):
        return CDeltaValue(180, varName)

    ###############################################
    elif (functionNameStr == "sum"):
        return CSum(1, varName)
    elif (functionNameStr == "sum3"):
        return CSum(3, varName)
    elif (functionNameStr == "sum7"):
        return CSum(7, varName)
    elif (functionNameStr == "sum14"):
        return CSum(14, varName)
    elif (functionNameStr == "sum30"):
        return CSum(30, varName)
    elif (functionNameStr == "sum60"):
        return CSum(60, varName)
    elif (functionNameStr == "sum90"):
        return CSum(90, varName)
    elif (functionNameStr == "sum180"):
        return CSum(180, varName)

    ###############################################
    elif (functionNameStr == "rate"):
        return CRateValue(1)
    elif (functionNameStr == "rate3"):
        return CRateValue(3)
    elif (functionNameStr == "rate7"):
        return CRateValue(7)
    elif (functionNameStr == "rate14"):
        return CRateValue(14)
    elif (functionNameStr == "rate30"):
        return CRateValue(30)
    elif (functionNameStr == "rate60"):
        return CRateValue(60)
    elif (functionNameStr == "rate90"):
        return CRateValue(90)
    elif (functionNameStr == "rate180"):
        return CRateValue(180)

    ###############################################
    elif (functionNameStr == "accel"):
        return CAccelerationValue(2)
    elif (functionNameStr == "accel3"):
        return CAccelerationValue(3)
    elif (functionNameStr == "accel7"):
        return CAccelerationValue(7)
    elif (functionNameStr == "accel14"):
        return CAccelerationValue(14)
    elif (functionNameStr == "accel30"):
        return CAccelerationValue(30)
    elif (functionNameStr == "accel60"):
        return CAccelerationValue(60)
    elif (functionNameStr == "accel90"):
        return CAccelerationValue(90)
    elif (functionNameStr == "accel180"):
        return CAccelerationValue(180)

    ###############################################
    elif (functionNameStr == "range"):
        return CRangeValue(True, 1)
    elif (functionNameStr == "range3"):
        return CRangeValue(True, 3)
    elif (functionNameStr == "range7"):
        return CRangeValue(True, 7)
    elif (functionNameStr == "range14"):
        return CRangeValue(True, 14)
    elif (functionNameStr == "range30"):
        return CRangeValue(True, 30)
    elif (functionNameStr == "range60"):
        return CRangeValue(True, 60)
    elif (functionNameStr == "range90"):
        return CRangeValue(True, 90)
    elif (functionNameStr == "range180"):
        return CRangeValue(True, 180)

    ###############################################
    elif (functionNameStr == "relrange"):
        return CRangeValue(False, 1)
    elif (functionNameStr == "relrange3"):
        return CRangeValue(False, 3)
    elif (functionNameStr == "relrange7"):
        return CRangeValue(False, 7)
    elif (functionNameStr == "relrange14"):
        return CRangeValue(False, 14)
    elif (functionNameStr == "relrange30"):
        return CRangeValue(False, 30)
    elif (functionNameStr == "relrange60"):
        return CRangeValue(False, 60)
    elif (functionNameStr == "relrange90"):
        return CRangeValue(False, 90)
    elif (functionNameStr == "relrange180"):
        return CRangeValue(False, 180)

    ###############################################
    elif (functionNameStr == "percentchange"):
        return CPercentChangeValue(2)
    elif (functionNameStr == "percentchange3"):
        return CPercentChangeValue(3)
    elif (functionNameStr == "percentchange7"):
        return CPercentChangeValue(7)
    elif (functionNameStr == "percentchange14"):
        return CPercentChangeValue(14)
    elif (functionNameStr == "percentchange30"):
        return CPercentChangeValue(30)
    elif (functionNameStr == "percentchange60"):
        return CPercentChangeValue(60)
    elif (functionNameStr == "percentchange90"):
        return CPercentChangeValue(90)
    elif (functionNameStr == "percentchange180"):
        return CPercentChangeValue(180)

    ###############################################
    elif (functionNameStr == "isstable"):
        return CIsStableValue(3, varName, 0.3)
    elif (functionNameStr == "isstable7"):
        return CIsStableValue(7, varName, 0.3)
    elif (functionNameStr == "isstable14"):
        return CIsStableValue(14, varName, 0.3)
    elif (functionNameStr == "isstable30"):
        return CIsStableValue(30, varName, 0.3)
    elif (functionNameStr == "isstable60"):
        return CIsStableValue(60, varName, 0.3)
    elif (functionNameStr == "isstable90"):
        return CIsStableValue(90, varName, 0.3)
    elif (functionNameStr == "isstable180"):
        return CIsStableValue(180, varName, 0.3)

    ###############################################
    elif ((functionNameStr == "runavg") or (functionNameStr == "runnavg")):
        return CRunningAvgValue(60)
    elif ((functionNameStr == "runavg3") or (functionNameStr == "runnavg3")):
        return CRunningAvgValue(3)
    elif ((functionNameStr == "runavg7") or (functionNameStr == "runnavg7")):
        return CRunningAvgValue(7)
    elif ((functionNameStr == "runavg14") or (functionNameStr == "runnavg14")):
        return CRunningAvgValue(14)
    elif (functionNameStr == "runavg30"):
        return CRunningAvgValue(30)
    elif (functionNameStr == "runavg60"):
        return CRunningAvgValue(60)
    elif (functionNameStr == "runavg90"):
        return CRunningAvgValue(90)
    elif (functionNameStr == "runavg180"):
        return CRunningAvgValue(180)

    ###############################################
    elif (functionNameStr == "below45"):
        return CThresholdValue(False, 45, 60)
    elif (functionNameStr == "below45_3"):
        return CThresholdValue(False, 45, 3)
    elif (functionNameStr == "below45_7"):
        return CThresholdValue(False, 45, 7)
    elif (functionNameStr == "below45_14"):
        return CThresholdValue(False, 45, 14)
    elif (functionNameStr == "below45_30"):
        return CThresholdValue(False, 45, 30)
    elif (functionNameStr == "below45_60"):
        return CThresholdValue(False, 45, 60)
    elif (functionNameStr == "below45_90"):
        return CThresholdValue(False, 45, 90)
    elif (functionNameStr == "below45_180"):
        return CThresholdValue(False, 45, 180)

    ###############################################
    elif (functionNameStr == "above45"):
        return CThresholdValue(True, 45, 60)
    elif (functionNameStr == "above45_3"):
        return CThresholdValue(True, 45, 3)
    elif (functionNameStr == "above45_7"):
        return CThresholdValue(True, 45, 7)
    elif (functionNameStr == "above45_14"):
        return CThresholdValue(True, 45, 14)
    elif (functionNameStr == "above45_30"):
        return CThresholdValue(True, 45, 30)
    elif (functionNameStr == "above45_60"):
        return CThresholdValue(True, 45, 60)
    elif (functionNameStr == "above45_90"):
        return CThresholdValue(True, 45, 90)
    elif (functionNameStr == "above45_180"):
        return CThresholdValue(True, 45, 180)

    ###############################################
    elif (functionNameStr == "vol"):
        return CVolatilityValue(60)
    elif (functionNameStr == "vol3"):
        return CVolatilityValue(3)
    elif (functionNameStr == "vol7"):
        return CVolatilityValue(7)
    elif (functionNameStr == "vol14"):
        return CVolatilityValue(14)
    elif (functionNameStr == "vol30"):
        return CVolatilityValue(30)
    elif (functionNameStr == "vol60"):
        return CVolatilityValue(60)
    elif (functionNameStr == "vol90"):
        return CVolatilityValue(90)
    elif (functionNameStr == "vol180"):
        return CVolatilityValue(180)

    ###############################################
    elif (functionNameStr == "bollup"):
        return CBollingerValue(True, 60)

    ###############################################
    elif (functionNameStr == "bolllow"):
        return CBollingerValue(False, 60)

    ###############################################
    elif (functionNameStr == "faster30than90"):
        return CRateCrossValue(30, 90, varName)

    ###############################################
    else:
        print("CreateTimeValueFunction. Unrecognized func: " + functionNameStr)
        return None
# End - CreateTimeValueFunction



