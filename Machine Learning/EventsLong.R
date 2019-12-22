library(reshape2)
library(ggplot2)

rownames(eventsCaptured) <- seq(length=nrow(eventsCaptured))
eventsCaptured <- eventsCaptured[,c("Time", "MQ2 ADC","MQ4 ADC", "MQ5 ADC", "MQ6 ADC",  "MQ7 ADC", "MQ8 ADC",  "MQ9 ADC",  "MQ135 ADC",
                                     "Temp (C*)", "Gas ohms", "Humidity", "Pressure pa")]

eventTemp <- data.frame()
events <- data.frame(matrix(NA, nrow = 50))
events <- events[-c(1)]
numEvents = nrow(eventsCaptured)/50
for (eventNum in 1:numEvents){
  #eventNum = 1
  eventStart = (50 * (eventNum - 1)) + 1
  eventStop = (50 * eventNum)
  eventTemp <- as.data.frame(eventsCaptured[eventStart:eventStop,])
  eventTemp["num"] <- seq(length=nrow(eventTemp))
  eventTemp <- melt(eventTemp, id=c("Time","num"))
  eventTemp["num"] <- seq(length=nrow(eventTemp))
  #colnames(eventTemp["value"]) <- c(paste("Event", toString(eventNum), sep=" "))
  events <- cbind(events, eventTemp[,4])
  names(events)[c(ncol(events))] <- paste("Event", toString(eventNum), sep=" ")
  #print(eventNum)
}
events <- as.data.frame(t(events))

#normalize
#events[,1:ncol(events)] <- as.data.frame(lapply(events[,1:ncol(events)], normalize))


# write.csv(events, file = "events.csv")