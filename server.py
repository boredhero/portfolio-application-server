from clientutils import ClientUtils
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
        self.__r_utils = RequestUtils()
        self.__c_utils = ClientUtils()

    @route('/api/ping', methods=['POST'])
    def ping(self):
        """
        Ping request. Logs the client ID and a timestamp to the firestore.

        Required Keys: "Client ID" (str)
        """
        mandatory_keys = ["Client ID", "Software Version"]
        v = self.__r_utils.combined_key_value_checks(mandatory_keys, request)
        if v is not True:
            return v
        else:
            body_json = request.get_json()
            ts = get_timestamp()
            ip = request.remote_addr
            cid = body_json["Client ID"]
            v = body_json["Software Version"]
            print(f"{ts}: PING from {cid} @ {ip} v{v}")
            self.__c_utils.log_client_ping(ts, cid, ip, v)

    @route('/api/send_test_message', methods=['POST'])
    def send_text(self):
        """
        Send a text to a phone number
        """
        mandatory_keys = ["Client ID", "Text Contents", "Phone"]
        v = self.__r_utils.combined_key_value_checks(mandatory_keys, request)
        if v is not True:
            return v
        else:
            body_json = request.get_json()

if __name__ == '__main__':
    #app.run(debug=False, host=HOST, port=PORT)
    print("hi")