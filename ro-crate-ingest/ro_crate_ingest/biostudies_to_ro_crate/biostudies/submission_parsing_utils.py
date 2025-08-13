from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Attribute,
    Section,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.filelist_api import File

from typing import Optional
import logging

logger = logging.getLogger("__main__." + __name__)


def attributes_to_dict(
    attributes: list[Attribute],
) -> dict[str, Optional[str | list[str]]]:
    attr_dict = {}
    for attr in attributes:
        normalised_key = attr.name.lower()
        if normalised_key in attr_dict:
            if isinstance(attr_dict[normalised_key], list):
                attr_dict[normalised_key].append(attr.value)
            else:
                attr_dict[normalised_key] = [
                    attr_dict[normalised_key],
                ]
                attr_dict[normalised_key].append(attr.value)
        else:
            attr_dict[normalised_key] = attr.value
    return attr_dict


def find_sections_recursive(
    section: Section, search_types: list[str], results: Optional[list[Section]] = None
) -> list[Section]:
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


def find_file_lists_under_section(
    section: Section,
    flists: list[str],
) -> list[str]:
    """
    Find all of the File lists in a Section, recursively descending through the subsections.

    Return a list of file list paths.
    """

    attr_dict = attributes_to_dict(section.attributes)

    if "file list" in attr_dict:
        flists.append(attr_dict["file list"])

    for subsection in section.subsections:
        subsection_type = type(subsection)
        if subsection_type == Section:
            find_file_lists_under_section(subsection, flists)

    return flists


def find_file_lists_in_submission(
    submission: Submission,
) -> list[str]:
    return find_file_lists_under_section(submission.section, [])


def find_files_under_section(section: Section) -> list[File]:
    """
    For earlier Biostudies submissions where files are documented in the pagetab json, rather than in a separate filelist
    """
    pass


def find_sections_with_filelists_recursive(
    section: Section,
    results: Optional[list[Section]] = None,
) -> list[Section]:
    """
    Find all of the Sections with a File lists, recursively descending through the subsections.

    Return a list of sections with filists.
    """

    if results == None:
        results = []

    attr_dict = attributes_to_dict(section.attributes)
    if "file list" in attr_dict:
        results.append(section)

    # Each thing in section.subsections is either Section or List[Section] which we want to flatten
    flattened = []
    for item in section.subsections:
        if isinstance(item, list):
            for sub_item in item:
                flattened.append(sub_item)
        else:
            flattened.append(item)

    for subsection in flattened:
        find_sections_with_filelists_recursive(subsection, results)

    return results
