#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################


import numpy as np
import pandas as pd
import random
import pydotplus

import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn import tree, metrics
from sklearn.tree import export_graphviz
from six import StringIO
from IPython.display import Image  
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split # Import train_test_split function


df = pd.read_csv(r'Python\machineLearning\downsampled\2021Mar18TimeDS.csv')
dfSim = pd.read_csv(r'Python\machineLearning\simulated\2021-03-18_simulatedData.csv') # simulated

split = StratifiedShuffleSplit(n_splits=2, test_size=0.3, random_state=random.seed())

cn =  np.unique(df['pred'])
fn = list(df.columns[1:])


for train_index, test_index in split.split(df, df['pred']):
    strat_train_set = df.loc[train_index]
    strat_test_set = df.loc[test_index]

###########################################################
# balanced data sets for classification   
y_train = strat_train_set['pred']
x_train = strat_train_set.iloc[:,1:strat_train_set.shape[1]]

y_test = strat_test_set['pred']
x_test = strat_test_set.iloc[:,1:strat_test_set.shape[1]]

clf = tree.DecisionTreeClassifier()

clf = clf.fit(x_train,y_train)
y_pred = clf.predict(x_test)
print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (4,4), dpi=1000)
tree.plot_tree(clf, class_names=cn, feature_names=fn, filled=True);
fig.savefig('decisionTree.png')


###########################################################
# simulated data to be used for testing
y_sim = dfSim['pred']
x_sim = dfSim.iloc[:,1:dfSim.shape[1]]

y_full = df['pred']
x_full = df.iloc[:,1:df.shape[1]]

clf = tree.DecisionTreeClassifier()

clf = clf.fit(x_sim,y_sim)
y_pred = clf.predict(x_full)
print("Accuracy:", metrics.accuracy_score(y_full, y_pred))
print(confusion_matrix(y_full, y_pred))
print(classification_report(y_full, y_pred))

fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (4,4), dpi=1000)
tree.plot_tree(clf, class_names=cn, feature_names=fn, filled=True);
fig.savefig('simdecisionTree.png')
##########################################################


################################################################
################################################################
# dot_data = StringIO()
# export_graphviz(clf, out_file=dot_data,  
#                 filled=True, rounded=True)
#                 #special_characters=True, feature_names = feature_cols, class_names=['0','1'])
# graph = pydotplus.graph_from_dot_data(dot_data.getvalue())  
# graph.write_png('decisionTree.png')


# Image(graph.create_png())