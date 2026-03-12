import logging
from urllib.parse import quote
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


def get_image_analysis_method_by_title(
    submission: Submission,
) -> dict[str, ro_crate_models.ImageAnalysisMethod]:
    sections = find_sections_recursive(submission.section, ["Image analysis"], [])

    roc_object_dict = {}
    for section in sections:
        roc_object = get_image_analysis_method(section)
        if not roc_object:
            continue
        roc_object_dict[roc_object.title] = roc_object
    return roc_object_dict


def get_image_analysis_method(
    section: Section,
) -> ro_crate_models.ImageAnalysisMethod | None:
    attr_dict = attributes_to_dict(section.attributes)

    # 20260312. New ST allowed some empty sections for a few studies.
    # Without a title, this section can't be associated to anything,
    # so we skip creating because it won't appear in any dataset.
    if not attr_dict.get("title", None):
        logger.debug(
            f"Skipping Image Analysis Method section with no title in submission {submission.accno}"
        )
        return

    model_dict = {
        "@id": f"#{quote(section.accno)}",
        "@type": ["bia:ImageAnalysisMethod"],
        "title": attr_dict["title"],
        "protocolDescription": attr_dict.get("image analysis overview", ""),
    }

    return ro_crate_models.ImageAnalysisMethod(**model_dict)
