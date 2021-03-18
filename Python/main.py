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

# desired threshold of change that determines if events occured
expectedChange = float(.06)
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
sensorData = pd.read_csv(r'Python\Data\thru2021March15JoulesGas.csv')
trialTimes = pd.read_csv(r'Python\Data\TrialTimes-Joules.csv')

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
sensorData.columns = ("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Gas_ohms", "Humidity",
                          "Pressure_pa", "CPU_Load", "Throttled")

# drops two columns that aren't useful in this application
del sensorData['CPU_Load']
del sensorData['Throttled']

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

# need to troubleshoot
# if using this, include flag in output?
if useMovingAvg == True:
    sensorData = movingAvg(sensorData, stat)
    
    movAvgCSV = (outputDir, today + 'MovingAvg.csv')
    movAvgCSV = "\\".join(movAvgCSV)
    sensorData.to_csv(movAvgCSV)
    
    # This program is not designed to use this "smoothed" data
    sys.exit("A new file has been created!")
    

# creates list of columns that will be used as the "trigger" for determining events
names = ("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")

# uses function on each signal
################## CHECK INDEXING #############################
for i in names:
    #input and output for function
    events, eventsTrim, parameterlst, sdThresh, balanceThis, triggerSensor \
        = eventDetection(today, scaler, expectedChange, windowSize, sensorData,
                   trialTimes, outputDir, i, pd, NaN, datetime)
        
    # this checks for outliers, doesn't change data only output to console. (it should anyways...)
    #outliers, = checkForOutliers(chems, eventsTrim, math, pd, stat, sdThresh)
    
    #downsampleData(cwd, pd, today, outputDir, balanceThis, triggerSensor)
    
    parameterdf = parameterdf.append(parameterlst)
    #break
            
    # If statement
    # Hyperparameterization

parameterdf.columns = ['triggerSensor','Threshold', 'Expected', 'True', 'False', 'Total']
paraCSV = (outputDir, "parameters",today + '_Parameters.csv')
paraCSV = "\\".join(paraCSV)
parameterdf.to_csv(paraCSV,index=False)