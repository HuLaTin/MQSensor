#Hunter Tiner
library(reshape2)
library(svDialogs)

normalize <- function(x)
{
  return ((x - min(x)) / (max(x) - min(x)))
}
#Choose your file
SensorData <- read.csv(file.choose(), header=FALSE, sep=",")

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
                            "U ppm", "Temp (C*)", "Gas ohms", "Humidity", "Pressure pa", "CPU Load")
}

SensorData <- SensorData[!(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData[(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData$Time <- as.POSIXct(SensorData$Time, origin="1970-01-01", tz="GMT")

#Prompt for Expected change
#add error handling?
ExpectedChange <- as.double(dlgInput("Enter Expected Change", default = ".03", Sys.info()["user"])$res)

#records time to determine elapsed time
start.time <- Sys.time()

names <- c("MQ2 ADC","MQ4 ADC", "MQ5 ADC","MQ6 ADC", "MQ7 ADC", "MQ8 ADC", "MQ9 ADC", "MQ135 ADC")

for (i in names)
{
  #normalize
  SensorData["ADC_N"] <- as.data.frame(lapply(SensorData[i], normalize))
  SensorData["Event"] <- NA
  SensorData[1,"Change"] = 0

  #calculation of Change
  print(paste("Calculating change for", toString(i)))
  for (row in 2:nrow(SensorData))
  {
    SensorData[row,"Change"] = (SensorData[row,"ADC_N"] - SensorData[row-1,"ADC_N"])
  }

  # determining if event occured
  EventIndex <- data.frame("start" = integer(0), "end" = integer(0))
  TimeIndex <- data.frame("Time" = integer(0))
  subsetCounter = 1
  EventIndex[1,1] = 0
  EventIndex[1,2] = 0
  print(paste("Finding events for", toString(i)))
  for (row in 1:nrow(SensorData)){
    # abs() for detecting negative change
    # if(abs(SensorData[row,"Change"])>(ExpectedChange)){

    if (SensorData[row,"Change"] > (ExpectedChange)){
      SensorData[row,"Event"] = "True"
      if (row > 5 && row < (nrow(SensorData)-44)){

        #captures data from 5 points before the event
        #and 44 after
        if (row > EventIndex[nrow(EventIndex),2]){
          EventIndex[subsetCounter,1] = row - 5
          EventIndex[subsetCounter,2] = row + 44
          subsetCounter = subsetCounter + 1

          TimeIndex[subsetCounter - 1,] <- SensorData[row - 1,"Time"]
        }
      }
    }
    else {
      SensorData[row,"Event"] = "False"
    }
  }
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


  rownames(eventsCaptured) <- seq(length=nrow(eventsCaptured))
  eventsCaptured <- eventsCaptured[,c("Time", "MQ2 ADC","MQ4 ADC", "MQ5 ADC", "MQ6 ADC",  "MQ7 ADC", "MQ8 ADC",  "MQ9 ADC",  "MQ135 ADC",
                                      "Temp (C*)", "Gas ohms", "Humidity", "Pressure pa")]

  eventTemp <- data.frame()
  events <- data.frame(matrix(NA, nrow = 50))
  events <- events[-c(1)]
  numEvents = nrow(eventsCaptured)/50
  for (eventNum in 1:numEvents){
    eventStart = (50 * (eventNum - 1)) + 1
    eventStop = (50 * eventNum)
    eventTemp <- as.data.frame(eventsCaptured[eventStart:eventStop,])
    #
    #normalizing sensor readings excluding gas ohms, temp, humidity, pressure
    eventTemp[,2:9] <- as.data.frame(lapply(eventTemp[,2:9], normalize))
    #eventTemp[,2:ncol(eventTemp)] <- as.data.frame(lapply(eventTemp[,2:ncol(eventTemp)], normalize))
    #
    eventTemp["num"] <- seq(length=nrow(eventTemp))
    eventTemp <- melt(eventTemp, id=c("Time","num"))
    events <- cbind(events, eventTemp[,4])
    names(events)[c(ncol(events))] <- paste("Event", toString(eventNum), sep=" ")
  }
  events <- as.data.frame(t(events))

  TimeIndex$Time <- as.POSIXct(TimeIndex$Time, origin="1970-01-01", tz="GMT")

  assign(paste(toString(i), "Index"), EventIndex)
  assign(paste(toString(i), "Captured"), eventsCaptured)
  assign(paste(toString(i), "Events"), events)
  assign(paste(toString(i), "Times"), TimeIndex)

}

end.time <- Sys.time()
total.time <- end.time - start.time

print("Program Completed!")
print(total.time)