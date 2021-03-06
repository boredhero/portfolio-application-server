import logging
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
        """
        Dispatch a message. If twilio_msg_obj is not None, will attempt to send a message object you made via twilio.messages.create()
        Otherwise, feed formatted string text and a to_phone and this will yeet it.

        :param str message_body: String formatted message body
        :param str to_phone: Phone to send the SMS to

        :returns: True if successful send, False if an exception occurred.
        """
        if twilio_msg_obj is not None:
            try:
                twilio_msg_obj.sid
                return True
            except Exception as e:
                logging.error("An issue occured trying to send a pre-constructed twilio msg object via Twilio\n", e)
                return False
        else:
            try:
                twilio_msg_obj = self.__tw.messages.create(
                    body = message_body,
                    from_ = self.__conf.twilio_from_phone,
                    to = to_phone
                )
                twilio_msg_obj.sid
                return True
            except Exception as e:
                logging.error("An issue occured trying to construct or send an SMS via Twilio.\n", e)
                return False
        