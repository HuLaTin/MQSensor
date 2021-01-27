#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

def movingAvg(sensorData, stat):
    """
    Function for creation of moving average of sensorData
    """
    avgData = sensorData
    names = list(avgData.columns.values)
    names.remove('Time')

    for i in names:
        for b in range(2, len(avgData)-2):
            startRow = b - 2
            endRow = b + 2
            avgData.loc[b,i] = stat.mean(sensorData.loc[startRow:endRow, i])
            
    avgData = avgData.loc[2:(len(avgData)-2),:]
    sensorData = avgData
    return sensorData
    

def eventDetection(today, scaler, expectedChange, windowSize, sensorData,
                   trialTimes, outputDir, i, pd, NaN, datetime):
    """
    Function used to detect, capture, identify, and save events
    """    
    triggerSensor = i
    eventName = (str(i), "ADC")
    # .join works similar to paste function
    i = eventName = "_".join(eventName)
    
    # applying scaler to column "i" (sensor column)
    sensorData["ADC_N"] = scaler.fit_transform(sensorData[[i]])
    
    # creates new columns
    # first value in "Change" is 0   
    sensorData.loc[0, "Change"] = 0
    sensorData['Event'] = None
    
    # determines change between each timepoint of normalized data column
    ######################
    # do we need this -1??
    for z in range(1, len(sensorData)-1):
        sensorData.loc[z, "Change"] = sensorData.loc[z, "ADC_N"] - sensorData.loc[z-1, "ADC_N"]
    
    # creation of empty dataframes containing these columns           
    eventIndex = pd.DataFrame(columns=['start', 'end'])
    timeIndex = pd.DataFrame(columns=['Time'])
    # initialize counter and set starting values
    subsetCounter = 0
    # test without these lines of code?
    eventIndex.loc[0,'start'] = 0
    eventIndex.loc[0,'end'] = 0
    sdThresh = 0
    
    # finding events
    ######################
    # do we need this -1??        
    for z in range(0, len(sensorData)-1):
        # if change is greater than expectedChange / "Event" is True
        if sensorData.loc[z, "Change"] > expectedChange:
            sensorData.loc[z, "Event"] = "True"
            # checks to make sure we dont run out of the dataframe
            # store start/end times of events
            if z > 4 and z < (len(sensorData)-(windowSize - 5)):
                eventIndex.loc[subsetCounter, 'start'] = (z - 4)
                eventIndex.loc[subsetCounter, 'end'] = (z + (windowSize - 4))
                subsetCounter = (subsetCounter + 1)
                timeIndex.loc[subsetCounter - 1, 'Time'] = sensorData.loc[z - 1, 'Time' ]
        else:
            # otherwise "False"
            sensorData.loc[z,'Event'] = "False"
    
    
    eventNumber = 1
    # initialize dataframe
    # stores columns between rows where an event was determined to have occured
    eventsCaptured = sensorData.iloc[eventIndex.loc[0,'start']:eventIndex.loc[0,'end'],0:12]
    
    # infinite loop
    # continues appending data of captured events
    while 1:
        dataToAppend = sensorData.iloc[eventIndex.loc[eventNumber,'start']:eventIndex.loc[eventNumber,'end'],0:12]
        eventsCaptured = eventsCaptured.append(dataToAppend)
        
        if eventNumber == len(eventIndex)-1:
            break
        eventNumber = eventNumber + 1

    # reset index of rows
    eventsCaptured = eventsCaptured.reset_index(drop=True)
    #####################################
    # check if we can normalize all columns?
    #####################################
    
    # new empty dataframes
    eventTemp = pd.DataFrame()
    events = pd.DataFrame()
    
    # determines number of total events
    numEvents = int(len(eventsCaptured)/windowSize)

    # breaks down "eventsCaptured" into each event
    # using melt function
    for eventNum in range(1, numEvents + 1):
        eventStart = (windowSize * (eventNum - 1))
        eventStop = (windowSize * eventNum)
        eventTemp = pd.DataFrame(eventsCaptured.iloc[eventStart:eventStop,:])    
        eventTemp.insert(0, "num", range(1, len(eventTemp)+1))
        eventTemp = pd.melt(eventTemp, id_vars=['Time', 'num'])
        # TEST used in trying to determine outliers    
        sdThresh = len(eventTemp)*.25
        
        events = pd.concat([events, eventTemp.iloc[:,3]], axis=1)

    # new empty column
    events['name'] = None
    
    # finds index of columns
    c = eventTemp.columns.get_loc('variable')
    d = eventTemp.columns.get_loc('value')
    
    # used to rename columns so we can see time point/signal
    for b in range(0, len(eventTemp)):
        var = eventTemp.iloc[b,c]
        num = eventTemp.iloc[b,d]
        eventLabel = (str(var),str(num))
        events.loc[b,"name"] = "_".join(eventLabel)
        
    # names events with number
    # seems redundant?
    for b in range(0, len(events.columns)-1):
        colLabel = (str("Event"), str(b+1))
        events.columns.values[b] = " ".join(colLabel)
        
    # transpose/flips dataframe
    events = events.T
    # renames columns using values contained in 'name' row
    events = events.rename(columns = events.loc['name',])
    # drop that useless row!
    events = events.drop(index = 'name')    
    
    # set time format    
    timeIndex['Time'] = pd.to_datetime(timeIndex['Time'], format='%Y-%m-%d %H:%M:%S.%f')
    
    timeIndex['timeDiff'] = 0
    events['ident'] = int(0)
    
    events.insert(0,'timeStamp','')    
    c = events.columns.get_loc("timeStamp")
        
    for b in range(0, len(events)):
        eTime = (str(timeIndex.iloc[b,0]), "Event")        
        events.iloc[b,c] = " ".join(eTime)
    
    events = events.reset_index(drop = True)
    
    # set format for our time stamps
    fmt = '%Y-%m-%d %H:%M:%S'
    timeIndex['Time'] = timeIndex['Time'].astype('datetime64[s]')
    # comparing timestamps
    # if event occurs within 5 mins of our recorded trial, the event is labeled as recorded chemical
    ### Our recorded experiments would occur atleast an hour apart ###
    for l in range(0, len(trialTimes)):
        for m in range(0, len(timeIndex)):
            tDelta = datetime.strptime(str(trialTimes.loc[l,'Time']),fmt) - datetime.strptime(str(timeIndex.loc[m, 'Time']),fmt)
            tDelta = tDelta.total_seconds()/60
            timeIndex.loc[m, 'timeDiff'] = tDelta
            if abs(timeIndex.loc[m, 'timeDiff']) <= 5:
                events.loc[m, 'timeStamp'] = trialTimes.loc[l, 'Chemical']
                events.loc[m, 'ident'] = 1
                break
    
    events = events.rename(columns={"timeStamp" : "chemical"})

    # subsets identified events into a new dataframe
    eventsTrim = events[(events.ident == 1)]
    events = events.drop(columns = 'ident')
    eventsTrim = eventsTrim.drop(columns = 'ident')
    
    #someone on stackoverflow said this was bad practice...
    #assign(paste("Index", toString(z), sep = "_"), EventIndex)
    #assign(paste("Captured", toString(z), sep = "_"), eventsCaptured)
    #assign(paste("Times", toString(z), sep = "_"), TimeIndex)
    
    # stores parameters for file naming
    csvParameters = [str(today), str(triggerSensor), str(expectedChange), str(windowSize)]
    
    # saves events to .csv
    # use .copy() otherwise it points to the list
    eventName = csvParameters.copy()
    eventName.append("Events.csv")
    eventName = "_".join(eventName)
    eventOutput = (outputDir, "events", eventName)
    eventOutput = "\\".join(eventOutput)
    events.to_csv(eventOutput,index=False)
    
    # saves eventsTrim to .csv, if dataframe contains an event
    balanceThis = None
    if len(eventsTrim) > 0:
        eventTrimName = csvParameters.copy()
        eventTrimName.append("EventsTrim.csv")
        eventTrimName = "_".join(eventTrimName)
        eventOutput = (outputDir,"eventsTrim", eventTrimName)
        balanceThis = eventOutput = "\\".join(eventOutput)
        eventsTrim.to_csv(eventOutput,index=False)
    
    # need to check row count here
    # count of expected events
    expectedEvents = len(trialTimes)
    eventsTrue = len(eventsTrim)
    eventsTotal = len(events)
    eventsFalse = (eventsTotal - eventsTrue)
    parameterlst = [triggerSensor, expectedChange, expectedEvents, eventsTrue, eventsFalse, eventsTotal]
    parameterlst = pd.DataFrame([parameterlst])
    
    return events, eventsTrim, parameterlst, sdThresh, balanceThis, triggerSensor

