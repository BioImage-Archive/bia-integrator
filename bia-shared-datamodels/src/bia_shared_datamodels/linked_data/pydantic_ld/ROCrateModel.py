from .LDModel import LDModel
from .FieldContext import FieldContext
from pydantic import Field
from rdflib import RDF, URIRef
from typing import Annotated, Union


class ROCrateModel(LDModel):
    id: str = Field(alias="@id")
    type: Union[str, list[str]] = Field(alias="@type")

    @classmethod
    def get_model_type(cls) -> URIRef:
        required_type = cls.model_config.get("model_type")
        return URIRef(required_type)
