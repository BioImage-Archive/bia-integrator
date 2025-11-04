from abc import ABC, abstractmethod


class Parser[T](ABC):

    def __init__(self, context=None) -> None:
        self._result = None
        super().__init__()

    @abstractmethod
    def parse(self, data):
        raise NotImplementedError

    @property
    def result(self) -> T:
        if self._result is None:
            raise RuntimeError("parse() must be called prior to accessing result")
        return self._result
