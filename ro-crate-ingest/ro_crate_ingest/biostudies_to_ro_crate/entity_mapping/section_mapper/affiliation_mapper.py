import logging
from urllib.parse import quote

from bia_ro_crate.models import ro_crate_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .base_section_mapper import SectionMapper

logger = logging.getLogger("__main__." + __name__)


class AffiliationMapper(SectionMapper):

    section_type = ["organisation", "organization"]

    def get_mapped_object(
        self, section: Section, association_map: dict[type, dict[str, str]]
    ):

        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            "@id": self.create_id(attr_dict, section),
            "@type": ["Organisation", "bia:Affiliation"],
            "displayName": attr_dict["name"],
            "website": attr_dict.get("website"),
            "address": attr_dict.get("address"),
        }

        return ro_crate_models.Affiliaton(**model_dict)

    def create_id(
        self, attribute_dict: dict[str, str | list[str]], section: Section
    ) -> str:
        rorid = attribute_dict.get("rorid")
        if rorid and isinstance(rorid, str):
            return rorid
        elif section.accno:
            return f"#{quote(section.accno)}"
        else:
            raise KeyError("Missing some key to use as ID for affiliation")
