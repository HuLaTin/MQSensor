#####################
###  HUNTER TINER ###
#####################

# Import libraries
import sys
# tells python interpreter to include this path when importing modules
#sys.path.append(r'C:\Users\Hunter Tiner\Documents\MQSensor\Python')
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
from Python.util import eventDetection, movingAvg

# set today's date
today = date.today()
today = today.strftime("%Y%b%d")

# Our scaler for the min/max normalization
scaler=MinMaxScaler()

# desired threshold of change that determines if events occured
expectedChange = float(.1)
windowSize = int(50)

useMovingAvg = False

# location of datafiles, readings and times of known experiments
sensorData = pd.read_csv(r'C:\Users\Hunter Tiner\Documents\MQSensor\R\Data\Joulesv2_20201208_SL.csv')
trialTimes = pd.read_csv(r'C:\Users\Hunter Tiner\Documents\MQSensor\R\Data\V2TrialTimes.csv')

# Set output
cwd = os.getcwd()
outputDir = ('Python\\eventsOutput')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

# always set random seed!
random.seed(datetime.now())

# creates a list of chemicals seen in "trialTimes"
chems = np.unique(trialTimes["Chemical"])

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

# need to troubleshoot
# if using this, include flag in output?
if useMovingAvg == True:
    sensorData = movingAvg(sensorData, stat)
    
    movAvgCSV = (outputDir, today + 'MovingAvg.csv')
    movAvgCSV = "\\".join(movAvgCSV)
    sensorData.to_csv(movAvgCSV)
    
# creating a dataframe to store useful counts 
parameterdf = pd.DataFrame()
parameterlst = []
events = None
eventsTrim = None

# creates list of columns that will be used as the "trigger" for determining events
names = ("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")

#uses function on each signal
################## CHECK INDEXING #############################
for i in names:
    #input and output for function
    events, eventsTrim, parameterlst, \
        = eventDetection(today, scaler, expectedChange, windowSize, sensorData,
                   trialTimes, outputDir, i, pd, NaN, datetime)
    
    parameterdf = parameterdf.append(parameterlst)
    
    break
    
    # If statement
    # Hyperparameterization

parameterdf.columns = ['Parameters', 'Expected', 'True', 'False', 'Total']
paraCSV = (outputDir, today + '_Parameters.csv')
paraCSV = "\\".join(paraCSV)
parameterdf.to_csv(paraCSV)

if len(eventsTrim) > 0:
    for y in chems:
        if len(eventsTrim[eventsTrim['chemical'].str.contains(y)]) > 0:
            trimTemp = eventsTrim[eventsTrim['chemical'].str.contains(y)]
            chemData = pd.DataFrame()
            deviData = pd.DataFrame()
            
            for x in range(1, len(trimTemp.columns)):
                chemData.loc[0, x] = stat.mean(trimTemp.iloc[:,x])
                
                
                ### Broken for loop
                # standard deviation
                #for w in range(0, len(trimTemp)):
                #    deviData.loc[w,x] = (trimTemp.loc[w,x] - chemData.loc[0,x])^2
                    
                ### insert math
                
deviData