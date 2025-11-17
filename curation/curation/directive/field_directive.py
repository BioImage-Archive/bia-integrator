from enum import Enum

from pydantic import (
    ConfigDict,
    ValidationError,
    model_validator,
)
from typing_extensions import Self

from curation.directive.base_directive import Directive


class FieldCommand(str, Enum):
    SET_FIELD = "set_field"

class FieldDirective(Directive[FieldCommand]):
    object_fields: dict
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def fields_match_object_type_fields(self) -> Self:
        for field in self.object_fields:
            if field not in self.object_type.model_fields:
                raise ValidationError(f"{field} does not exist in api model object fields.")
            if field in ("version", "type", "uuid"):
                raise ValidationError(f"Do not attempt to modify the {field} of an api object as part of curation directive.")
        return self

        