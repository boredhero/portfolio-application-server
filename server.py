from sms_utils import TwilioDispatcher
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
        self.__td = TwilioDispatcher()

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
            return self.__r_utils.blank_success_template()

    @route('/api/send_test_message', methods=['POST'])
    def send_text(self):
        """
        Send a text to a phone number
        """
        mandatory_keys = ["Client ID", "SMS Body", "Phone"]
        v = self.__r_utils.combined_key_value_checks(mandatory_keys, request)
        if v is not True:
            return v
        else:
            body_json = request.get_json()
            message_body = body_json["SMS Body"]
            to_phone = body_json["Phone"]
            t_res = self.__td.dispatch(message_body, to_phone)
            timestamp = get_timestamp()
            self.__c_utils.log_sms_sent(timestamp, body_json["Client ID"], message_body, to_phone, t_res)
            if t_res is False:
                return self.__r_utils.failure_template("An unknown error occured trying to send SMS")
            else:
                return self.__r_utils.blank_success_template()

if __name__ == '__main__':
    #app.run(debug=False, host=HOST, port=PORT)
    print("hi")