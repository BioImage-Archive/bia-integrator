import logging
from pathlib import Path
import hashlib
import uuid
from typing import List, Any, Dict, Optional, Tuple, Type, Union
from pydantic import BaseModel
from ..biostudies import (
    Submission,
    attributes_to_dict,
    Section,
    Attribute,
)
from ..config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# TODO: Put comments and docstring
def get_generic_section_as_list(
    root: Submission | Section,
    section_name: List[str],
    key_mapping: List[Tuple[str, str, str | None | List]],
    mapped_object: Optional[Any] = None,
    mapped_attrs_dict: Optional[Dict[str, Any]] = None,
) -> List[Any | Dict[str, str | List[str]]]:
    """
    Map biostudies.Submission objects to either semantic_models or bia_data_model equivalent
    """
    if type(root) is Submission:
        sections = find_sections_recursive(root.section, section_name, [])
    else:
        sections = find_sections_recursive(root, section_name, [])

    return_list = []
    for section in sections:
        if mapped_attrs_dict is None:
            attr_dict = attributes_to_dict(section.attributes)
        else:
            attr_dict = mattributes_to_dict(section.attributes, mapped_attrs_dict)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        if mapped_object is None:
            return_list.append(model_dict)
        else:
            return_list.append(mapped_object.model_validate(model_dict))
    return return_list


# TODO: Put comments and docstring
def get_generic_section_as_dict(
    root: Submission | Section,
    section_name: List[str],
    key_mapping: List[Tuple[str, str, Union[str, None, List]]],
    mapped_object: Optional[Any] = None,
) -> Dict[str, Any | Dict[str, Dict[str, str | List[str]]]]:
    """
    Map biostudies.Submission objects to dict containing either semantic_models or bia_data_model equivalent
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
            return_dict[section.accno] = mapped_object.model_validate(model_dict)
    return return_dict


# This function instantiates any API model given a dict of its attributes
# Hence the use of the pydantic BaseModel which all API models
# are derived from in the type hinting
def dicts_to_api_models(
    dicts: List[Dict[str, Any]], api_model_class: Type[BaseModel]
) -> BaseModel:

    api_models = []
    for model_dict in dicts:
        api_models.append(api_model_class.model_validate(model_dict))

    return api_models


def find_sections_recursive(
    section: Section, search_types: List[str], results: Optional[List[Section]] = []
) -> List[Section]:
    """
    Find all sections of search_types within tree, starting at given section
    """

    search_types_lower = [s.lower() for s in search_types]
    if section.type.lower() in search_types_lower:
        results.append(section)

    # Each thing in section.subsections is either Section or List[Section]
    # First, let's make sure we ensure they're all lists:
    nested = [
        [item] if not isinstance(item, list) else item for item in section.subsections
    ]
    # Then we can flatten this list of lists:
    flattened = sum(nested, [])

    for section in flattened:
        find_sections_recursive(section, search_types, results)

    return results


# TODO check type of reference_dict. Possibly Dict[str, str], but need to
# verify. This also determines type returned by function
def mattributes_to_dict(
    attributes: List[Attribute], reference_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Return attributes as dictionary dereferencing attribute references

    Return the list of attributes supplied as a dictionary. Any attributes
    whose values are references are 'dereferenced' using the reference_dict
    """

    def value_or_dereference(attr):
        if attr.reference:
            return reference_dict[attr.value]
        else:
            return attr.value

    return {attr.name: value_or_dereference(attr) for attr in attributes}


# TODO: Need to use a canonical version for this function e.g. from API
def dict_to_uuid(my_dict: Dict[str, Any], attributes_to_consider: List[str]) -> str:
    """
    Create uuid from specific keys in a dictionary
    """

    seed = "".join([f"{my_dict[attr]}" for attr in attributes_to_consider])
    hexdigest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return str(uuid.UUID(version=4, hex=hexdigest))


def persist(object_list: List, object_path: str, sumbission_accno: str):
    output_dir = Path(settings.bia_data_dir) / object_path / sumbission_accno
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True)
        logger.info(f"Created {output_dir}")
    for object in object_list:
        output_path = output_dir / f"{object.uuid}.json"
        output_path.write_text(object.model_dump_json(indent=2))
        logger.info(f"Written {output_path}")


def filter_model_dictionary(dictionary: dict, target_model: Type[BaseModel]):
    accepted_fields = target_model.model_fields.keys()
    result_dict = {key: dictionary[key] for key in accepted_fields if key in dictionary}
    return result_dict
