import logging
import typing as typing


def get_file_handler(level: int = logging.WARNING):
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(CustomFormatter.def_format))
    return file_handler


def get_stream_handler(level: int = logging.DEBUG):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(CustomFormatter())
    # stream_handler.addFilter(CustomFilter())
    return stream_handler


def get_logger(name, level=logging.DEBUG, stream_level: int = logging.DEBUG, file_level: int = logging.WARN):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(get_file_handler(level=file_level))
    logger.addHandler(get_stream_handler(level=stream_level))
    return logger


class CustomFilter(logging.Filter):

    COLOR = {
        "DEBUG": "GREEN",
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "RED",
    }

    def filter(self, record):
        record.color = CustomFilter.COLOR[record.levelname]
        return True


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    # COLORS = lambda **kwargs: type("COLORS", (), kwargs) #type('', (), {})()
    COLORS = obj = type('COLORS', (object,), {
        'grey': "\x1b[38;21m",
        'yellow': "\x1b[33;21m",
        'red': "\x1b[31;21m",
        'bold_red': "\x1b[31;1m",
        'black': "\x1b[30;21m",
        'green': "\x1b[32;21m",
        'blue': "\x1b[34;21m",
        'magenta': "\x1b[35;21m",
        'cyan': "\x1b[36;21m",
        'white': "\x1b[37;21m",
        'reset': "\x1b[0m"
    })()
    '''COLORS.grey = "\x1b[38;21m"
    COLORS.yellow = "\x1b[33;21m"
    COLORS.red = "\x1b[31;21m"
    COLORS.bold_red = "\x1b[31;1m"
    COLORS.reset = "\x1b[0m"'''
    '''Black: \u001b[30;1m
    Red: \u001b[31;1m
    Green: \u001b[32;1m
    Yellow: \u001b[33;1m
    Blue: \u001b[34;1m
    Magenta: \u001b[35;1m
    Cyan: \u001b[36;1m
    White: \u001b[37;1m'''

    def_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    def __init__(self, fmt=def_format, datefmt=None, style='%', validate=True):
        super(CustomFormatter, self).__init__(
            fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self.FORMATS = {
            logging.DEBUG: CustomFormatter.COLORS.cyan + fmt + CustomFormatter.COLORS.reset,
            logging.INFO: CustomFormatter.COLORS.grey + fmt + CustomFormatter.COLORS.reset,
            logging.WARNING: CustomFormatter.COLORS.yellow + fmt + CustomFormatter.COLORS.reset,
            logging.ERROR: CustomFormatter.COLORS.red + fmt + CustomFormatter.COLORS.reset,
            logging.CRITICAL: CustomFormatter.COLORS.bold_red +
            fmt + CustomFormatter.COLORS.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
