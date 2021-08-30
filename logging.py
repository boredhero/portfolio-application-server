from utils import InfoProivder, ConfigProvider, get_timestamp
from colorama import Fore, Style

class LoggingUtils:

    def __init__(self):
        """
        Logging utils. W.I.P
        """
        self.__info = InfoProivder()
        self.__config = ConfigProvider()

    def print_startup_message(self):
        """
        Print startup message
        """
        if self.__config.test_mode is True:
            server_mode = "TEST"
        elif self.__config.test_mode is False:
            server_mode = "PRODUCTION"
        else:
            server_mode = "ERROR"
        print(Fore.CYAN, "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
        print(Fore.CYAN, f"Portfolio App Server v{self.__info.version} '{self.__info.nickname}'")
        print(Fore.CYAN, f"Created by {self.__info.author} under the {self.__info.license} license")
        print(Fore.CYAN, "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
        print(Fore.CYAN, f"Server Mode: {server_mode}")
        print(Fore.CYAN, f"Starting Server at {get_timestamp()} ...", Style.RESET_ALL)