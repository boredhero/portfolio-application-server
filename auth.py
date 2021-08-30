from firebase_admin import firestore, credentials
import firebase_admin
from twilio.rest import Client
from utils import ConfigProvider, Singleton
import logging

class AuthHolder(metaclass=Singleton):

    def __init__(self):
        """
        Holds API objects as a singleton so that we don't try to create them over and over again (this would cause issues with firestore, for instance.)
        """
        self.__conf = ConfigProvider()
        self.firestore = self.__firestore_authenticator()
        self.twilio = self.__twilio_authenticator()

    def __firestore_authenticator(self):
        """
        Create a firestore client object

        :returns: Firestore Client() if successful, else returns None if an Exception occurred
        """
        try:
            # Initialize key file
            key = credentials.Certificate(self.__conf.firestore_key_filepath)
            # Initialize the app
            firebase_admin.initialize_app(key)
            # Create and return the client object
            return firestore.client()
        except Exception as e:
            print(e)
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
