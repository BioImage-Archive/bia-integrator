import logging
import re
from typing import Any, Type
from urllib.parse import quote

from bia_ro_crate.models import ro_crate_models
from bia_shared_datamodels import semantic_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .base_mapper import Mapper

logger = logging.getLogger("__main__." + __name__)


class StudyMapper(Mapper):

    def __init__(self, combined_file_list_id: str = "combined_file_list.tsv") -> None:
        self.combined_file_list_id = (
            combined_file_list_id  # Default should match default in file_list_generator
        )

        super().__init__()

    def map(self, submission: Submission, association_map: dict[type, dict[str, str]]):
        submission_attributes = attributes_to_dict(submission.attributes)
        study_attributes = attributes_to_dict(submission.section.attributes)

        has_part_ids = self.get_all_id_references(
            association_map, ro_crate_models.Dataset
        )
        has_part_ids.append({"@id": self.combined_file_list_id})

        study_dict = {
            "@id": "./",
            "@type": ["Dataset", "bia:Study"],
            "accessionId": submission.accno,
            "name": self.study_title_from_submission(submission),
            "license": self.get_license(study_attributes),
            "datePublished": submission_attributes["releasedate"],
            "description": study_attributes.get("description")
            or study_attributes.get("abstract"),
            "acknowledgement": study_attributes.get("acknowledgements", None),
            "keyword": self.get_keywords(study_attributes.get("keywords", [])),
            "contributor": self.get_all_id_references(
                association_map, ro_crate_models.Contributor
            ),
            "hasPart": has_part_ids,
            "associationFileMetadata": {"@id": self.combined_file_list_id},
            "seeAlso": self.get_all_id_references(
                association_map, ro_crate_models.ExternalReference
            ),
            "relatedPublication": self.get_all_id_references(
                association_map, ro_crate_models.Publication
            ),
            "funding": self.get_all_id_references(
                association_map, ro_crate_models.Grant
            ),
        }

        self.mapped_object.append(ro_crate_models.Study(**study_dict))

    @staticmethod
    def study_title_from_submission(submission: Submission) -> str:
        submission_attr_dict = attributes_to_dict(submission.attributes)
        study_section_attr_dict = attributes_to_dict(submission.section.attributes)

        study_title = submission_attr_dict.get("title", None)
        if not study_title:
            study_title = study_section_attr_dict.get("title", "Unknown")

        return study_title

    @staticmethod
    def get_license(study_attributes: dict[str, Any]) -> semantic_models.Licence:
        """
        Return enum version of licence of study
        """
        temp = re.sub(r"\s", "_", study_attributes.get("license", "CC0"))
        licence = re.sub(r"\.", "", temp)
        licence = licence.replace("-", "_")
        return semantic_models.Licence[licence]

    @staticmethod
    def get_keywords(keywords: str | list[str] | None) -> list:
        if isinstance(keywords, list):
            return keywords
        elif isinstance(keywords, str):
            return keywords.split(",")
        else:
            return []

    @staticmethod
    def get_all_id_references(
        association_map: dict[type, dict[str, str]], ro_crate_type: Type
    ):
        return [
            {"@id": external_ref_id}
            for external_ref_id in association_map[ro_crate_type].values()
        ]
