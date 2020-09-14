#sensor array program: MQ2, MQ4, MQ5, MQ6, MQ7, MQ8, MQ9, MQ135, BME680, PMS5003

#Hunter Tiner / Hulatin@gmail.com
#original program by Elizabeth Dourlain

import time
import math
import RPi.GPIO as GPIO
from gpiozero import MCP3008
import board
import busio
import adafruit_bme680
import serial
import datetime
import os
import os.path

#location of analog signals
adc0 = MCP3008(channel=0)
adc1 = MCP3008(channel=1)
adc2 = MCP3008(channel=2)
adc3 = MCP3008(channel=3)
adc4 = MCP3008(channel=4)
adc5 = MCP3008(channel=5)
adc6 = MCP3008(channel=6)
adc7 = MCP3008(channel=7)          
            
#defines inital analog signal before start
mq2sensorValue=0
mq4sensorValue=0
mq5sensorValue=0
mq6sensorValue=0
mq7sensorValue=0
mq8sensorValue=0
mq9sensorValue=0
mq135sensorValue=0

#loops analog signal to get average of value for air
#calibration
x=0
for x in range(0, 500):
    
    mq2sensorValue = mq2sensorValue + adc0.value
    mq4sensorValue = mq4sensorValue + adc1.value
    mq5sensorValue = mq5sensorValue + adc2.value
    mq6sensorValue = mq6sensorValue + adc3.value
    mq7sensorValue = mq7sensorValue + adc4.value
    mq8sensorValue = mq8sensorValue + adc5.value
    mq9sensorValue = mq9sensorValue + adc6.value
    mq135sensorValue = mq135sensorValue + adc7.value
    #loops 500 times
    x=x+1

#Gets average of analog value
mq2sensorValue1 = mq2sensorValue/500
mq4sensorValue1 = mq4sensorValue/500
mq5sensorValue1 = mq5sensorValue/500
mq6sensorValue1 = mq6sensorValue/500
mq7sensorValue1 = mq7sensorValue/500
mq8sensorValue1 = mq8sensorValue/500
mq9sensorValue1 = mq9sensorValue/500
mq135sensorValue1 = mq135sensorValue/500

#calculates the sensing resitance in "clean air"
#may need to be 5
####################
mq2RSair = ((3.3*10)/mq2sensorValue1)-10
mq4RSair = ((3.3*10)/mq4sensorValue1)-10
mq5RSair = ((3.3*10)/mq5sensorValue1)-10
mq6RSair = ((3.3*10)/mq6sensorValue1)-10
mq7RSair = ((3.3*10)/mq7sensorValue1)-10
mq8RSair = ((3.3*10)/mq8sensorValue1)-10
mq9RSair = ((3.3*10)/mq9sensorValue1)-10
mq135RSair = ((3.3*10)/mq135sensorValue1)-10

#Calc sensor restistance in clean air from RS using air
#value at 1000ppm air from datasheet
mq2R0 = mq2RSair/9.9
mq4R0 = mq4RSair/4.4
mq5R0 = mq5RSair/6.5
mq6R0 = mq6RSair/9.9
mq7R0 = mq7RSair/28
mq8R0 = mq8RSair/70
mq9R0 = mq9RSair/9.9
mq135R0 = mq135RSair/3.8

#settings for BME680 sensor
i2c = busio.I2C(board.SCL, board.SDA)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

#print(bme680)

bme680.sea_level_pressure = 1028.6

