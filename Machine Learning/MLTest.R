#Hunter Tiner

library(reshape2)
library(cluster)
library(factoextra)
#library(svDialogs)

normalize <- function(x)
{
  return ((x - min(x)) / (max(x) - min(x)))
}

#SensorData
#trialTimes
#ExpectedChange
#windowSize

#Set directory
#resultsdir = "C:\Users\Hunter Tiner\Documents\MQSensor\Machine Learning\eventsOutput"
infileCSVone <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "thru20200312Joules.csv")
infileCSVtwo <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "trialTimes.csv")
ExpectedChange <- as.double(.03)
windowSize <- as.integer(50)

#Kmeans = TRUE, PAM = FALSE
kSwitch <- TRUE


#file.exists(infileCSVone)
#file.exists(infileCSVtwo)
#exists("ExpectedChange")
#exists("windowSize")

SensorData <- read.csv(infileCSVone, header = TRUE, sep=",")
trialTimes <- read.csv(infileCSVtwo, header = TRUE, sep=",", stringsAsFactors = FALSE)

#############################################################
#Choose your file
#print("Choose file of sensor readings. (.csv)")
#SensorData <- read.csv(file.choose(), header=TRUE, sep=",")

#print("Choose file of trial times. (.csv)")
#trialTimes <- read.csv(file.choose(), header=TRUE, sep=",", stringsAsFactors = FALSE)

#ExpectedChange <- as.double(dlgInput("Enter Expected Change.", default = ".03", Sys.info()["user"])$res)
#windowSize <- as.integer(dlgInput("Enter desired 'window' size. (Increments of 25)", default = "50", Sys.info()["user"])$res)

# if (windowSize %% 25 != 0){
#   while (TRUE){
#     windowSize <- as.integer(dlgInput("Invalid entry. Please enter desired 'window' size. (Increments of 25)", default = "50", Sys.info()["user"])$res)
#     if (windowSize %% 25 == 0){
#       print("Invalid entry. window size must be in increments of 25")
#       break    }
#   }
# }
##############################################################

#records time to determine elapsed time
start.time <- Sys.time()
set.seed(Sys.time())

for (row in 1:nrow(trialTimes))
{
  #print(paste(trialTimes[row,"Chemical"], row, sep="-"))
  trialTimes[row, "Chemical"] <- paste(trialTimes[row,"Chemical"], row, sep="-")
}

#Sets column names.
colnames(SensorData, do.NULL = FALSE)

if (ncol(SensorData) == 34){
  colnames(SensorData) <- c("Time", "MQ2_ADC", "LPG_ppm",
                            "MQ4_ADC", "CH4", "MQ5_ADC", "MQ5LPG_ppm",
                            "MQ6_ADC", "MQ6_LPG ppm", "MQ7_ADC", "H2_ppm" ,
                            "MQ8_ADC", "MQ8H2_ppm", "MQ9_ADC", "CO_ppm", "MQ135_ADC",
                            "U_ppm", "Temp_C*", "Gas_ohms", "Humidity", "Pressure_pa",
                            "CPU_Load", "PM1.0_CF.1", "PM2.5_CF.1", "PM10_CF.1", "PM1.0_STD",
                            "PM2.5_STD", "PM10_STD", "x.0.3um", "x.0.5um", "x.1.0um", "x.2.5um", "x.5.um", "x.10.um")
} else {
  colnames(SensorData) <- c("Time", "MQ2_ADC", "LPG_ppm",
                            "MQ4_ADC", "CH4", "MQ5_ADC", "MQ5LPG_ppm",
                            "MQ6_ADC", "MQ6_LPG_ppm", "MQ7_ADC", "H2_ppm" ,
                            "MQ8_ADC", "MQ8H2_ppm", "MQ9_ADC", "CO_ppm", "MQ135_ADC",
                            "U_ppm", "Temp_C*", "Gas_ohms", "Humidity", "Pressure_pa", "CPU_Load")
}

