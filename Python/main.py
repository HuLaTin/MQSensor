#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

# Import libraries
import os
from numpy.core.numeric import NaN
from numpy.lib.function_base import append, average
import pandas as pd
import random
from datetime import datetime, date
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import statistics as stat
from Python.util import eventDetection

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

# desired threshold of change that determines if events occured
sRun = 3
futureAvg = 1
expectedChange = .1

preWindow = 4
postWindow = 95

windowSize = preWindow + postWindow + 1

#normalize output?
normColumns = True
resample = False

useMovingAvg = False

# creating a dataframe to store useful counts 
parameterdf = pd.DataFrame()
parameterlst = []

# initializing for use later
events = None
eventsTrim = None
sdThresh = 0

# location of datafiles, readings and times of known experiments
sensorData = pd.read_csv(r'Python\Data\thru2021June17StriderGas.csv')
trialTimes = pd.read_csv(r'Python\Data\striderTrials.csv')

# pickleJar import
# sensorData = pd.read_csv(r'Python\Data\pickleJar\sensorData.csv)
# trialTimes = pd.read_csv(r'Python\Data\pickleJar\trialTimes.csv')

# always set random seed!
random.seed(datetime.now())

# renames chemicals in "trialTimes", adds a number at end for easier identification
for x in range(0, len(trialTimes)):
    chemName = (trialTimes.loc[x, "Chemical"], str(x+1))
    trialTimes.loc[x, "Chemical"] = "-".join(chemName)
    
# rename columns in "sensorData"
if len(sensorData.columns) == 15:
    sensorData.columns = ("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Gas_ohms", "Humidity",
                          "Pressure_pa", "CPU_Load", "Throttled")
    
    del sensorData['CPU_Load']
    del sensorData['Throttled']
else:
    sensorData.columns = ("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Humidity",  "Gas_ohms",
                          "Pressure_pa")
    
sensorData = sensorData[["Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Humidity",  "Gas_ohms",
                          "Pressure_pa"]]


# for dropping rows that contain no time stamp
# not currently being used
########################################################################################
# sensorData['Time'].replace('', np.nan, inplace=True)
# sensorData.dropna(subset=['Time'], inplace=True)
# sensorData = sensorData.reset_index(drop=True)
#######################################################################################

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
    
tDeltaCheck = sensorData.loc[:100,"Time"].astype(np.int64)
tDeltaList = []
for i in range(1, len(tDeltaCheck)):
  tDeltaList.insert(i, (tDeltaCheck[i] - tDeltaCheck[i-1]))
tDAvg = stat.mean(tDeltaList) / 1e9

print('\n')
print("Average timeDelta between readings - ", tDAvg, " seconds.")
print('\n')

if resample == True:
    if tDAvg <= 60:
        print("Readings taken less than a minute apart.")
        sensorData = sensorData.iloc[::2].reset_index(drop = True)
        #sensorData.iloc[1::2]
    

# creates list of columns that will be used as the "trigger" for determining events
#names = ("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")
names = ("MQ2",)


# uses function on each signal
################## CHECK INDEXING #############################
for i in names:
    #input and output for function
    events, eventsTrim, parameterlst, sdThresh, balanceThis, triggerSensor \
        = eventDetection(today, scaler, stat, normColumns, sRun, futureAvg, expectedChange, preWindow, postWindow, windowSize, sensorData,
                   trialTimes, outputDir, i, pd, NaN, datetime)
        
    # this checks for outliers, doesn't change data only output to console. (it should anyways...)
    #outliers, = checkForOutliers(chems, eventsTrim, math, pd, stat, sdThresh)
        
    parameterdf = parameterdf.append(parameterlst)

parameterdf.columns = ['triggerSensor', 'sRun', 'futureAvg', 'Threshold', 'Expected', 'True', 'False', 'Total']
paraCSV = (outputDir, "parameters",today + '_Parameters.csv')
paraCSV = "\\".join(paraCSV)
parameterdf.to_csv(paraCSV,index=False)