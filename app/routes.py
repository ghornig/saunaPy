from flask import Flask, render_template, Response
import time
from app import app
import random

# app = Flask(__name__)

@app.route('/content') # render the content a url differnt from index. This will be streamed into the iframe
def content():
    def timer(t):
        for i in range(t):
            time.sleep(1) #put 60 here if you want to have seconds
            yield str(i)
    return Response(timer(10), mimetype='text/html') #at the moment the time value is hardcoded in the function just for simplicity

@app.get("/temperature/")
def temp():
    tempval = random.uniform(20, 30)

    #Do anything here...
    #Here i'm returning the current value of count, so you can get
    #It in you web site
    return str(tempval)

@app.route('/')
@app.route('/index')
def index():
    return render_template('test.html') # render a template at the index. The content will be embedded in this template

# if __name__ == '__main__':
#     app.run(use_reloader=False)