def downsampleData(cwd, pd, today, outputDir, balanceThis, triggerSensor):
    '''
    used to downsample to balance classes
    '''
    # setting output directory
    outputDir = ('Python\\machineLearning\downsampled')
    outputDir = (cwd, outputDir)
    outputDir = "\\".join(outputDir)

    dsName = [str(today), str(triggerSensor), "downsampled.csv"]
    dsName = "_".join(dsName)

    folderPath = (outputDir, dsName)
    dsCSV = "\\".join(folderPath)

    # import csv
    chemEvents = pd.read_csv(balanceThis)

    # split string, selects chemical name (drops the numbering)
    chemEvents['chemical'] = chemEvents['chemical'].str.split("-").str[0]

    # rename column
    chemEvents = chemEvents.rename(columns={"chemical": "pred"})

    # groups by class/chemical, downsamples to balance the dataset
    g = chemEvents.groupby('pred')
    chemEvents = pd.DataFrame(g.apply(lambda chemEvents: chemEvents.sample(g.size().min()).reset_index(drop=True)))
    
    # saves to csv
    chemEvents.to_csv(dsCSV,index=False)
    
    
def checkForOutliers(chems, eventsTrim, math, pd, stat, sdThresh):
    '''
    Used to check for outliers in the identified events.
    '''
    outliers = [] 
    if len(eventsTrim) > 0:
        for y in chems:
            if len(eventsTrim[eventsTrim['chemical'].str.contains(y)]) > 0:
                trimTemp = eventsTrim[eventsTrim['chemical'].str.contains(y)]
                chemData = pd.DataFrame()
                deviData = pd.DataFrame()
                
                for x in range(1, len(trimTemp.columns)):
                    chemData.loc[0, x] = stat.mean(trimTemp.iloc[:,x])
                                    
                    # standard deviation
                    for w in range(0, len(trimTemp)):
                        deviData.loc[w,x] = ((trimTemp.iloc[w,x] - chemData.loc[0,x]) ** 2)
                    
                    ### insert math
                    # Check my indexing!
                    doMath = math.sqrt(sum(deviData.iloc[:,x-1])/len(deviData))
                    chemData.loc[1,x] = doMath*2 # multiple by two for 2 deviations
                
                # Checking for outliers using standard deviation    
                for w in range(0, len(trimTemp)):
                    q = 0
                    for  x in range(1, len(trimTemp.columns)):
                        chemData.loc[2,x] = trimTemp.iloc[w,x]
                        
                        if (chemData.loc[2,x]>(chemData.loc[0,x]+chemData.loc[2,x])) or (chemData.loc[2,x]<(chemData.loc[0,x]-chemData.loc[1,x])):
                            q = q + 1
                
                    if q >= sdThresh:
                        outliers.append(str(trimTemp.loc[w,'chemical']))

    return outliers
