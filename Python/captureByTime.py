#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

# Import libraries
import sys
import os
from numpy.core.numeric import False_, NaN
from numpy.lib.function_base import append
import pandas as pd
import random
from datetime import datetime, date
from pandas.core.frame import DataFrame
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import statistics as stat
import math
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

#Chemicals to ignore during downSampling
to_drop = ['Methyl Benzoate']

# Our scaler for the min/max normalization
scaler=MinMaxScaler()

timeIndex = pd.DataFrame(columns=['start', 'end'])

preWindow = int(4)
postWindow = int(46)
windowSize = preWindow + postWindow

# location of datafiles, readings and times of known experiments
# if importing from github - use pickleJar.py to extract the data for use here
sensorData = pd.read_csv(r'Python\Data\ThruFeb02GasStream.csv')
trialTimes = pd.read_csv(r'Python\Data\TrialTimes-Joules.csv')

# always set random seed!
random.seed(datetime.now())

# renames chemicals in "trialTimes", adds a number at end for easier identification
for x in range(0, len(trialTimes)):
    chemName = (trialTimes.loc[x, "Chemical"].strip(), str(x+1))
    trialTimes.loc[x, "Chemical"] = "-".join(chemName)
    
# rename columns in "sensorData"
sensorData.columns = ("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Gas_ohms", "Humidity",
                          "Pressure_pa", "CPU_Load", "Throttled")

# drops two columns that aren't useful in this application
del sensorData['CPU_Load']
del sensorData['Throttled']

# for dropping rows that contain no time stamp
diff = len(sensorData)
sensorData['Time'].replace('', np.nan, inplace=True)
sensorData.dropna(subset=['Time'], inplace=True)
sensorData = sensorData.reset_index(drop=True)
print(diff - len(sensorData))

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
len(trialTimes)
eventCounter = 0

fmt = '%Y-%m-%d %H:%M:%S'
trialTimes['Time'] = trialTimes['Time'].astype('datetime64[s]')
sensorData['Time'] = sensorData['Time'].astype('datetime64[s]')

for i in range(len(trialTimes)):
    for j in range(len(sensorData)):
        tDelta = datetime.strptime(str(trialTimes.loc[i,'Time']),fmt) - datetime.strptime(str(sensorData.loc[j,'Time']),fmt)
        tDelta = tDelta.total_seconds()/60
        if abs(tDelta) <= .75:
            eventCounter = eventCounter + 1
            trialTimes.loc[i,'Time']
            sensorData.loc[j,'Time']
            print(str(abs(eventCounter - len(trialTimes))) , " - events left to collect")
            timeIndex.loc[i,'start'] = j - preWindow
            timeIndex.loc[i,'end'] = j + postWindow

            
            break
        
eventNumber = 1
# initialize dataframe
# stores columns between rows where an event was determined to have occured
eventsCaptured = sensorData.iloc[timeIndex.loc[0,'start']:timeIndex.loc[0,'end'],0:12]

while 1:
        dataToAppend = sensorData.iloc[timeIndex.loc[eventNumber,'start']:timeIndex.loc[eventNumber,'end'],0:12]
        eventsCaptured = eventsCaptured.append(dataToAppend)
        
        if eventNumber == len(timeIndex)-1:
            break
        eventNumber = eventNumber + 1
        
eventsCaptured = eventsCaptured.reset_index(drop=True)

# new empty dataframes
eventTemp = pd.DataFrame()
events = pd.DataFrame()

# determines number of total events
numEvents = len(trialTimes)
windowSize = preWindow + postWindow

# breaks down "eventsCaptured" into each event
# using melt function
for eventNum in range(1, numEvents + 1):
    eventStart = (windowSize * (eventNum - 1))
    eventStop = (windowSize * eventNum)
    eventTemp = pd.DataFrame(eventsCaptured.iloc[eventStart:eventStop,:])    
    eventTemp.insert(0, "num", range(1, len(eventTemp)+1))
    eventTemp = pd.melt(eventTemp, id_vars=['Time', 'num'])
    # TEST used in trying to determine outliers    
    
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
for b in range(0, len(trialTimes)):
    colLabel = trialTimes.loc[b,'Chemical']
    events.columns.values[b] = colLabel
    
# transpose/flips dataframe
events = events.T
# renames columns using values contained in 'name' row
events = events.rename(columns = events.loc['name',])
# drop that useless row!
events = events.drop(index = 'name')

events = events.reset_index(drop=False)

events.rename(columns={ events.columns[0]: "chemical" }, inplace = True)

# removing a chemical downsampling will create problems
events = events[~events.chemical.str.contains('|'.join(to_drop))]

byTimeCSV = (outputDir, "captureByTime",today + '_captureByTime.csv')
byTimeCSV = "\\".join(byTimeCSV)
events.to_csv(byTimeCSV,index=False)

downsampleData(cwd, pd, today, outputDir, byTimeCSV, "Time")
