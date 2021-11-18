from firebase_admin import firestore, credentials
import firebase_admin
from twilio.rest import Client
from utils import ConfigProvider, Singleton
import logging
import sqlite3

class AuthHolder(metaclass=Singleton):

    def __init__(self):
        """
        Holds API objects as a singleton so that we don't try to create them over and over again (this would cause issues with firestore, for instance.)
        """
        self.__conf = ConfigProvider()
        self.firestore = self.__firestore_authenticator()
        self.twilio = self.__twilio_authenticator()
        self.sqlite_connection = self.__sqlite_connector()
        self.sqlite_cursor = self.__sqlite_cursor()

    def __firestore_authenticator(self):
        """
        Create a firestore client object

        :returns: Firestore Client() if successful, else returns None if an Exception occurred or if Firestore was not selected as the database type
        """
        if self.__conf.database_type == "firestore":
            try:
                # Initialize key file
                key = credentials.Certificate(self.__conf.firestore_key_filepath)
                # Initialize the app
                firebase_admin.initialize_app(key)
                # Create and return the client object
                return firestore.client()
            except Exception as e:
                logging.error("An unknown exception occured trying to authneticate Google Firestore! Check your config.yml")
                logging.error(e)
                return None
        else:
            return None

    def __twilio_authenticator(self):
        """
        Create a twilio auth object

        :returns: Twilio auth object if successful, else returns None if an Exception occurred
        """
        try:
            client = Client(self.__conf.twilio_acc_sid, self.__conf.twilio_auth_token)
            return client
        except Exception as e:
            logging.error("An unknown exception occured trying to authenticate twilio! Check your config.yml")
            logging.error(e)
            return None

    def __sqlite_connector(self):
        """
        Create connection object and cursor object for sqlite3 local database

        :returns: Connector object if enabled in config, otherwise null
        """
        if self.__conf.database_type == "sqlite_local":
            try:
                con = sqlite3.connect(self.__conf.sqlite_local_filepath)
                return con
            except Exception as e:
                if self.__conf.database_type == "sqlite_local":
                    logging.error("An unknown exception occured trying to create a connection to sqlite3 database. Check your config!")
                    logging.error(e)
                    return None
                else:
                    logging.debug("sqlite_local was not selected in config. __sqlite_connector will return None")
                    return None
        else:
            return None

    def __sqlite_cursor(self):
        """
        Create sqlite3 Cursor object and return it for sqlite3 local database

        :returns: Cursor object if enabled in config, otherwise null
        """
        if self.__conf.database_type == "sqlite_local" and self.sqlite_connection is not None:
            try:
                cur = self.sqlite_connection.cursor()
                return cur
            except Exception as e:
                if self.__conf.database_type == "sqlite_local":
                    logging.error("An unknown exception occured trying to create a Cursor object for sqlite3 database. Check your config!")
                    logging.error(e)
                    return None
                else:
                    logging.debug("sqlite_local was not selected in config. __sqlite_cursor will return None")
                    return None

