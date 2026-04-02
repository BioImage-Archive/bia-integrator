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


class SpecimenImagingPreprationProtocolMapper(SimpleMapper):

    section_type = "Specimen"

    def get_mapped_object(
        self,
        section: Section,
    ) -> ro_crate_models.SpecimenImagingPreparationProtocol:

        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            "@id": f"#{quote(section.accno)}",
            "@type": ["bia:SpecimenImagingPreparationProtocol"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("sample preparation protocol", ""),
            "signalChannelInformation": [],
        }

        return ro_crate_models.SpecimenImagingPreparationProtocol(**model_dict)
