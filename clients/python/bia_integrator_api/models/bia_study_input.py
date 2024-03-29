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


from typing import Any, Optional
from pydantic import BaseModel, Field

class BIAStudyInput(BaseModel):
    """
    BIAStudyInput
    """
    uuid: Optional[Any] = Field(...)
    version: Optional[Any] = Field(...)
    model: Optional[Any] = None
    title: Optional[Any] = Field(...)
    description: Optional[Any] = Field(...)
    authors: Optional[Any] = None
    organism: Optional[Any] = Field(...)
    release_date: Optional[Any] = Field(...)
    accession_id: Optional[Any] = Field(...)
    imaging_type: Optional[Any] = None
    attributes: Optional[Any] = None
    annotations: Optional[Any] = None
    example_image_uri: Optional[Any] = None
    example_image_annotation_uri: Optional[Any] = None
    tags: Optional[Any] = None
    file_references_count: Optional[Any] = None
    images_count: Optional[Any] = None
    additional_properties: Dict[str, Any] = {}
    __properties = ["uuid", "version", "model", "title", "description", "authors", "organism", "release_date", "accession_id", "imaging_type", "attributes", "annotations", "example_image_uri", "example_image_annotation_uri", "tags", "file_references_count", "images_count"]

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
    def from_json(cls, json_str: str) -> BIAStudyInput:
        """Create an instance of BIAStudyInput from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                            "additional_properties"
                          },
                          exclude_none=True)
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        # set to None if uuid (nullable) is None
        # and __fields_set__ contains the field
        if self.uuid is None and "uuid" in self.__fields_set__:
            _dict['uuid'] = None

        # set to None if version (nullable) is None
        # and __fields_set__ contains the field
        if self.version is None and "version" in self.__fields_set__:
            _dict['version'] = None

        # set to None if model (nullable) is None
        # and __fields_set__ contains the field
        if self.model is None and "model" in self.__fields_set__:
            _dict['model'] = None

        # set to None if title (nullable) is None
        # and __fields_set__ contains the field
        if self.title is None and "title" in self.__fields_set__:
            _dict['title'] = None

        # set to None if description (nullable) is None
        # and __fields_set__ contains the field
        if self.description is None and "description" in self.__fields_set__:
            _dict['description'] = None

        # set to None if authors (nullable) is None
        # and __fields_set__ contains the field
        if self.authors is None and "authors" in self.__fields_set__:
            _dict['authors'] = None

        # set to None if organism (nullable) is None
        # and __fields_set__ contains the field
        if self.organism is None and "organism" in self.__fields_set__:
            _dict['organism'] = None

        # set to None if release_date (nullable) is None
        # and __fields_set__ contains the field
        if self.release_date is None and "release_date" in self.__fields_set__:
            _dict['release_date'] = None

        # set to None if accession_id (nullable) is None
        # and __fields_set__ contains the field
        if self.accession_id is None and "accession_id" in self.__fields_set__:
            _dict['accession_id'] = None

        # set to None if imaging_type (nullable) is None
        # and __fields_set__ contains the field
        if self.imaging_type is None and "imaging_type" in self.__fields_set__:
            _dict['imaging_type'] = None

        # set to None if attributes (nullable) is None
        # and __fields_set__ contains the field
        if self.attributes is None and "attributes" in self.__fields_set__:
            _dict['attributes'] = None

        # set to None if annotations (nullable) is None
        # and __fields_set__ contains the field
        if self.annotations is None and "annotations" in self.__fields_set__:
            _dict['annotations'] = None

        # set to None if example_image_uri (nullable) is None
        # and __fields_set__ contains the field
        if self.example_image_uri is None and "example_image_uri" in self.__fields_set__:
            _dict['example_image_uri'] = None

        # set to None if example_image_annotation_uri (nullable) is None
        # and __fields_set__ contains the field
        if self.example_image_annotation_uri is None and "example_image_annotation_uri" in self.__fields_set__:
            _dict['example_image_annotation_uri'] = None

        # set to None if tags (nullable) is None
        # and __fields_set__ contains the field
        if self.tags is None and "tags" in self.__fields_set__:
            _dict['tags'] = None

        # set to None if file_references_count (nullable) is None
        # and __fields_set__ contains the field
        if self.file_references_count is None and "file_references_count" in self.__fields_set__:
            _dict['file_references_count'] = None

        # set to None if images_count (nullable) is None
        # and __fields_set__ contains the field
        if self.images_count is None and "images_count" in self.__fields_set__:
            _dict['images_count'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> BIAStudyInput:
        """Create an instance of BIAStudyInput from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return BIAStudyInput.parse_obj(obj)

        _obj = BIAStudyInput.parse_obj({
            "uuid": obj.get("uuid"),
            "version": obj.get("version"),
            "model": obj.get("model"),
            "title": obj.get("title"),
            "description": obj.get("description"),
            "authors": obj.get("authors"),
            "organism": obj.get("organism"),
            "release_date": obj.get("release_date"),
            "accession_id": obj.get("accession_id"),
            "imaging_type": obj.get("imaging_type"),
            "attributes": obj.get("attributes"),
            "annotations": obj.get("annotations"),
            "example_image_uri": obj.get("example_image_uri"),
            "example_image_annotation_uri": obj.get("example_image_annotation_uri"),
            "tags": obj.get("tags"),
            "file_references_count": obj.get("file_references_count"),
            "images_count": obj.get("images_count")
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


