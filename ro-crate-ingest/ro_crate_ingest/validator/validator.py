from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


from logging import getLevelName


class Severity(str, Enum):
    """
    Copying logging levels from the logging module
    """

    CRITICAL = "CRICITCAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    # DEBUG = "DEBUG"


@dataclass
class ValidationError:
    message: str
    severity: Severity
    location_description: Optional[str] = None


class ValidationResult:
    issues: list[ValidationError]
    result: int
    validated_object: Optional[Any] = None

    def __init__(
        self, issues: list[ValidationError], validated_object: Optional[Any] = None
    ):
        self.issues = issues
        if len(issues) > 0:
            self.result = 1
        else:
            self.result = 0

        if validated_object:
            self.validated_object = validated_object
        else:
            self.validated_object = None


class Validator(ABC):
    issues: list[ValidationError]

    def __init__(self):
        self.issues = []

    @abstractmethod
    def validate(self):
        pass
