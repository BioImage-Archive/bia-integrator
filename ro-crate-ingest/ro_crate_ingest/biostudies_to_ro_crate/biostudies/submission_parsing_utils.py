import logging

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Attribute,
    Section,
    Submission,
)

logger = logging.getLogger("__main__." + __name__)


def attributes_to_dict(
    attributes: list[Attribute],
) -> dict[str, str | list[str]]:
    attr_dict = {}
    for attr in attributes:
        if not attr.value:
            logger.warning(
                f"Skipping attribute {attr.name} from attribute dict, as it has no value!"
            )
        else:
            normalised_key = attr.name.lower()
            if normalised_key in attr_dict:
                if not isinstance(attr_dict[normalised_key], list):
                    attr_dict[normalised_key] = [
                        attr_dict[normalised_key],
                    ]
                attr_dict[normalised_key].append(attr.value)
            else:
                attr_dict[normalised_key] = attr.value
    return attr_dict


def find_sections_recursive(
    section: Section, search_types: list[str], results: list[Section] | None = None
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


def find_section_types_recursive(
    section: Section, results: list[Section] | None = None
) -> list[str]:
    """
    Find all types of sections within tree, starting at given section
    """
    if results == None:
        results = []

    results.append(section.type)

    # Each thing in section.subsections is either Section or List[Section] which we want to flatten
    flattened = []
    for item in section.subsections:
        if isinstance(item, list):
            for sub_item in item:
                flattened.append(sub_item)
        else:
            flattened.append(item)

    for section in flattened:
        find_section_types_recursive(section, results)

    return results


def filter_section_by_attribute_key(
    sections: list[Section],
    required_attr_keys: list[str],
) -> list[Section]:

    filtered_sections = []
    required_keys_as_set = set([k.lower() for k in required_attr_keys])
    for section in sections:
        attr_dict = attributes_to_dict(section.attributes)
        if all([attr_dict.get(k) for k in required_keys_as_set]):
            filtered_sections.append(section)
        else:
            logger.warning(
                f"Skipping Section of type {section.type} with accno {section.accno} as it's attribute dict does not have valid entries for one or more of {required_keys_as_set}"
            )
    return filtered_sections


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
        if isinstance(subsection, Section):
            find_file_lists_under_section(subsection, flists)

    return flists


def find_file_lists_in_submission(
    submission: Submission,
) -> list[str]:
    return find_file_lists_under_section(submission.section, [])


def find_sections_with_filelists_recursive(
    section: Section,
    results: list[Section] | None = None,
    ignore_types: list[str] | None = None,
) -> list[Section]:
    """
    Find all of the Sections with a File lists, recursively descending through the subsections.

    Return a list of sections with filists.
    """

    if results == None:
        results = []

    attr_dict = attributes_to_dict(section.attributes)
    if "file list" in attr_dict:
        if ignore_types:
            ignore_types_lower = [s.lower() for s in ignore_types]
            if section.type.lower() not in ignore_types_lower:
                results.append(section)
        else:
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
        find_sections_with_filelists_recursive(subsection, results, ignore_types)

    return results


# TODO - discuss if this can be a method of section. Issue is it depends on `attr_to_dict` function
def is_section_empty(section: Section) -> bool:
    """Check if a section is empty. Recursively check any subsections"""

    # Check Section attributes.
    attr_dict = attributes_to_dict(section.attributes)
    for attr_value in attr_dict.values():
        if attr_value:
            return False

    # Check links
    if section.links:
        return False

    # Check attached files
    if section.files:
        return False

    # Recursively check through subsections. False if any none empty subsection
    for subsection in section.subsections:
        is_empty = is_section_empty(subsection)
        if not is_empty:
            return False

    return True
