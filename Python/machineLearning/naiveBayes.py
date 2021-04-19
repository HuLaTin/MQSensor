#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################


import numpy as np
import pandas as pd
import random

import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import export_graphviz
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split # Import train_test_split function


df = pd.read_csv(r'Python\machineLearning\downsampled\2021Mar18TimeDS.csv')
dfSim = pd.read_csv(r'Python\machineLearning\simulated\2021-03-18_simulatedData.csv') # simulated
dfOG = pd.read_csv(r'Python\eventsOutput\captureByTime\2021Mar18_captureByTimeFixed.csv')

split = StratifiedShuffleSplit(n_splits=2, test_size=0.1, random_state=random.seed())


# pred = df["pred"]
# data = df.iloc[:,1:]

# gnb =  GaussianNB()
# gnb.fit(data, pred)

# for train_index, test_index in split.split(df, df['pred']):
#     strat_train_set = df.loc[train_index]
#     strat_test_set = df.loc[test_index]
    
for train_index, test_index in split.split(dfOG, dfOG['pred']):
    strat_train_set = df.loc[train_index]
    strat_test_set = df.loc[test_index]
    
y_train = strat_train_set['pred']
x_train = strat_train_set.iloc[:,1:strat_train_set.shape[1]]

y_test = strat_test_set['pred']
x_test = strat_test_set.iloc[:,1:strat_test_set.shape[1]]
    
gnb =  GaussianNB()

y_pred = gnb.fit(x_train, y_train).predict(x_test)
print("Number of mislabeled points out of a total %d points : %d" % (x_test.shape[0], (y_test != y_pred).sum()))

###########################################################
# simulated data to be used for testing
y_sim = dfSim['pred']
x_sim = dfSim.iloc[:,1:dfSim.shape[1]]

y_full = df['pred']
x_full = df.iloc[:,1:df.shape[1]]

gnb =  GaussianNB()
y_pred = gnb.fit(x_sim, y_sim).predict(x_full)
print("Number of mislabeled points out of a total %d points : %d" % (x_full.shape[0], (y_full != y_pred).sum()))
