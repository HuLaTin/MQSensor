#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

# Import libraries
import sys
import os
from numpy.core.numeric import NaN
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

# Our scaler for the min/max normalization
scaler=MinMaxScaler()

timeIndex = pd.DataFrame(columns=['start', 'end'])

preWindow = int(5)
postWindow = int(45)

# location of datafiles, readings and times of known experiments
# if importing from github - use pickleJar.py to extract the data for use here
sensorData = pd.read_csv(r'Python\Data\ThruFeb02GasStream.csv')
trialTimes = pd.read_csv(r'Python\Data\TrialTimes-Joules.csv')

# always set random seed!
random.seed(datetime.now())

# renames chemicals in "trialTimes", adds a number at end for easier identification
for x in range(0, len(trialTimes)):
    chemName = (trialTimes.loc[x, "Chemical"], str(x+1))
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
            print(str(abs(eventCounter - len(trialTimes))) , " - events let to collect")
            timeIndex.loc[i,'start'] = j - preWindow
            timeIndex.loc[i,'end'] = j + postWindow

            
            break



timeIndex


# for l in range(0, len(trialTimes)):
#     for m in range(0, len(timeIndex)):
#         tDelta = datetime.strptime(str(trialTimes.loc[l,'Time']),fmt) - datetime.strptime(str(timeIndex.loc[m, 'Time']),fmt)
#         tDelta = tDelta.total_seconds()/60
#         timeIndex.loc[m, 'timeDiff'] = tDelta
#         if abs(timeIndex.loc[m, 'timeDiff']) <= 5:
#             events.loc[m, 'timeStamp'] = trialTimes.loc[l, 'Chemical']
#             events.loc[m, 'ident'] = 1
#             break