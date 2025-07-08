from ro_crate_ingest.biostudies_to_ro_crate.biostudies.api import (
    Attribute,
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.biostudies_processing_version import (
    BioStudiesProcessingVersion,
)

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
