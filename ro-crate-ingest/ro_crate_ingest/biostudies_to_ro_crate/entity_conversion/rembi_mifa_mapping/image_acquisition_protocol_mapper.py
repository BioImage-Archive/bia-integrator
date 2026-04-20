import logging
from urllib.parse import quote

from bia_ro_crate.models import ro_crate_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)

from .simple_mapper import SimpleMapper

logger = logging.getLogger("__main__." + __name__)


class ImageAcquisitionProtocolMapper(SimpleMapper):

    section_type = "Image acquisition"

    def get_mapped_object(self, section: Section) -> ro_crate_models.ROCrateModel:
        attr_dict = attributes_to_dict(section.attributes)

        if "imaging method" not in attr_dict:
            imagingMethodName, fbbi_id = self._get_imaging_method_fbbi_from_subsection(
                section
            )
        elif isinstance(attr_dict["imaging method"], list):
            imagingMethodName = attr_dict["imaging method"]
            fbbi_id = []
        else:
            imagingMethodName = [attr_dict["imaging method"]]
            fbbi_id = []

        model_dict = {
            "@id": f"#{quote(section.accno)}",
            "@type": ["bia:ImageAcquisitionProtocol"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("image acquisition parameters", ""),
            "imagingInstrumentDescription": attr_dict.get("imaging instrument", ""),
            "imagingMethodName": imagingMethodName,
            "fbbiId": fbbi_id,
        }

        return ro_crate_models.ImageAcquisitionProtocol(**model_dict)

    @staticmethod
    def _get_imaging_method_fbbi_from_subsection(
        image_acquisition_section: Section,
    ) -> tuple[list[str], list[str]]:
        sections = find_sections_recursive(
            image_acquisition_section, ["Imaging Method"]
        )
        imaging_method_name = []
        fbbi_id = []
        for section in sections:
            attr_dict = attributes_to_dict(section.attributes)
            if attr_dict.get("ontology term id") and attr_dict.get("ontology value"):
                imaging_method_name.append(f"{attr_dict['ontology value']}")
                fbbi_id.append(f"{attr_dict['ontology term id']}")
            elif attr_dict["ontology value"]:
                imaging_method_name.append(f"{attr_dict['ontology value']}")
        return (imaging_method_name, fbbi_id)
