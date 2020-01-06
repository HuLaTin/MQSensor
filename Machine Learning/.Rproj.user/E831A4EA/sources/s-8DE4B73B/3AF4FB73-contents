#graphing
sensorSlim <- SensorData[250:1000,]
SensorData_m <- melt(sensorSlim, id.var="Time", measure.vars=c(colnames(sensorSlim[,c(2,7,9,11,13,15,17,19)])))
plot1 <- ggplot(SensorData_m, aes(x=Time, y=value, color=variable))+
    geom_point(size=.4)


Acetone1 <- SensorData[7:56,]
Acetone1 <- melt(Acetone1, id.var="Time", measure.vars=c(colnames(Acetone1[,c(2,7,9,11,13,15,17,19)])))
Acetone1["num"] <- seq(length=nrow(Acetone1))


Ethanol2 <- SensorData[7675:7724,]
Ethanol2 <- melt(Ethanol2, id.var="Time", measure.vars=c(colnames(Ethanol2[,c(2,7,9,11,13,15,17,19)])))
Ethanol2["num"] <- seq(length=nrow(Ethanol2))

Cyclohexane36 <- SensorData[110228:110277,]
Cyclohexane36 <- melt(Cyclohexane36, id.var="Time", measure.vars=c(colnames(Cyclohexane36[,c(2,7,9,11,13,15,17,19)])))
Cyclohexane36["num"] <- seq(length=nrow(Cyclohexane36))


Acetone1plot <- ggplot(Acetone1, aes(x=num, y=value, color=variable))+
  geom_point(size=1)

Ethanol2plot <- ggplot(Ethanol2, aes(x=num, y=value, color=variable))+
  geom_point(size=1)

Cyclohexane36plot <- ggplot(Cyclohexane36, aes(x=num, y=value, color=variable))+
  geom_point(size=1)

plot1
Acetone1plot
Ethanol2plot
Cyclohexane36plot
