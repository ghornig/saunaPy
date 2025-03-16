from flask import Flask, render_template, Response
from app import app, socketio
import time
import random
import threading

import re, subprocess
 
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

lowertemp = 0
uppertemp = 0
hum = 0
ec02 = 0
pressure = 0
lightOn = False
# https://stackoverflow.com/questions/70796161/countdown-timer-how-to-update-variable-in-python-flask-with-html

def updateVals():
    while True:
        global lowertemp, uppertemp, hum, ec02, pressure
        uppertemp = random.uniform(20, 30)
        lowertemp = random.uniform(0, 100)
        hum = random.uniform(0, 100)
        ec02 = random.uniform(0, 100)
        pressure = random.uniform(0, 100)
        # print("upper temp: " + str(uppertemp))
        # print("lower temp: " + str(lowertemp))
        # print("humidity: " + str(hum))
        # print("ec02: " + str(ec02))
        # print("pressure: " + str(pressure))        
        time.sleep(1)

t1 = threading.Thread(target=updateVals)
t1.daemon = True
t1.start()

@app.get("/cputemperature/")
def cputemp():
    return str(check_CPU_temp())

@app.get("/lowertemperature/")
def lowertemp():
    global lowertemp
    return str(lowertemp)

@app.get("/uppertemperature/")
def uppertemp():
    global uppertemp
    return str(uppertemp)

@app.get("/lowerhumidity/")
def lowerhumidity():
    global hum
    return str(hum)

@app.get("/lowerec02/")
def lowerec02():
    global ec02
    return str(ec02)

@app.get("/lowerpressure/")
def lowerpressure():
    global pressure
    return str(pressure)

@app.get("/activatesauna/")
def activatesauna():
    print("sauna activated")
    return ""

@app.get("/toggleoutdoorlight/")
def togglelight():
    global lightOn
    lightOn = not lightOn
    if lightOn:
        print("outdoor light turned off")
    else:
        print("outdoor light turned on")
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