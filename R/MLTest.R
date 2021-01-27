#Hunter Tiner

suppressMessages(library(reshape2, quietly = TRUE))
suppressMessages(library(cluster, quietly = TRUE))
suppressMessages(library(factoextra, quietly = TRUE))
suppressMessages(library(dplyr, quietly = TRUE))
suppressMessages(library(rpart, quietly = TRUE))
suppressMessages(library(rpart.plot, quietly = TRUE))
suppressMessages(library(e1071, quietly = TRUE))
suppressMessages(library(caTools, quietly = TRUE))
suppressMessages(library(caret, quietly = TRUE))

normalize <- function(x)
{
  return ((x - min(x)) / (max(x) - min(x)))
}


#Set directory
infileCSVone <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "Data", "Joulesv2_20201208_SL.csv")
infileCSVtwo <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "Data", "V2TrialTimes.csv")
output <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "eventsOutput")
ExpectedChange <- as.double(.035)
windowSize <- as.integer(30)

SensorData <- read.csv(infileCSVone, header = TRUE, sep=",", stringsAsFactors = FALSE)
trialTimes <- read.csv(infileCSVtwo, header = TRUE, sep=",", stringsAsFactors = FALSE)

expectedEvents <- nrow(trialTimes)

set.seed(Sys.time())

chems <- unique(trialTimes[,"Chemical"])

#this numbers the Chemicals events
for (row in 1:nrow(trialTimes))
{
  trialTimes[row, "Chemical"] <- paste(trialTimes[row,"Chemical"], row, sep="-")
}

#Sets column names.
colnames(SensorData) <- c("Time", "MQ2_ADC", "MQ3_ADC", "MQ4_ADC", "MQ5_ADC",
                          "MQ6_ADC", "MQ7_ADC", "MQ8_ADC", "MQ9_ADC",
                          "Temp_C*", "Gas_ohms", "Humidity",
                          "Pressure_pa", "CPU_Load", "Throttled")

#remove CPU_Load and Throttled from our dataset.
SensorData <- SensorData[ -c(14, 15) ]


