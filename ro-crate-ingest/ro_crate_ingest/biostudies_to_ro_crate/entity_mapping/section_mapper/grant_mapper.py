import logging

from bia_ro_crate.models import ro_crate_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .base_section_mapper import SectionMapper

logger = logging.getLogger("__main__." + __name__)


class GrantMapper(SectionMapper):

    section_type = "Funding"
    bnode_int: int

    def __init__(self) -> None:
        self.bnode_int = 0
        super().__init__()

    def get_mapped_object(
        self, section: Section, association_map: dict[type, dict[str, str]]
    ):
        attributes = attributes_to_dict(section.attributes)

        grant_funder = None

        if attributes.get("agency"):
            grant_funder = {
                "@id": f"_:gf{self.bnode_int}",
                "@type": ["Organisation", "bia:FundingBody"],
                "name": attributes.get("agency"),
            }

        grant_dict = {
            "@id": f"_:g{self.bnode_int}",
            "@type": ["Grant", "bia:Grant"],
            "funder": [{"@id": grant_funder["@id"]}] if grant_funder else [],
            "identifier": attributes.get("grant_id"),
        }

        self.bnode_int += 1

        if grant_funder:
            return [
                ro_crate_models.Grant(**grant_dict),
                ro_crate_models.FundingBody(**grant_funder),
            ]
        else:
            return ro_crate_models.Grant(**grant_dict)
