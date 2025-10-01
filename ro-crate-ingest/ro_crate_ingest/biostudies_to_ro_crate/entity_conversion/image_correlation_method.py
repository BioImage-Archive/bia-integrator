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


def get_image_correlation_method_by_title(
    submission: Submission,
) -> dict[str, ro_crate_models.ImageCorrelationMethod]:

    sections = find_sections_recursive(submission.section, ["Image correlation"], [])

    roc_object_dict = {}
    for section in sections:
        roc_object = get_image_correlation_method(section)
        # Note growth protocol title is from Specimen title, so matches association from biostudies.
        roc_object_dict[roc_object.title] = roc_object
    return roc_object_dict


def get_image_correlation_method(
    section: Section,
) -> ro_crate_models.ImageCorrelationMethod:
    attr_dict = attributes_to_dict(section.attributes)

    model_dict = {
        "@id": f"_:{section.accno}",
        "@type": ["bia:ImageCorrelationMethod"],
        "title": attr_dict["title"],
        "protocolDescription": attr_dict.get("spatial and temporal alignment", ""),
        "fiducialsUsed": attr_dict.get("fiducials used", None),
        "transformationMatrix": attr_dict.get("transformation matrix", None),
    }

    return ro_crate_models.ImageCorrelationMethod(**model_dict)
