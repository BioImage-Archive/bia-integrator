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


from typing import List, Optional
from pydantic import BaseModel, StrictStr, conint, conlist
from bia_integrator_api.models.search_annotation import SearchAnnotation
from bia_integrator_api.models.search_study import SearchStudy

class SearchStudyFilter(BaseModel):
    """
    SearchStudyFilter
    """
    annotations_any: Optional[conlist(SearchAnnotation)] = None
    study_match: Optional[SearchStudy] = None
    start_uuid: Optional[StrictStr] = None
    limit: Optional[conint(strict=True, ge=0)] = 10
    __properties = ["annotations_any", "study_match", "start_uuid", "limit"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> SearchStudyFilter:
        """Create an instance of SearchStudyFilter from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in annotations_any (list)
        _items = []
        if self.annotations_any:
            for _item in self.annotations_any:
                if _item:
                    _items.append(_item.to_dict())
            _dict['annotations_any'] = _items
        # override the default output from pydantic by calling `to_dict()` of study_match
        if self.study_match:
            _dict['study_match'] = self.study_match.to_dict()
        # set to None if study_match (nullable) is None
        # and __fields_set__ contains the field
        if self.study_match is None and "study_match" in self.__fields_set__:
            _dict['study_match'] = None

        # set to None if start_uuid (nullable) is None
        # and __fields_set__ contains the field
        if self.start_uuid is None and "start_uuid" in self.__fields_set__:
            _dict['start_uuid'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> SearchStudyFilter:
        """Create an instance of SearchStudyFilter from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return SearchStudyFilter.parse_obj(obj)

        _obj = SearchStudyFilter.parse_obj({
            "annotations_any": [SearchAnnotation.from_dict(_item) for _item in obj.get("annotations_any")] if obj.get("annotations_any") is not None else None,
            "study_match": SearchStudy.from_dict(obj.get("study_match")) if obj.get("study_match") is not None else None,
            "start_uuid": obj.get("start_uuid"),
            "limit": obj.get("limit") if obj.get("limit") is not None else 10
        })
        return _obj

