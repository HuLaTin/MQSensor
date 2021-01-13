import os
import pandas as pd
import random
from datetime import datetime
import sklearn
import numpy as np

output = os.path.join("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Python MQ", "eventsOutput")
expectedChange = float(.035)
windowSize = int(30)

sensorData = pd.read_csv(r"C:\Users\Hunter Tiner\Documents\MQSensor\R MQ\Data\Joulesv2_20201208_SL.csv")
trialTimes = pd.read_csv(r'C:\Users\Hunter Tiner\Documents\MQSensor\R MQ\Data\V2TrialTimes.csv')

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

# SensorData <- SensorData[!(is.na(SensorData$Time) | SensorData$Time==""), ]
# SensorData$Time <- as.POSIXct(SensorData$Time, origin="1970-01-01", tz="GMT")
# trialTimes$Time <- as.POSIXct(trialTimes$Time, origin="1970-01-01", tz="GMT")

# parameterdf <- data.frame(expected=NA, true=NA, False=NA, Total=NA)[0, ]


names = ("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")

for i in names:
    z = i
    eventName = (str(i), "ADC")
    i = eventName = "_".join(eventName)
    # SensorData["ADC_N"] <- as.data.frame(lapply(SensorData[i], normalize))
    # SensorData["Event"] <- NA
    # SensorData[1,"Change"] = 0