from firebase_admin import firestore, credentials
import firebase_admin
from utils import ConfigProvider, Singleton

class FirestoreAuthenticator():

    def __init__(self):
        """
        Firestore Auth Object.

        NOTE: This class does not currently support more than one firestore database. You need to assign names to them for that and I haven't built that out yet, so please only talk to one database for the time being.
        """
        self.__config = ConfigProvider()
        self.firestore_auth_obj = self.__make_auth()
    
    def __new__(cls):
            return self.firestore_auth_obj

    def __make_auth(self):
        try:
            # Initialize key file
            key = credentials.Certificate(self.__config.firestore_key_filepath)
            # Initialize the app
            firebase_admin.initialize_app(key)
            # Create and return the client object
            return firestore.client()
        except Exception as e:
            print(e)
            return None