SensorData <- SensorData[!(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData$Time <- as.POSIXct(SensorData$Time, origin="1970-01-01", tz="GMT")
trialTimes$Time <- as.POSIXct(trialTimes$Time, origin="1970-01-01", tz="GMT")

parameterdf <- data.frame(expected=NA, true=NA, False=NA, Total=NA)[0, ]


names <- c("MQ2", "MQ3", "MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9")

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

  #this would remove everything but sensors
  #eventsCaptured <- eventsCaptured[-c(10:ncol(eventsCaptured))]

  #This removes ohms and pressure
  #eventsCaptured <- eventsCaptured[-c(11,13)]
  ##############################################################

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
    #This sets the fraction of values to look for, outside of the sd range we select later
    sdThresh <- ((ncol(eventTemp)-1)*windowSize)*.25
    ###
    eventTemp["num"] <- seq(length=nrow(eventTemp))
    eventTemp <- melt(eventTemp, id=c("Time","num"))

    #not sure what this line is for...
    #rowNameFrame <- data.frame()
    events <- cbind(events, eventTemp[,4])

    for (b in 1:nrow(eventTemp)) {
      row.names(events)[b] <- paste(eventTemp[b,3], eventTemp[b,2], sep="_")
    }

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

  if (nrow(eventsTrim)>0) {
    EventsTrim <- paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), "EventsTrim.csv", sep="-")
    write.csv(eventsTrim, paste(output, EventsTrim, sep = "/"),)
    assign(paste("EventsTrim", toString(z), sep = "_"), eventsTrim)
  }

  parameters <- paste(toString(z), toString(ExpectedChange), toString(windowSize), sep=" ")
  eventsTrue <- nrow(eventsTrim)
  eventsTotal <- nrow(events)
  eventsFalse <- (eventsTotal - eventsTrue)

  paraTemp <- data.frame(expectedEvents, eventsTrue, eventsFalse, eventsTotal, row.names = parameters)
  parameterdf <- rbind(paraTemp, parameterdf)

  if (nrow(eventsTrim)>0) {
    for (y in chems) {
      if (nrow(eventsTrim[grep(y, rownames(eventsTrim)), ])>0) {

        trimTemp <- eventsTrim[grep(y, rownames(eventsTrim)), ]


        ##########################################################################################################################
        #chemTrim = trimTemp
        #chemTrim <- chemTrim[-c(1)]
        chemData <- data.frame()
        deviData <- data.frame()

        for (x in 1:ncol(trimTemp)) {
          chemData[1,x] <- mean(trimTemp[,x])

          #Standard deviation
          for (w in 1:nrow(trimTemp)) {
            deviData[w,x] <- (trimTemp[w,x] - chemData[1,x])^2
          }

          #chemData[2,x]  <- (sqrt(sum(deviData[,x])/nrow(deviData)))*3 #3 standard deviations
          chemData[2,x]  <- (sqrt(sum(deviData[,x])/nrow(deviData)))*2 #2 standard deviations
          #chemData[2,x]  <- sqrt(sum(deviData[,x])/nrow(deviData)) #1 standard deviation

        }


        for (w in 1:nrow(trimTemp)) {
          q=0
          for (x in 1:ncol(trimTemp)) {
            chemData[3,x] <- trimTemp[w,x]

            if ((chemData[3,x]>(chemData[1,x]+chemData[2,x])) || (chemData[3,x]<(chemData[1,x]-chemData[2,x]))) {
              q <- q+1
              #print(q)
            }
          }
          if (q>=sdThresh) {
            #q would be compared to some threshold decided here
            #should be a percentage of windowsize*ncol(SensorData)-1
            #this way it will always be the same fraction of the amount of readings

            #print(rownames(trimTemp[w,]))
            print(paste(rownames(trimTemp[w,]), "is looking wack! Maybe You should remove it.", sep=" "))
            #drop row??
          }

        }

        rownames(trimTemp) = NULL
        trimTemp <- cbind("chem" = y, trimTemp)
        ##########################################################################################################################

        assign(paste(toString(z), toString(ExpectedChange), toString(windowSize), toString(y), "Chem",sep = "_"), trimTemp)


      }
    }
  }



  eventList <- c("events", "eventsTrim")

  ###############
  #Some Machine learning bits
  ###############

  for (i in eventList)
  {
    events <- get(i)

    if (i == "eventsTrim" && nrow(eventsTrim)>0) {

      desired_length <- length(chems)
      list <- vector(mode = "list", length = desired_length)

      for (y in chems){
        list[[y]] <- nrow(events[grep(y, rownames(events)), ])
        #dat <- nrow(events[grep(y, rownames(events)), ])
      }

      dsNum <- min(unlist(list))

      #not sure if this is needed anymore
      if (dsNum <= 1){
        next
      }

      dsData <- data.frame()
      for (y in chems) {
        #print(y)

        idx_chem <- events[grep(y, rownames(events)), ]
        idx_chem["pred"] <- as.factor(y)
        data <- sample_n(idx_chem, dsNum)

        dsData <- rbind(dsData, data)
      }

      dsData <- dsData[,c(ncol(dsData),1:(ncol(dsData)-1))]

      ############################################################################
      ############################################################################

      ### Creation of test and training sets ###
      sample <- sample.split(dsData$pred, SplitRatio = .7)
      train <- subset(dsData, sample == TRUE)
      test  <- subset(dsData, sample == FALSE)

      ##### Naive Bayes Test ######
      nbModel <- naiveBayes(pred ~., data = train)
      nbPredict <- predict(nbModel, test[,-1])
      table(pred=nbPredict,true=test$pred)

      CFMat <- confusionMatrix(nbPredict, test$pred)
      assign(paste(toString(i), "NBMat", sep = "_"), CFMat)


      ### Decision Tree ###
      ### this S#its gonna be so tight when it works ###

      tree <- rpart(pred ~ .,
                    data = train,
                    method = "class")

      rpart.plot(tree, nn=TRUE)

      #probably need to remove column by name instead
      treePredict <- predict(object=tree,test[-1],type="class")

      table(treePredict, test$pred)

      confusionMatrix(treePredict, test$pred)

    }

    # eventDF <- events
    # eventHeat <- as.matrix(eventDF)
    #
    # k <- round(sqrt(nrow(eventDF)))
    # #print(k)
    #
    # #km.res <- kmeans(eventDF, k, nstart = 25)
    # ##########################################nstart???
    # if (kSwitch == TRUE){
    #   # K-Means Cluster Analysis
    #   km.res <- kmeans(eventDF, k)
    #   aggregate(eventDF,by=list(km.res$cluster),FUN=mean)
    #   eventDF <- data.frame(eventDF, km.res$cluster)
    # } else {
    #   # K-means with pam()
    #   km.res <- pam(eventDF, k)
    #   aggregate(eventDF,by=list(km.res$cluster),FUN=mean)
    #   eventDF <- data.frame(eventDF, km.res$cluster)
    # }
    #
    # #####################################################################
    #
    # # Ward Hierarchical Clustering
    # distance <- dist(eventDF, method = "euclidean") # distance matrix
    # fit <- hclust(distance, method="ward.D2")
    # groups <- cutree(fit, k)
    #
    # # Events <- paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), "Events.csv", sep="-")
    # # write.csv(events, paste(output, Events, sep = "/"),)
    #
    # dendro <- paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), toString(i), "Dendrogram.png", sep="-")
    # png(paste(output, dendro, sep = "/"), width = 1200, height = 600)
    # plot(fit, main = paste(toString(z), toString(ExpectedChange), toString(windowSize), "Dendrogram","| Clusters:", toString(k), sep=" "))
    #
    # #groups <- cutree(fit, k)
    # rect.hclust(fit, k, border="red")
    # dev.off()
    #
    # #km.res <- kmeans(eventDF, k, nstart = 25)
    # fvizclust<- paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), toString(i), "FvizCluster.png", sep="-")
    # png(paste(output, fvizclust, sep = "/"), width = 800, height = 800)
    # print(fviz_cluster(km.res, eventDF, main = paste(z, "Cluster Plot", "| Clusters:", toString(k))))
    # dev.off()
    #
    # #d3heatmap or heatmaply
    # my_palette <- colorRampPalette(c("red", "yellow", "green"))(n = 300)
    # heatMap <- paste(toString(Sys.Date()), toString(z), toString(ExpectedChange), toString(windowSize), toString(i), "HeatMap.png", sep="-")
    # png(paste(output, heatMap, sep = "/"), width = 1600, height = 1200)
    # print(heatmap(eventHeat[,], main = paste(z, "Heat Map"),col=my_palette))
    # #print(heatmap(eventDF[,150:210], main = paste(z, "Heat Map")))
    # dev.off()
  }
}
parameterdf <- parameterdf[rev(seq_len(nrow(parameterdf))), , drop = FALSE]


write.csv(parameterdf, paste(Sys.Date(), ExpectedChange, windowSize, "paraDF", sep="_"))
