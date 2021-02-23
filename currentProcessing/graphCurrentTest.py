import plotly.express as px
import pandas as pd

df = pd.read_csv(r'currentProcessing\currentTest02p.csv')


fig = px.line(df, x='Time', y='0', title = "currentTest")
fig.add_scatter(x=df['Time'], y=df['1']) 

fig.show()