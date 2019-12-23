#Hunter Tiner

normalize <- function(x)
{
  return ((x - min(x)) / (max(x) - min(x)))
}
#Choose your file
SensorData <- read.csv(file.choose(), header=TRUE, sep=",")
SensorData <- SensorData[,2:22]
# SensorData2 <- read.csv(file.choose(), header=FALSE, sep=",")
# SensorDatamerge <- rbind(SensorData, SensorData2)

#Sets column names
colnames(SensorData, do.NULL = FALSE)
if (ncol(SensorData) == 34){
  colnames(SensorData) <- c("Time", "MQ2 ADC", "LPG ppm",
                            "MQ4 ADC", "CH4", "MQ5 ADC", "MQ5LPG ppm",
                            "MQ6 ADC", "MQ6 LPG ppm", "MQ7 ADC", "H2 ppm" ,
                            "MQ8 ADC", "MQ8H2 ppm", "MQ9 ADC", "CO ppm", "MQ135 ADC",
                            "U ppm", "Temp (C*)", "Gas ohms", "Humidity", "Pressure pa",
                            "CPU Load", "PM1.0 CF.1", "PM2.5 CF.1", "PM10 CF.1", "PM1.0 STD",
                            "PM2.5 STD", "PM10 STD", "x.0.3um", "x.0.5um", "x.1.0um", "x.2.5um", "x.5.um", "x.10.um")
} else {
  colnames(SensorData) <- c("Time", "MQ2 ADC", "LPG ppm",
                            "MQ4 ADC", "CH4", "MQ5 ADC", "MQ5LPG ppm",
                            "MQ6 ADC", "MQ6 LPG ppm", "MQ7 ADC", "H2 ppm" ,
                            "MQ8 ADC", "MQ8H2 ppm", "MQ9 ADC", "CO ppm", "MQ135 ADC",
                            "U ppm", "Temp (C*)", "Gas ohms", "Humidity", "Pressure pa")
#                            "CPU Load")
}

SensorData <- SensorData[!(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData[(is.na(SensorData$Time) | SensorData$Time==""), ]

SensorData$Time <- as.POSIXct(SensorData$Time, origin="1970-01-01", tz="GMT")

#Prompt for Expected change to be detected?
ExpectedChange = .03

#normalize
SensorData["MQ2_n"] <- as.data.frame(lapply(SensorData["MQ2 ADC"], normalize))
#creation of new columns for calculations
SensorData["Event"] <- NA
#setting 1st value of MQ2_n change to 0
SensorData[1,"MQ2_n Change"] = 0

SensorData <- SensorData[,c("Time", "MQ2 ADC", "MQ2_n", "MQ2_n Change", "Event", "LPG ppm", "MQ4 ADC", "CH4",
                            "MQ5 ADC", "MQ5LPG ppm", "MQ6 ADC", "MQ6 LPG ppm", "MQ7 ADC", "H2 ppm" , "MQ8 ADC",
                            "MQ8H2 ppm", "MQ9 ADC", "CO ppm", "MQ135 ADC", "U ppm", "Temp (C*)", "Gas ohms",
                            "Humidity", "Pressure pa")]

#calculation of MQ2_n Change
for (row in 2:nrow(SensorData))
{
  SensorData[row,"MQ2_n Change"] = (SensorData[row,"MQ2_n"] - SensorData[row-1,"MQ2_n"])
}

# determining if event occured
EventIndex <- data.frame("start" = integer(0), "end" = integer(0))
subsetCounter = 1
EventIndex[1,1] = 0
EventIndex[1,2] = 0
for (row in 1:nrow(SensorData)){
  # abs() for detecting negative change
  # if(abs(SensorData[row,"Change"])>(ExpectedChange)){

  if (SensorData[row,"MQ2_n Change"] > (ExpectedChange)){
    SensorData[row,"Event"] = "True"
     if (row > 5){

       #captures data from 5 points before the event
       #and 44 after
       if (row > EventIndex[nrow(EventIndex),2]){
         EventIndex[subsetCounter,1] = row - 5
         EventIndex[subsetCounter,2] = row + 44
         subsetCounter = subsetCounter + 1
       }
    }
  }
  else {
    SensorData[row,"Event"] = "False"
  }
}

#creation of eventsCaptured, where we will place our Event data, using information of EventIndex
eventNumber = 2
eventsCaptured = SensorData[EventIndex[1,1]:EventIndex[1,2],1:24]

while(1){
  eventStart = EventIndex[eventNumber, 1]
  eventEnd = EventIndex[eventNumber, 2]
  eventsCaptured <- rbind(eventsCaptured, SensorData[eventStart:eventEnd,1:24])

  if (eventNumber == nrow(EventIndex))
    break
  eventNumber = eventNumber + 1
}

