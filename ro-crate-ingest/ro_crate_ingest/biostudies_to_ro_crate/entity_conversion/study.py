import logging
import re
from collections.abc import Iterable
from typing import Any

from bia_shared_datamodels import ro_crate_models, semantic_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

logger = logging.getLogger("__main__." + __name__)


def get_study(
    submission: Submission,
    contributors: list[ro_crate_models.Contributor],
    datasets: Iterable[ro_crate_models.Dataset],
    combined_file_list: ro_crate_models.FileList,
    external_refernces: list[ro_crate_models.ExternalReference],
) -> ro_crate_models.Study:
    submission_attributes = attributes_to_dict(submission.attributes)
    study_attributes = attributes_to_dict(submission.section.attributes)

    has_part_ids = [{"@id": d.id} for d in datasets]
    if combined_file_list:
        has_part_ids.append({"@id": combined_file_list.id})

    study_dict = {
        "@id": "./",
        "@type": ["Dataset", "bia:Study"],
        "accessionId": submission.accno,
        "name": study_title_from_submission(submission),
        "license": get_license(study_attributes),
        "datePublished": submission_attributes["releasedate"],
        "description": study_attributes.get("description", None),
        "acknowledgement": study_attributes.get("acknowledgements", None),
        "keyword": study_attributes.get("keywords", []),
        "contributor": [{"@id": c.id} for c in contributors],
        "hasPart": has_part_ids,
        "associationFileMetadata": (
            {"@id": combined_file_list.id} if combined_file_list else None
        ),
        "seeAlso": [{"@id": external_ref.id} for external_ref in external_refernces],
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


def get_license(study_attributes: dict[str, Any]) -> semantic_models.Licence:
    """
    Return enum version of licence of study
    """
    temp = re.sub(r"\s", "_", study_attributes.get("license", "CC0"))
    licence = re.sub(r"\.", "", temp)
    licence = licence.replace("-", "_")
    return semantic_models.Licence[licence]
