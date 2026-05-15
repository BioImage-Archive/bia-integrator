import logging

from bia_ro_crate.models import ro_crate_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .base_rembi_mifa_section_mapper import RembiMifaSectionMapper

logger = logging.getLogger("__main__." + __name__)


class GrowthProtocolMapper(RembiMifaSectionMapper):

    section_type = "Specimen"

    def get_mapped_object(
        self,
        section: Section,
        association_map,
    ) -> ro_crate_models.Protocol | None:
        if not section.accno:
            raise KeyError(
                "Missing accno for rembi/mifa object, which is required for ID creation."
            )

        attr_dict = attributes_to_dict(section.attributes)

        if "growth protocol" not in attr_dict:
            return None

        model_dict = {
            "@id": self.create_id(
                section, prefix="_"
            ),  # Note Growth Protocol has a extra _ at the start to avoid clashing with the specimen imaging preparation protocol ID
            "@type": ["bia:Protocol"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("growth protocol", ""),
        }

        return ro_crate_models.Protocol(**model_dict)
