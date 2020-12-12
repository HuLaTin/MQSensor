# float simNumber(float lower, float upper, float location) {
#   return (((location*100) * (upper - lower) / 100) + lower);
# }



#chemTrim = MQ2_0.03_50_Ethanol_Chem
#y <- "Ethanol"

chemTrim = MQ2_0.03_50_Acetone_Chem
y <- "Acetone"

chemTrim <- chemTrim[-c(1)]
chemData <- data.frame()
simNum <- 11
simData <- data.frame(matrix(NA, nrow=simNum))
simData <- simData[-c(1)]
simData["pred"] <- as.factor(y)
randoNum <- data.frame(runif(simNum, min=0, max=1))

for (x in 1:ncol(chemTrim)) {
  chemData[1,x] <- mean(chemTrim[,x])
  chemData[2:3,x] <- range(chemTrim[,x])

  simData[paste("V", x, sep="")] <- NA
  lower <- chemData[2,x]
  upper <- chemData[3,x]

  for (z in 1:nrow(randoNum)) {
    rLoc <- randoNum[z,]
    simData[z,x+1] <- ((rLoc*100) * (upper - lower) / 100) + lower
  }
}


assign(paste(y, "simPara", sep = "_"), chemData)
assign(paste(y, "simData", sep = "_"), simData)


simTotalData<- rbind(Ethanol_simData, Acetone_simData)

#######################################################################################################
#######################################################################################################


##### Naive Bayes Test ######
nbModel <- naiveBayes(pred ~., data = simTotalData)
nbPredict <- predict(nbModel, dsData[,-1])
table(pred=nbPredict,true=dsData$pred)

CFMat <- confusionMatrix(nbPredict, dsData$pred)
CFMat

#####################################################
#####################################################
### Decision Tree ###

tree <- rpart(pred ~ .,
              data = simTotalData,
              method = "class")

rpart.plot(tree, nn=TRUE)

#probably need to remove column by name instead
treePredict <- predict(object=tree,dsData[-1],type="class")

table(treePredict, dsData$pred)

confusionMatrix(treePredict, dsData$pred)