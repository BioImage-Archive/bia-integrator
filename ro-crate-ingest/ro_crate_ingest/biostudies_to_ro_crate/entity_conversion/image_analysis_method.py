import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.api import (
    Submission,
    Section,
)

from bia_shared_datamodels import ro_crate_models

logger = logging.getLogger("__main__." + __name__)


def get_image_analysis_method_by_title(
    submission: Submission,
) -> dict[str, ro_crate_models.ImageAnyalysisMethod]:

    sections = find_sections_recursive(
        submission.section, ["Image analysis"], []
    )

    roc_object_dict = {}
    for section in sections:
        roc_object = get_image_analysis_method(section)
        roc_object_dict[roc_object.title] = roc_object
    return roc_object_dict


def get_image_analysis_method(
    section: Section,
) -> ro_crate_models.ImageAnyalysisMethod:
    attr_dict = attributes_to_dict(section.attributes)

    model_dict = {
        "@id": f"biostudies_iam:{section.accno}",
        "@type": ["bia:AnnotationMethod"],
        "title": attr_dict["title"],
        "protocolDescription": attr_dict.get("image analysis overview", ""),
    }

    return ro_crate_models.ImageAnyalysisMethod(**model_dict)
