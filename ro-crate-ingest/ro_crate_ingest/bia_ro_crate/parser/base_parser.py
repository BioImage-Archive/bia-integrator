from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseParser[ParsedType](ABC):
    """Generic parser for any kind of file needed to be parsed in an ro-crate."""

    def __init__(self, *, context: Any | None = None) -> None:
        self._result = None
        super().__init__()

    @abstractmethod
    def parse(self, path: Path):
        raise NotImplementedError

    @property
    def result(self) -> ParsedType:
        if self._result is None:
            raise RuntimeError("parse() must be called prior to accessing result")
        return self._result
