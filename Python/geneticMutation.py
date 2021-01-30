# Import libraries
import sys
import os
from numpy.core.numeric import NaN
from numpy.lib.function_base import append
import pandas as pd
import random
from datetime import datetime, date
from sklearn.preprocessing import MinMaxScaler
from Python.util import geneticMutateScore, genRandomBits, getNeighbors, getValueOfBits

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

bitMinValue = 0.05
bitMaxValue = .5


# desired threshold of change that determines if events occured
expectedChange = float(.1)
windowSize = int(50)

score = 0
numBits = 10

# creating a dataframe to store useful counts 
parameterdf = pd.DataFrame()
parameterlst = []

# initializing for use later
events = None

# location of datafiles, readings and times of known experiments
sensorData = pd.read_csv(r'Python\Data\Joulesv2_20201208_SL.csv')
trialTimes = pd.read_csv(r'Python\Data\V2TrialTimes.csv')

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

bits = genRandomBits(random, numBits)
# bits = {0:0,1:0,2:0,3:0,4:0,5:1,6:0,7:0}
#################################################################

names = ("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")

for i in names:
    # parameterlst, score = geneticMutateScore(expectedEvents, scaler, expectedChange, windowSize, sensorData,
    #                trialTimes, i, pd,  datetime)
    
    parameterlst = getNeighbors(bitMinValue, bitMaxValue, bits, expectedEvents, scaler, expectedChange, windowSize, sensorData,
                trialTimes, i, pd,  datetime)
    
    #parameterdf = parameterdf.append(parameterlst)
    
    break
    

parameterdf.columns = ['triggerSensor','Threshold', 'Expected', 'True', 'False', 'Score']
paraCSV = (outputDir, today + 'score.csv')
paraCSV = "\\".join(paraCSV)
parameterdf.to_csv(paraCSV,index=False)
