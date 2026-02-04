from enum import Enum


class Severity(str, Enum):
    """
    Copying logging levels from the logging module
    """

    CRITICAL = "CRICITCAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
