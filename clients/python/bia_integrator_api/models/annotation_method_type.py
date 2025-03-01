# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import json
from enum import Enum
from typing_extensions import Self


class AnnotationMethodType(str, Enum):
    """
    AnnotationMethodType
    """

    """
    allowed enum values
    """
    CLASS_LABELS = 'class_labels'
    BOUNDING_BOXES = 'bounding_boxes'
    COUNTS = 'counts'
    DERIVED_ANNOTATIONS = 'derived_annotations'
    GEOMETRICAL_ANNOTATIONS = 'geometrical_annotations'
    GRAPHS = 'graphs'
    POINT_ANNOTATIONS = 'point_annotations'
    SEGMENTATION_MASK = 'segmentation_mask'
    TRACKS = 'tracks'
    WEAK_ANNOTATIONS = 'weak_annotations'
    OTHER = 'other'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of AnnotationMethodType from a JSON string"""
        return cls(json.loads(json_str))


