## R demo Phil Williams
###
## R --slave --args setdir fileOne.csv fileTwo.csv 0.5 100 < demoCommandLineArgs.r
###

args <- commandArgs(trailingOnly = F)
print(args)


setDir = args[4]
csvFileOne = args[5]
csvFileTwo = args[6]
thresHold = args[7]
windowSize = args[8]

file.exists(csvFileOne)
file.exists(csvFileTwo)

#library(reshape2)
#library(factoextra)

################################################
#stop("just stop here")