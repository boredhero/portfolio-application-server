import sqlite3
from auth import AuthHolder

class SQLLiteIO():

    def __init__(self):
        """
        WARNING! THIS IS A BETA! DEFAULT TO FIRESTORE UNTIL FURTHER TESTING!

        An experimental SQLLite local database module as an alternative to the FSIO module.
        """
        