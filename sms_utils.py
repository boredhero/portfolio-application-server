from auth import AuthHolder
from utils import ConfigProvider

class TwilioDispatcher():

    def __init__(self):
        """
        Twilio dispatch class
        """
        self.__conf = ConfigProvider()

    def dispatch(self, message_body, to_phone, twilio_msg_obj=None)