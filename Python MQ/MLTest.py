import os
from numpy.core.numeric import NaN
from numpy.lib.function_base import append
import pandas as pd
import random
from datetime import datetime
from pandas.core.frame import DataFrame
from sklearn.preprocessing import MinMaxScaler
import numpy as np

scaler=MinMaxScaler()

#output = os.path.join("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Python MQ", "eventsOutput")
expectedChange = float(.2)
windowSize = int(50)

sensorData = pd.read_csv(r"C:\Users\Hunter Tiner\Documents\MQSensor\R MQ\Data\Joulesv2_20201208_SL.csv")
trialTimes = pd.read_csv(r'C:\Users\Hunter Tiner\Documents\MQSensor\R MQ\Data\V2TrialTimes.csv')

#print(sensorData.describe())

expectedEvents = len(trialTimes)-1

random.seed(datetime.now())

chems = np.unique(trialTimes["Chemical"])

for x in range(0, len(trialTimes)):
    chemName = (trialTimes.loc[x, "Chemical"], str(x+1))
    trialTimes.loc[x, "Chemical"] = "-".join(chemName)
        
sensorData.columns = ("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Gas_ohms", "Humidity",
                          "Pressure_pa", "CPU_Load", "Throttled")

del sensorData['CPU_Load']
del sensorData['Throttled']

########################################################################################
#sensorData['Time'].replace('', np.nan, inplace=True)
#sensorData.dropna(subset=['Time'], inplace=True)
#sensorData.reset_index(drop=True)
#####################################################################################

sensorData['Time'] = pd.to_datetime(sensorData['Time'], format='%Y-%m-%d %H:%M:%S.%f')
trialTimes['Time'] = pd.to_datetime(trialTimes['Time'], format='%Y-%m-%d %H:%M:%S.%f')

# parameterdf <- data.frame(expected=NA, true=NA, False=NA, Total=NA)[0, ]

names = ("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")
#eventsCaptured = pd.DataFrame()

for i in names:
    z = i
    eventName = (str(i), "ADC")
    i = eventName = "_".join(eventName)
    
    sensorData["ADC_N"] = scaler.fit_transform(sensorData[[i]])
    
    sensorData.loc[0, "Change"] = 0
    sensorData['Event'] = None
    
    #do we need this -1??
    for z in range(1, len(sensorData)-1):
        sensorData.loc[z, "Change"] = sensorData.loc[z, "ADC_N"] - sensorData.loc[z-1, "ADC_N"]
                
    eventIndex = pd.DataFrame(columns=['start', 'end'])
    timeIndex = pd.DataFrame(columns=['Time'])
    subsetCounter = 0
    eventIndex.loc[0,'start'] = 0
    eventIndex.loc[0,'end'] = 0
    
    #do we need this -1??        
    for z in range(0, len(sensorData)-1):
        if sensorData.loc[z, "Change"] > expectedChange:
            sensorData.loc[z, "Event"] = "True"
            if z > 4 and z < (len(sensorData)-(windowSize - 5)):
                eventIndex.loc[subsetCounter, 'start'] = (z - 4)
                eventIndex.loc[subsetCounter, 'end'] = (z + (windowSize - 4))
                subsetCounter = (subsetCounter + 1)
                timeIndex.loc[subsetCounter - 1, 'Time'] = sensorData.loc[z - 1, 'Time' ]
        else:
            sensorData.loc[z,'Event'] = "False"
    
    eventNumber = 1
    eventsCaptured = sensorData.iloc[eventIndex.loc[0,'start']:eventIndex.loc[0,'end'],0:12]
    
    while 1:
        dataToAppend = sensorData.iloc[eventIndex.loc[eventNumber,'start']:eventIndex.loc[eventNumber,'end'],0:12]
        eventsCaptured = eventsCaptured.append(dataToAppend)
        
        if eventNumber == len(eventIndex)-1:
            break
        eventNumber = eventNumber + 1

    eventsCaptured.reset_index(drop=True)
    #####################################

    #####################################
    eventTemp = pd.DataFrame()
    events = pd.DataFrame()
    numEvents = int(len(eventsCaptured)/windowSize)

    for eventNum in range(1, numEvents + 1):
        eventStart = (windowSize * (eventNum - 1))
        eventStop = (windowSize * eventNum)
        eventTemp = pd.DataFrame(eventsCaptured.iloc[eventStart:eventStop,:])    
        eventTemp.insert(0, "num", range(1, len(eventTemp)+1))
        #eventTemp.reset_index(drop=True)
        eventTemp = pd.melt(eventTemp, id_vars=['Time', 'num'])    
        sdThresh = len(eventTemp)*.25
        
        events = pd.concat([events, eventTemp.iloc[:,3]], axis=1)

    events['name'] = None
    
    for b in range(0, len(eventTemp)):
        var = eventTemp.iloc[b,2]
        num = eventTemp.iloc[b,1]
        eventLabel = (str(var),str(num))
        events.loc[b,"name"] = "_".join(eventLabel)
        
    events.set_index('name')
    
    for b in range(0, len(events.columns)-1):
        colLabel = (str("Event"), str(b+1))
        events.columns.values[b] = " ".join(colLabel)
        
    events = events.set_index('name').T
    
    break


