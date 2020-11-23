#Hunter Tiner

library(reshape2)
library(cluster)
library(factoextra)
library(dplyr)
library(rpart)
library(rpart.plot)
library(e1071)
library(caTools)
library(caret)

normalize <- function(x)
{
  return ((x - min(x)) / (max(x) - min(x)))
}


#Set directory
infileCSVone <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "Data", "Joulesv2_20201122_SL.csv")
infileCSVtwo <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "Data", "V2TrialTimes.csv")
output <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "eventsOutput")
ExpectedChange <- as.double(.03)
windowSize <- as.integer(50)
#k <- as.integer(5)

#Kmeans = TRUE / PAM = FALSE
kSwitch <- TRUE

SensorData <- read.csv(infileCSVone, header = TRUE, sep=",", stringsAsFactors = FALSE)
trialTimes <- read.csv(infileCSVtwo, header = TRUE, sep=",", stringsAsFactors = FALSE)

set.seed(Sys.time())

for (row in 1:nrow(trialTimes))
{
  #print(paste(trialTimes[row,"Chemical"], row, sep="-"))
  trialTimes[row, "Chemical"] <- paste(trialTimes[row,"Chemical"], row, sep="-")
}

print(head(SensorData))

#Sets column names.
colnames(SensorData) <- c("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Gas_ohms", "Humidity",
                          "Pressure_pa", "CPU_Load", "Throttled")

SensorData <- SensorData[ -c(14, 15) ]


