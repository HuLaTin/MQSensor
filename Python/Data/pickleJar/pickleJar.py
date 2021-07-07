#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

import pickle
import pandas as pd
import os

# get current working directory
cwd = os.getcwd()

# Set output
outputDir = ('Python\\Data\\pickleJar\\')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

# location of datafiles, readings and times of known experiments
sensorData = pd.read_csv(r'Python\Data\thru2021July07StriderGas.csv')
trialTimes = pd.read_csv(r'Python\Data\striderTrials.csv')
events25 = pd.read_csv(r'Python\eventsOutput\events\2021Jul07_MQ2_0.1_5_20_Events.csv')
events50 = pd.read_csv(r'Python\eventsOutput\events\2021Jul07_MQ2_0.1_5_45_Events.csv')
events100 = pd.read_csv(r'Python\eventsOutput\events\2021Jul07_MQ2_0.1_5_95_Events.csv')



pickle.dump(sensorData, open( outputDir + "sensorData.p", "wb" ) )
pickle.dump(trialTimes, open( outputDir + "trialTimes.p", "wb" ) )
pickle.dump(events25, open( outputDir + "chemEvents25.p", "wb" ) )
pickle.dump(events50, open( outputDir + "chemEvents50.p", "wb" ) )
pickle.dump(events100, open( outputDir + "chemEvents100.p", "wb" ) )


# used to load pickled data
# sensorData = pickle.load( open( outputDir + "sensorData.p", "rb" ) )
# trialTimes = pickle.load( open( outputDir + "trialTimes.p", "rb" ) )

# sensorData.to_csv(outputDir + "pickledSensorData.csv",index=False)
# trialTimes.to_csv(outputDir + "pickledTrialTimes.csv",index=False)