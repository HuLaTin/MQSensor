# Import libraries
import sys
import os.path
from os import path
from numpy.core.numeric import NaN
from numpy.lib.function_base import append
import pandas as pd
import random
from datetime import datetime, date
from sklearn.preprocessing import MinMaxScaler
from Python.util import genRandomBits, getNeighbors

# get current working directory
cwd = os.getcwd()

# Set output
outputDir = ('Python\\eventsOutput')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

# set today's date
today = date.today()
today = today.strftime("%Y%b%d")

genColNames = ["sensor", "range", "expectedChange", "True", "False", "bestScore", "bestBits"]
geneticScoring = ["0", "0", "0", "0", "0", "0", "0"]
geneticScoring = pd.DataFrame(geneticScoring).T
geneticScoring.columns = genColNames
genCSV = (outputDir, "mutation" ,today + '_geneticScore.csv')
genCSV = "\\".join(genCSV)

# so that we don't write over with a blank .CSV
# also creates one if it doesn't exist
if path.exists(genCSV) == False:
    geneticScoring.to_csv(genCSV, index=False)


# Our scaler for the min/max normalization
scaler=MinMaxScaler()

# creating a dataframe to store useful counts 
parameterdf = pd.DataFrame()
parameterlst = []

# initializing for use later
events = None

# location of datafiles, readings and times of known experiments
sensorData = pd.read_csv(r'Python\Data\ThruFeb02GasStream.csv')
trialTimes = pd.read_csv(r'Python\Data\TrialTimes-Joules.csv')

# renames chemicals in "trialTimes", adds a number at end for easier identification
for x in range(0, len(trialTimes)):
    chemName = (trialTimes.loc[x, "Chemical"], str(x+1))
    trialTimes.loc[x, "Chemical"] = "-".join(chemName)
    
# rename columns in "sensorData"
sensorData.columns = ("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Gas_ohms", "Humidity",
                          "Pressure_pa", "CPU_Load", "Throttled")

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

expectedEvents = len(trialTimes)

numBits = 10

bitMinValue = 0.1
bitMaxValue = .15
# bits = {0:0,1:0,2:0,3:0,4:0,5:1,6:0,7:0}
bits = genRandomBits(random, numBits)

# desired threshold of change that determines if events occured
expectedChange = float(.1)
windowSize = int(50)
score = 0

i = ("MQ2_ADC")

# this is a recursive funtion
getNeighbors(bitMinValue, bitMaxValue, bits, expectedEvents, scaler, expectedChange, windowSize, sensorData,
            trialTimes, i, pd,  datetime, genCSV)
