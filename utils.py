import json, yaml, os, platform, subprocess
from threading import Timer
from datetime import datetime

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
                        print("SimpleJsonYmlReader: read_file: Error: Filetype not JSON or YAML. Please check your fileextension")
            except FileNotFoundError as e:
                print(f"SimpleJsonYmlReader: read_file: File not found: {self.__filepath}\n", e)
            except json.JSONDecodeError as e:
                print(f"SimpleJsonYmlReader: read_file: Error decoding JSON file: {self.__filepath}\n", e)
            except yaml.YAMLError as e:
                print(f"SimpleJsonYmlReader: read_file: Error decoding YML file {self.__filepath}\n", e)
            except Exception as e:
                print(f"SimpleJsonYmlReader: read_file: An unknown error occured proccessing the file {self.__filepath}\n", e)
        else:
            print(f"SimpleJsonYmlReader: read_file: Error: File extension {self.__ext} not a valid extension!")
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
        except Exception as e:
            print(f"ConfigProvider: An unknown error occured or a value was missing from your config.yml. Check your config.yml.TEMPLATE file for a correct example\n", e)

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
            print("InfoProvider: An unknown error occured or a value was missing from your info.yml. Check that your info file exists!\n", e)
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