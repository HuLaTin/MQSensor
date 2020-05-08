#Hunter Tiner
#Clustering test

library(svDialogs)
library(cluster)
library(factoextra)
#library(fpc)

set.seed(Sys.time())
magicSwitch <- TRUE

sensor <- c("MQ2","MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9", "MQ135")

for (i in sensor)
{
  print(i)
  eventName <- paste("Events", toString(i), "ADC", sep = "_")
  eventDF <- get(eventName)

  eventDF <- read.csv(file.choose(), header=TRUE, row.names = 1, sep=",", stringsAsFactors = FALSE)

  # Zero-Variance
  #print(which(apply(eventDF, 2, var) == 0))
  #if there aren't any columns returned it breaks dataframe
  #eventDF <- eventDF[ - as.numeric(which(apply(eventDF, 2, var) == 0))]

  # Scree Plot
  wss <- (nrow(eventDF)-1)*sum(apply(eventDF,2,var))
  for (x in 2:10) wss[x] <- sum(kmeans(eventDF, centers=x)$withinss)
  plot(1:10, wss, type="b", main="Scree Plot", xlab="Number of Clusters", ylab="Within groups sum of squares")

  #can use Scree plot to help determine number of clusters
  k <- round(sqrt(nrow(eventDF)))
  print(k)

  #km.res <- kmeans(eventDF, k, nstart = 25)
  #nstart???
  if (magicSwitch == TRUE){
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

  ############################################################################################################

  # A robust version of K-means based on mediods can be invoked by using pam( ) instead of kmeans( ).
  # The function pamk( ) in the fpc package is a wrapper for pam that also prints the suggested number of clusters based on optimum average silhouette width.

  # investigate clara()

  ############################################################################################################

  # Ward Hierarchical Clustering
  distance <- dist(eventDF, method = "euclidean") # distance matrix
  fit <- hclust(distance, method="ward.D2")
  groups <- cutree(fit, k)


  #change naming scheme
  png(paste(toString(Sys.Date()), toString(i), toString(ExpectedChange), toString(windowSize), "Dendrogram.png", sep="-"), width = 1200, height = 600)
  #png("plot.png", width = 1200, height = 600)
  plot(fit, main = paste(toString(i), toString(ExpectedChange), toString(windowSize), "Dendrogram", sep=" "))

  #groups <- cutree(fit, k)
  rect.hclust(fit, k, border="red")
  dev.off()

  #km.res <- kmeans(eventDF, k, nstart = 25)
  png(paste(toString(Sys.Date()), toString(i), toString(ExpectedChange), toString(windowSize), "FvizCluster.png", sep="-"), width = 800, height = 800)
  fviz_cluster(km.res, eventDF, main = paste(i, "Cluster Plot"))
  dev.off()
}
#Hunter Tiner
