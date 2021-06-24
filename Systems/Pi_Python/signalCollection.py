#!/usr/bin/env python3

import datetime, time, gspread, board, busio, adafruit_bme680
from gpiozero import MCP3008
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/Hunter-Programs/gasChamber_Data.json', scope)
client = gspread.authorize(creds)
sheet = client.open("gasChamber_Data").sheet1

adc0 = MCP3008(channel=0)
adc1 = MCP3008(channel=1)
adc2 = MCP3008(channel=2)
adc3 = MCP3008(channel=3)
adc4 = MCP3008(channel=4)
adc5 = MCP3008(channel=5)
adc6 = MCP3008(channel=6)
adc7 = MCP3008(channel=7)

i2c = busio.I2C(board.SCL, board.SDA)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

while True:
    values = []
    when = datetime.datetime.now()
    mq2sensorValue = adc0.value
    mq3sensorValue = adc1.value
    mq4sensorValue = adc2.value
    mq5sensorValue = adc3.value
    mq6sensorValue = adc4.value
    mq7sensorValue = adc5.value
    mq8sensorValue = adc6.value
    mq9sensorValue = adc7.value

    values = [when.strftime('%Y-%m-%d %H:%M:%S.%f'), mq2sensorValue, mq3sensorValue, mq4sensorValue, mq5sensorValue,
            mq6sensorValue,mq7sensorValue, mq8sensorValue, mq9sensorValue, bme680.temperature, bme680.humidity,
            bme680.gas, bme680.pressure]

    f = open("/home/pi/Hunter-Programs/GasStream.csv","a+")
    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s'
            '' %(when.strftime('%Y-%m-%d %H:%M:%S.%f'), mq2sensorValue, mq3sensorValue,
                 mq4sensorValue, mq5sensorValue, mq6sensorValue,mq7sensorValue, mq8sensorValue,
                 mq9sensorValue, bme680.temperature, bme680.humidity, bme680.gas, bme680.pressure))
    f.write("\n")
    f.close()

    try:
        sheet.insert_row(values, 2, value_input_option='RAW')
    except:
        try:
            print(when, " Upload failed.")
            client = gspread.authorize(creds)
            print("Reauthenticating...")
            sheet.insert_row(values, 2, value_input_option='RAW')
            print(when, " Upload attempt.")
            continue
        except:
            continue
    finally:
        time.sleep(30)