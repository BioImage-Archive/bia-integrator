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


def get_image_acquisition_protocol_by_title(
    submission: Submission,
) -> dict[str, ro_crate_models.ImageAcquisitionProtocol]:

    sections = find_sections_recursive(submission.section, ["Image acquisition"], [])

    roc_object_dict = {}
    for section in sections:
        roc_object = get_image_acquisition_protocol(section)
        roc_object_dict[roc_object.title] = roc_object
    return roc_object_dict


def get_image_acquisition_protocol(
    section: Section,
) -> ro_crate_models.ImageAcquisitionProtocol:

    attr_dict = attributes_to_dict(section.attributes)

    if not "imaging method" in attr_dict:
        imagingMethodName, fbbi_id = get_imaging_method_fbbi_from_subsection(section)
    elif isinstance(attr_dict["imaging method"], list):
        imagingMethodName = attr_dict["imaging method"]
        fbbi_id = []
    else:
        imagingMethodName = [attr_dict["imaging method"]]
        fbbi_id = []

    model_dict = {
        "@id": f"_:{section.accno}",
        "@type": ["bia:ImageAcquisitionProtocol"],
        "title": attr_dict["title"],
        "protocolDescription": attr_dict.get("image acquisition parameters", ""),
        "imagingInstrumentDescription": attr_dict.get("imaging instrument", ""),
        "imagingMethodName": imagingMethodName,
        "fbbiId": fbbi_id,
    }

    return ro_crate_models.ImageAcquisitionProtocol(**model_dict)


def get_imaging_method_fbbi_from_subsection(
    image_acquisition_section: Section,
) -> list:
    sections = find_sections_recursive(image_acquisition_section, ["Imaging Method"])
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
