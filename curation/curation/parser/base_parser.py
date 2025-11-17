from abc import ABC, abstractmethod


class Parser[OutputType](ABC):
    """
    Generic parser class
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def parse(self, data) -> OutputType:
        raise NotImplementedError