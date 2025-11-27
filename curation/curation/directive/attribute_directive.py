import inspect
from enum import Enum
from functools import cache
from typing import Any

from bia_integrator_api import models
from bia_integrator_api.models import Provenance
from bia_shared_datamodels import attribute_models, semantic_models
from pydantic import Field, ValidationError, field_validator, model_validator
from typing_extensions import Self

from curation.directive.base_directive import Directive


class AttributeCommand(str, Enum):
    ADD_ATTRIBUTE = "add_attribute"
    DELETE_ATTRIBUTE = "delete_attribute"
    UPDATE_ATTRIBUTE = "update_attribute"


class AttributeDirective(Directive[AttributeCommand]):
    provenance: Provenance = Field(Provenance.BIA_CURATION)
    name: str
    value: str | dict | None = Field(None)
    attribute_model: type[semantic_models.Attribute] | None = Field(None)

    @field_validator("attribute_model", mode="before")
    @classmethod
    def attribute_model_name_to_class(
        cls, value: Any
    ) -> type[semantic_models.Attribute]:
        if value == None:
            return value
        elif isinstance(value, type) and issubclass(value, semantic_models.Attribute):
            return value
        elif isinstance(value, str):
            attribute_class_lookup = cls._get_attribute_class_lookup()
            if value not in attribute_class_lookup:
                raise ValidationError(
                    f"{value} is not the name of a subclass of Attribute."
                )
            else:
                return attribute_class_lookup[value]
        else:
            raise ValidationError(
                f"Unexpected type for attribute_model field (found: {type(value)})"
            )

    @model_validator(mode="after")
    def value_required(self) -> Self:
        """Delete attribute commads do not require a value, but otherwise they are necessary."""
        if self.command != AttributeCommand.DELETE_ATTRIBUTE:
            if not self.value:
                raise ValidationError(
                    f"value field is required for directives performing {self.command}."
                )
        return self

    def assemble_attribute(self) -> models.Attribute:
        if isinstance(self.value, str):
            # 'Basic' attribute case, where we don't really need a dictionary, so the only key is the same as the name.
            value = {self.name: self.value}
        elif isinstance(self.value, dict):
            value = self.value
        else:
            raise TypeError(
                f"Expected dictionary or string for attribute, found: {type(self.value)}"
            )

        attribute_dict = {
            "name": self.name,
            "provenance": self.provenance,
            "value": value,
        }

        if self.attribute_model:
            # Just check attribute if directive follow the model definition.
            self.attribute_model.model_validate(attribute_dict)

        return models.Attribute(**attribute_dict)

    @classmethod
    @cache
    def _get_attribute_class_lookup(cls) -> dict[str, type[semantic_models.Attribute]]:
        return {
            name: attribute_class
            for name, attribute_class in inspect.getmembers(
                attribute_models,
                lambda member: inspect.isclass(member)
                and member.__module__ == "bia_shared_datamodels.attribute_models"
                and issubclass(member, semantic_models.Attribute),
            )
        }

    def is_clashing(self, other: Directive) -> bool:
        if not isinstance(other, AttributeDirective):
            return False
        elif (
            self.target_uuid != other.target_uuid
            or self.object_type != other.object_type
            or self.name != other.name
        ):
            return False
        elif self.value == other.value:
            return False
        else:
            return True
