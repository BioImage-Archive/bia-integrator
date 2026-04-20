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


class ImageCorrelationMethodMapper(SimpleMapper):

    section_type = "Image correlation"

    def get_mapped_object(self, section: Section) -> ro_crate_models.ROCrateModel:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            "@id": f"#{quote(section.accno)}",
            "@type": ["bia:ImageCorrelationMethod"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("spatial and temporal alignment", ""),
            "fiducialsUsed": attr_dict.get("fiducials used", None),
            "transformationMatrix": attr_dict.get("transformation matrix", None),
        }

        return ro_crate_models.ImageCorrelationMethod(**model_dict)
