#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

from numpy.core.numeric import tensordot
import pandas as pd
from pandas.core.frame import DataFrame

sensorData1 = pd.read_csv(r'Python\eventsOutput\eventsTrim\Joules-2021Jun08_MQ2_0.1_5_45_EventsTrim.csv', header=0)
sensorData2 = pd.read_csv(r'Python\eventsOutput\eventsTrim\Strider-resample-2021Jun08_MQ2_0.1_5_45_EventsTrim.csv', header=0)

result1 = sensorData1.append([sensorData2], ignore_index=False)
# result2 = result1.append([sensorData3], ignore_index=False)
# result3 = result2.append([sensorData4], ignore_index=False)
# result4 = result3.append([sensorData5], ignore_index=False)
# result5 = result4.append([sensorData6], ignore_index=False)
# result5

result1 = result1.iloc[1:]

result1.to_csv('JoulesStriderResampleJune08.csv', index = False)