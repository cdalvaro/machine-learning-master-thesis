import logging


class Logger():

    _logger: logging.Logger = None

    @staticmethod
    def instance() -> logging.Logger:
        if Logger._logger:
            return Logger._logger

        Logger._logger = logging.getLogger('Gaia Downloader')

        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(CustomFormatter())
        Logger._logger.addHandler(ch)

        return Logger._logger


class ColorCodes:
    grey = "\033[0;37m"
    green = "\033[0;32m"
    yellow = "\033[1;33m"
    red = "\033[0;31m"
    bold_red = "\033[31;1m"
    blue = "\033[0;34m"
    purple = "\033[0;35m"
    reset = "\033[0m"


def _custom_format(color: str):
    return f"{color}%(levelname)s{ColorCodes.reset}: %(message)s"


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    datefmt = "%Y-%m-%d %H:%M:%S"

    FORMATS = {
        logging.DEBUG: _custom_format(color=ColorCodes.purple),
        logging.INFO: _custom_format(color=ColorCodes.green),
        logging.WARNING: _custom_format(color=ColorCodes.yellow),
        logging.ERROR: _custom_format(color=ColorCodes.red),
        logging.CRITICAL: _custom_format(color=ColorCodes.bold_red)
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
