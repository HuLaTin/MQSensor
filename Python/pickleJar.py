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
sensorData = pd.read_csv(r'Python\Data\Joulesv2_20201208_SL.csv')
trialTimes = pd.read_csv(r'Python\Data\V2TrialTimes.csv')

pickle.dump(sensorData, open( outputDir + "sensorData.p", "wb" ) )
pickle.dump(trialTimes, open( outputDir + "trialTimes.p", "wb" ) )

sensorData = pickle.load( open( outputDir + "sensorData.p", "rb" ) )
trialTimes = pickle.load( open( outputDir + "trialTimes.p", "rb" ) )

sensorData.to_csv(outputDir + "sensorData.csv",index=False)
trialTimes.to_csv(outputDir + "trialTimes.csv",index=False)