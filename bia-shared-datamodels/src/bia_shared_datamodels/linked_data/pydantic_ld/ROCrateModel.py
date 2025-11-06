from .LDModel import LDModel
from pydantic import Field, field_validator, model_validator
from rdflib import URIRef
from typing import Union


class ROCrateModel(LDModel):
    id: str = Field(alias="@id")
    type: Union[str, list[str]] = Field(alias="@type")

    @classmethod
    def get_model_type(cls) -> URIRef:
        required_type = cls.model_config.get("model_type")
        return URIRef(required_type)

    @field_validator("type", mode="after")
    @classmethod
    def includes_expected_type(
        cls, value: Union[str, list[str]]
    ) -> Union[str, list[str]]:
        """
        Note, this assume the object has either been expanded to have full urls for the types, or the standard bia context is being used. The actual document context is not checked.
        """
        expected_class: str = cls.model_config.get("model_type")
        short_string = expected_class.replace(
            "http://www.w3.org/ns/csvw#", "csvw:"
        ).replace("http://bia/", "bia:")

        if isinstance(value, str):
            if value != expected_class and value != short_string:
                raise ValueError(
                    f"Expected {expected_class}, or {short_string} in types, found: {value}"
                )
        else:
            if expected_class not in value and short_string not in value:
                raise ValueError(
                    f"Expected {expected_class}, or {short_string} in types, found: {value}"
                )

        return value

    @model_validator(mode="after")
    def coerce_dataset_ids(self):
        dataset_class = [
            "http://schema.org/Dataset",
            "https://schema.org/Dataset",
            "Dataset",
        ]
        rdf_types = self.type if isinstance(self.type, list) else [self.type]
        for class_string in dataset_class:
            if class_string in rdf_types:
                self.id = f"{self.id}/" if not str.endswith(self.id, "/") else self.id

        return self
