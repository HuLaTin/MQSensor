#Hunter Tiner
#Clustering test

library(svDialogs)
library(factoextra)

set.seed(Sys.time())

#for loop
sensor <- c("MQ2","MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9", "MQ135")

for (i in sensor)
{
  print(i)
  eventName <- paste("Events", toString(i), "ADC", sep = "_")
  eventDF <- get(eventName)

  eventDF <- read.csv(file.choose(), header=TRUE, row.names = 1, sep=",", stringsAsFactors = FALSE)

  # Zero-Variance
  print(which(apply(eventDF, 2, var) == 0))
  eventDF <- eventDF[ - as.numeric(which(apply(eventDF, 2, var) == 0))]

  # Scree Plot
  wss <- (nrow(eventDF)-1)*sum(apply(eventDF,2,var))
  for (x in 2:20) wss[x] <- sum(kmeans(eventDF, centers=x)$withinss)
  plot(1:20, wss, type="b", main="Scree Plot", xlab="Number of Clusters", ylab="Within groups sum of squares")

  #can use Scree plot to help determine number of clusters
  clustnum <- round(sqrt(nrow(eventDF)))
  print(clustnum)

  ############################################################################################################

  # K-Means Cluster Analysis
  kclustering <- kmeans(eventDF, clustnum)
  # append cluster assignment
  events <- data.frame(eventDF, kclustering$cluster)

  events$cluster <- kclustering$cluster
  table(events$cluster)
  events.feature = as.matrix(events)

  #Dendrogram
  hc <- hclust(dist(events.feature), "ave")
  plot(hc, hang = -1, main = paste(i, "Cluster Dendrogram"))

  # Ward Hierarchical Clustering
  d <- dist(events, method = "euclidean") # distance matrix
  fit <- hclust(d, method="ward.D")
  plot(fit, main = paste(i, "Ward Hierarchical Clustering")) # display dendogram

  groups <- cutree(fit, k=clustnum) #k is how many clusters
  rect.hclust(fit, k=clustnum, border="red")

  fviz_cluster(kclustering, data = get(eventDF), main = paste(i, "Cluster Plot"))
}
