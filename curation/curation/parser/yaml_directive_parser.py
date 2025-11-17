from pathlib import Path

from ruamel.yaml import YAML

from curation.directive.base_directive import Directive
from curation.parser.directive_parser import DirectiveParser


class YamlDirectivePaser(DirectiveParser):

    def parse(self, data) -> list[Directive]:
        try:
            data = Path(data)
        except:
            raise ValueError(f"Expected {data} to be Path or parseable into a Path object.")
            
        yaml = YAML()

        with open(data) as yaml_file:
            raw_directives = yaml.load(yaml_file)

        if isinstance(raw_directives, dict):
            raw_directives = [raw_directives]

        directives = []
        for directive_dict in raw_directives:
            command = directive_dict["command"]
            directive_class = self.command_to_directive_lookup.get(command)
            if not directive_class:
                raise RuntimeError(f"Directive with command {command}, did not match any know types of Directive")
            directives.append(directive_class.model_validate(directive_dict))

        return directives
            

        