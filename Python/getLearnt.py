import numpy as np
import pandas as pd
import random
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import StratifiedShuffleSplit

chemEvents = pd.read_csv(r'Python\eventsOutput\events\2021Jun07_MQ2_0.1_10_90_Events.csv')

ignoreChem = 'Cyclohexane'
numSplits = 2
testSize = 0.1
loops = 10

gnb =  GaussianNB()

colList = ["Temp_C*", "Humidity",  "Gas_ohms", "Pressure_pa"]
for i in colList:
        
    ignoreCol = colList[i]
    #ignoreCol = 'Gas_ohms'
    ignoreCol = '^', ignoreCol
    ignoreCol = ''.join(ignoreCol)

    # split string, selects chemical name (drops the numbering)
    chemEvents['chemical'] = chemEvents['chemical'].str.split("-").str[0]
    # rename column
    chemEvents = chemEvents.rename(columns={"chemical": "pred"})

    chemEvents = chemEvents[~chemEvents.pred.str.contains(ignoreChem)]
    chemEvents = chemEvents.loc[:,~chemEvents.columns.str.contains(ignoreCol)]

    # groups by class/chemical, downsamples to balance the dataset
    g = chemEvents.groupby('pred')
    chemEvents = pd.DataFrame(g.apply(lambda chemEvents: chemEvents.sample(g.size().min()).reset_index(drop=True)))
    
    x = 0
    while(1):
        x = x + 1
    
        split = StratifiedShuffleSplit(n_splits=numSplits, test_size=testSize, random_state=random.seed())
        
        for train_index, test_index in split.split(chemEvents, chemEvents['pred']):
            strat_train_set = chemEvents.loc[train_index]
            strat_test_set = chemEvents.loc[test_index]

        y_train = strat_train_set['pred']
        x_train = strat_train_set.iloc[:,1:strat_train_set.shape[1]]

        y_test = strat_test_set['pred']
        x_test = strat_test_set.iloc[:,1:strat_test_set.shape[1]]
        
        y_pred = gnb.fit(x_train, y_train).predict(x_test)
        print("Number of mislabeled points out of a total %d points : %d" % (x_test.shape[0], (y_test != y_pred).sum()))   
        
        if x == loops:
            break