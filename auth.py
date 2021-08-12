from firebase_admin import firestore, credentials
import firebase_admin
from utils import ConfigProvider, Singleton

class AuthHolder(metaclass=Singleton):

    def __init__(self):
        """
        Holds API objects as a singleton so that we don't try to create them over and over again (this would cause issues with firestore, for instance.)
        """
        self.firestore = self.__firestore_authenticator()

    def __firestore_authenticator(self):
        """
        Create a firestore client object

        :returns: Firestore Client() if successful, else returns None if an Exception occurred
        """
        config = ConfigProvider()
        try:
            # Initialize key file
            key = credentials.Certificate(config.firestore_key_filepath)
            # Initialize the app
            firebase_admin.initialize_app(key)
            # Create and return the client object
            return firestore.client()
        except Exception as e:
            print(e)
            return None