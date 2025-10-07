import logging
import re
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import Submission

from bia_shared_datamodels import ro_crate_models, semantic_models
from collections.abc import Iterable
from typing import Any

logger = logging.getLogger("__main__." + __name__)


def get_study(
    submission: Submission,
    contributors: list[ro_crate_models.Contributor],
    datasets: Iterable[ro_crate_models.Dataset],
) -> ro_crate_models.Study:
    submission_attributes = attributes_to_dict(submission.attributes)
    study_attributes = attributes_to_dict(submission.section.attributes)

    study_dict = {
        "@id": "./",
        "@type": ["Dataset", "bia:Study"],
        "accessionId": submission.accno,
        "title": study_title_from_submission(submission),
        "licence": get_licence(study_attributes),
        "datePublished": submission_attributes["releasedate"],
        "description": study_attributes.get("description", None),
        "acknowledgement": study_attributes.get("acknowledgements", None),
        "keyword": study_attributes.get("keywords", []),
        "contributor": [{"@id": c.id} for c in contributors],
        "hasPart": [{"@id": d.id} for d in datasets],
        # TODO handle grants & funding statements
    }

    return ro_crate_models.Study(**study_dict)


def study_title_from_submission(submission: Submission) -> str:
    submission_attr_dict = attributes_to_dict(submission.attributes)
    study_section_attr_dict = attributes_to_dict(submission.section.attributes)

    study_title = submission_attr_dict.get("title", None)
    if not study_title:
        study_title = study_section_attr_dict.get("title", "Unknown")

    return study_title


def get_licence(study_attributes: dict[str, Any]) -> semantic_models.Licence:
    """
    Return enum version of licence of study
    """
    temp = re.sub(r"\s", "_", study_attributes.get("license", "CC0"))
    licence = re.sub(r"\.", "", temp)
    licence = licence.replace("-", "_")
    return semantic_models.Licence[licence]
