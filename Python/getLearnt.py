import numpy as np
import pandas as pd
import random
import os
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn import neighbors
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix, classification_report


from sklearn.model_selection import StratifiedShuffleSplit

chemEvents = pd.read_csv(r'Python\eventsOutput\events\Strider-resample-2021Jun08_MQ2_0.1_5_45_Events.csv')

# get current working directory
cwd = os.getcwd()

# Set output
outputDir = ('Python\\machineLearning\\output')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

ignoreChem = ' '
numSplits = 2
testSize = 0.3
loops = 10

learner = 'gnb'

#########################################################################
#Supervised Learning Estimators
#gnb =  GaussianNB() #Naive Bayes
#lr = LinearRegression(normalize=True) # Linear Regression
#svc = SVC(kernel='linear') #Support Vector Machines
#knn = neighbors.KNeighborsClassifier(n_neighbors=5)

#Unsupervised Learning Estimators
#pca = PCA(n_components=0.95)
#k_means = KMeans(n_clusters=3, random_state=0)
#########################################################################


# split string, selects chemical name (drops the numbering)
chemEvents['chemical'] = chemEvents['chemical'].str.split("-").str[0]
# rename column
chemEvents = chemEvents.rename(columns={"chemical": "pred"})

chemEvents = chemEvents[~chemEvents.pred.str.contains(ignoreChem)]

#colList = ["Temp_C*", "Humidity",  "Gas_ohms", "Pressure_pa"]
colList = [" "]

for i in range(0, len(colList)):
        
    ignoredCol = ignoreCol = colList[i]
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
        
        #Naive Bayes 
        if learner == 'gnb':
            from sklearn.naive_bayes import GaussianNB

            gnb =  GaussianNB()                    
            y_pred = gnb.fit(x_train, y_train).predict(x_test)
            
            print("Mislabeled points out of %d : %d" % (x_test.shape[0], (y_test != y_pred).sum()))   
            print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
            print('CMat', confusion_matrix(y_test, y_pred))
            print('classification Report', classification_report(y_test, y_pred))
            
        #Decision Tree    
        if learner == 'tree':
            
            from sklearn import tree
            import matplotlib.pyplot as plt

            clf = tree.DecisionTreeClassifier()
            
            cn =  np.unique(chemEvents['pred'])
            fn = list(chemEvents.columns[1:])
            
            clf = clf.fit(x_train,y_train)
            y_pred = clf.predict(x_test)
            print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
            print(confusion_matrix(y_test, y_pred))
            print(classification_report(y_test, y_pred))
            
            treeFig = (outputDir, "dTree", str(ignoredCol) + str(x) + '_decisionTree.png')
            treeFig = "\\".join(treeFig)

            fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (4,4), dpi=1000)
            tree.plot_tree(clf, class_names=cn, feature_names=fn, filled=True);
            fig.savefig(treeFig)         
            
        
        
        if x == loops:
            print('\n')
            break