import twilio
from auth import AuthHolder
from utils import ConfigProvider

class TwilioDispatcher():

    def __init__(self):
        """
        Twilio dispatch class
        """
        self.__conf = ConfigProvider()
        self.__auth = AuthHolder()
        self.__tw = self.__auth.twilio

    def dispatch(self, message_body, to_phone, twilio_msg_obj=None):
        if twilio_msg_obj is not None:
            try:
                twilio_msg_obj.sid
            except Exception as e:
                print("An issue occured trying to send a pre-constructed twilio msg object via Twilio\n", e)
        else:
            try:
                twilio_msg_obj = self.__tw.messages.create(
                    body = message_body,
                    from_ = self.__conf.twilio_from_phone,
                    to = to_phone
                )
                twilio_msg_obj.sid
            except Exception as e:
                print("An issue occured trying to construct or send an SMS via Twilio.\n", e)
        