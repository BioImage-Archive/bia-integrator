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


class ImageCorrelationMethodMapper(RembiMifaSectionMapper):

    section_type = "Image correlation"

    def get_mapped_object(self, section: Section, association_map) -> ro_crate_models.ROCrateModel:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            "@id": self.create_id(section),
            "@type": ["bia:ImageCorrelationMethod"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("spatial and temporal alignment", ""),
            "fiducialsUsed": attr_dict.get("fiducials used", None),
            "transformationMatrix": attr_dict.get("transformation matrix", None),
        }

        return ro_crate_models.ImageCorrelationMethod(**model_dict)