SensorData <- SensorData[!(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData[(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData$Time <- as.POSIXct(SensorData$Time, origin="1970-01-01", tz="GMT")
trialTimes$Time <- as.POSIXct(trialTimes$Time, origin="1970-01-01", tz="GMT")

#names <- c("MQ2_ADC","MQ4_ADC", "MQ5_ADC","MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC", "MQ135_ADC")
names <- c("MQ2","MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9", "MQ135")

for (i in names)
{
  z <- i
  i <- eventName <- paste(toString(i), "ADC", sep="_")
  SensorData["ADC_N"] <- as.data.frame(lapply(SensorData[i], normalize))
  SensorData["Event"] <- NA
  SensorData[1,"Change"] = 0

  #calculation of Change
  print(paste(toString(z), ": Calculating with threshold of", toString(ExpectedChange) ))
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
  print(paste("Finding events for", toString(z)))
  for (row in 1:nrow(SensorData)){
    # abs() for detecting negative change
    # if(abs(SensorData[row,"Change"])>(ExpectedChange)){

    if (SensorData[row,"Change"] > (ExpectedChange)){
      SensorData[row,"Event"] = "True"
      #if (row > 5 && row < (nrow(SensorData)-44)){
      if (row > 5 && row < (nrow(SensorData)-(windowSize - 6))){


        #captures data from 5 points before the event and 44 after
        if (row > EventIndex[nrow(EventIndex),2]){
          #
          #
          EventIndex[subsetCounter,1] = row - 5
          #EventIndex[subsetCounter,2] = row + 44
          EventIndex[subsetCounter,2] = row + (windowSize - 6)
          #
          #
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
  eventsCaptured <- eventsCaptured[,c("Time", "MQ2_ADC","MQ4_ADC", "MQ5_ADC", "MQ6_ADC",  "MQ7_ADC", "MQ8_ADC",  "MQ9_ADC",  "MQ135_ADC",
                                      "Temp_C*", "Gas_ohms", "Humidity", "Pressure_pa")]
  eventTemp <- data.frame()
  events <- data.frame(matrix(NA, nrow = 50))
  events <- events[-c(1)]
  numEvents = nrow(eventsCaptured)/windowSize
  for (eventNum in 1:numEvents){
    eventStart = (windowSize * (eventNum - 1)) + 1
    eventStop = (windowSize * eventNum)
    eventTemp <- as.data.frame(eventsCaptured[eventStart:eventStop,])
    ################################################################################################
    eventTemp[,2:9] <- as.data.frame(lapply(eventTemp[,2:9], normalize))
    #eventTemp[,2:9] <- as.data.frame(lapply(eventTemp[,2:9], scale))

    #eventTemp[,2:ncol(eventTemp)] <- as.data.frame(lapply(eventTemp[,2:ncol(eventTemp)], normalize))
    #eventTemp[,2:ncol(eventTemp)] <- as.data.frame(lapply(eventTemp[,2:ncol(eventTemp)], scale))

    ################################################################################################
    eventTemp["num"] <- seq(length=nrow(eventTemp))
    eventTemp <- melt(eventTemp, id=c("Time","num"))
    events <- cbind(events, eventTemp[,4])
    names(events)[c(ncol(events))] <- paste("Event", toString(eventNum), sep=" ")
  }
  events <- as.data.frame(t(events))

  TimeIndex$Time <- as.POSIXct(TimeIndex$Time, origin="1970-01-01", tz="GMT")

  TimeIndex["Timediff"] <- NA
  row.names(events) <- paste(TimeIndex$Time, "Event")

  for (l in 1:nrow(trialTimes))
  {
    for (m in 1:nrow(TimeIndex))
    {
      TimeIndex[m, "Timediff"] = difftime(trialTimes[l, "Time"], TimeIndex[m, "Time"], units="mins")

      if (abs(TimeIndex[m,"Timediff"]) <= 5){
        rownames(events)[m] <- trialTimes$Chemical[l]
        break
      }
    }
  }

  assign(paste("Index", toString(z), sep = "_"), EventIndex)
  assign(paste("Captured", toString(z), sep = "_"), eventsCaptured)
  assign(paste("Times", toString(z), sep = "_"), TimeIndex)

  write.csv(events, paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), "Events.csv", sep="-"),)
  assign(paste("Events", toString(z), sep = "_"), events)

  eventDF <- events

  #Scree plot
  #wss <- (nrow(eventDF)-1)*sum(apply(eventDF,2,var))
  #for (x in 2:10) wss[x] <- sum(kmeans(eventDF, centers=x)$withinss)
  # png(paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), "ScreePlot.png", sep="-"), width = 600, height = 600)
  # plot(1:10, wss, type="b", main="Scree Plot", xlab="Number of Clusters", ylab="Within groups sum of squares")
  # dev.off()

  k <- round(sqrt(nrow(eventDF)))
  #print(k)

  #km.res <- kmeans(eventDF, k, nstart = 25)
  ##########################################nstart???
  if (kSwitch == TRUE){
    # K-Means Cluster Analysis
    km.res <- kmeans(eventDF, k)
    aggregate(eventDF,by=list(km.res$cluster),FUN=mean)
    eventDF <- data.frame(eventDF, km.res$cluster)
  } else {
    # K-means with pam()
    km.res <- pam(eventDF, k)
    aggregate(eventDF,by=list(km.res$cluster),FUN=mean)
    eventDF <- data.frame(eventDF, km.res$cluster)
  }

  # Ward Hierarchical Clustering
  distance <- dist(eventDF, method = "euclidean") # distance matrix
  fit <- hclust(distance, method="ward.D2")
  groups <- cutree(fit, k)

  #change naming scheme
  png(paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), "Dendrogram.png", sep="-"), width = 1200, height = 600)
  #png("plot.png", width = 1200, height = 600)
  plot(fit, main = paste(toString(z), toString(ExpectedChange), toString(windowSize), "Dendrogram","| Clusters:", toString(k), sep=" "))

  #groups <- cutree(fit, k)
  rect.hclust(fit, k, border="red")
  dev.off()

  #km.res <- kmeans(eventDF, k, nstart = 25)
  png(paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), "FvizCluster.png", sep="-"), width = 800, height = 800)
  fviz_cluster(km.res, eventDF, main = paste(z, "Cluster Plot", "| Clusters:", toString(k)))
  dev.off()
}

end.time <- Sys.time()
total.time <- end.time - start.time

print("Program Completed!")
print(total.time)
#Hunter Tiner