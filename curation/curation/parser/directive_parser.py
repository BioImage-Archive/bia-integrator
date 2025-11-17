import inspect
from typing import Iterable

from curation import directive
from curation.directive import DIRECTIVE_CLASSES, base_directive
from curation.parser.base_parser import Parser


class DirectiveParser(Parser[list[base_directive.Directive]]):
    """
    Superclass for all directive parsers.
    """
    directive_types: set[type[directive.Directive]]
    command_to_directive_lookup: dict[str, type[directive.Directive]]

    def __init__(self, directive_types: Iterable[type[directive.Directive]] | None = None) -> None:
        self.directive_types = set()
        self.register_directives(directive_types or DIRECTIVE_CLASSES)
 
        self.command_to_directive_lookup = self._build_command_lookup()
        super().__init__()
        
    def register_directives(self, directive_types: Iterable[type[directive.Directive]]):
        for directive_type in directive_types:
            if inspect.isabstract(directive_type):
                continue
            self.directive_types.add(directive_type)
    
    def _build_command_lookup(self) -> dict[str, type[directive.Directive]]:
        lookup = {}
        for directive_type in self.directive_types:
            command_enum = directive_type.model_fields["command"].annotation
            for command_instance in command_enum:
                if command_instance in lookup:
                    raise KeyError("Two registered command types have the same value for the comamnd enum.")
                lookup[command_instance.value] = directive_type
        return lookup