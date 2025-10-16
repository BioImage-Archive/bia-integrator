from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """
    Copying logging levels from the logging module
    """

    CRITICAL = "CRICITCAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


@dataclass
class ValidationError:
    message: str
    severity: Severity
    location_description: str | None = None


class ValidationResult:
    issues: list[ValidationError]
    result: int
    validated_object: Any = None

    def __init__(self, issues: list[ValidationError], validated_object: Any = None):
        self.issues = issues
        if len(issues) > 0:
            self.result = 1
        else:
            self.result = 0

        self.validated_object = validated_object


class Validator(ABC):
    issues: list[ValidationError]

    def __init__(self):
        self.issues = []

    @abstractmethod
    def validate(self) -> ValidationResult:
        raise NotImplementedError
