from os import name
from numpy.core.fromnumeric import shape
import pandas as pd
import plotly.express as px


# df = pd.read_csv(r'Python\Data\GasZap\2021March09BugZapOn.csv')
# df = pd.read_csv(r'Python\Data\GasZap\2021March10BugZapOn.csv') # This is only 3 datapoints from when we restarted the pi and turned off the Zapper
df = pd.read_csv(r'Python\Data\GasZap\2021March11BugZapOff.csv')

# rename columns in "sensorData"
df.columns = ("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "CPU_Load", "Throttled")

# drops two columns that aren't useful in this application
del df['CPU_Load']
del df['Throttled']

rows = list(df.columns)

fig = px.line(df, x='Time', y= str(df.columns[1]) , title = "dataGraph")
for i in range(2 , len(rows)):
    print(rows[i])
    fig.add_scatter(x=df['Time'], y=df[str(rows[i])], name = str(rows[i]))

fig.show()