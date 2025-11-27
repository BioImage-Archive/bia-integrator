from enum import Enum

from pydantic import (
    ValidationError,
    model_validator,
)
from typing_extensions import Self

from curation.directive.base_directive import Directive


class FieldCommand(str, Enum):
    SET_FIELD = "set_field"


class FieldDirective(Directive[FieldCommand]):
    object_fields: dict

    @model_validator(mode="after")
    def fields_match_object_type_fields(self) -> Self:
        for field in self.object_fields:
            if field not in self.object_type.model_fields:
                raise ValidationError(
                    f"{field} does not exist in api model object fields."
                )
            if field in ("version", "type", "uuid"):
                raise ValidationError(
                    f"Do not attempt to modify the {field} of an api object as part of curation directive."
                )
        return self

    def is_clashing(self, other: Directive) -> bool:
        if not isinstance(other, FieldDirective):
            return False
        elif (
            self.target_uuid != other.target_uuid
            or self.object_type != other.object_type
        ):
            return False
        elif self.object_fields == other.object_fields:
            return False
        else:
            for key, value in self.object_fields:
                if key in other.object_fields and value != other.object_fields[key]:
                    return True
            return False
