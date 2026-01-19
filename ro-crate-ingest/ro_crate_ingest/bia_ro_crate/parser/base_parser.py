from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Parser[ParsedType](ABC):
    """Generic parser for any kind of file needed to be parsed in an ro-crate."""

    def __init__(self, *, context: Any | None = None) -> None:
        # TODO init to take a root path for the ro-crate.
        self._result = None
        super().__init__()

    @abstractmethod
    def parse(self, path: Path):
        # TODO update this path to always be relative to the root of the ro-crate for consistency
        raise NotImplementedError

    @property
    def result(self) -> ParsedType:
        if self._result is None:
            raise RuntimeError("parse() must be called prior to accessing result")
        return self._result