SensorData <- SensorData[!(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData[(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData$Time <- as.POSIXct(SensorData$Time, origin="1970-01-01", tz="GMT")
trialTimes$Time <- as.POSIXct(trialTimes$Time, origin="1970-01-01", tz="GMT")

names <- c("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")

for (i in names)
{
  z <- i
  i <- eventName <- paste(toString(i), "ADC", sep="_")
  SensorData["ADC_N"] <- as.data.frame(lapply(SensorData[i], normalize))
  SensorData["Event"] <- NA
  SensorData[1,"Change"] = 0

  ##################################################
  #program for moving averages?
  ##################################################

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
      if (row > 5 && row < (nrow(SensorData)-(windowSize - 6))){

        if (row > EventIndex[nrow(EventIndex),2]){
          #
          #
          EventIndex[subsetCounter,1] = row - 5
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
  eventsCaptured = SensorData[EventIndex[1,1]:EventIndex[1,2],1:13]
  while(1){
    eventStart = EventIndex[eventNumber, 1]
    eventEnd = EventIndex[eventNumber, 2]
    eventsCaptured <- rbind(eventsCaptured, SensorData[eventStart:eventEnd,1:13])

    if (eventNumber == nrow(EventIndex))
      break
    eventNumber = eventNumber + 1

  }
  rownames(eventsCaptured) <- seq(length=nrow(eventsCaptured))

  ###############################################################
  #when trying to normalize or scale ALL columns NAs are created.
  ##############################################################

  #This removes ohms and pressure
  #eventsCaptured <- eventsCaptured[-c(11,13)]

  eventTemp <- data.frame()
  events <- data.frame(matrix(NA, nrow = windowSize))
  events <- events[-c(1)]
  numEvents = nrow(eventsCaptured)/windowSize
  for (eventNum in 1:numEvents){
    eventStart = (windowSize * (eventNum - 1)) + 1
    eventStop = (windowSize * eventNum)
    eventTemp <- as.data.frame(eventsCaptured[eventStart:eventStop,])
    ################################################################################################

    #eventTemp[,2:9] <- as.data.frame(scale(eventTemp[,2:9]))
    #eventTemp[,2:9] <- as.data.frame(lapply(eventTemp[,2:9], normalize))
    #eventTemp[,2:ncol(eventTemp)] <- as.data.frame(scale(eventTemp[,2:ncol(eventTemp)]))
    #eventTemp[,2:ncol(eventTemp)] <- as.data.frame(lapply(eventTemp[,2:ncol(eventTemp)], normalize))

    ################################################################################################
    eventTemp["num"] <- seq(length=nrow(eventTemp))
    eventTemp <- melt(eventTemp, id=c("Time","num"))
    events <- cbind(events, eventTemp[,4])
    names(events)[c(ncol(events))] <- paste("Event", toString(eventNum), sep=" ")
  }
  #which(is.na(events))
  events <- as.data.frame(t(events))

  TimeIndex$Time <- as.POSIXct(TimeIndex$Time, origin="1970-01-01", tz="GMT")

  TimeIndex["Timediff"] <- NA
  events["Ident"] <- 0

  row.names(events) <- paste(TimeIndex$Time, "Event")

  for (l in 1:nrow(trialTimes))
  {
    for (m in 1:nrow(TimeIndex))
    {
      TimeIndex[m, "Timediff"] = difftime(trialTimes[l, "Time"], TimeIndex[m, "Time"], units="mins")

      if (abs(TimeIndex[m,"Timediff"]) <= 5){
        rownames(events)[m] <- trialTimes$Chemical[l]
        events[m, "Ident"] <- 1
        break
      }
    }
  }

  eventsTrim <- subset(events, Ident=='1')
  events <- subset(events, select = -c(Ident))
  eventsTrim <- subset(eventsTrim, select = -c(Ident))

  assign(paste("Index", toString(z), sep = "_"), EventIndex)
  assign(paste("Captured", toString(z), sep = "_"), eventsCaptured)
  assign(paste("Times", toString(z), sep = "_"), TimeIndex)


  Events <- paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), "Events.csv", sep="-")
  write.csv(events, paste(output, Events, sep = "/"),)
  assign(paste("Events", toString(z), sep = "_"), events)

  EventsTrim <- paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), "EventsTrim.csv", sep="-")
  write.csv(eventsTrim, paste(output, EventsTrim, sep = "/"),)
  assign(paste("EventsTrim", toString(z), sep = "_"), eventsTrim)

  eventList <- c("events", "eventsTrim")

  ###############
  #Some Machine learning bits
  ###############
  for (i in eventList)
  {
    events <- get(i)

    idx_Acetone <- events[grep("Acetone", rownames(events)), ]
    idx_Ethanol <- events[grep("Ethanol", rownames(events)), ]
    #idx_Cyclohexane <- events[grep("Cyclohexane", rownames(events)), ]

    #dsNum <- min(nrow(idx_Acetone), nrow(idx_Ethanol), nrow(idx_Cyclohexane))
    dsNum <- min(nrow(idx_Acetone), nrow(idx_Ethanol))


    dsAce <- sample_n(idx_Acetone, dsNum)
    dsEth <- sample_n(idx_Ethanol, dsNum)
    #dsCyc <- sample_n(idx_Cyclohexane, dsNum)

    dsAce["pred"] <- as.factor("Acetone")
    dsEth["pred"] <- as.factor("Ethanol")
    #dsCyc["pred"] <- as.factor("Cyclohexane")

    #dsData <- rbind(dsAce, dsEth, dsCyc)
    dsData <- rbind(dsAce, dsEth)


    #do we need to randomize the rows here?
    #just in case...

    rows <- sample(nrow(dsData))
    dsData <- dsData[rows, ]

    dsData <- dsData[c(501,1:500)]

    ### Need to build training and test sets ###


    ######################################################################
    ### need to create a train/test sets for this part!!! ###
    ### can use a GREP? ###

    ##### Naive Bayes Test ######
    ##### Need to balance sets ####
    nbModel <- naiveBayes(pred ~., data = dsData)
    nbPredict <- predict(nbModel, test[,-1])
    table(pred=nbPredict,true=eventDF$Event)

    confusionMatrix(nbPredict, eventDF$Event)


    ### Decision Tree ###
    ### also awaiting balanced sets ###
    ### this S#its gonna be so tight when it works ###

    ##################################################
    treeTest <- rpart(
      pred~.,
      data = dsData,
      method = "class",
      minsplit = 5,
      minbucket = 5,
      cp = -1
    )

    rpart.plot(treeTest, nn=TRUE)
    ##################################################

    tree <- rpart(pred ~ .,
                  data = dsData,
                  method = "class")

    rpart.plot(tree, nn=TRUE)

    #probably need to remove column by name instead
    treePredict <- predict(object=tree,dsData[-1],type="class")

    table(treePredict, dsData$pred)

    confusionMatrix(treePredict, dsData$pred)

    ####################################################################

    eventDF <- events
    eventHeat <- as.matrix(eventDF)

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

    #####################################################################

    # Ward Hierarchical Clustering
    distance <- dist(eventDF, method = "euclidean") # distance matrix
    fit <- hclust(distance, method="ward.D2")
    groups <- cutree(fit, k)

    png(paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), toString(i), "Dendrogram.png", sep="-"), width = 1200, height = 600)
    plot(fit, main = paste(toString(z), toString(ExpectedChange), toString(windowSize), "Dendrogram","| Clusters:", toString(k), sep=" "))

    #groups <- cutree(fit, k)
    rect.hclust(fit, k, border="red")
    dev.off()

    #km.res <- kmeans(eventDF, k, nstart = 25)
    png(paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), toString(i), "FvizCluster.png", sep="-"), width = 800, height = 800)
    print(fviz_cluster(km.res, eventDF, main = paste(z, "Cluster Plot", "| Clusters:", toString(k))))
    dev.off()

    #d3heatmap or heatmaply
    my_palette <- colorRampPalette(c("red", "yellow", "green"))(n = 300)
    png(paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), toString(i), "HeatMap.png", sep="-"), width = 1600, height = 1200)
    print(heatmap(eventHeat[,], main = paste(z, "Heat Map"),col=my_palette))
    #print(heatmap(eventDF[,150:210], main = paste(z, "Heat Map")))
    dev.off()
  }
}
