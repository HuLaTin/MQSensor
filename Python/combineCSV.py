#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

import pandas as pd

sensorData1 = pd.read_csv(r'Python\Data\thru2021June08StriderGas.csv', header = None)
sensorData2 = pd.read_csv(r'Python\Data\20210615StriderGasStream.csv', header = None)


result1 = sensorData1.append([sensorData2], ignore_index=False)
# result2 = result1.append([sensorData3], ignore_index=False)
# result3 = result2.append([sensorData4], ignore_index=False)
# result4 = result3.append([sensorData5], ignore_index=False)
# result5 = result4.append([sensorData6], ignore_index=False)
# result5

result1 = result1.iloc[1:]

result1.to_csv('thru2021June15StriderGas.csv', index = False)