# Import libraries
import sys
import os
from numpy.core.numeric import NaN
from numpy.lib.function_base import append, average
import pandas as pd
import random
from datetime import datetime, date
from pandas.core.frame import DataFrame
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import statistics as stat
from Python.util import checkForOutliers, eventDetection, movingAvg, downsampleData

# get current working directory
cwd = os.getcwd()

# Set output
outputDir = ('Python\\eventsOutput')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

# set today's date
today = date.today()
today = today.strftime("%Y%b%d")

# Our scaler for the min/max normalization
scaler=MinMaxScaler()

#expectedChange = float(.06)
windowSize = int(50)

useMovingAvg = False

# creating a dataframe to store useful counts 
parameterdf = pd.DataFrame()
parameterlst = []

# initializing for use later
events = None
eventsTrim = None
sdThresh = 0

# location of datafiles, readings and times of known experiments
sensorData = pd.read_csv(r'Python\Data\20200601StriderGasStream.csv')
trialTimes = pd.read_csv(r'Python\Data\striderTrials.csv')

# always set random seed!
random.seed(datetime.now())

# renames chemicals in "trialTimes", adds a number at end for easier identification
for x in range(0, len(trialTimes)):
    chemName = (trialTimes.loc[x, "Chemical"], str(x+1))
    trialTimes.loc[x, "Chemical"] = "-".join(chemName)
    
sensorData.columns = ("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Humidity",  "Gas_ohms",
                          "Pressure_pa")

# sets our 'Time" columns to a datetime format
sensorData['Time'] = pd.to_datetime(sensorData['Time'], format='%Y-%m-%d %H:%M:%S.%f')
trialTimes['Time'] = pd.to_datetime(trialTimes['Time'], format='%Y-%m-%d %H:%M:%S.%f')

# sets range of times
startRange = sensorData.loc[0,'Time']
endRange = sensorData.loc[len(sensorData)-1, 'Time']

# inserts new column
trialTimes['withinRange'] = False

# compares times
for y in range(0, len(trialTimes)):
    if startRange < trialTimes.loc[y,'Time'] and trialTimes.loc[y,'Time'] < endRange:
        trialTimes.loc[y, 'withinRange'] = True

# removes data that occured outside our range        
trialTimes = trialTimes[trialTimes['withinRange'] == True]
trialTimes = trialTimes.drop(columns = 'withinRange')
trialTimes = trialTimes.reset_index(drop=True)

# creates a list of chemicals seen in "trialTimes"
chems = np.unique(trialTimes["Chemical"])

# need to troubleshoot
# if using this, include flag in output?
if useMovingAvg == True:
    sensorData = movingAvg(sensorData, stat)
    
    movAvgCSV = (outputDir, today + 'MovingAvg.csv')
    movAvgCSV = "\\".join(movAvgCSV)
    sensorData.to_csv(movAvgCSV)
    
    # This program is not designed to use this "smoothed" data
    sys.exit("A new file has been created!")
    
tDeltaCheck = sensorData.loc[:100,"Time"].astype(np.int64)
tDeltaList = []
for i in range(1, len(tDeltaCheck)):
  tDeltaList.insert(i, (tDeltaCheck[i] - tDeltaCheck[i-1]))
tDAvg = stat.mean(tDeltaList) / 1e9

print("Average timeDelta between readings - ", tDAvg, " seconds.")

if tDAvg <= 60:
    print("Readings taken less than a minute apart.")
    #remove alternate lines?

# creates list of columns that will be used as the "trigger" for determining events
names = ("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")
##################################################################################
#################################################################################
################################################################################
i = "MQ2"
#for average across '3' values use '2' due to indexing
sRun = 3
futureAvg = 1
expectedChange = .1
################################################################################
###############################################################################
##############################################################################

triggerSensor = i
eventName = (str(i), "ADC")
# .join works similar to paste function
i = eventName = "_".join(eventName)

# applying scaler to column "i" (sensor column)
sensorData["ADC_N"] = scaler.fit_transform(sensorData[[i]])

# creates new columns
# first value in "Change" is 0   
sensorData["sRun"] = 0
sensorData["sRun-Delta"] = 0
sensorData["futureAverage"] = 0
sensorData["Change"] = 0
sensorData["future-past"] = 0
sensorData["Event"] = None

