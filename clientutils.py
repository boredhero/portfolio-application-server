from utils import *
from fsio import FirestoreIO

class MachineUtils:

    def __init__(self):
        conf = ConfigProvider()
        fsio = FirestoreIO()

    def log_client_ping(self):
        """
        Log the IP and timestamp by client ID
        """