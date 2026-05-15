import logging
from abc import ABC
from urllib.parse import quote

from bia_ro_crate.models.linked_data.pydantic_ld.ROCrateModel import ROCrateModel

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)

from ..base_section_mapper import SectionMapper

logger = logging.getLogger("__main__." + __name__)


class RembiMifaSectionMapper(SectionMapper, ABC):

    required_fields: list[str] = ["Title"]

    def get_biostudies_reference(self, section: Section, ro_crate_object: ROCrateModel):
        title = getattr(ro_crate_object, "title", None)
        return title or super().get_biostudies_reference(section, ro_crate_object)

    @staticmethod
    def create_id(section: Section, prefix: str = "") -> str:
        if not section.accno:
            raise KeyError(
                "Missing accno for rembi/mifa object, which is required for ID generation."
            )

        return f"#{prefix}{quote(section.accno)}"
