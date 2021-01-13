args <- commandArgs(trailingOnly = FALSE)
print(args)

outDir = args[4]

infileCSVone = args[5]


#infileCSVone <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "thru20200312Joules.csv")
SensorData <- read.csv(infileCSVone, header = TRUE, sep=",")

if (ncol(SensorData) == 34){
  colnames(SensorData) <- c("Time", "MQ2_ADC", "LPG_ppm",
                            "MQ4_ADC", "CH4", "MQ5_ADC", "MQ5LPG_ppm",
                            "MQ6_ADC", "MQ6_LPG ppm", "MQ7_ADC", "H2_ppm" ,
                            "MQ8_ADC", "MQ8H2_ppm", "MQ9_ADC", "CO_ppm", "MQ135_ADC",
                            "U_ppm", "Temp_C*", "Gas_ohms", "Humidity", "Pressure_pa",
                            "CPU_Load", "PM1.0_CF.1", "PM2.5_CF.1", "PM10_CF.1", "PM1.0_STD",
                            "PM2.5_STD", "PM10_STD", "x.0.3um", "x.0.5um", "x.1.0um", "x.2.5um", "x.5.um", "x.10.um")
} else {
  colnames(SensorData) <- c("Time", "MQ2_ADC", "LPG_ppm",
                            "MQ4_ADC", "CH4", "MQ5_ADC", "MQ5LPG_ppm",
                            "MQ6_ADC", "MQ6_LPG_ppm", "MQ7_ADC", "H2_ppm" ,
                            "MQ8_ADC", "MQ8H2_ppm", "MQ9_ADC", "CO_ppm", "MQ135_ADC",
                            "U_ppm", "Temp_C*", "Gas_ohms", "Humidity", "Pressure_pa", "CPU_Load")
}
SensorData <- SensorData[,c("Time", "MQ2_ADC", "MQ4_ADC", "MQ5_ADC", "MQ6_ADC", "MQ7_ADC",
                            "MQ8_ADC", "MQ9_ADC", "MQ135_ADC", "Temp_C*", "Gas_ohms", "Humidity", "Pressure_pa", "CPU_Load")]

SensorData <- SensorData[!(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData[(is.na(SensorData$Time) | SensorData$Time==""), ]
SensorData$Time <- as.POSIXct(SensorData$Time, origin="1970-01-01", tz="GMT")

AvgSensor <- SensorData

names <- c("MQ2_ADC", "MQ4_ADC", "MQ5_ADC", "MQ6_ADC", "MQ7_ADC","MQ8_ADC", "MQ9_ADC", "MQ135_ADC", "Temp_C*", "Gas_ohms", "Humidity", "Pressure_pa", "CPU_Load")

for (i in names)
{
  print(i)
  for (row in 3:(nrow(SensorData)-2))
  {

    #print(SensorData[i])
    startRow <- row-2
    endRow <- row+2

    # print(row)
    # print(startRow)
    # print(endRow)

    AvgSensor[row,i] <- mean(SensorData[startRow:endRow,i])

    # if (row >= 100)
    #   break()

  }
}

#drop unaverage rows
AvgSensor <- AvgSensor[3:(nrow(AvgSensor)-2),]
write.csv(AvgSensor, "AvgSensor.csv" ,)
