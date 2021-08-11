from flask import Flask, request
from flask_classful import FlaskView, route
from utils import *

config = ConfigProvider()
HOST = config.host
PORT = config.port
DEBUG = config.debug_mode

app = Flask(__name__)

# TODO: Print startup method

class RequestHandler(FlaskView):
    route_base = '/'

    def __init__(self):
        """
        Request Handler class
        """
        self.__conf = ConfigProvider()
        self.__test_mode = self.__conf.test_mode

    @route('/api/ping', methods=['POST'])
    def ping(self):
        """
        Ping request. Logs the client ID and a timestamp to the firestore.

        Required Keys: "Client ID" (str)
        """
        required_keys = "Client ID"
        


if __name__ == '__main__':
    #app.run(debug=False, host=HOST, port=PORT)
    print("hi")