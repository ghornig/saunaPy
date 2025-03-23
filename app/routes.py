from flask import Flask, render_template, Response
from app import app, socketio
import time
import random
import threading
from KitronikAirQualityControlHAT import *

import re, subprocess
 
zipLEDs = KitronikZIPLEDs(autoShow = False)

r = 255
g = 0
b = 0
zipLEDs.setPixel(0, (r, g, b))
zipLEDs.show()


def check_CPU_temp():
    temp = None
    err, msg = subprocess.getstatusoutput('vcgencmd measure_temp')
    if not err:
        m = re.search(r'-?\d\.?\d*', msg)   # a solution with a  regex
        try:
            temp = float(m.group())
        except ValueError: # catch only error needed
            pass
    return temp

def adcToTemp(adcReading):
    adcMax = 4095
    voltageMax = 3.3
    resistance = 12000
    alpha = 28095 #offset
    beta = 395 #slope
    gamma = 128549946
    delta = -2.48798

    vmeas = (adcReading/adcMax)*voltageMax
    # return ((resistance /((voltageMax/vmeas) - 1)) - alpha) / beta
    return math.pow(math.log(((resistance /((voltageMax/vmeas) - 1))) / gamma) / delta, 10)
    # return vmeas
lowertemp = 0
uppertemp = 0
hum = 0
ec02 = 0
pressure = 0
lightOn = False
# https://stackoverflow.com/questions/70796161/countdown-timer-how-to-update-variable-in-python-flask-with-html


def pushButton():
    servo = KitronikServo()
    # push down
    servo.changePercent(15)
    servo.start()
    time.sleep(0.5)
    servo.stop()
    time.sleep(1)
    # push up
    servo.changePercent(90)
    servo.start()
    time.sleep(0.5)
    servo.stop()

def toggleRelay():
    global lightOn
    global zipLEDs
    gpio24 = KitronikGPIO(24) # Without PWM
    if lightOn:
        gpio24.turnOff()
        r = 255
        g = 0
        b = 0
        zipLEDs.setPixel(0, (r, g, b))
        zipLEDs.show()
    else:
        gpio24.turnOn()
        r = 0
        g = 255
        b = 0
        zipLEDs.setPixel(0, (r, g, b))
        zipLEDs.show()
    lightOn = not lightOn


def updateVals():
    oled = KitronikOLED()
    oled.displayText("Hello dev :)", 1)
    # Update the OLED display with the changes
    oled.show()

    bme688 = KitronikBME688()
    bme688.calcBaselines(oled) # Takes OLED as input to show progress

    adc1 = KitronikADC(1)

    while True:
        global lowertemp, uppertemp, hum, ec02, pressure
        bme688.measureData()
        uppertemp = float(adcToTemp(adc1.read()))
        lowertemp = float(bme688.readTemperature())
        # Update the sensor values
        hum = float(bme688.readHumidity())
        oled.clear()
        ec02 =  float(bme688.readeCO2())
        pressure = float(bme688.readPressure())
        oled.clear()
        # Read and output the sensor values to the OLED display
        oled.displayText("Temperature:" + str(bme688.readTemperature()), 1)
        oled.displayText("Pressure:" + str(bme688.readPressure()), 2)
        oled.displayText("Humidity:"+  str(bme688.readHumidity()), 3)
        oled.displayText("eCO2:" + str(bme688.readeCO2()), 4)
        oled.displayText("Air Quality %:" + str(bme688.getAirQualityPercent()), 5)
        oled.displayText("Air Quality Score:" + str(bme688.getAirQualityScore()), 6)
        oled.show()

        time.sleep(1)

t1 = threading.Thread(target=updateVals)
t1.daemon = True
t1.start()

@app.get("/cputemperature/")
def cputemp():
    return str(check_CPU_temp())

@app.get("/lowertemperature/")
def getlowertemp():
    global lowertemp
    return str(lowertemp)

@app.get("/uppertemperature/")
def getuppertemp():
    global uppertemp
    return str(uppertemp)

@app.get("/lowerhumidity/")
def getlowerhumidity():
    global hum
    return str(hum)

@app.get("/lowerec02/")
def getlowerec02():
    global ec02
    return str(ec02)

@app.get("/lowerpressure/")
def getlowerpressure():
    global pressure
    return str(pressure)

@app.get("/activatesauna/")
def activatesauna():
    print("sauna activated")
    pushButton()
    return ""

@app.get("/toggleoutdoorlight/")
def toggleoutdoorlight():
    global lightOn
    toggleRelay()
    return str(lightOn)

# https://flask-socketio.readthedocs.io/en/latest/getting_started.html#receiving-messages
@socketio.on('message')
def handle_message(data):
    print('received message: ' + data['foo'])

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html') # render a template at the index. The content will be embedded in this template

@app.route('/bootstrap')
def bootstrap():
    return render_template('bootstrap.html')

# if __name__ == '__main__':
#     app.run(use_reloader=False)