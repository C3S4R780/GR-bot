import os
import random
from flask import Flask
from threading import Thread
from waitress import serve

app = Flask('GR-bot')

@app.route('/')
def home():
    return "<div style='background-color:#152238;color:#fff;width:100vw;height:100vh;display:flex;justify-content:center;align-items:center;font-family:sans-serif;font-size:8em;font-weight:bold;margin:-8px;'>Bot online!</div>"

def run():
    os.system("cls")
    print("Bot online!")
    serve(app, host="0.0.0.0", port=random.randint(2000, 9000))

def keep_alive():
    '''
	Creates and starts new thread that runs the function run.
	'''
    t = Thread(target=run)
    t.start()