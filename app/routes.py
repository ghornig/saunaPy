from flask import Flask, render_template, Response
from app import app, socketio
import time
import random

cache = {}
# https://stackoverflow.com/questions/70796161/countdown-timer-how-to-update-variable-in-python-flask-with-html

@app.route('/content') # render the content a url differnt from index. This will be streamed into the iframe
def content():
    def timer(t):
        for i in range(t):
            time.sleep(1) #put 60 here if you want to have seconds
            yield str(i)
    return Response(timer(10), mimetype='text/html') #at the moment the time value is hardcoded in the function just for simplicity

@app.get("/lowertemperature/")
def lowertemp():
    tempval = random.uniform(20, 30)
    return str(tempval)

@app.get("/uppertemperature/")
def uppertemp():
    tempval = random.uniform(20, 30)
    return str(tempval)

@app.get("/lowerhumidity/")
def lowerhumidity():
    humval = random.uniform(0, 100)
    return str(humval)

@app.get("/lowerec02/")
def lowerec02():
    ec02val = random.uniform(0, 100)
    return str(ec02val)

@app.get("/lowerpressure/")
def lowerpressure():
    pressureval = random.uniform(0, 100)
    return str(pressureval)

@app.get("/activatesauna/")
def activatesauna():
    print("sauna activated")
    return ""

@app.get("/toggleoutdoorlight/")
def togglelight():
    lightOn = not lightOn
    if lightOn:
        print("outdoor light turned off")
    else:
        print("outdoor light turned on")
    return ""

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data['foo'])

@app.route('/')
@app.route('/index')
def index():
    return render_template('test.html') # render a template at the index. The content will be embedded in this template

# if __name__ == '__main__':
#     app.run(use_reloader=False)