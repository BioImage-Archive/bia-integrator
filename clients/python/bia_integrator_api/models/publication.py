# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class Publication(BaseModel):
    """
    A published paper or written work.
    """ # noqa: E501
    authors_name: StrictStr = Field(description="The list of names of the authors as displayed in the publication.")
    title: StrictStr = Field(description="The title of the publication.")
    publication_year: StrictInt = Field(description="Year the article was published")
    pubmed_id: Optional[StrictStr] = None
    doi: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["authors_name", "title", "publication_year", "pubmed_id", "doi"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of Publication from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # set to None if pubmed_id (nullable) is None
        # and model_fields_set contains the field
        if self.pubmed_id is None and "pubmed_id" in self.model_fields_set:
            _dict['pubmed_id'] = None

        # set to None if doi (nullable) is None
        # and model_fields_set contains the field
        if self.doi is None and "doi" in self.model_fields_set:
            _dict['doi'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Publication from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "authors_name": obj.get("authors_name"),
            "title": obj.get("title"),
            "publication_year": obj.get("publication_year"),
            "pubmed_id": obj.get("pubmed_id"),
            "doi": obj.get("doi")
        })
        return _obj

