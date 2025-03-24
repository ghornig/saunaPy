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
adcReading = 0
latestMessage = "Hi!"
lightOn = True
gpioLightOut = KitronikGPIO(24, isPWM = False) # Without PWM
gpioLightOut.turnOn()

oled = KitronikOLED()
oled.displayText("Hello dev :)", 1)
# Update the OLED display with the changes
oled.show()

bme688 = KitronikBME688()
bme688.calcBaselines(oled) # Takes OLED as input to show progress

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
    global gpioLightOut    
    if lightOn:
        gpioLightOut.turnOn()
        r = 0
        g = 255
        b = 0
        zipLEDs.setPixel(0, (r, g, b))
        zipLEDs.show()    
    else:
        gpioLightOut.turnOff()
        r = 255
        g = 0
        b = 0
        zipLEDs.setPixel(0, (r, g, b))
        zipLEDs.show()
    lightOn = not lightOn


def screenUpdater():
    global lowertemp, uppertemp, hum, ec02, pressure, latestMessage, oled

    while True:
        # Screen one: env data
        try:
            oled.clear()
            # Read and output the sensor values to the OLED display
            oled.displayText("Temperature:" + str(lowertemp), 1)
            oled.displayText("Pressure:" + str(pressure), 2)
            oled.displayText("Humidity:"+  str(hum), 3)
            oled.displayText("eCO2:" + str(ec02), 4)
            oled.displayText("ADC Reading:" + str(adcReading), 5)
            oled.displayText("Upper Temp:" + str(uppertemp), 6)        

            oled.show()

            time.sleep(3)
        except:
            print("Error updating screen 1")
            pass
        
        # Screen two: technical info
        try:
            oled.clear()
            ssid = subprocess.check_output('iwgetid -r', shell=True).decode('utf-8').strip()
            # Read wifi signal
            wifiSignal = subprocess.check_output('iwconfig wlan0 | grep Signal', shell=True)
            # write link quality and signal level to two oled displaytext lines
            wifiSignal = wifiSignal.decode('utf-8').strip()
            match = re.search(r'Link Quality=(\d+/\d+)\s+Signal level=(-\d+ dBm)', wifiSignal)
            if match:
                link_quality = match.group(1)
                signal_level = match.group(2)
                oled.displayText("SSID:" + ssid, 1)
                oled.displayText("Link Quality:" + link_quality, 2)
                oled.displayText("Signal Level:" + signal_level, 3)

            oled.displayText(latestMessage, 4)

            oled.show()        
            time.sleep(3)
        except:
            print("Error updating screen 2")
            pass


def updateVals():


    adc1 = KitronikADC(1)

    while True:
        try:
            global lowertemp, uppertemp, hum, ec02, pressure, adcReading, bme688, zipLEDs
            bme688.measureData()
            adcReading = adc1.read()
            # uppertemp = float(adcToTemp(adcReading))
            uppertemp = float((adcReading))
            lowertemp = float(bme688.readTemperature())
            # Update the sensor values
            hum = float(bme688.readHumidity())
            oled.clear()
            ec02 =  float(bme688.readeCO2())
            pressure = float(bme688.readPressure())

            isRemoteUser = False
            who_output = subprocess.check_output('pgrep -ai sshd', shell=True).decode('utf-8').strip()
            if "sshd: gjh" in who_output:
                isRemoteUser = True

            if isRemoteUser:
                r = 0
                g = 0
                b = 255
                zipLEDs.setPixel(2, (r, g, b))
                zipLEDs.show()
            else:
                r = 0
                g = 0
                b = 0
                zipLEDs.setPixel(2, (r, g, b))
                zipLEDs.show()
        except:
            print("Error updating values")
            pass
        time.sleep(1)

t1 = threading.Thread(target=updateVals)
t1.daemon = True
t1.start()

t2 = threading.Thread(target=screenUpdater)
t2.daemon = True
t2.start()

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

@app.get('/outdoorlightstatus/')
def outdoorlightstatus():
    global lightOn
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