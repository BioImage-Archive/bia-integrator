import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
    Section,
)
from bia_shared_datamodels import ro_crate_models

logger = logging.getLogger("__main__." + __name__)


def get_specimen_imaging_prepratation_protocol_by_title(
    submission: Submission,
) -> dict[str, ro_crate_models.SpecimenImagingPreparationProtocol]:

    sections = find_sections_recursive(submission.section, ["Specimen"], [])

    roc_object_dict = {}
    for section in sections:
        roc_object = get_specimen_imaging_prepratation_protocol(section)
        roc_object_dict[roc_object.title] = roc_object
    return roc_object_dict


def get_specimen_imaging_prepratation_protocol(
    section: Section,
) -> ro_crate_models.SpecimenImagingPreparationProtocol:
    attr_dict = attributes_to_dict(section.attributes)

    model_dict = {
        "@id": f"_:{section.accno}",
        "@type": ["bia:SpecimenImagingPreparationProtocol"],
        "title": attr_dict["title"],
        "protocolDescription": attr_dict.get("sample preparation protocol", ""),
        "signalChannelInformation": [],
    }

    return ro_crate_models.SpecimenImagingPreparationProtocol(**model_dict)
