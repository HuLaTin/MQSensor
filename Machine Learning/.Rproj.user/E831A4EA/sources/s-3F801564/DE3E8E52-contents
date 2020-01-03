
#write.csv(events, file = "events.csv")
#events <- read.csv("events.csv", header=TRUE, sep=",")
#events <- events[-c(1)]
#events <- events[,51:100]


#normalize
#print("The 'events' data frame will be normalized and transposed.")
#events[,1:ncol(events)] <- as.data.frame(lapply(events[,1:ncol(events)], normalize))
#events <- as.data.frame(t(events))

rownames(events) <- c("1-Acetone", "2-Ethanol", "3-Acetone", "4-Ethanol", "5-Acetone", "6-Acetone",
                      "7-Ethanol", "8-Acetone", "9-Ethanol", "10-Acetone", "11-Ethanol", "12-Acetone",
                      "13-Unknown", "14-Unknown", "15-Ethanol", "16-Unknown", "17-Unknown", "18-Unknown",
                      "19-Unknown", "20-Unknown", "21-Unknown", "22-Unknown", "23-Ethanol", "24-Ethanol",
                      "25-Unknown", "26-Ethanol", "27-Unknown", "28-Ethanol", "29-Ethanol", "30-Ethanol",
                      "31-Ethanol", "32-Ethanol", "33-Ethanol", "34-Unknown", "35-Ethanol", "36-Cyclohexane",
                      "37-Cyclohexane", "38-Cyclohexane", "39-Cyclohexane", "40-Unknown", "41-Cyclohexane",
                      "42-Cyclohexane", "43-Unknown", "44-Unknown", "45-Unknown", "46-Unknown", "47-Unknown")

set.seed(100)

# Determine number of clusters
wss <- (nrow(events)-1)*sum(apply(events,2,var))
for (i in 2:84) wss[i] <- sum(kmeans(events, centers=i)$withinss)
plot(1:84, wss, type="b", xlab="Number of Clusters", ylab="Within groups sum of squares")


# K-Means Cluster Analysis
kclustering <- kmeans(events, 9)
str(kclustering)
library(factoextra)
fviz_cluster(kclustering, data = events)

# get cluster means
aggregate(events,by=list(kclustering$cluster),FUN=mean)
# append cluster assignment
events <- data.frame(events, kclustering$cluster)

#data points in each group
kclustering$size

events$cluster <- kclustering$cluster
table(events$cluster)
events.feature = as.matrix(events)

#Dendrogram
hc <- hclust(dist(events.feature), "ave")
plot(hc, hang = -1)


# Ward Hierarchical Clustering
d <- dist(events, method = "euclidean") # distance matrix
fit <- hclust(d, method="ward")
plot(fit) # display dendogram
groups <- cutree(fit, k=5) # cut tree into 7 clusters
# draw dendogram with red borders around the 7 clusters
rect.hclust(fit, k=5, border="red")

#Heatmap
library(gplots)
library(RColorBrewer)
my_palette <- colorRampPalette(c("green", "black", "red"))(n = 1000)
heatmap.2(events.feature,col=my_palette, dendrogram = "row", trace = "none", key = 5,
          cexCol = .8, margin = c(4,4), cexRow = .5, symbreaks = FALSE)