# determines change between each timepoint of normalized data column
for z in range(sRun, len(sensorData)-futureAvg):
    #sensorData.loc[z, "Z-2"] = stat.mean(sensorData.loc[z-2:z, i])
    #sensorData.loc[z, "Z-1"] = stat.mean(sensorData.loc[z-1:z, i])
    
    sensorData.loc[z, "sRun"] = stat.mean(sensorData.loc[z-sRun:z-1, 'ADC_N'])
    sensorData.loc[z, "futureAverage"] = stat.mean(sensorData.loc[z:z+futureAvg, 'ADC_N'])
    sensorData.loc[z, "future-past"] = sensorData.loc[z, "futureAverage"] - sensorData.loc[z, "sRun"]
    #sensorData.loc[z, 'sRun-Delta'] = sensorData.loc[z, 'ADC_N'] - sensorData.loc[z, 'sRun']
    #sensorData.loc[z, 'Change'] = sensorData.loc[z, 'ADC_N'] - sensorData.loc[z-1, 'ADC_N']
    
# creation of empty dataframes containing these columns           
eventIndex = pd.DataFrame(columns=['start', 'end'])
timeIndex = pd.DataFrame(columns=['Time'])

# initialize counter and set starting values
subsetCounter = 0
# test without these lines of code?
eventIndex.loc[0,'start'] = 0
eventIndex.loc[0,'end'] = 0
sdThresh = 0

# finding events
######################
# do we need this -1??        
for z in range(2, len(sensorData)):
    # if change is greater than expectedChange / "Event" is True
    if sensorData.loc[z, "future-past"] >= expectedChange:
        sensorData.loc[z, "Event"] = "True"
        # checks to make sure we dont run out of the dataframe
        # store start/end times of events
        if z > 4 and z < (len(sensorData)-(windowSize - 5)):
            eventIndex.loc[subsetCounter, 'start'] = (z - 4)
            eventIndex.loc[subsetCounter, 'end'] = (z + (windowSize - 4))
            subsetCounter = (subsetCounter + 1)
            timeIndex.loc[subsetCounter - 1, 'Time'] = sensorData.loc[z - 1, 'Time' ]
    else:
        # otherwise "False"
        sensorData.loc[z,'Event'] = "False"
        

eventIndex["flag"] = 'False'
timeIndex["flag"] = 'False'
z = 0
while(True):
#for z in range(len(eventIndex)-1):
    start = eventIndex.loc[z, 'start']
    end = eventIndex.loc[z, 'end']
    for x in range(z+1, len(eventIndex)):
        if eventIndex.loc[x, 'start'] > start and end < eventIndex.loc[x, 'end']:
            if eventIndex.loc[x, 'start'] - start <= windowSize:
                eventIndex.loc[x, "flag"] = 'True'
                timeIndex.loc[x, "flag"] = 'True'
                # need to remove event from timeIndex
    #print(eventIndex)
    eventIndex = eventIndex[eventIndex['flag'].str.contains('False')]
    timeIndex = timeIndex[timeIndex['flag'].str.contains('False')]
    eventIndex = eventIndex.reset_index(drop=True)
    timeIndex = timeIndex.reset_index(drop=True)

    if z == len(eventIndex)-1:
        break
    z = z + 1

eventNumber = 1
# initialize dataframe
# stores columns between rows where an event was determined to have occured
eventsCaptured = sensorData.iloc[eventIndex.loc[0,'start']:eventIndex.loc[0,'end'],0:12]

# infinite loop
# continues appending data of captured events
while 1:
    dataToAppend = sensorData.iloc[eventIndex.loc[eventNumber,'start']:eventIndex.loc[eventNumber,'end'],0:12]
    eventsCaptured = eventsCaptured.append(dataToAppend)
    
    if eventNumber == len(eventIndex)-1:
        break
    eventNumber = eventNumber + 1

# reset index of rows
eventsCaptured = eventsCaptured.reset_index(drop=True)
#####################################
# check if we can normalize all columns?
#####################################

# new empty dataframes
eventTemp = pd.DataFrame()
events = pd.DataFrame()

# determines number of total events
numEvents = int(len(eventsCaptured)/windowSize)

# breaks down "eventsCaptured" into each event
# using melt function
for eventNum in range(1, numEvents + 1):
    eventStart = (windowSize * (eventNum - 1))
    eventStop = (windowSize * eventNum)
    eventTemp = pd.DataFrame(eventsCaptured.iloc[eventStart:eventStop,:])    
    eventTemp.insert(0, "num", range(1, len(eventTemp)+1))
    eventTemp = pd.melt(eventTemp, id_vars=['Time', 'num'])
    # TEST used in trying to determine outliers    
    sdThresh = len(eventTemp)*.25
    
    events = pd.concat([events, eventTemp.iloc[:,3]], axis=1)

