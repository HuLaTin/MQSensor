#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################


import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn import tree


df = pd.read_csv(r'Python\machineLearning\downsampled\2021Jan27_MQ2_downsampled.csv')
#df = pd.read_csv(r'C:\Users\Hunter Tiner\Documents\MQSensor\Python\machineLearning\simulated\2021-01-27_simulatedData.csv') # simulated

sss = StratifiedShuffleSplit(n_splits=2, test_size=0.7,random_state=0)
sss


clf = tree.DecisionTreeClassifier()
