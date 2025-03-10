import logging
from typing import List, Any, Dict, Optional, Tuple, Union
from pydantic import BaseModel, ValidationError
from bia_ingest.biostudies.submission_parsing_utils import (
    find_sections_recursive,
    mattributes_to_dict,
    attributes_to_dict,
    case_insensitive_get,
)
from .api import (
    Submission,
    Section,
)
from ..cli_logging import IngestionResult, log_failed_model_creation


logger = logging.getLogger("__main__." + __name__)


# TODO: Put comments and docstring
def get_generic_section_as_list(
    root: Submission | Section,
    section_name: List[str],
    key_mapping: List[Tuple[str, str, Union[str, None, List]]],
    mapped_object: Optional[BaseModel] = None,
    mapped_attrs_dict: Optional[Dict[str, Any]] = None,
    valdiation_error_tracking: Optional[IngestionResult] = None,
) -> List[BaseModel | Dict[str, str | List[str]]]:
    """
    Map biostudies.Submission objects to a list of semantic_models or bia_data_model equivalent, or return a dictionary if no model provided.
    """
    if type(root) is Submission:
        sections = find_sections_recursive(root.section, section_name)
    else:
        sections = find_sections_recursive(root, section_name)

    return_list = []
    for section in sections:
        if mapped_attrs_dict is None:
            attr_dict = attributes_to_dict(section.attributes)
        else:
            attr_dict = mattributes_to_dict(section.attributes, mapped_attrs_dict)
        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }
        if mapped_object is None:
            return_list.append(model_dict)
        else:
            try:
                return_list.append(mapped_object.model_validate(model_dict))
            except ValidationError:
                log_failed_model_creation(mapped_object, valdiation_error_tracking)
    return return_list


# TODO: Put comments and docstring
def get_generic_section_as_dict(
    root: Submission | Section,
    section_name: List[str],
    key_mapping: List[Tuple[str, str, Union[str, None, List]]],
    mapped_object: Optional[BaseModel] = None,
    valdiation_error_tracking: Optional[IngestionResult] = None,
) -> Dict[str, Dict[str, str | List[str]] | BaseModel]:
    """
    Map biostudies.Submission objects to dict or an object
    """
    if type(root) is Submission:
        sections = find_sections_recursive(root.section, section_name, [])
    else:
        sections = find_sections_recursive(root, section_name, [])

    return_dict = {}
    for section in sections:
        attr_dict = attributes_to_dict(section.attributes)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        if mapped_object is None:
            return_dict[section.accno] = model_dict
        else:
            try:
                return_dict[section.accno] = mapped_object.model_validate(model_dict)
            except ValidationError:
                log_failed_model_creation(mapped_object, valdiation_error_tracking)
    return return_dict



def object_value_pair_to_dict(
    objects: List[Any], key_attr: str, value_attr: Optional[str]
) -> Dict[str, List[Any]]:
    """Create a dict grouping objects by value specified by 'key_attr'

    Utility function for common pattern in conversion to create a dict
    that groups objects (or an attribue) by a specified object attribute
    """

    object_dict = {}
    for obj in objects:
        key = getattr(obj, key_attr)
        object_dict[key] = getattr(obj, key, [])
        if value_attr:
            object_dict[key].append(getattr(obj, value_attr))
        else:
            object_dict[key].append(obj)

    return object_dict


class Association(BaseModel):
    image_analysis: Optional[str] = None
    image_correlation: Optional[str] = None
    biosample: Optional[str] = None
    image_acquisition: Optional[str] = None
    specimen: Optional[str] = None


def get_associations_for_section(
    section: Section,
) -> list[Association]:
    """Return the associations for a section (assume Study Component)"""
    key_mapping = [
        (
            "image_analysis",
            "Image analysis",
            None,
        ),
        (
            "image_correlation",
            "Image correlation",
            None,
        ),
        (
            "biosample",
            "Biosample",
            None,
        ),
        (
            "image_acquisition",
            "Image acquisition",
            None,
        ),
        (
            "specimen",
            "Specimen",
            None,
        ),
    ]
    associations = get_generic_section_as_list(
        section,
        [
            "Associations",
        ],
        key_mapping,
        mapped_object=Association,
    )
    return associations
