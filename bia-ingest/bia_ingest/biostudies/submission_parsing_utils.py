from bia_ingest.biostudies.api import (
    Attribute,
    File,
    Section,
    Submission,
    flist_from_flist_fname,
)

from typing import Any, Dict, List, Optional, Union

from bia_ingest.logging_configuration import logging_config

logger = logging_config.getLogger("__main__." + __name__)


def attributes_to_dict(
    attributes: List[Attribute],
) -> Dict[str, Optional[str | List[str]]]:
    # TODO check type of reference_dict. Possibly Dict[str, str], but need to
    # verify. This also determines type returned by function
    attr_dict = {}
    for attr in attributes:
        if attr.name in attr_dict:
            if isinstance(attr_dict[attr.name], list):
                attr_dict[attr.name].append(attr.value)
            else:
                attr_dict[attr.name] = [
                    attr_dict[attr.name],
                ]
                attr_dict[attr.name].append(attr.value)
        else:
            attr_dict[attr.name] = attr.value
    return attr_dict


def find_file_lists_in_section(
    section: Section, flists: List[Dict[str, Union[str, None, List[str]]]]
) -> List[Dict[str, Union[str, None, List[str]]]]:
    """
    Find all of the File Lists in a Section, recursively descending through the subsections.

    Return a list of dictionaries.
    """

    attr_dict = attributes_to_dict(section.attributes)

    if "File List" in attr_dict:
        flists.append(attr_dict)
        # Get details of any associations in this subsection
        attr_dict["associations"] = []
        for subsection in section.subsections:
            if subsection.type == "Associations":
                attr_dict["associations"].append(
                    attributes_to_dict(subsection.attributes)
                )

    for subsection in section.subsections:
        subsection_type = type(subsection)
        if subsection_type == Section:
            find_file_lists_in_section(subsection, flists)  # type: ignore
        else:
            logger.warning(
                f"Not processing subsection as type is {subsection_type}, not 'Section'. Contents={subsection}"
            )
            logger.info(f"TABLE ::: WARNING ::: Unprocessed subsection, type: {subsection_type} :::")


    return flists


def find_file_lists_in_submission(
    submission: Submission,
) -> List[Dict[str, Union[str, None, List[str]]]]:
    return find_file_lists_in_section(submission.section, [])


def find_files_in_submission_file_lists(submission: Submission) -> List[File]:
    file_list_dicts = find_file_lists_in_submission(submission)
    file_lists = []
    for file_list_dict in file_list_dicts:
        fname = file_list_dict["File List"]
        extra_attribute = []
        if "Title" in file_list_dict:
            extra_attribute.append(
                Attribute(name="Title", value=file_list_dict["Title"])
            )
        if "associations" in file_list_dict:
            extra_attribute.append(
                Attribute(
                    name="associations", value=f"{file_list_dict['associations']}"
                )
            )
        file_list = flist_from_flist_fname(submission.accno, fname, extra_attribute)
        file_lists.append(file_list)

    return sum(file_lists, [])


def find_files_in_submission(submission: Submission) -> List[File]:
    """Find all of the files in a submission, both attached directly to
    the submission and as file lists."""

    all_files = find_files_in_submission_file_lists(submission)

    def descend_and_find_files(section, files_list=[]):
        section_type = type(section)
        if section_type == Section:
            for file in section.files:
                if isinstance(file, List):
                    files_list += file
                else:
                    files_list.append(file)

            for subsection in section.subsections:
                descend_and_find_files(subsection, files_list)
        else:
            logger.warning(
                f"Not processing subsection as type is {section_type}, not 'Section'. Contents={section}"
            )

    descend_and_find_files(submission.section, all_files)

    return all_files


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


def find_sections_recursive(
    section: Section, search_types: List[str], results: Optional[list[Section]] = None
) -> List[Section]:
    """
    Find all sections of search_types within tree, starting at given section
    """
    if results == None:
        results = []

    search_types_lower = [s.lower() for s in search_types]
    if section.type.lower() in search_types_lower:
        results.append(section)

    # Each thing in section.subsections is either Section or List[Section] which we want to flatten
    flattened = []
    for item in section.subsections:
        if isinstance(item, list):
            for sub_item in item:
                flattened.append(sub_item)
        else:
            flattened.append(item)

    for section in flattened:
        find_sections_recursive(section, search_types, results)

    return results


def find_datasets_with_file_lists(
    submission: Submission,
) -> Dict[str, List[Dict[str, Union[str, None, List[str]]]]]:
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


def case_insensitive_get(d: dict, key: str, default: Any = "") -> Any:
    """Access dict values with case insensitive keys

    i.e. get value from {"Key": value} using "Key", "key", "KEY", etc.
    """
    if key in d:
        return d[key]

    # Line below assumes dict keys are unique when converted to lcase.
    mapping_dict = {k.lower(): k for k in d.keys()}

    key = key.lower()
    if key in mapping_dict:
        return d[mapping_dict[key]]
    else:
        return default
