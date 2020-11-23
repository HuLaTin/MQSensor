infileCSVone <- file.path("C:", "Users", "Hunter Tiner", "Documents", "MQSensor", "Machine Learning", "Data", "Joulesv2_20201122.csv")
df <- read.csv(infileCSVone, header = FALSE, sep=",", stringsAsFactors = FALSE)

df <- df[ -c(3,5,7,9,11,13,15,17) ]

df <- df[, c(1:2,9,3:8,10:15)]

write.csv(df , "Joulesv2_20201122_SL.csv",row.names = FALSE)
