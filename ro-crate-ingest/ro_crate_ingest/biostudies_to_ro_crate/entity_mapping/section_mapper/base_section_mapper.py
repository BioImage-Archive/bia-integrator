from abc import ABC, abstractmethod
from typing import Sequence

from bia_ro_crate.models.linked_data.pydantic_ld.ROCrateModel import ROCrateModel

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    filter_section_by_attribute_key,
    find_sections_recursive,
)

from ..base_mapper import Mapper


class SectionMapper(Mapper, ABC):
    """
    Superclass of the basic mappers from sections where we only need 1 mapping function fall all sections that correspond to the section_type

    Subclasses need to define the section_type with which to filter classes
    """

    section_type: str | list[str]
    required_fields: list[str] = []

    def get_sections_to_map(self, submission: Submission) -> list[Section]:
        if not self.section_type:
            raise NotImplementedError("Missing class variable section_type.")

        section_types = self.section_type
        if not isinstance(section_types, list):
            section_types = [section_types]

        sections_of_type = find_sections_recursive(submission.section, section_types)
        if self.required_fields:
            return filter_section_by_attribute_key(
                sections_of_type,
                self.required_fields,
            )
        else:
            return sections_of_type

    @abstractmethod
    def get_mapped_object(
        self, section: Section, association_map: dict[type, dict[str, str]]
    ) -> Sequence[ROCrateModel] | ROCrateModel | None:
        raise NotImplementedError

    def skip_object(self, ro_crate_object: ROCrateModel) -> bool:
        """
        Override this function with more specific logic to ignore objects
        """
        return False

    def get_biostudies_reference(self, section: Section, ro_crate_object: ROCrateModel):
        return section.accno or ro_crate_object.id

    def map(self, submission: Submission, association_map: dict[type, dict[str, str]]):

        sections = self.get_sections_to_map(submission)

        for section in sections:
            ro_crate_objects = self.get_mapped_object(section, association_map)

            if not ro_crate_objects:
                continue

            if not isinstance(ro_crate_objects, Sequence):
                ro_crate_objects = [ro_crate_objects]

            for ro_crate_object in ro_crate_objects:
                if not self.skip_object(ro_crate_object):
                    biostudies_reference = self.get_biostudies_reference(
                        section, ro_crate_object
                    )
                    self.mapped_object.append(ro_crate_object)
                    association_map[type(ro_crate_object)][
                        biostudies_reference
                    ] = ro_crate_object.id