# new empty column
events['name'] = None

# finds index of columns
c = eventTemp.columns.get_loc('variable')
d = eventTemp.columns.get_loc('num')

# used to rename columns so we can see time point/signal
for b in range(0, len(eventTemp)):
    var = eventTemp.iloc[b,c]
    num = eventTemp.iloc[b,d]
    eventLabel = (str(var),str(num))
    events.loc[b,"name"] = "_".join(eventLabel)
    
# names events with number
# seems redundant?
## CHECK THIS ( previously len()-1 )
for b in range(0, len(events.columns)-1):
    colLabel = (str("Event"), str(b+1))
    events.columns.values[b] = " ".join(colLabel)
# transpose/flips dataframe
events = events.T
# renames columns using values contained in 'name' row
events = events.rename(columns = events.loc['name',])
# drop that useless row!
events = events.drop(index = 'name')    

# set time format    
timeIndex['Time'] = pd.to_datetime(timeIndex['Time'], format='%Y-%m-%d %H:%M:%S.%f')

timeIndex['timeDiff'] = 0
events['ident'] = int(0)

events.insert(0,'timeStamp','')    
c = events.columns.get_loc("timeStamp")
    
for b in range(0, len(events)):
    eTime = (str(timeIndex.iloc[b,0]), "Event")        
    events.iloc[b,c] = " ".join(eTime)

events = events.reset_index(drop = True)

# set format for our time stamps
fmt = '%Y-%m-%d %H:%M:%S'
timeIndex['Time'] = timeIndex['Time'].astype('datetime64[s]')
# comparing timestamps
# if event occurs within 5 mins of our recorded trial, the event is labeled as recorded chemical
### Our recorded experiments would occur atleast an hour apart ###
for l in range(0, len(trialTimes)):
    for m in range(0, len(timeIndex)):
        tDelta = datetime.strptime(str(trialTimes.loc[l,'Time']),fmt) - datetime.strptime(str(timeIndex.loc[m, 'Time']),fmt)
        tDelta = tDelta.total_seconds()/60
        timeIndex.loc[m, 'timeDiff'] = tDelta
        if abs(timeIndex.loc[m, 'timeDiff']) <= 5:
            events.loc[m, 'timeStamp'] = trialTimes.loc[l, 'Chemical']
            events.loc[m, 'ident'] = 1
            break

events = events.rename(columns={"timeStamp" : "chemical"})

# subsets identified events into a new dataframe
eventsTrim = events[(events.ident == 1)]
events = events.drop(columns = 'ident')
eventsTrim = eventsTrim.drop(columns = 'ident')

#someone on stackoverflow said this was bad practice...
#assign(paste("Index", toString(z), sep = "_"), EventIndex)
#assign(paste("Captured", toString(z), sep = "_"), eventsCaptured)
#assign(paste("Times", toString(z), sep = "_"), TimeIndex)

# stores parameters for file naming
csvParameters = [str(today), str(triggerSensor), str(round(expectedChange,2)), str(windowSize)]

# saves events to .csv
# use .copy() otherwise it points to the list
eventName = csvParameters.copy()
eventName.append("Events.csv")
eventName = "_".join(eventName)
eventOutput = (outputDir, "events", eventName)
eventOutput = "\\".join(eventOutput)
events.to_csv(eventOutput,index=False)

# saves eventsTrim to .csv, if dataframe contains an event
balanceThis = None
if len(eventsTrim) > 0:
    eventTrimName = csvParameters.copy()
    eventTrimName.append("EventsTrim.csv")
    eventTrimName = "_".join(eventTrimName)
    eventOutput = (outputDir,"eventsTrim", eventTrimName)
    balanceThis = eventOutput = "\\".join(eventOutput)
    eventsTrim.to_csv(eventOutput,index=False)

# need to check row count here
# count of expected events
expectedEvents = len(trialTimes)
eventsTrue = len(eventsTrim)
eventsTotal = len(events)
eventsFalse = (eventsTotal - eventsTrue)
parameterlst = [triggerSensor, sRun, futureAvg, expectedChange, expectedEvents, eventsTrue, eventsFalse, eventsTotal]
parameterlst = pd.DataFrame([parameterlst])