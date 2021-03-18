from os import name
from numpy.core.fromnumeric import shape
import pandas as pd
import plotly.express as px


df = pd.read_csv(r'Python\eventsOutput\captureByTime\2021Mar18_captureByTime.csv', header = None)

rows = list(df[0])

df = df.T
df.columns = rows

df = df.drop(index=0)

df =df.reset_index()


fig = px.line(df, x='index', y=str(rows[1]), title = "EventGraph")
for i in range(2 , len(rows)):
    print(rows[i])
    fig.add_scatter(x=df['index'], y=df[str(rows[i])], name = str(rows[i])) 

fig.show()
