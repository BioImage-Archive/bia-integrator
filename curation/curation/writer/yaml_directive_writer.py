from pathlib import Path
from typing import Iterable

from curation.directive.base_directive import Directive
from ruamel.yaml import YAML
from curation.parser.yaml_directive_parser import YamlDirectivePaser
from curation.writer.base_directive_writer import DirectiveWriter, ReplacementMode


class YamlDirectiveWriter(DirectiveWriter):

    def write(self, path: Path, directives: Iterable[Directive]):
        
        path.parent.mkdir(exist_ok=True, parents=True)

        directive_list = self._directives_to_dict_list(directives)
        yaml = YAML()
        with open(path, "w") as yamlfile:
            yaml.dump(directive_list, yamlfile)

    def update(
        self,
        path: Path,
        directives: Iterable[Directive],
        replacement_mode=ReplacementMode.INPLACE,
    ):

        if path.exists():
            existing_directives = YamlDirectivePaser().parse(path)
        else:
            existing_directives = []

        resulting_directives = self._combine_directive_list(
            directives, existing_directives, replacement_mode
        )

        self.write(path, resulting_directives)
