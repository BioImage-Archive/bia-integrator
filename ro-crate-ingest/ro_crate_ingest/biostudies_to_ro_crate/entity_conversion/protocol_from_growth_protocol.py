import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
    Section,
)
from typing import Optional
from bia_shared_datamodels import ro_crate_models


logger = logging.getLogger("__main__." + __name__)


def get_growth_protocol_by_title(
    submission: Submission,
    study_uuid: str,
) -> dict[str, ro_crate_models.Protocol]:

    sections = find_sections_recursive(submission.section, ["Specimen"], [])

    roc_object_dict = {}
    for section in sections:
        roc_object = get_growth_protocol(
            section,
        )
        # Note growth protocol title is from Specimen title, so matches association from biostudies.
        if roc_object:
            roc_object_dict[roc_object.title] = roc_object
    return roc_object_dict


def get_growth_protocol(section: Section) -> Optional[ro_crate_models.Protocol]:
    attr_dict = attributes_to_dict(section.attributes)

    if "growth protocol" not in attr_dict:
        return None

    model_dict = {
        "@id": f"_:_{section.accno}",  # Note Growth Protocol has a extra _ at the start to avoid clashing with the specimen imaging preparation protocol ID
        "@type": ["bia:Protocol"],
        "title": attr_dict["title"],
        "protocolDescription": attr_dict.get("growth protocol", ""),
    }

    return ro_crate_models.Protocol(**model_dict)
