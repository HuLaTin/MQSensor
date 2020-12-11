#This function returns the first appearing set of modes.
#https://stackoverflow.com/questions/2547402/how-to-find-the-statistical-mode
# Mode <- function(x) {
#   ux <- unique(x)
#   ux[which.max(tabulate(match(x, ux)))]
# }

#This will return all modes
# Modes <- function(x) {
#   ux <- unique(x)
#   tab <- tabulate(match(x, ux))
#   ux[tab == max(tab)]
# }

chemTrim = MQ2_0.03_50_Ethanol_Chem
y <- "Ethanol"

# chemTrim = MQ2_0.03_50_Acetone_Chem
# y <- "Acetone"

chemTrim <- chemTrim[-c(1)]
chemData <- data.frame()
simNum <- 15
simData <- data.frame(matrix(NA, nrow=simNum))
simData <- simData[-c(1)]
simData["pred"] <- as.factor(y)

for (x in 1:ncol(chemTrim)) {
  chemData[1,x] <- mean(chemTrim[,x])
  chemData[2:3,x] <- range(chemTrim[,x])
  simData <- cbind(simData, data.frame(runif(simNum, min = chemData[2,x], max = chemData[3,x])))
}

for (x in 2:ncol(simData)) {
  #print(colnames(simData[x]))
  colnames(simData)[x] <-  paste("V", x-1, sep = "")

}

assign(paste(y, "simPara", sep = "_"), chemTrim)
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
