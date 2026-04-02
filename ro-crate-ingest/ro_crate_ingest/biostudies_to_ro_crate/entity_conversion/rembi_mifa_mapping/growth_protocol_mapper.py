import logging
from urllib.parse import quote

from bia_shared_datamodels import ro_crate_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .simple_mapper import SimpleMapper

logger = logging.getLogger("__main__." + __name__)


class GrowthProtocolMapper(SimpleMapper):

    section_type = "Specimen"

    def get_mapped_object(
        self,
        section: Section,
    ) -> ro_crate_models.Protocol | None:
        attr_dict = attributes_to_dict(section.attributes)

        if "growth protocol" not in attr_dict:
            return None

        model_dict = {
            "@id": f"#_{quote(section.accno)}",  # Note Growth Protocol has a extra _ at the start to avoid clashing with the specimen imaging preparation protocol ID
            "@type": ["bia:Protocol"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("growth protocol", ""),
        }

        return ro_crate_models.Protocol(**model_dict)
