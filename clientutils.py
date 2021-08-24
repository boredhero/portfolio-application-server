from datetime import time
from utils import *
from fsio import FirestoreIO

class ClientUtils:

    def __init__(self):
        """
        Helper class full of random methods useful for wrangling/logging client data
        """
        self.__FIRESTORE_PING_LOG_PATH = "/Clients/Last Ping Log"
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
            print(f"Error: database_type {self.__conf.database_type} not currently supported.")
        
    def __log_client_ping_firestore(self, timestamp, client_id, client_ip, client_version):
        """
        Log client IP firestore
        """
        if self.fsio is None:
            print("Error: Trying to run a firestore logger when database_type is set to something other than 'firestore'")
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
                print(f"{timestamp}: Error occured trying to log PING from {client_id} v{client_version} @ {client_ip}")