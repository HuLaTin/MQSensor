
simNum <- 10

sensor <- "MQ2"
threshold <- 0.03
windowSize <- 50

chems <- c("Acetone", "Ethanol")

testData <- data.frame()

for (y in chems) {
  chemTrim <- get(paste(sensor,threshold,windowSize,y,"Chem", sep="_"))
  colNamedf <- as.data.frame(colnames(chemTrim))
  hD <- chemTrim

  set.seed(Sys.time())
  chemTrim <- chemTrim[-c(1)]
  chemData <- data.frame()
  simData <- data.frame(matrix(NA, nrow=simNum))
  simData <- simData[-c(1)]
  simData["pred"] <- as.factor(y)
  randoNum <- data.frame(runif(simNum, min=0, max=1))
  deviData <- data.frame()

  for (x in 1:ncol(chemTrim)) {
    chemData[1,x] <- mean(chemTrim[,x])

    for (z in 1:nrow(chemTrim)) {
      deviData[z,x] <- (chemTrim[z,x] - chemData[1,x])^2
    }

    chemData[2,x]  <- (sqrt(sum(deviData[,x])/nrow(deviData)))*2 #2 standard deviations
    #chemData[2,x]  <- sqrt(sum(deviData[,x])/nrow(deviData)) #1 standard deviation


    simData[paste(colNamedf[x+1,], sep="")] <- NA

    lower <- chemData[1,x]-chemData[2,x]
    upper <- chemData[1,x]+chemData[2,x]

    for (z in 1:nrow(randoNum)) {
      rLoc <- randoNum[z,]
      simData[z,x+1] <- ((rLoc*100) * (upper - lower) / 100) + lower
    }
  }

  testData <- rbind(hD, testData)
  assign(paste(y, "simPara", sep = "_"), chemData)
  assign(paste(y, "simData", sep = "_"), simData)

}

################
simTotalData <- data.frame()
for (y in chems) {
  chemSim <- paste(y, "simData", sep="_")
  simTotalData <- rbind(get(chemSim), simTotalData)
}

#######################################################################################################

##### Naive Bayes Test ######
nbModel <- naiveBayes(pred ~., data = simTotalData)
nbPredict <- predict(nbModel, testData[,-1])
table(pred=nbPredict,true=testData$chem)

CFMat <- confusionMatrix(nbPredict, testData$chem)
CFMat

write.csv(simTotalData, "simData.csv", row.names = FALSE)
write.csv(testData, "testData.csv", row.names = FALSE)

#####################################################
#####################################################
### Decision Tree ###

tree <- rpart(pred ~ .,
              data = simTotalData,
              method = "class")

rpart.plot(tree, nn=TRUE)

#probably need to remove column by name instead
treePredict <- predict(object=tree,testData[-1],type="class")

table(treePredict, testData$chem)

confusionMatrix(treePredict, testData$chem)


########################################################################
#This was used to see if our simulated data followed the deviation stuff
# ######################################################################
# chemData <- data.frame()
# deviData <- data.frame()
# simData <- simData[-c(1)]
#
# for (x in 1:ncol(simData)) {
#   chemData[1,x] <- mean(simData[,x])
#
#   #Standard deviation
#   for (w in 1:nrow(simData)) {
#     deviData[w,x] <- (simData[w,x] - chemData[1,x])^2
#     #print(x)
#     #print(w)
#   }
#
#   #chemData[2,x]  <- (sqrt(sum(deviData[,x])/nrow(deviData)))*3 #3 standard deviations
#   chemData[2,x]  <- (sqrt(sum(deviData[,x])/nrow(deviData)))*2 #2 standard deviations
#   #chemData[2,x]  <- sqrt(sum(deviData[,x])/nrow(deviData)) #1 standard deviation
#
# }
# a=0
# for (w in 1:nrow(simData)) {
#   q=0
#   for (x in 1:ncol(simData)) {
#     chemData[3,x] <- simData[w,x]
#     #chemData[4,x] <- (chemData[3,x] - chemData[1,x])
#
#     if ((chemData[3,x]>(chemData[1,x]+chemData[2,x])) || (chemData[3,x]<(chemData[1,x]-chemData[2,x]))) {
#       q <- q+1
#     }
#   }
#   if (q>=60) {
#     a <- a+1
#     #q would be compared to some threshold decided here
#     #should be a percentage of windowsize*ncol(SensorData)-1
#     #this way it will always be the same fraction of the amount of readings
#
#     #print(rownames(trimTemp[w,]))
#     #print(paste(rownames(deviData[w,]), "has reached threshold q", sep=" "))
#     #drop row??
#   }
# }
# print(a)
##############################################