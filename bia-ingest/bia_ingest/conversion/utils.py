import logging
from pathlib import Path
from uuid import UUID
import hashlib
import uuid
from typing import List, Any, Dict, Optional, Tuple, Type, Union
from pydantic import BaseModel, ValidationError
from pydantic.alias_generators import to_snake
from ..biostudies import (
    Submission,
    attributes_to_dict,
    Section,
    Attribute,
    find_file_lists_in_submission,
)
from ..config import settings, api_client
from ..cli_logging import IngestionResult
import bia_integrator_api.models as api_models

logger = logging.getLogger("__main__." + __name__)


def log_failed_model_creation(
    model_class: Type[BaseModel], valdiation_error_tracking: IngestionResult
) -> None:
    logger.error(f"Failed to create {model_class.__name__}")
    logger.debug("Pydantic Validation Error:", exc_info=True)
    field_name = f"{model_class.__name__}_ValidationErrorCount"
    valdiation_error_tracking.__setattr__(
        field_name, valdiation_error_tracking.__getattribute__(field_name) + 1
    )


def log_model_creation_count(
    model_class: Type[BaseModel], count: int, valdiation_error_tracking: IngestionResult
) -> None:
    logger.info(f"Created {model_class.__name__}. Count: {count}")
    field_name = f"{model_class.__name__}_CreationCount"
    valdiation_error_tracking.__setattr__(
        field_name, valdiation_error_tracking.__getattribute__(field_name) + count
    )


# TODO: Put comments and docstring
def get_generic_section_as_list(
    root: Submission | Section,
    section_name: List[str],
    key_mapping: List[Tuple[str, str, str | None | List]],
    mapped_object: Optional[BaseModel] = None,
    mapped_attrs_dict: Optional[Dict[str, Any]] = None,
    valdiation_error_tracking: Optional[IngestionResult] = None,
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
            if not valdiation_error_tracking:
                raise RuntimeError(
                    "If a mapped_object is provided, valdiation_error_tracking needs to also be provided."
                )
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
            if not valdiation_error_tracking:
                raise RuntimeError(
                    "If a mapped_object is provided, valdiation_error_tracking needs to also be provided."
                )
            try:
                return_dict[section.accno] = mapped_object.model_validate(model_dict)
            except ValidationError:
                log_failed_model_creation(mapped_object, valdiation_error_tracking)
    return return_dict


# This function instantiates any API model given a dict of its attributes
# Hence the use of the pydantic BaseModel which all API models
# are derived from in the type hinting
def dicts_to_api_models(
    dicts: List[Dict[str, Any]],
    api_model_class: Type[BaseModel],
    valdiation_error_tracking: IngestionResult,
) -> BaseModel:
    api_models = []
    for model_dict in dicts:
        try:
            api_models.append(api_model_class.model_validate(model_dict))
        except ValidationError:
            log_failed_model_creation(api_model_class, valdiation_error_tracking)
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


def persist(object_list: List[BaseModel], object_path: str, sumbission_accno: str):
    if object_path == "api":
        for obj in object_list:
            api_creation_method = f"post_{to_snake(obj.model.type_name)}"
            api_obj = getattr(api_models, obj.model.type_name).model_validate_json(
                obj.model_dump_json()
            )
            getattr(api_client, api_creation_method)(api_obj)
            logger.info(f"persisted {obj.uuid} to API")
    else:
        output_dir = Path(settings.bia_data_dir) / object_path / sumbission_accno
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
            logger.debug(f"Created {output_dir}")
        for obj in object_list:
            output_path = output_dir / f"{obj.uuid}.json"
            output_path.write_text(obj.model_dump_json(indent=2))
            logger.debug(f"Written {output_path}")


def filter_model_dictionary(dictionary: dict, target_model: Type[BaseModel]):
    accepted_fields = target_model.model_fields.keys()
    result_dict = {key: dictionary[key] for key in accepted_fields if key in dictionary}
    return result_dict


def find_datasets_with_file_lists(
    submission: Submission,
) -> List[Dict[str, List[Dict[str, Union[str, None, List[str]]]]]]:
    """
    Return dict with dataset names as keys and file lists dicts as values

    Wrapper around 'biostudies.find_file_lists_in_submission'. Creates a
    dict whos keys are the dataset titles and values are list of dicts
    of the file list details.

    'datasets' can be sections of type 'Study component' or 'Annotation'
    """

    file_list_dicts = find_file_lists_in_submission(submission)

    # Associate each dataset name with a list because there is no thing
    # preventing different datasets having the same title. If this happens
    # values will be appended instead of being overwritten
    datasets_with_file_lists = {}
    for fld in file_list_dicts:
        if "Name" in fld:
            if fld["Name"] not in datasets_with_file_lists:
                datasets_with_file_lists[fld["Name"]] = []
            datasets_with_file_lists[fld["Name"]].append(fld)
        elif "Title" in fld:
            if fld["Title"] not in datasets_with_file_lists:
                datasets_with_file_lists[fld["Title"]] = []
            datasets_with_file_lists[fld["Title"]].append(fld)

    return datasets_with_file_lists


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


# TODO: Find out how to get generic type for bia_data_model (baseclass?)
def get_bia_data_model_by_uuid(
    uuid: UUID, model_class: Type[BaseModel], accession_id: str = ""
) -> BaseModel:
    """Instantiate a bia_data_model from a json file on disk"""
    import re

    model_name_parts = [
        s.lower() for s in re.split(r"(?=[A-Z])", model_class.__name__) if len(s) > 0
    ]
    model_subdir = "_".join(model_name_parts) + "s"
    input_path = (
        Path(settings.bia_data_dir) / model_subdir / accession_id / f"{uuid}.json"
    )
    return model_class.model_validate_json(input_path.read_text())


def merge_dicts(dict_list: List[Dict[str, str]]) -> Dict:
    """Merge list of dicts to one dict. Values for repeated keys are put into lists

    Assumes all input dict values are strings as in function type hint
    """

    if not dict_list:
        return {}

    merged_dict = dict_list[0]

    for dictionary in dict_list[1:]:
        for key, value in dictionary.items():
            # If the key already exists in the merged dictionary
            if key in merged_dict:
                # If it's not already a list, convert the current value to a list
                if not isinstance(merged_dict[key], list):
                    merged_dict[key] = [merged_dict[key]]
                # Append the new value to the list
                merged_dict[key].append(value)
            else:
                # If the key does not exist, add it to the merged dictionary
                merged_dict[key] = value

    return merged_dict