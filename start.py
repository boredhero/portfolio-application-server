from flask import app
from server import app, init_logger
from loggingutils import LoggingUtils

if __name__ == "__main__":
    log = LoggingUtils()
    log.print_startup_message()
    init_logger()
    app.run()