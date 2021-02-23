import pandas as pd 

df = pd.read_csv(r'Processing\currentTest02.csv', header = None)

dfTime = df[df[0].str.contains("2021")]
df0 = df[df[0].str.contains("0: ")]
df1 = df[df[0].str.contains("1: ")]

currentTest = pd.concat([dfTime.reset_index(drop=True), df0.reset_index(drop=True), df1.reset_index(drop=True)], axis=1)
currentTest.columns = ['Time', '0', '1']

#currentTest['0'] = currentTest['0'].map(lambda x: x.lstrip('0: '))
currentTest['0'] = currentTest['0'].replace({'0: ':''}, regex=True)
currentTest['1'] = currentTest['1'].replace({'1: ':''}, regex=True)

currentTest.to_csv("currentTest02p.csv",index=False)