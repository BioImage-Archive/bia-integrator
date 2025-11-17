from abc import ABC, abstractmethod

from typing import Any

from curation.directive.base_directive import Directive


class ObjectCurator(ABC):
    """
    Class that handles updating objects according to the instructions in a Directive.
    """
    settings: dict

    def __init__(self, *, settings: dict | None = None) -> None:
        if settings:
            self.settings = settings
        else:
            self.settings = {}

    @abstractmethod
    def update(self, target_object: Any, directive: Directive):
        """
        Note, it is not recommended to update the version of the object as part of this method.
        The version should be be updated once all changes are applied by all directives, to avoid unnecessary version pumps.
        """
        raise NotImplementedError