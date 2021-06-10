import numpy as np
import pandas as pd
import random, os
import statistics as stat
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from Python.util import classificationReports

from sklearn.model_selection import StratifiedShuffleSplit

simDataExist = False
avgColumns = True

chemEvents = pd.read_csv(r'Python\eventsOutput\events\Strider-2021Jun08_MQ2_0.1_10_90_Events.csv')
#chemSim = pd.read_csv(r'Python\machineLearning\simulated\strider-30-100-2021-06-09_simulatedData.csv'); simDataExist = True

# get current working directory
cwd = os.getcwd()

# Set output
outputDir = ('Python\\machineLearning\\output')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

ignoreChem = ' '

numSplits = 2
testSize = 0.7

loops = 1

# select Machine Learning
# gnb = Naive Bayes         || tree = Decision Tree
# knn = K-Nearest Neighbor  || lr = Linear Regression
# kmeans = K-Means          || svm = Support Vector Machine
# pca = Principal Component Analysis

learner = 'gnb'

# Model Accuracy: how often is the classifier correct?
# Model Precision: what percentage of positive tuples are labeled as such?
# Model Recall: what percentage of positive tuples are labelled as such?

if avgColumns == True:
    
    colList = ["MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC", "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                "Temp_C*", "Humidity",  "Gas_ohms", "Pressure_pa"]
    chemEventsMean = pd.DataFrame()
    chemEventsMean['chemical'] = chemEvents['chemical']
    for i in range(len(chemEvents)):
        for j in colList:
            chemEventsMean.loc[i, j] = stat.mean(chemEvents.loc[i,chemEvents.filter(like=j).columns])
    chemEvents = chemEventsMean

# split string, selects chemical name (drops the numbering)
chemEvents['chemical'] = chemEvents['chemical'].str.split("-").str[0]

# rename column
chemEvents = chemEvents.rename(columns={"chemical": "pred"})

chemEvents = chemEvents[~chemEvents.pred.str.contains(ignoreChem)]

#colList = ["Temp_C*", "Humidity",  "Gas_ohms", "Pressure_pa"]
colList = [" "]
      
print('learner -', learner)
for i in range(0, len(colList)):
        
    ignoredCol = ignoreCol = colList[i]
    ignoreCol = '^', ignoreCol
    ignoreCol = ''.join(ignoreCol)
    
    print('ignoring ', ignoredCol)
    
    chemDF = chemEvents.loc[:,~chemEvents.columns.str.contains(ignoreCol)]

    # groups by class/chemical, downsamples to balance the dataset
    g = chemDF.groupby('pred')
    chemDF = pd.DataFrame(g.apply(lambda chemDF: chemDF.sample(g.size().min())))
    chemDF = chemDF.reset_index(drop=True)
    
    X, y = chemDF.iloc[:,1:].values, chemDF['pred'].values
       
    x = 0
    while(1):
        x = x + 1
  
        
        if simDataExist == False:
            split = StratifiedShuffleSplit(n_splits=numSplits, test_size=testSize, random_state=random.seed())

            
            for train_index, test_index in split.split(chemDF, chemDF['pred']):
                strat_train_set = chemDF.loc[train_index]
                strat_test_set = chemDF.loc[test_index]

            y_train = strat_train_set['pred']
            x_train = strat_train_set.iloc[:,1:strat_train_set.shape[1]]

            y_test = strat_test_set['pred']
            x_test = strat_test_set.iloc[:,1:strat_test_set.shape[1]]
            
        else:
            
            y_train = chemSim['pred']
            x_train = chemSim.iloc[:,1:]

            y_test = chemEvents['pred']
            x_test = chemEvents.iloc[:,1:]
                            
        ## Supervised Learning ##
        
        # Naive Bayes 
        if learner == 'gnb':
            from sklearn.naive_bayes import GaussianNB
            gnb =  GaussianNB()                    
            y_pred = gnb.fit(x_train, y_train).predict(x_test)
            
            accuracy, cmat, classReport \
                = classificationReports(accuracy_score, confusion_matrix, classification_report, y_test, y_pred)
                
            print(accuracy)
            print(cmat)
            print(classReport)
        
        # Decision Tree    
        if learner == 'tree':
            
            from sklearn import tree
            import matplotlib.pyplot as plt
            
            #gini or entropy
            clf = tree.DecisionTreeClassifier(criterion='gini')
            
            cn =  np.unique(chemEvents['pred'])
            fn = list(chemEvents.columns[1:])
            
            clf = clf.fit(x_train,y_train)
            y_pred = clf.predict(x_test)
            
            treeFig = (outputDir, "decisionTree", str(ignoredCol) + str(x) + '_decisionTree.png')
            treeFig = "\\".join(treeFig)

            fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (4,4), dpi=2000)
            tree.plot_tree(clf, class_names=cn, feature_names=fn, filled=True, rounded=True);
            fig.savefig(treeFig)
            
            accuracy, cmat, classReport \
                = classificationReports(accuracy_score, confusion_matrix, classification_report, y_test, y_pred)
                
            print(accuracy)
            print(cmat)
            print(classReport)         
     
        # Random Forest Classifier
        if learner == 'randomforestC':
            from sklearn.ensemble import RandomForestClassifier
            import matplotlib.pyplot as plt
            import seaborn as sns       
            
            cn =  np.unique(chemEvents['pred'])
            fn = list(chemEvents.columns[1:])
            
            clf = RandomForestClassifier(n_estimators=100)
            clf = clf.fit(x_train, y_train)
            y_pred = clf.predict(x_test)
            feature_imp = pd.Series(clf.feature_importances_,index=fn).sort_values(ascending=False)
            feature_imp
            
            #forestFig = (outputDir, "randomforest", str(ignoredCol) + str(x) + '_randomForestImp.png')
            #forestFig = "\\".join(forestFig)
            
            sns.barplot(x=feature_imp, y=feature_imp.index)
            plt.xlabel('Feature Importance Score')
            plt.ylabel('Features')
            plt.title("Visualizing Important Features")
            plt.legend()
            plt.show()
            
            accuracy, cmat, classReport \
                = classificationReports(accuracy_score, confusion_matrix, classification_report, y_test, y_pred)
                
            print(accuracy)
            print(cmat)
            print(classReport) 


            
        # K Nearest Neighbor
        if learner == 'knn':
            from sklearn import neighbors
            knn = neighbors.KNeighborsClassifier(n_neighbors=3)
            knn = knn.fit(x_train, y_train)
            y_pred = knn.predict(x_test)
            
                    
        # Support Vector Machine    
        if learner == 'svm':
            from sklearn.svm import SVC
            svc = SVC(kernel = 'linear')
            svc = svc.fit(x_train, y_train)
            y_pred = svc.predict(x_test)
                     
        
        ###########################
        ## Unsupervised Learning ##
                
        # K Means
        if learner == 'kmeans':
            from sklearn.cluster import KMeans
            k_means = KMeans(n_clusters=4, n_init=10)
            k_means = k_means.fit(x_train)
            y_pred = k_means.predict(x_test)
            
        if learner == "pca":
            from sklearn.decomposition import PCA
            pca = PCA(n_components=0.95)
            pca_model = pca.fit_transform(x_train)

        if x == loops:
            print('\n')
            break