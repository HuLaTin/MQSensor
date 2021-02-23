import math
import time
import csv
import datetime
import numpy as np
from grove.adc import ADC

__all__ = ["GroveSlidePotentiometer"]

pin0 = 0
pin1 = 1
f=('/home/pi/Running_Programs/currentTest.csv')


class GroveSlidePotentiometer(ADC):
    '''
    Grove Slide Poteniometer Sensor class

    Args:
        pin(int): number of analog pin/channel the sensor connected.
    '''
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
    
    @property
    def value(self):
        '''
        Get the position value, max position is 100.0%.

        Returns:
            (int): ratio, 0(0.0%) - 1000(100.0%)
        '''
        return self.adc.read(self.channel)


Grove = GroveSlidePotentiometer


def main():
    from grove.helper import SlotHelper
    #sh = SlotHelper(SlotHelper.ADC)
    
    sensor0 = GroveSlidePotentiometer(pin0)
    sensor1 = GroveSlidePotentiometer(pin1)
    i = 0
    
    pinValues = []
    pinValues.append([])
    #print(pinValues)
    #f=open('/home/pi/Running_Programs/currentTest.dat', 'ab')
    #f='/home/pi/Running_Programs/currentTest.csv'

    while True:
        when = datetime.datetime.now()
        #pinValues = pinValues[len(pinValues)+1].append([[str(when), sensor0.value, sensor1.value]])
        pinValues = np.append(pinValues, [str(when), "0: "+str(sensor0.value), "1: "+str(sensor1.value)])
        #print(pinValues)
        i = i + 1
                
        if i == 499:
            i = 0
            # print(pinValues)
            with open("/home/pi/Running_Programs/currentTest.csv", "ab") as f:
                np.savetxt(f, pinValues, fmt = "%s")
            #np.savetxt(f, pinValues, delimiter = "     ", fmt="%s")

            
            pinValues = np.array([])
                       
        # time.sleep(.1)    


if __name__ == '__main__':
    main()
