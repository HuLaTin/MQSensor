SensorData0 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData1 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData2 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData3 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData4 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData5 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData6 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData7 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData8 <- read.csv(file.choose(), header=FALSE, sep=",")
SensorData9 <- read.csv(file.choose(), header=FALSE, sep=",")


SensorDataMerge <- rbind(SensorData0, SensorData1, SensorData2, SensorData3, SensorData4, SensorData5, SensorData6, SensorData7,
                         SensorData8, SensorData9)
JoulesData <- SensorDataMerge

SensorData <- read.csv(file.choose(), header=TRUE, sep=",")
SensorData <- SensorData[,2:23]
SensorDataMerge <- rbind(SensorData, SensorData2)


write.csv(SensorDataMerge, file = "20191120JoulesData.csv")
