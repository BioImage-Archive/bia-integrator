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


class ImageAnalysisMethodMapper(RembiMifaSectionMapper):

    section_type = "Image analysis"

    def get_mapped_object(
        self,
        section: Section,
        association_map
    ) -> ro_crate_models.ImageAnalysisMethod:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            "@id": self.create_id(section),
            "@type": ["bia:ImageAnalysisMethod"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("image analysis overview", ""),
        }

        return ro_crate_models.ImageAnalysisMethod(**model_dict)
