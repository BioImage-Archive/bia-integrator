import logging
from abc import ABC, abstractmethod

from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    filter_section_by_attribute_key,
    find_sections_recursive,
)

from .base_mapper import Mapper

logger = logging.getLogger("__main__." + __name__)


class SimpleMapper(Mapper, ABC):
    """
    Subclasses need to define the section type with which to filter classes
    """

    section_type: str
    required_fields: list[str] = ["Title"]

    def __init__(self) -> None:
        if not self.section_type or not isinstance(self.section_type, str):
            raise NotImplementedError(
                "Missing class variable section_type of type string."
            )
        super().__init__()

    def get_sections(self, submission: Submission):
        return filter_section_by_attribute_key(
            find_sections_recursive(submission.section, [self.section_type], []),
            self.required_fields,
        )

    def map(
        self, submission: Submission, association_map: dict[type, dict[str, str]]
    ) -> None:
        sections = self.get_sections(submission)

        for section in sections:
            if not section.accno:
                raise ValueError("Missing accno required for object id generation.")

            roc_object = self.get_mapped_object(section)

            if not roc_object:
                continue

            title = getattr(roc_object, "title", None)
            if title:
                association_map[type(roc_object)][title] = roc_object.id
            else:
                # Add to association using accno as fallback
                association_map[type(roc_object)] = {section.accno: roc_object.id}

            self.mapped_object.append(roc_object)

    @abstractmethod
    def get_mapped_object(self, section: Section) -> ROCrateModel | None:
        raise NotImplementedError
