import logging
from utils import *
from fsio import FirestoreIO

class ClientUtils:

    def __init__(self):
        """
        Helper class full of random methods useful for wrangling/logging client data
        """
        self.__FIRESTORE_PING_LOG_PATH = "/Logging/Last Ping Log"
        self.__SMS_LOG_PATH = "/Logging/SMS Log"
        self.__conf = ConfigProvider()
        if self.__conf.database_type == "firestore":
            self.__fsio = FirestoreIO()
        else:
            self.__fsio = None


    def log_client_ping(self, timestamp, client_id, client_ip, client_version):
        """
        Log the IP and timestamp by client ID

        :param str timestamp: Timestamp
        :param str client_id: Client Identifier
        :param str client_ip: Client IP Address
        :param str client_version: Client software version number
        """
        if self.__conf.database_type == "firestore":
            self.__log_client_ping_firestore(timestamp, client_id, client_ip, client_version)
        else:
            logging.error(f"ClientUtils: log_client_ping: database_type {self.__conf.database_type} not currently supported.")

    def log_sms_sent(self, timestamp, client_id, message_contents, to_phone, success_bool):
        """
        Log text messages sent via the server

        :param str timestamp: Timestamp
        :param str client_id: Client Identifier
        :param str message_contents: String contents of the message sent
        :param str to_phone: Phone number the message was sent to
        :param bool success_bool: True if you didn't get any errors sending it, False if you did
        """
        if self.__conf.database_type == "firestore":
            self.__log_sms_sent_firestore(timestamp, client_id, message_contents, to_phone, success_bool)
        else:
            logging.error(f"ClientUtils: log_sms_sent: database_type {self.__conf.database_type} not currently supported.")
        
    def __log_sms_sent_firestore(self, timestamp, client_id, message_contents, to_phone, success_bool):
        """
        Log sms sent firestore
        """
        if self.__fsio is None:
            logging.error("ClientUtils: __log_sms_sent_firestore: Trying to run a firestore logger when database_type is set to something other than 'firestore'")
        else:
            part_dict = {
                "clients": {
                    client_id: {
                        timestamp: {
                            "message_contents": message_contents,
                            "to_phone": to_phone,
                            "success": bool(success_bool)
                        }
                    }
                }
            }
            w_res = self.__fsio.write_doc(self.__SMS_LOG_PATH, part_dict)
            if w_res is not True:
                logging.error(f"ClientUtils: __log_sms_sent_firestore: Error occurred trying to log SEND_TEXT from {client_id}")
        
    def __log_client_ping_firestore(self, timestamp, client_id, client_ip, client_version):
        """
        Log client IP firestore
        """
        if self.__fsio is None:
            logging.error("ClientUtils: __log_client_ping_firestore: Trying to run a firestore logger when database_type is set to something other than 'firestore'")
        else:
            part_dict = {
                "clients": {
                    client_id: {
                        "timestamp": timestamp,
                        "last ip": client_ip,
                        "client version": client_version
                    }
                }
            }
            w_res = self.__fsio.write_doc(self.__FIRESTORE_PING_LOG_PATH, part_dict)
            if w_res is not True:
                logging.error(f"ClientUtils: __log_client_ping_firestore: Error occured trying to log PING from {client_id} v{client_version} @ {client_ip}")