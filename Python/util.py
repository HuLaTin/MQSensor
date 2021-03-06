#####################
###  HUNTER TINER ###
#####################
## HuLaTin @ GMAIL ##
#####################

def eventDetection(today, scaler, stat, normColumns, sRun, futureAvg, expectedChange, preWindow, postWindow, windowSize, sensorData,
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
    sensorData["sRun"] = 0
    sensorData["sRun-Delta"] = 0
    sensorData["futureAverage"] = 0
    sensorData["Change"] = 0
    sensorData["future-past"] = 0
    sensorData["Event"] = None

    # determines change between each timepoint of normalized data column
    for z in range(sRun, len(sensorData)-futureAvg):
        #sensorData.loc[z, "Z-2"] = stat.mean(sensorData.loc[z-2:z, i])
        #sensorData.loc[z, "Z-1"] = stat.mean(sensorData.loc[z-1:z, i])
        
        sensorData.loc[z, "sRun"] = stat.mean(sensorData.loc[z-sRun:z-1, 'ADC_N'])
        sensorData.loc[z, "futureAverage"] = stat.mean(sensorData.loc[z:z+futureAvg, 'ADC_N'])
        sensorData.loc[z, "future-past"] = sensorData.loc[z, "futureAverage"] - sensorData.loc[z, "sRun"]
        #sensorData.loc[z, 'sRun-Delta'] = sensorData.loc[z, 'ADC_N'] - sensorData.loc[z, 'sRun']
        #sensorData.loc[z, 'Change'] = sensorData.loc[z, 'ADC_N'] - sensorData.loc[z-1, 'ADC_N']
        
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
    for z in range(sRun, len(sensorData)):
        # if change is greater than expectedChange / "Event" is True
        if sensorData.loc[z, "future-past"] >= expectedChange:
            sensorData.loc[z, "Event"] = "True"
            # checks to make sure we dont run out of the dataframe
            # store start/end times of events
            if z > preWindow and z < (len(sensorData)-(windowSize - 5)):
                eventIndex.loc[subsetCounter, 'start'] = (z - preWindow)
                eventIndex.loc[subsetCounter, 'end'] = (z + (windowSize - preWindow))
                subsetCounter = (subsetCounter + 1)
                timeIndex.loc[subsetCounter - 1, 'Time'] = sensorData.loc[z - 1, 'Time' ]
        else:
            # otherwise "False"
            sensorData.loc[z,'Event'] = "False"
            

    eventIndex["flag"] = 'False'
    timeIndex["flag"] = 'False'
    z = 0
    while(True):
    #for z in range(len(eventIndex)-1):
        start = eventIndex.loc[z, 'start']
        end = eventIndex.loc[z, 'end']
        for x in range(z+1, len(eventIndex)):
            if eventIndex.loc[x, 'start'] > start and end < eventIndex.loc[x, 'end']:
                if eventIndex.loc[x, 'start'] - start <= windowSize:
                    eventIndex.loc[x, "flag"] = 'True'
                    timeIndex.loc[x, "flag"] = 'True'
        eventIndex = eventIndex[eventIndex['flag'].str.contains('False')]
        timeIndex = timeIndex[timeIndex['flag'].str.contains('False')]
        eventIndex = eventIndex.reset_index(drop=True)
        timeIndex = timeIndex.reset_index(drop=True)

        if z == len(eventIndex)-1:
            break
        z = z + 1

    eventNumber = 1
    # initialize dataframe
    # stores columns between rows where an event was determined to have occured
    eventsCaptured = sensorData.iloc[eventIndex.loc[0,'start']:eventIndex.loc[0,'end'],0:13]

    # infinite loop
    # continues appending data of captured events
    while 1:
        dataToAppend = sensorData.iloc[eventIndex.loc[eventNumber,'start']:eventIndex.loc[eventNumber,'end'],0:13]
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
    
    dfCols = list(eventsCaptured.columns.values)

    # breaks down "eventsCaptured" into each event
    # using melt function
    for eventNum in range(1, numEvents + 1):
        eventStart = (windowSize * (eventNum - 1))
        eventStop = (windowSize * eventNum)
        eventTemp = pd.DataFrame(eventsCaptured.iloc[eventStart:eventStop,:])
        #####################################################################
        if normColumns == True:
            for i in dfCols[1:]:
                eventTemp[i] = scaler.fit_transform(eventTemp[[i]])                
        #Normalize here?
        #####################################################################
        eventTemp.insert(0, "num", range(1, len(eventTemp)+1))
        eventTemp = pd.melt(eventTemp, id_vars=['Time', 'num'])
        # TEST used in trying to determine outliers    
        sdThresh = len(eventTemp)*.25
        
        events = pd.concat([events, eventTemp.iloc[:,3]], axis=1)

    # new empty column
    events['name'] = None

    # finds index of columns
    c = eventTemp.columns.get_loc('variable')
    d = eventTemp.columns.get_loc('num')

    # used to rename columns so we can see time point/signal
    for b in range(0, len(eventTemp)):
        var = eventTemp.iloc[b,c]
        num = eventTemp.iloc[b,d]
        eventLabel = (str(var),str(num))
        events.loc[b,"name"] = "_".join(eventLabel)
        
    # names events with number
    # seems redundant?
    ## CHECK THIS ( previously len()-1 )
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
    csvParameters = [str(today), str(triggerSensor), str(round(expectedChange,2)), str(preWindow+1), str(postWindow)]
    
    if normColumns == True:
        csvParameters.append('N')

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
    parameterlst = [triggerSensor, sRun, futureAvg, expectedChange, expectedEvents, eventsTrue, eventsFalse, eventsTotal]
    parameterlst = pd.DataFrame([parameterlst])
    
    return events, eventsTrim, parameterlst, sdThresh, balanceThis, triggerSensor
    
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

def getNeighbors(stat, bitMinValue, bitMaxValue, runbitMinValue, runbitMaxValue, futurebitMinValue, futurebitMaxValue, bits, expectedEvents, scaler, sRun, futureAvg, expectedChange, windowSize, sensorData,
            trialTimes, l, pd,  datetime, genCSV):
    '''
    
    '''
    # Returns a dict where the key is the bit of bits that was flipped, the value is the cost of the resulting dict (from the flipped bit)
    neighborBitsCost = bits.copy()
    neighborBitsScore = bits.copy()
    eventsTrue = 0
    eventsFalse = 0
    #changeScore = float()
    for i in neighborBitsCost:
        neighborBitsCost[i] = flipBit(neighborBitsCost[i])
        expectedChange = getValueOfBits(dict(list(neighborBitsCost.items())[0:10]), bitMinValue, bitMaxValue)
        sRun = int(getValueOfBits(dict(list(neighborBitsCost.items())[10:14]), runbitMinValue, runbitMaxValue))
        futureAvg = int(getValueOfBits(dict(list(neighborBitsCost.items())[14:18]), futurebitMinValue, futurebitMaxValue))
        score, eventsTrue, eventsFalse = geneticMutateScore(stat, bitMaxValue, runbitMaxValue, futurebitMaxValue, expectedEvents, scaler, sRun, futureAvg, expectedChange, windowSize, sensorData,
                   trialTimes, l, pd, datetime)
        # x = getValueOfBits(neighborBitsCost,bitMinValue, bitMaxValue)
        neighborBitsScore[i] = score
        neighborBitsCost[i] = flipBit(neighborBitsCost[i])
    bestScore = 0
    bestBits = dict()
    for j in neighborBitsScore:
        if neighborBitsScore[j] >= bestScore:
            bestScore = neighborBitsScore[j]
            bestBits = bits.copy()
            bestBits[j] = flipBit(bestBits[j])
            print(bestBits)
            print("Flipped bit: " + str(j))
            print("Expected Change - " + str(getValueOfBits(dict(list(bestBits.items())[0:10]), bitMinValue, bitMaxValue)))
            print("sRun - " + str(getValueOfBits(dict(list(bestBits.items())[10:14]), runbitMinValue, runbitMaxValue)))
            print("fAvg - " + str(getValueOfBits(dict(list(bestBits.items())[14:18]), futurebitMinValue, futurebitMaxValue)))

            print("Best score = " + str(bestScore))
            genScoring = [l, (str(bitMinValue) + " - " + str(bitMaxValue)), float(expectedChange), str(sRun), str(futureAvg), int(eventsTrue), int(eventsFalse), float(bestScore), str(bestBits)]
            scoringCSV(genScoring, genCSV, pd)
    getNeighbors(stat, bitMinValue, bitMaxValue, runbitMinValue, runbitMaxValue, futurebitMinValue, futurebitMaxValue, bits, expectedEvents, scaler, sRun, futureAvg, expectedChange, windowSize, sensorData,
            trialTimes, l, pd,  datetime, genCSV)
    return
     
def geneticMutateScore(stat, bitMaxValue, runbitMaxValue, futurebitMaxValue, expectedEvents, scaler, sRun, futureAvg, expectedChange, windowSize, sensorData,
                   trialTimes, i, pd, datetime):
    '''
    Tommy Haycraft & Hunter Tiner
    '''
    preWindow = 4
    #triggerSensor = i
    eventName = i
    i = eventName
    
    # applying scaler to column "i" (sensor column)
    sensorData["ADC_N"] = scaler.fit_transform(sensorData[[i]])
    
    # creates new columns
    # first value in "Change" is 0   
    sensorData["sRun"] = 0
    sensorData["sRun-Delta"] = 0
    sensorData["futureAverage"] = 0
    sensorData["Change"] = 0
    sensorData["future-past"] = 0
    sensorData["Event"] = None
    
    # determines change between each timepoint of normalized data column
    for z in range(sRun, len(sensorData)-futureAvg):
        
        sensorData.loc[z, "sRun"] = stat.mean(sensorData.loc[z-sRun:z-1, 'ADC_N'])
        sensorData.loc[z, "futureAverage"] = stat.mean(sensorData.loc[z:z+futureAvg, 'ADC_N'])
        sensorData.loc[z, "future-past"] = sensorData.loc[z, "futureAverage"] - sensorData.loc[z, "sRun"]

     
    # creation of empty dataframes containing these columns           
    eventIndex = pd.DataFrame(columns=['start', 'end'])
    timeIndex = pd.DataFrame(columns=['Time'])

    # initialize counter and set starting values
    subsetCounter = 0
    # test without these lines of code?
    eventIndex.loc[0,'start'] = 0
    eventIndex.loc[0,'end'] = 0
    
    # finding events
    ######################
    # do we need this -1??        
    for z in range(sRun, len(sensorData)):
        # if change is greater than expectedChange / "Event" is True
        if sensorData.loc[z, "future-past"] >= expectedChange:
            sensorData.loc[z, "Event"] = "True"
            # checks to make sure we dont run out of the dataframe
            # store start/end times of events
            if z > preWindow and z < (len(sensorData)-(windowSize - 5)):
                eventIndex.loc[subsetCounter, 'start'] = (z - preWindow)
                eventIndex.loc[subsetCounter, 'end'] = (z + (windowSize - preWindow))
                subsetCounter = (subsetCounter + 1)
                timeIndex.loc[subsetCounter - 1, 'Time'] = sensorData.loc[z - 1, 'Time' ]
        else:
            # otherwise "False"
            sensorData.loc[z,'Event'] = "False"
      
    eventIndex["flag"] = 'False'
    timeIndex["flag"] = 'False'
    z = 0
    
    while(True):
    #for z in range(len(eventIndex)-1):
        start = eventIndex.loc[z, 'start']
        end = eventIndex.loc[z, 'end']
        for x in range(z+1, len(eventIndex)):
            if eventIndex.loc[x, 'start'] > start and end < eventIndex.loc[x, 'end']:
                if eventIndex.loc[x, 'start'] - start <= windowSize:
                    eventIndex.loc[x, "flag"] = 'True'
                    timeIndex.loc[x, "flag"] = 'True'
        eventIndex = eventIndex[eventIndex['flag'].str.contains('False')]
        timeIndex = timeIndex[timeIndex['flag'].str.contains('False')]
        eventIndex = eventIndex.reset_index(drop=True)
        timeIndex = timeIndex.reset_index(drop=True)

        if z == len(eventIndex)-1:
            break
        z = z + 1
    
    # set time format    
    timeIndex['Time'] = pd.to_datetime(timeIndex['Time'], format='%Y-%m-%d %H:%M:%S.%f')  
    # set format for our time stamps
    fmt = '%Y-%m-%d %H:%M:%S'
    timeIndex['Time'] = timeIndex['Time'].astype('datetime64[s]')       
    for l in range(0, len(trialTimes)):
        for m in range(0, len(timeIndex)):
            tDelta = datetime.strptime(str(trialTimes.loc[l,'Time']),fmt) - datetime.strptime(str(timeIndex.loc[m, 'Time']),fmt)
            tDelta = tDelta.total_seconds()/60
            timeIndex.loc[m, 'timeDiff'] = tDelta
            if abs(timeIndex.loc[m, 'timeDiff']) <= 5:
                timeIndex.loc[m, 'Event'] = "True"
                break

    eventsTrue = 0
    eventsFalse = 0
    
    if len(timeIndex) >= 1:
        #valueCounts = timeIndex.Event.value_counts()
        eventsTrue = len(timeIndex[timeIndex['Event'].str.contains("True")])
        eventsFalse = len(timeIndex[timeIndex['Event'].str.contains("False")])
        
        print("True: " + str(eventsTrue))
        print("False: " + str(eventsFalse))
    
    smallNumber = (bitMaxValue - expectedChange) / 10
    runsmallNumber = (runbitMaxValue - (sRun/10)) / 10
    futuresmallNumber = (futurebitMaxValue - (futureAvg/10)) / 10

    score = ((eventsTrue * 1.1) / (expectedEvents + eventsFalse)) + smallNumber + runsmallNumber + futuresmallNumber

    print("score: " + str(score))
    
    return(score, eventsTrue, eventsFalse)

def scoringCSV(genScoring, genCSV, pd):
    '''
    '''
    openGenCSV = pd.read_csv(genCSV)
    df_length = len(openGenCSV)
    openGenCSV.loc[df_length] = genScoring
    openGenCSV.to_csv(genCSV, index=False)
    
def genRandomBits(random, numBits):
    '''
    Returns dictionary with random bits
    '''
    bits = dict()
    for i in range(numBits):
        if random.random() > 0.5:
            bits[i] = 1
        else:
            bits[i] = 0
    return(bits)

def flipBit(num):
    '''
    1s becomes 0s, 0s becomes 1s
    '''
    if num == 1:
        num = 0
    else:
        num = 1
    return num

def getValueOfBits(bits,min,max):
    '''
    takes dictionary of bits, and converts to a number between min and max
    '''
    bits = {i: v for i, v in enumerate(bits.values())}
    maxValueOfBits = (2**len(bits))-1

    x = 0
    for i in bits:
        x += (2**i)*bits[i]
    # Gets the percentage of 0-1023, converts to a %, and returns the number equal to the percent between min and max
    return((((x/maxValueOfBits)*100) * (max - min) / 100) + min)

def classificationReports(accuracy_score, recall_score, precision_score, confusion_matrix, classification_report, y_test, y_pred):
    accuracy = accuracy_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred, average='macro')
    precision = precision_score(y_test, y_pred, average='macro')

    cmat = confusion_matrix(y_test, y_pred)
    classReport = classification_report(y_test, y_pred)
    
    return accuracy, recall, precision, cmat, classReport
