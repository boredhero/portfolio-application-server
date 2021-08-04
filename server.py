from flask import Flask, request
from flask_classful import FlaskView, route
from utils import *

config = ConfigProvider()
HOST = config.host
PORT = config.port
DEBUG = config.debug_mode

app = Flask(__name__)

if __name__ == '__main__':
    #app.run(debug=False, host=HOST, port=PORT)
    print("hi")