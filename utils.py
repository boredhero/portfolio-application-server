import json, yaml, os, platform, subprocess
import flask
from threading import Timer
from datetime import datetime
import logging

class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        """
        Make me your metaclass to be a singleton! It's *magic*
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SimpleJsonYmlReader:

    def __init__(self, filepath):
        """
        A very simple json/yml file reader

        :param str filepath: Filepath
        """

        if filepath is not None:
            self.FILETYPES = [".json", ".yml", ".JSON", ".YML", ".yaml", ".YAML"]
            self.YML = [".yml", ".YML", ".yaml", ".YAML"]
            self.JSON = [".json", ".JSON"]
            self.__filepath = filepath
            self.__ext = self.__get_file_extension(filepath)
        else:
            print("SimpleJsonYmlReader: Error: Filepath was None")

    def __get_file_extension(self, filepath):
        root,ext = os.path.splitext(filepath)
        if ext in ['.gz', '.bz2']:
            ext = os.path.splitext(root)[1] + ext
        return ext

    def read_file(self):
        """
        Read JSON/YML into a dict
        
        :returns dict filedict: File contents
        """
        file = None
        if self.__ext in self.FILETYPES:
            try:
                with open(self.__filepath) as f:
                    if self.__ext in self.YML:
                        file = yaml.load(f, Loader=yaml.FullLoader)
                    elif self.__ext in self.JSON:
                        file = json.load(f)
                    else:
                        logging.error("SimpleJsonYmlReader: read_file: Filetype not JSON or YAML. Please check your fileextension")
            except FileNotFoundError as e:
                logging.error(f"SimpleJsonYmlReader: read_file: File not found: {self.__filepath}\n", e)
            except json.JSONDecodeError as e:
                logging.error(f"SimpleJsonYmlReader: read_file: Error decoding JSON file: {self.__filepath}\n", e)
            except yaml.YAMLError as e:
                logging.error(f"SimpleJsonYmlReader: read_file: Error decoding YML file {self.__filepath}\n", e)
            except Exception as e:
                logging.error(f"SimpleJsonYmlReader: read_file: An unknown error occured proccessing the file {self.__filepath}\n", e)
        else:
            logging.error(f"SimpleJsonYmlReader: read_file: Error: File extension {self.__ext} not a valid extension!")
        return file

class ConfigProvider(metaclass=Singleton):

    def __init__(self):
        """
        Holds config.yml data points for easy access. Will not update when values are changed without a server restart.
        """
        self.__config_file = SimpleJsonYmlReader("config.yml")
        self.__config_dict = self.__config_file.read_file()
        try:
            self.port = int(self.__config_dict["port"])
            self.host = str(self.__config_dict["host"])
            self.debug_mode = bool(self.__config_dict["debug_mode"])
            self.test_mode = bool(self.__config_dict["test_mode"])
            self.database_type = str(self.__config_dict["database_type"])
            self.firestore_key_filepath = str(self.__config_dict["firestore_key_filepath"])
            self.firestore_project_name = str(self.__config_dict["firestore_project_name"])
            self.twilio_acc_sid = str(self.__config_dict["twilio_acc_sid"])
            self.twilio_auth_token = str(self.__config_dict["twilio_auth_token"])
            self.twilio_from_phone = str(self.__config_dict["twilio_from_phone"])
        except Exception as e:
            logging.error(f"ConfigProvider: An unknown error occured or a value was missing from your config.yml. Check your config.yml.TEMPLATE file for a correct example\n", e)

class InfoProivder(metaclass=Singleton):

    def __init__(self):
        """
        Holds info.yml data points for easy access. Will not update when values are changed without a server restart.
        """
        self.__info_file = SimpleJsonYmlReader("info.yml")
        self.__info_dict = self.__info_file.read_file()
        try:
            self.version = str(self.__info_dict["version"])
            self.nickname = str(self.__info_dict["nickname"])
            self.author = str(self.__info_dict["author"])
            self.license = str(self.__info_dict["license"])
        except Exception as e:
            logging.error("InfoProvider: An unknown error occured or a value was missing from your info.yml. Check that your info file exists!\n", e)
            self.version = "Unknown"
            self.nickname = "Unknown"
            self.author = "Unknown"
            self.license = "Unknown"

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

# Utility methods not contained within classes below

def get_timestamp():
    """
    Formatted date/time

    :returns str: datetime timestamp
    """
    return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

def ping(ip_addr):
    """
    Ping an IP

    :param str ip_addr: IP Address

    :returns bool: True if able to ping, False if unable to ping
    """
    ip_addr = str(ip_addr)
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_addr]
    return subprocess.call(command) == 0

class RequestUtils():

    def __init__(self):
        """
        Utility Methods for request handling
        """

    def failure_template(self, err):
        """
        Get a failure/error dict to send back as a template.

        :param str err: Reason for error
        """
        return {
            "Status": "Fail",
            "Cause": err
        }

    def blank_success_template(self):
        """
        Get a blank success dict with no other keys and values
        """
        return {
            "Status": "Success"
        }

    def failure_template_missing_keys(self, keys):
        """
        Generate a request response based on required keys which are missing from the request body (raw json body)

        :param list keys: List of strings of the *MISSING* keys.
        """
        m_keys = ', '.join(keys)
        err = f"Missing required keys from request body: {m_keys}"
        return self.failure_template(err)

    def failure_template_null_values(self, keys):
        """
        Generate a request response based on a list of keys which are missing their correct values (raw json body)

        :param list keys: List of strings of the keys with invalid values
        """
        n_value_keys = ', '.join(keys)
        err = f"Request data values were invalud for the following keys in body: {n_value_keys}"
        return self.failure_template(err)

    def validate_request_body_keys(self, mandatory_keys, flask_request):
        """
        Ensure the required keys are in the body and that the body is not NoneType

        :param list mandatory_keys: List of the required keys as str
        :param flask_request: Flask request object

        :returns: A dict if there was an err, so that you can return this as response to the client, else returns True if no issues found
        """
        missing_keys = []
        request_body_dict = flask_request.get_json()
        if request_body_dict is None:
            return self.failure_template("Request body was 'None'")
        for key in mandatory_keys:
            if key not in request_body_dict:
                missing_keys.append(key)
        if len(missing_keys) > 0:
            return self.failure_template_missing_keys(missing_keys)
        return True

    def validate_request_body_key_values(self, mandatory_keys, flask_request):
        """
        Check that the values of keys are not None. NOTE: Will NOT handle checking for keys. You need validate_request_body_keys() for that

        :param list mandatory_keys: List of the required keys as str
        :param flask_request: FLask request object

        :returns: A dict if there as an issue, which you should send to the client, else returns True if no error occurred.
        """
        none_keys = []
        request_body_dict = flask_request.get_json()
        if request_body_dict is None:
            return self.failure_template("Request body was 'None'")
        for key in mandatory_keys:
            if request_body_dict[key] is None:
                none_keys.append(key)
        if len(none_keys) > 0:
            return self.failure_template_null_values(none_keys)
        return True

    def combined_key_value_checks(self, mandatory_keys, flask_request):
        """
        Runs both validate_request_body_keys() and validate_request_body_key_values() to check for keys and return ones which are None.
        If both produce an error, the output from validate_request_body_keys() will be preferred.

        :param list mandatory_keys: String list of keys you want checked in the body
        :param flask_request: Flask request object

        :returns: A dict if an issue occured, which you should send to the client directly, or else returns True if no error occured. 
        """
        v = self.validate_request_body_keys(mandatory_keys, flask_request)
        if v is not True:
            return v
        else:
            v = self.validate_request_body_key_values(mandatory_keys, flask_request)
            if v is not True:
                return v
        return True