import logging
from urllib.parse import quote

from bia_ro_crate.models import ro_crate_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .simple_mapper import SimpleMapper

logger = logging.getLogger("__main__." + __name__)


class ImageAnalysisMethodMapper(SimpleMapper):

    section_type = "Image analysis"

    def get_mapped_object(
        self,
        section: Section,
    ) -> ro_crate_models.ImageAnalysisMethod:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            "@id": f"#{quote(section.accno)}",
            "@type": ["bia:ImageAnalysisMethod"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("image analysis overview", ""),
        }

        return ro_crate_models.ImageAnalysisMethod(**model_dict)
