import os
import pandas as pd
import numpy as np
import statistics as stat
import math
import random
from datetime import datetime, date

# set date
today = date.today()

# set output directory
cwd = os.getcwd()
outputDir = ('Python\\machineLearning\simulated')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

simName = [str(today), "simulatedData.csv"]
simName = "_".join(simName)

folderPath = (outputDir, simName)
simName = "\\".join(folderPath)

# seed for random
random.seed(datetime.now())

# how many simulated rows for each chemical?
##############
simNum = 15  #
##############

# import data
trueData = pd.read_csv(r'C:\Users\Hunter Tiner\Documents\MQSensor\Python\machineLearning\downsampled\2021Jan26_MQ2_downsampled.csv')

# creates a list of all chemicals that appear
chems =  np.unique(trueData['pred'])

allSimChem = pd.DataFrame()
for y in chems:
    # select rows that contain 'y' chemical
    trueChem = trueData[trueData['pred'].str.contains(y)]
    chemData = pd.DataFrame()
    deviData = pd.DataFrame()
    simData = pd.DataFrame()
    # uniform distribution of samples / read numpy.random.uniform doc
    randoNum = pd.DataFrame(np.random.uniform(0,1, simNum))

    
    for x in range(1, len(trueData.columns)):
        chemData.loc[0, x] = stat.mean(trueData.iloc[:,x])
                    
        # standard deviation
        for w in range(0, len(trueData)):
            deviData.loc[w,x] = ((trueData.iloc[w,x] - chemData.loc[0,x]) ** 2)
    
        doMath = math.sqrt(sum(deviData.iloc[:,x-1])/len(deviData))
        chemData.loc[1,x] = doMath*2 # multiple by two for 2 deviations
        
        lower = chemData.loc[0,x]-chemData.loc[1,x]
        upper = chemData.loc[0,x]+chemData.loc[1,x]
        
        # double check what this is doing
        for z in range(0, len(randoNum)):
            rLoc = randoNum.loc[z,]
            simData.loc[z,x+1] = ((float(rLoc)*100) * (upper - lower) / 100) + lower
   
    # adds chemical identifier and column names
    simData.insert(0,'pred',y)    
    simData.columns=trueData.columns.values
    
    allSimChem = allSimChem.append(simData)

allSimChem.to_csv(simName,index=False)

