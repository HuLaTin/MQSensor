import pandas as pd

df = pd.read_csv(r'Python\eventsOutput\captureByTime\2021Mar18_captureByTime.csv')
df = df[:61]
df.to_csv(r'Python\eventsOutput\captureByTime\2021Mar18_captureByTimeFixed.csv',index=False)


# outputDir = ('Python\\machineLearning\downsampled')
# outputDir = (cwd, outputDir)
# outputDir = "\\".join(outputDir)

# dsName = [str(today), str(triggerSensor), "downsampled.csv"]
# dsName = "_".join(dsName)

# folderPath = (outputDir, dsName)
# dsCSV = "\\".join(folderPath)

chemEvents = df

# import csv
#chemEvents = pd.read_csv(balanceThis)

# split string, selects chemical name (drops the numbering)
chemEvents['chemical'] = chemEvents['chemical'].str.split("-").str[0]

# rename column
chemEvents = chemEvents.rename(columns={"chemical": "pred"})

# groups by class/chemical, downsamples to balance the dataset
g = chemEvents.groupby('pred')
chemEvents = pd.DataFrame(g.apply(lambda chemEvents: chemEvents.sample(g.size().min()).reset_index(drop=True)))

# saves to csv
chemEvents.to_csv('2021Mar18TimeDS.csv',index=False)