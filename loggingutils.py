from utils import InfoProivder, ConfigProvider, get_timestamp
from colorama import Fore, Style

import os, sys, logging

def windows_enable_ansi_terminal():
    if (sys.platform == "win32"):
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            result = kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            if result is 0:
                raise Exception
                return True
        except:
            return False
    else:
        return None

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


class LogFormatter(logging.Formatter):

    config = ConfigProvider()
    if config.enable_custom_log_color_config is False:
        COLOR_CODES = {
            logging.CRITICAL: "\033[1;35m",
            logging.ERROR: "\033[1;31m",
            logging.WARNING: "\033[1;33m",
            logging.INFO: "\033[1;32m",
            logging.DEBUG: "\033[1;30m"
        }
    else:
        COLOR_CODES = {
            logging.CRITICAL: config.critical_color,
            logging.ERROR: config.error_color,
            logging.WARNING: config.warning_color,
            logging.INFO: config.info_color,
            logging.DEBUG: config.debug_color
        }

    RESET_CODE = "\033[0m"

    def __init__(self, color, *args, **kwargs):
        super(LogFormatter, self).__init__(*args, **kwargs)
        self.color = color

    def format(self, record, *args, **kwargs):
        if self.color is True and record.levelno in self.COLOR_CODES:
            record.color_on = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
        else:
            record.color_on = ""
            record.color_off = ""
        return super(LogFormatter, self).format(record, *args, **kwargs)


def setup_logging(console_log_output, console_log_level, console_log_color, logfile_file, logfile_log_level, logfile_log_color, log_line_template):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        console_log_output = console_log_output.lower()
        if console_log_output == "stdout":
            console_log_output = sys.stdout
        elif console_log_output == "stderr":
            console_log_output = sys.stderr
        else:
            print(f"Failed to set console output: invalid output: '{console_log_output}'")
            return False
        console_handler = logging.StreamHandler(console_log_output)
        try:
            console_handler.setLevel(console_log_level.upper())
        except Exception as e:
            print(f"Failed to set console log level: invalid level {console_log_level}\n", e)
            return False
        console_formatter = LogFormatter(fmt=log_line_template, color=console_log_color)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        try:
            logfile_handler = logging.FileHandler(logfile_file)
        except Exception as e:
            print("Failed to set up log file\n", e)
            return False
        try:
            logfile_handler.setLevel(logfile_log_level.upper())
        except Exception as e:
            print(f"Failed to set log file log level: invalid level: '{logfile_log_level}'\n", e)
            return False
        logfile_formatter = LogFormatter(fmt=log_line_template, color=logfile_log_color)
        logfile_handler.setFormatter(logfile_formatter)
        logger.addHandler(logfile_handler)
        return True