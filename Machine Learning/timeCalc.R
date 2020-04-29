for (k in names)
{
  mqTime <- (paste("Times", toString(k), sep = "_"))
  mqEvent <- (paste("Events", toString(k), sep = "_"))
  timeCalc <- (get(mqTime))
  print(mqEvent)

  timeCalc["Timediff"] <- NA

  for (l in 1:nrow(trialTimes))
  {
    for(m in 1:nrow(timeCalc))
    {
      timeCalc[m, "Timediff"] = difftime(trialTimes[l, "Time"], timeCalc[m, "Time"], units="mins")

      if (abs(timeCalc[m,"Timediff"]) < 5){
        print(timeCalc[m, "Timediff"])
        print(rownames(get(mqEvent))[m])
        print(trialTimes$Chemical[l])


        rownames(get(mqEvent))[m] <- trialTimes$Chemical[l]

        #assign(rownames(get(mqEvent))[m], trialTimes$Chemical[l], pos = -1)
        #rowname of Events_MQx_ADC set to trialTimes$chemical
        #rownames(timeCalc)[m] <- trialTimes$Chemical[l]
        #rownames(Events_MQ2_ADC)[m] <- trialTimes$Chemical[l]
        #assign(rownames(get(mqEvent))[m], trialTimes$Chemical[l])
        #print(rownames(get(mqEvent))[m])
        #print(trialTimes$Chemical[l])
        #assign(rownames(mqEvent)[m], trialTimes$Chemical[l])

        break

      }
    }
  }
}

