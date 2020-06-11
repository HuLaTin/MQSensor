import pandas as pd
#infileCSVone = file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "thru20200312Joules.csv")
#infileCSVtwo = file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "trialTimes.csv")
#ExpectedChange = as.double(.03)
#windowSize = as.integer(50)

infileCSVone = open('C:/Users/Hunter Tiner/DOcuments/MQSensor/Machine Learning/thru20200312Joules.csv')
infileCSVtwo = open('C:/Users/Hunter Tiner/DOcuments/MQSensor/Machine Learning/trialTimes.csv')
ExpectedChange = .03
windowSize = 50

mytxt = infileCSVone.read()
mytxt.head()

