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


def get_protocol_by_title(
    submission: Submission,
) -> dict[str, ro_crate_models.Protocol]:

    sections = find_sections_recursive(submission.section, ["Protocol"], [])

    roc_object_dict = {}
    for section in sections:
        roc_object = get_protocol(section)
        roc_object_dict[roc_object.title] = roc_object
    return roc_object_dict


def get_protocol(
    section: Section,
) -> ro_crate_models.Protocol:

    attr_dict = attributes_to_dict(section.attributes)


    model_dict = {
        "@id": f"_:{section.accno}",
        "@type": ["bia:Protocol"],
        "title": f"{section.accno}",
        "protocolDescription": attr_dict.get("description", ""),
    }

    return ro_crate_models.Protocol(**model_dict)
