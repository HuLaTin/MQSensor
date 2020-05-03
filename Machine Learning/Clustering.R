library(svDialogs)
library(factoextra)

set.seed(Sys.time())

#for loop
sensor <- c("MQ2","MQ4", "MQ5","MQ6", "MQ7", "MQ8", "MQ9", "MQ135")

for (i in sensor)
{
print(i)
#sensorName <- toString(dlgInput("Which sensor?", default = "MQ2", Sys.info()["user"])$res)
#sensorName <- sensorName
sensorName <- i
eventName <- paste("Events", toString(sensorName), "ADC", sep = "_")

#get(sensorName)

# Determine number of clusters
# wss <- (nrow(get(sensorName))-1)*sum(apply(get(sensorName),2,var))
# for (i in 2:nrow(get(sensorName)))
# wss[i] <- sum(kmeans(get(sensorName), centers=i)$withinss)
# plot(1:nrow(get(sensorName)), wss, type="b", xlab="Number of Clusters", ylab="Within groups sum of squares")

clustnum <- sqrt(nrow(get(eventName)))
clustnum <- round(clustnum)

#print number of clusters
clustnum


# K-Means Cluster Analysis
kclustering <- kmeans(get(eventName), clustnum)

#str(kclustering)
fviz_cluster(kclustering, data = get(eventName), main = paste(sensorName, "Cluster Plot"))

# get cluster means
#aggregate(get(sensorName),by=list(kclustering$cluster),FUN=mean)

# append cluster assignment
events <- data.frame(get(eventName), kclustering$cluster)

#data points in each group
#kclustering$size

events$cluster <- kclustering$cluster
table(events$cluster)
events.feature = as.matrix(events)

#Dendrogram
hc <- hclust(dist(events.feature), "ave")
plot(hc, hang = -1, main = paste(sensorName, "Cluster Dendrogram"))

# Ward Hierarchical Clustering
d <- dist(events, method = "euclidean") # distance matrix
fit <- hclust(d, method="ward.D")
plot(fit, main = paste(sensorName, "Ward Hierarchical Clustering")) # display dendogram

groups <- cutree(fit, k=clustnum) # cut tree into 7 clusters
rect.hclust(fit, k=clustnum, border="red")

#Heatmap
# library(gplots)
# library(RColorBrewer)
# my_palette <- colorRampPalette(c("green", "black", "red"))(n = 1000)
# heatmap.2(events.feature,col=my_palette, dendrogram = "row", trace = "none", key = 5,
#           cexCol = .8, margin = c(4,4), cexRow = .5, symbreaks = FALSE)

}
