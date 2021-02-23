#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

from numpy.core.numeric import tensordot
import pandas as pd
from pandas.core.frame import DataFrame

sensorData1 = pd.read_csv(r'Python\Data\Old\2020Dec08GasStream.csv', header=None)
sensorData2 = pd.read_csv(r'Python\Data\Old\2020Dec11GasStream.csv', header=None)
sensorData3 = pd.read_csv(r'Python\Data\Old\2020Dec18GasStream.csv', header=None)
sensorData4 = pd.read_csv(r'Python\Data\Old\2020Dec21GasStream-MQ4MQ5.csv', header=None)
sensorData5 = pd.read_csv(r'Python\Data\Old\2021Jan25GasStream.csv', header=None)
sensorData6 = pd.read_csv(r'Python\Data\Old\2021Feb02GasStream.csv', header=None)

result1 = sensorData1.append([sensorData2], ignore_index=False)
result2 = result1.append([sensorData3], ignore_index=False)
result3 = result2.append([sensorData4], ignore_index=False)
result4 = result3.append([sensorData5], ignore_index=False)
result5 = result4.append([sensorData6], ignore_index=False)
result5

result5 = result5.iloc[1:]

result5.to_csv('Python\Data\ThruFeb02GasStream.csv', index = False)
