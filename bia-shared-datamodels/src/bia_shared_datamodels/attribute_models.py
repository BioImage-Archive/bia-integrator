from __future__ import annotations

from typing import Optional, Any
from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator, field_validator
from .semantic_models import Attribute, Provenance
from uuid import UUID

# For shared models that are placed inside Attribute objects
# The API does not enforce what is created inside an Attribute object's value (beyond it being a dicitionary).
# This allows us to have additional freeform information from submitters.
# Model here are for use by BIA internal code packages that require a shared source of truth.


class SubAttributeMixin(BaseModel):
    def __eq__(self, other):
        if other.__class__ == Attribute:
            attribute_self = Attribute.model_validate(self.model_dump())
            return attribute_self.__eq__(other)
        else:
            return BaseModel.__eq__(self, other)


class DatasetAssociationValue(BaseModel):
    # Allows None, but requires fields to be present
    image_analysis: Optional[str] = Field()
    image_correlation: Optional[str] = Field()
    biosample: Optional[str] = Field()
    image_acquisition: Optional[str] = Field()
    specimen: Optional[str] = Field()


class DatasetAssociationAttribute(Attribute, SubAttributeMixin):
    """
    Model for storing user provided Associations from biostudies in an Attribute on a dataset.
    """

    @field_validator("provenance", mode="after")
    @classmethod
    def attribute_provenance(cls, value: Provenance) -> Provenance:
        if value != Provenance.bia_ingest:
            raise ValueError(
                f"Provenance for this type of attribute must be {Provenance.bia_ingest}"
            )

        return value

    @field_validator("name", mode="after")
    @classmethod
    def attribute_name(cls, value: str) -> str:
        if value != "associations":
            raise ValueError(
                f"name field for this type of attribute must be 'associations'"
            )
        return value

    @field_validator("value", mode="after")
    @classmethod
    def attribute_value(cls, value: dict) -> dict:
        if len(value.keys()) != 1:
            raise ValueError("Value dictionary should have exactly one 1 key")
        elif "associations" not in value.keys():
            raise ValueError(f'The value dictionary key must be "associations"')
        return value

    value: dict[str, list[DatasetAssociationValue]] = Field()


class DatasetAssociatedUUIDAttribute(Attribute, SubAttributeMixin):
    """
    Model for storing uuid of objects linked to a dataset, for use in code downstream of ingest.
    """

    @field_validator("provenance", mode="after")
    @classmethod
    def attribute_provenance(cls, value: Provenance) -> Provenance:
        if value != Provenance.bia_ingest:
            raise ValueError(
                f"Provenance for this type of attribute must be {Provenance.bia_ingest}"
            )
        return value

    @field_validator("name", mode="after")
    @classmethod
    def validate_attribute_name(cls, value) -> Self:
        valid_associations = [
            "image_acquisition_protocol_uuid",
            "specimen_imaging_preparation_protocol_uuid",
            "bio_sample_uuid",
            "annotation_method_uuid",
            "protocol_uuid",
        ]
        if value not in valid_associations:
            raise ValueError(
                f"Name for this type of attribute must be one of: {valid_associations}"
            )

        return value

    @model_validator(mode="after")
    def validate_attribute_value_key(self) -> Self:
        if len(self.value.keys()) != 1:
            raise ValueError("Value dictionary should have exactly one 1 key")
        elif self.name not in self.value.keys():
            raise ValueError(f"The key for this type of attribute must be {self.name}")
        return self

    value: dict[str, list[str]] = Field()


class DocumentUUIDUinqueInputAttribute(Attribute, SubAttributeMixin):
    """
    Model for storing the string that was used to generate the uuid of the object.
    Note this does not need to contain the type nor the study uuid, since those should be findable in the rest of the document / through object links.
    """

    @field_validator("name", mode="after")
    @classmethod
    def validate_attribute_name(cls, value) -> Self:
        if value != "uuid_unique_input":
            raise ValueError(
                f"Name for this type of attribute must be 'uuid_unique_input'"
            )
        return value

    @field_validator("value", mode="after")
    @classmethod
    def attribute_value(cls, value: dict) -> dict:
        if len(value.keys()) != 1:
            raise ValueError("Value dictionary should have exactly one 1 key")
        elif "uuid_unique_input" not in value.keys():
            raise ValueError(f'The value dictionary key must be "uuid_unique_input"')
        return value

    value: dict[str, str] = Field()
