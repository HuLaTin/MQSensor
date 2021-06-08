import numpy as np
import pandas as pd
import random
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import StratifiedShuffleSplit

chemEvents = pd.read_csv(r'Python\eventsOutput\events\2021Jun07_MQ2_0.1_10_90_Events.csv')

ignoreChem = 'Cyclohexane'
numSplits = 2
testSize = 0.3
loops = 10

gnb =  GaussianNB()

# split string, selects chemical name (drops the numbering)
chemEvents['chemical'] = chemEvents['chemical'].str.split("-").str[0]
# rename column
chemEvents = chemEvents.rename(columns={"chemical": "pred"})

chemEvents = chemEvents[~chemEvents.pred.str.contains(ignoreChem)]

colList = ["Temp_C*", "Humidity",  "Gas_ohms", "Pressure_pa"]
for i in range(0, len(colList)):
        
    ignoreCol = colList[i]
    #ignoreCol = 'Gas_ohms'
    ignoreCol = '^', ignoreCol
    ignoreCol = ''.join(ignoreCol)
    
    chemDF = chemEvents.loc[:,~chemEvents.columns.str.contains(ignoreCol)]

    # groups by class/chemical, downsamples to balance the dataset
    g = chemDF.groupby('pred')
    chemDF = pd.DataFrame(g.apply(lambda chemDF: chemDF.sample(g.size().min())))
    chemDF = chemDF.reset_index(drop=True)
       
    x = 0
    while(1):
        x = x + 1
  
        split = StratifiedShuffleSplit(n_splits=numSplits, test_size=testSize, random_state=random.seed())
        
        for train_index, test_index in split.split(chemDF, chemDF['pred']):
            strat_train_set = chemDF.loc[train_index]
            strat_test_set = chemDF.loc[test_index]

        y_train = strat_train_set['pred']
        x_train = strat_train_set.iloc[:,1:strat_train_set.shape[1]]

        y_test = strat_test_set['pred']
        x_test = strat_test_set.iloc[:,1:strat_test_set.shape[1]]
        
        y_pred = gnb.fit(x_train, y_train).predict(x_test)
        print("Number of mislabeled points out of a total %d points : %d" % (x_test.shape[0], (y_test != y_pred).sum()))   
        
        if x == loops:
            print('\n')
            break