#runs detection program
while True:
    try:
        
        #time stamp for data
        when = datetime.datetime.now()
        print(when)
        
        #get cpu load
        #load = os.popen('uptime | cut -d, -f4 | cut -d: -f2').read()
        load = os.popen('uptime | cut -d" " -f12 | cut -d, -f1').read()
        load = load.rstrip()
   
        #get Throttled
        throttle = os.popen('vcgencmd get_throttled | cut -d= -f2').read()
        
    #slope and intercept values calculated from calibration
    #on data sheet y=mx+b === log(y) = mlog(x) + b
        LPGm = -0.47  #mq2
        LPGb = 1.506  #mq2
        CH4m = -0.37  #mq4
        CH4b = 1.13   #mq4
        MQ5LPGm = -0.39 #mq5
        MQ5LPGb = 0.76  #mq5
        MQ6LPGm = -0.43 #mq6
        MQ6LPGb = 1.31  #mq6
        H2m = -1.04   #mq7
        H2b = 2.30    #mq7
        MQ8H2m = -1.52  #mq8
        MQ8H2b = 4.56   #mq8
        COm = -0.47   #mq9
        COb = 1.31    #mq9
        Um = -0.31    #mq135
        Ub = 0.49     #mq135
 
    #analog value from detection
        mq2sensorValue = adc0.value
        mq4sensorValue = adc1.value
        mq5sensorValue = adc2.value
        mq6sensorValue = adc3.value
        mq7sensorValue = adc4.value
        mq8sensorValue = adc5.value
        mq9sensorValue = adc6.value
        mq135sensorValue = adc7.value
    
    #RS calc from detection
        #########################################
        mq2RSgas = ((3.3*10)/mq2sensorValue)-10
        mq4RSgas = ((3.3*10)/mq4sensorValue)-10
        mq5RSgas = ((3.3*10)/mq5sensorValue)-10
        mq6RSgas = ((3.3*10)/mq6sensorValue)-10
        mq7RSgas = ((3.3*10)/mq7sensorValue)-10
        mq8RSgas = ((3.3*10)/mq8sensorValue)-10
        mq9RSgas = ((3.3*10)/mq9sensorValue)-10
        mq135RSgas = ((3.3*10)/mq135sensorValue)-10
    
    #ratio from detection
        mq2ratio1 = (mq2RSgas/mq2R0)
        mq4ratio1 = (mq4RSgas/mq4R0)
        mq5ratio1 = (mq5RSgas/mq5R0)
        mq6ratio1 = (mq6RSgas/mq5R0)
        mq7ratio1 = (mq7RSgas/mq7R0)
        mq8ratio1 = (mq8RSgas/mq8R0)
        mq9ratio1 = (mq9RSgas/mq9R0)
        mq135ratio1 = (mq135RSgas/mq135R0)
    
    #log of ration to calc ppm
        mq2ratio = math.log10(mq2ratio1)
        mq4ratio = math.log10(mq4ratio1)
        mq5ratio = math.log10(mq5ratio1)
        mq6ratio = math.log10(mq6ratio1)
        mq7ratio = math.log10(mq7ratio1)
        mq8ratio = math.log10(mq8ratio1)
        mq9ratio = math.log10(mq9ratio1)
        mq135ratio = math.log10(mq135ratio1)
    
    #Below are equation to calc seperate components
        LPGratio = (mq2ratio-LPGb)/LPGm
        LPGppm = math.pow(10,LPGratio)
        LPGperc = LPGppm/10000
    
        CH4ratio = (mq4ratio-CH4b)/CH4m
        CH4ppm = math.pow(10,CH4ratio)
        CH4perc = CH4ppm/10000
    
        MQ5LPGratio = (mq5ratio-MQ5LPGb)/MQ5LPGm
        MQ5LPGppm = math.pow(10,MQ5LPGratio)
        MQ5LPGperc = MQ5LPGppm/10000
    
        MQ6LPGratio = (mq6ratio-MQ6LPGb)/MQ6LPGm
        MQ6LPGppm = math.pow(10,MQ6LPGratio)
        MQ6LPGperc = MQ6LPGppm/10000
    
        H2ratio = (mq7ratio-H2b)/H2m
        H2ppm = math.pow(10,H2ratio)
        H2perc = H2ppm/10000
    
        MQ8H2ratio = (mq8ratio-MQ8H2b)/MQ8H2m
        MQ8H2ppm = math.pow(10,MQ8H2ratio)
        MQ8H2perc = MQ8H2ppm/10000
    
        COratio = (mq9ratio-COb)/COm
        COppm = math.pow(10,COratio)
        COperc = COppm/10000
    
        Uratio = (mq135ratio-Ub)/Um #not sure what this symbol is on ds -Elizabeth
        Uppm = math.pow(10,Uratio)
        Uperc = Uppm/10000
        
        
    
        print(LPGperc, "LPG%", CH4perc, "CH4%", MQ5LPGperc, "MQ5LPG%", MQ6LPGperc,
              "MQ6LPG%", H2perc, "H2%", MQ8H2perc, "MQ8H2%", COperc, "CO%", Uperc,
              "U%")
    
        print(LPGppm, "LPGppm", CH4ppm, "CH4ppm", MQ5LPGppm, "MQ5LPGppm",MQ6LPGppm,
              "MQ6LPGppm", H2ppm, "H2ppm", MQ8H2ppm, "MQ8H2ppm", COppm, "COppm", Uppm,
              "Uppm")
    #BME680
        print("Temperature: %0.1f C" % bme680.temperature)
        print("Gas: %d ohm" % bme680.gas)
        print("Humidity: %0.1f %%" % bme680.humidity)
        print("Pressure: %0.1f hPa" % bme680.pressure)
        print("Altitude = %0.2f meters" % bme680.altitude)
        
    #Pi info
        print("Load =", load)
        print("Throttle =", throttle)
    
    #name of file to write data
        inFile = open("/home/pi/Running_Programs/ArrayThrottle.csv","a")
    #what is being written to file
        inFile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s'
                     '' %(when, mq2sensorValue, LPGppm,
                            mq4sensorValue, CH4ppm, mq5sensorValue,
                            MQ5LPGppm, mq6sensorValue,
                            MQ6LPGppm, mq7sensorValue, H2ppm,
                            mq8sensorValue, MQ8H2ppm,
                            mq9sensorValue, COppm, mq135sensorValue,
                            Uppm, bme680.temperature, bme680.gas,
                            bme680.humidity,bme680.pressure,                        
                            load,throttle))
    
    
    #close file being written
        inFile.close()
    
    #sleep for 60 seconds cycles
        time.sleep(60)
    
    except KeyboardInterrupt:
        GPIO.cleanup()
        quit()
        

        