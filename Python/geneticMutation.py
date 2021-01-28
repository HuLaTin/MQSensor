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
expectedChange = float(.1)
windowSize = int(50)

# creating a dataframe to store useful counts 
parameterdf = pd.DataFrame()
parameterlst = []

# initializing for use later
events = None
eventsTrim = None

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

names = ("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")

#uses function on each signal
################## CHECK INDEXING #############################
for i in names:    
    triggerSensor = i
    eventName = (str(i), "ADC")
    # .join works similar to paste function
    i = eventName = "_".join(eventName)
    
    # applying scaler to column "i" (sensor column)
    sensorData["ADC_N"] = scaler.fit_transform(sensorData[[i]])
    
    # creates new columns
    # first value in "Change" is 0   
    sensorData.loc[0, "Change"] = 0
    sensorData['Event'] = None
    
    # determines change between each timepoint of normalized data column
    ######################
    # do we need this -1??
    for z in range(1, len(sensorData)-1):
        sensorData.loc[z, "Change"] = sensorData.loc[z, "ADC_N"] - sensorData.loc[z-1, "ADC_N"]
    
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
    for z in range(0, len(sensorData)-1):
        # if change is greater than expectedChange / "Event" is True
        if sensorData.loc[z, "Change"] > expectedChange:
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
        events = pd.concat([events, eventTemp.iloc[:,3]], axis=1)

    # new empty column
    events['name'] = None
    
    # finds index of columns
    c = eventTemp.columns.get_loc('variable')
    d = eventTemp.columns.get_loc('value')
    
    # used to rename columns so we can see time point/signal
    for b in range(0, len(eventTemp)):
        var = eventTemp.iloc[b,c]
        num = eventTemp.iloc[b,d]
        eventLabel = (str(var),str(num))
        events.loc[b,"name"] = "_".join(eventLabel)
        
    # names events with number
    # seems redundant?
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
    
    expectedEvents = len(trialTimes)
    eventsTrue = len(eventsTrim)
    eventsTotal = len(events)
    eventsFalse = (eventsTotal - eventsTrue)
    score = eventsTrue - eventsFalse
    parameterlst = [triggerSensor, expectedChange, expectedEvents, eventsTrue, eventsFalse, eventsTotal, score]
    parameterlst = pd.DataFrame([parameterlst])

    parameterdf = parameterdf.append(parameterlst)

parameterdf.columns = ['triggerSensor','Threshold', 'Expected', 'True', 'False', 'Total', 'Score']
paraCSV = (outputDir, today + 'score.csv')
paraCSV = "\\".join(paraCSV)
parameterdf.to_csv(paraCSV,index=False)
