import inspect
from abc import ABC
from functools import cache
from typing import Any
from uuid import UUID

from bia_integrator_api import models
from pydantic import BaseModel, ValidationError, field_validator


class Directive[CommandType](BaseModel, ABC):
    """
    Directives are re-runnable commands that modify objects we store.
    """
    target_uuid: UUID
    object_type: type[BaseModel]
    command: CommandType #Sub-type directive should define enum

    @field_validator('object_type', mode="before")
    @classmethod
    def object_type_name_to_class(cls, value: Any) -> type:
        document_type_lookup = cls._get_document_type_lookup()
        if isinstance(value, type) and value in document_type_lookup.values():
            return value
        elif isinstance(value, str) and value in document_type_lookup:
            return document_type_lookup[value]
        else:
            raise ValidationError(f"{value} does not correspond to an API object type.")

    @classmethod
    @cache
    def _get_document_type_lookup(cls) -> dict[str, type[BaseModel]]:
        return  {
            name: attribute_class
            for name, attribute_class in inspect.getmembers(
                models,
                lambda member: inspect.isclass(member)
                and member.__module__.startswith("bia_integrator_api.models")
                and issubclass(member, BaseModel),
            )
        }

    def print_command(self):
        print(f"{self.target_uuid}, {self.object_type}: {self.command}")