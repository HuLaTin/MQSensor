#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

import pickle
import pandas as pd
import numpy as np
import os

# get current working directory
cwd = os.getcwd()

# Set output
outputDir = ('Python\\Data\\pickleJar\\')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

# location of datafiles, readings and times of known experiments
# sensorData = pd.read_csv(r'Python\Data\ThruFeb02GasStream.csv')
# trialTimes = pd.read_csv(r'Python\Data\TrialTimes-Joules.csv')

# pickle.dump(sensorData, open( outputDir + "sensorData.p", "wb" ) )
# pickle.dump(trialTimes, open( outputDir + "trialTimes.p", "wb" ) )

# used to load pickled data
sensorData = pickle.load( open( outputDir + "sensorData.p", "rb" ) )
trialTimes = pickle.load( open( outputDir + "trialTimes.p", "rb" ) )

sensorData.to_csv(outputDir + "pickledSensorData.csv",index=False)
trialTimes.to_csv(outputDir + "pickledTrialTimes.csv",index=False)