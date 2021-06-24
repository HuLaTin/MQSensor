import numpy as np
import pandas as pd
import random, os
import statistics as stat
from sklearn.metrics import accuracy_score, recall_score, precision_score, confusion_matrix, classification_report
from Python.util import classificationReports
from datetime import date
from sklearn.model_selection import StratifiedShuffleSplit

#from sklearn.metrics import average_precision_score

avgColumns = False

chemEvents = pd.read_csv(r'Python\eventsOutput\events\2021Jun22_MQ2_0.1_5_20_Events.csv') #25
#chemEvents = pd.read_csv(r'Python\eventsOutput\events\2021Jun22_MQ2_0.1_5_45_Events.csv') #50
#chemEvents = pd.read_csv(r'Python\eventsOutput\events\2021Jun22_MQ2_0.1_5_95_Events.csv') #100
#chemEvents = chemEvents.append(chemEvents); chemEvents= chemEvents.reset_index(drop=True)
# get current working directory
cwd = os.getcwd()

# set today's date
today = date.today()
today = today.strftime("%Y%b%d")

# Set output
outputDir = ('Python\\machineLearning\\output')
outputDir = (cwd, outputDir)
outputDir = "\\".join(outputDir)

ignoreChem = ' '

numSplits = 10
trainSize = 0.5

# select Machine Learning
# gnb = Naive Bayes         || tree = Decision Tree
# knn = K-Nearest Neighbor  || svm = Support Vector Machine
# rf = Random Forest Classifier
# ovr = One Versus Rest

learner = 'svm'

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

#this removes BME680 readings
#chemEvents = chemEvents.loc[:,~chemEvents.columns.str.contains("Temp_C*")]; chemEvents = chemEvents.loc[:,~chemEvents.columns.str.contains("Humidity")]; chemEvents = chemEvents.loc[:,~chemEvents.columns.str.contains("Gas_ohms")]; chemEvents = chemEvents.loc[:,~chemEvents.columns.str.contains("Pressure_pa")]

#colList = ["Temp_C*", "Humidity",  "Gas_ohms", "Pressure_pa"]
#colList = ["None", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC", "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC"]
colList = ["None"]

for i in range(0, len(colList)):
    x = 0

    ignoredCol = ignoreCol = colList[i]
    ignoreCol = '^', ignoreCol
    ignoreCol = ''.join(ignoreCol)
    
    chemDF = chemEvents.loc[:,~chemEvents.columns.str.contains(ignoreCol)]

    # groups by class/chemical, downsamples to balance the dataset
    #g = chemDF.groupby('pred')
    #chemDF = pd.DataFrame(g.apply(lambda chemDF: chemDF.sample(g.size().min())))
    #chemDF = chemDF.reset_index(drop=True)
    
    X, y = chemDF.iloc[:,1:].values, chemDF['pred'].values
    
    split = StratifiedShuffleSplit(n_splits=numSplits, train_size=trainSize, random_state=random.seed())
       
    for train_index, test_index in split.split(chemDF, chemDF['pred']):
        x = x + 1
        
        strat_train_set = chemDF.loc[train_index]
        strat_test_set = chemDF.loc[test_index]
            
        y_train = strat_train_set['pred']
        x_train = strat_train_set.iloc[:,1:strat_train_set.shape[1]]

        y_test = strat_test_set['pred']
        x_test = strat_test_set.iloc[:,1:strat_test_set.shape[1]]
            
        #learninglst = [str(learner), str(trainSize), str(len(x_train)), str(colList[i]), str(len(chemDF.columns)-1)]
        #print(learninglst)
        
        # Naive Bayes 
        if learner == 'gnb':
            from sklearn.naive_bayes import GaussianNB
            gnb =  GaussianNB()                    
            y_pred = gnb.fit(x_train, y_train).predict(x_test)
            
        # Decision Tree    
        if learner == 'tree':
            
            from sklearn import tree
            import matplotlib.pyplot as plt
            
            #gini or entropy
            clf = tree.DecisionTreeClassifier(criterion='entropy', max_depth=2)
            
            cn =  np.unique(chemDF['pred'])
            fn = list(chemDF.columns[1:])
            
            clf = clf.fit(x_train,y_train)
            y_pred = clf.predict(x_test)
            
            treeFig = (outputDir, "decisionTree", str(ignoredCol) + '-' + str(x) + '-decisionTree.png')
            treeFig = "\\".join(treeFig)

            fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (4,4), dpi=2000)
            tree.plot_tree(clf, class_names=cn, feature_names=fn, filled=True, rounded=True);
            fig.savefig(treeFig)
            plt.close       
     
        # Random Forest Classifier
        if learner == 'rf':
            from sklearn.ensemble import RandomForestClassifier
                  
            
            cn =  np.unique(chemDF['pred'])
            fn = list(chemDF.columns[1:])
            
            clf = RandomForestClassifier(n_estimators=100, max_depth=None, criterion='entropy')
            clf = clf.fit(x_train, y_train)
            y_pred = clf.predict(x_test)
            feature_imp = pd.Series(clf.feature_importances_,index=fn).sort_values(ascending=False)
            
            if avgColumns == True:
                import matplotlib.pyplot as plt
                import seaborn as sns 
                forestFig = (outputDir, "randomforest", str(ignoredCol) + str(x) + '_forestTree.png')
                forestFig = "\\".join(forestFig)
            
                fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (6,6), dpi=1000)
                sns.barplot(x=feature_imp, y=feature_imp.index)
                plt.xlabel('Feature Importance Score')
                plt.ylabel('Features')
                plt.title("Visualizing Important Features")
                #plt.legend()
                #plt.show()
                fig.savefig(forestFig)
                plt.close

            #print('feature importance -', feature_imp)    
               
        # K Nearest Neighbor
        if learner == 'knn':
            from sklearn import neighbors
            knn = neighbors.KNeighborsClassifier(n_neighbors=5)
            knn = knn.fit(x_train, y_train)
            y_pred = knn.predict(x_test)
                  
        # Support Vector Machine    
        if learner == 'svm':
            from sklearn.svm import SVC
            svc = SVC(kernel = 'linear')
            svc = svc.fit(x_train, y_train)
            y_pred = svc.predict(x_test)
        
        if learner == 'ovr':
            from sklearn.multiclass import OneVsRestClassifier
            from sklearn.svm import SVC
            
            ovr = OneVsRestClassifier(SVC()).fit(x_train, x_train)
            y_pred = ovr.predict(x_test)


            
        accuracy, recall, precision, cmat, classReport \
                    = classificationReports(accuracy_score, recall_score, precision_score, confusion_matrix, classification_report, y_test, y_pred)
        
        print(str(learner), ' - ', str(x))
        print('\n')
        print('accuracy -  ', accuracy)
        print('recall -    ', recall)
        print('precision - ', precision)
        print(cmat)
        print('\n')

        #print(classReport)
        #print(average_precision_score(y_test, y_pred))

                


