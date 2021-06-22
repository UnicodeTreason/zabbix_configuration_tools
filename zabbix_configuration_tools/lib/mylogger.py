#!/usr/bin/env python3
# Import pips
import logging
import logging.handlers


class OneLineExceptionFormatter(logging.Formatter):
    ''' A class used to generate a custom log format for exceptions

    It should take any exception and munge it into a single line for output to a log file

    # TODO:
    # Learn how this works to better document it

    Source: https://docs.python.org/3/howto/logging-cookbook.html#customized-exception-formatting

    Attributes:
        logging.Formatter (object??): a reference to the logger Formatter class??
        exc_info (str):             an exception object

    Methods:
        formatException(self, exc_info):
        format

    Returns:
        Logger object magic
    '''
    def formatException(self, exc_info):
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result)

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '')
        return s


def init(name: str, path: str) -> object:
    '''Initialise a logger object for logging

    Args:
        name (str): the name of the logger
        path (str): the absolute path of the file handler output

    Returns:
        N/A
    '''
    formatter = OneLineExceptionFormatter('%(asctime)s %(levelname)s %(name)s[%(process)s]: %(message)s')

    log_handler_console = logging.StreamHandler()
    log_handler_console.setLevel(logging.INFO)
    log_handler_console.setFormatter(formatter)

    # WatchedFileHandler to handle log change during script execution
    log_handler_file = logging.handlers.WatchedFileHandler(path)
    log_handler_file.setLevel(logging.DEBUG)
    log_handler_file.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler_console)
    logger.addHandler(log_handler_file)

    logger.debug('Logging initialised')

    return logger
