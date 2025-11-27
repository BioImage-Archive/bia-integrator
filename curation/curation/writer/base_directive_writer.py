from pathlib import Path
from typing import Iterable
from abc import ABC, abstractmethod
from curation.directive import Directive
from enum import Enum
import json


class ReplacementMode(str, Enum):
    INPLACE = "inplace"
    APPEND = "append"


class DirectiveWriter(ABC):
    @staticmethod
    def _directives_to_dict_list(directives: Iterable[Directive]) -> list[dict]:
        dict_list = []
        for directive in directives:
            dict_list.append(json.loads(directive.model_dump_json()))
        return dict_list

    @abstractmethod
    def write(self, path: Path, directives: Iterable[Directive]):
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        path: Path,
        directives: Iterable[Directive],
        replacement_mode: ReplacementMode,
    ):
        raise NotImplementedError

    def _combine_directive_list(
        self,
        directives: list[Directive],
        existing_directives: list[Directive],
        replacement_mode: ReplacementMode,
    ) -> list[Directive]:

        directives_to_process = existing_directives + directives
        resulting_directives = []

        for p_directive in directives_to_process:
            directives_index_to_replace = []
            for r_index, r_directive in enumerate(resulting_directives):
                if p_directive.is_clashing(r_directive):
                    directives_index_to_replace.append(r_index)

            if len(directives_index_to_replace) > 1:
                raise RuntimeError

            if directives_index_to_replace:
                index = directives_index_to_replace[0]
                match replacement_mode:
                    case ReplacementMode.INPLACE:
                        resulting_directives[index] = p_directive
                    case ReplacementMode.APPEND:
                        resulting_directives.pop(index)
                        resulting_directives.append(p_directive)
                    case _:
                        raise ValueError("Unknown replacement mode")
            else:
                resulting_directives.append(p_directive)

        return resulting_directives
