from pathlib import Path
from typing import Iterable

from directive import Directive
from ruamel.yaml import YAML


class YamlDirectiveWriter():

    @staticmethod
    def _directives_to_dict(directives: Iterable[Directive]):
        dict_list = [] 
        for directive in directives:
            dict_list.append(directive.model_dump())

    def write(self, path: Path, directives: Iterable[Directive]):

        directive_list = self._directives_to_dict(directives)
        yaml = YAML()
        with open(path, 'w') as yamlfile:
            yaml.dump(directive_list, yamlfile)