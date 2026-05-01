import logging
from collections import defaultdict
from urllib.parse import quote

from bia_ro_crate.models import ro_crate_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
    find_sections_with_filelists_recursive,
)

logger = logging.getLogger("__main__." + __name__)


class DatasetMapper:

    study_component_dataset: dict[str, ro_crate_models.Dataset]
    annotation_dataset: dict[str, ro_crate_models.Dataset]
    file_list_dataset: dict[str, ro_crate_models.Dataset]
    generated_dataset: ro_crate_models.Dataset | None

    def __init__(self) -> None:
        self.study_component_dataset = {}
        self.annotation_dataset = {}
        self.file_list_dataset = {}
        self.generated_dataset = None

    def has_mapped_objects(self):
        has_mapped_objects = any(
            (
                self.study_component_dataset,
                self.annotation_dataset,
                self.file_list_dataset,
                self.generated_dataset,
            )
        )
        return has_mapped_objects

    def map(
        self,
        submission: Submission,
        association_map: dict[type, dict[str, str]],
    ):
        self._get_dataset_from_study_components(submission, association_map)

        self._get_dataset_from_annotation_component(submission, association_map)

        self._get_dataset_from_generic_filelist_section(submission, association_map)

        if not self.has_mapped_objects():
            self._create_root_dataset_for_submission(submission)

    def get_mapped_objects(
        self, submission: Submission, association_map: dict[type, dict[str, str]]
    ) -> list[ro_crate_models.Dataset]:
        if not self.has_mapped_objects():
            self.map(submission, association_map)

        mapped_objects = []
        mapped_objects += self.study_component_dataset.values()
        mapped_objects += self.annotation_dataset.values()
        mapped_objects += self.file_list_dataset.values()
        if self.generated_dataset:
            mapped_objects.append(self.generated_dataset)

        return mapped_objects

    def get_accno_lookup(self) -> dict[str | None, str]:
        lookup = {}
        lookup = lookup | {
            accno: dataset.id for accno, dataset in self.study_component_dataset.items()
        }
        lookup = lookup | {
            accno: dataset.id for accno, dataset in self.annotation_dataset.items()
        }
        lookup = lookup | {
            accno: dataset.id for accno, dataset in self.file_list_dataset.items()
        }
        if self.generated_dataset:
            lookup[None] = self.generated_dataset.id
        return lookup

    def get_type_lookup(self) -> dict[str, str]:
        lookup = {}
        lookup = lookup | {
            dataset.id: "Study Component"
            for dataset in self.study_component_dataset.values()
        }
        lookup = lookup | {
            dataset.id: "Annotations" for dataset in self.annotation_dataset.values()
        }
        lookup = lookup | {
            dataset.id: "File List Dataset"
            for dataset in self.file_list_dataset.values()
        }
        if self.generated_dataset:
            lookup[self.generated_dataset.id] = "Generated"
        return lookup

    def _get_dataset_from_study_components(
        self,
        submission: Submission,
        association_map: dict[type, dict[str, str]],
    ):
        study_comp_sections = find_sections_recursive(
            submission.section, ["Study Component"], []
        )

        for section in study_comp_sections:
            association_dict = DatasetMapper._get_association_fields(
                section=section,
                association_map=association_map,
            )

            roc_id = f"#{quote(section.accno)}"

            attr_dict = attributes_to_dict(section.attributes)

            model_dict = association_dict | {
                "@id": roc_id,
                "@type": ["Dataset", "bia:Dataset"],
                "name": attr_dict["name"],
                "description": attr_dict["description"],
            }

            self.study_component_dataset[section.accno] = ro_crate_models.Dataset(
                **model_dict
            )

    def _get_dataset_from_annotation_component(
        self,
        submission: Submission,
        association_map: dict[type, dict[str, str]],
    ):
        annotation_sections = find_sections_recursive(
            submission.section, ["Annotations"], []
        )

        for section in annotation_sections:

            roc_id = f"#{quote(section.accno)}"

            attr_dict = attributes_to_dict(section.attributes)

            model_dict = {
                "@id": roc_id,
                "@type": ["Dataset", "bia:Dataset"],
                "name": attr_dict["title"],
                "description": attr_dict.get("annotation overview", None),
                "associatedAnnotationMethod": [
                    {
                        "@id": association_map[ro_crate_models.AnnotationMethod][
                            attr_dict["title"]
                        ]
                    }
                ],
            }
            self.annotation_dataset[section.accno] = ro_crate_models.Dataset(
                **model_dict
            )

    def _get_dataset_from_generic_filelist_section(
        self,
        submission: Submission,
        association_map: dict[type, dict[str, str]],
    ):

        generic_section_with_filelist = find_sections_with_filelists_recursive(
            submission.section, ignore_types=["Study Component", "Annotations"]
        )

        for section in generic_section_with_filelist:
            roc_id = f"#{quote(section.accno)}"

            attr_dict = attributes_to_dict(section.attributes)

            # Handle older submission formats (prior to v4 template submission) by creating protocols for the subsections.
            protocol_subsections_ids = [
                protocol.accno
                for protocol in find_sections_recursive(section, ["Protocol"])
            ]

            model_dict = {
                "@id": roc_id,
                "@type": ["Dataset", "bia:Dataset"],
                "name": f"{section.accno}",
                "description": attr_dict.get("Description", None),
                "associatedProtocol": [
                    {"@id": association_map[ro_crate_models.Protocol][accno]}
                    for accno in protocol_subsections_ids
                ],
            }

            self.file_list_dataset[section.accno] = ro_crate_models.Dataset(
                **model_dict
            )

    @staticmethod
    def _get_association_fields(
        section: Section, association_map: dict[type, dict[str, str]]
    ) -> dict[str, list[dict[str, str]]]:

        association_ro_crate_fields = defaultdict(list)

        basic_rembi_component_mapping = [
            (
                "image acquisition",
                ro_crate_models.ImageAcquisitionProtocol,
                "associatedImageAcquisitionProtocol",
            ),
            (
                "specimen",
                ro_crate_models.SpecimenImagingPreparationProtocol,
                "associatedSpecimenImagingPreparationProtocol",
            ),
            (
                "image correlation",
                ro_crate_models.ImageCorrelationMethod,
                "associatedImageCorrelationMethod",
            ),
            (
                "image analysis",
                ro_crate_models.ImageAnalysisMethod,
                "associatedImageAnalysisMethod",
            ),
        ]

        associations = find_sections_recursive(section, ["Associations"], [])
        for association in associations:
            attr_dict = attributes_to_dict(association.attributes)
            # Handle basic case
            for mapping in basic_rembi_component_mapping:
                if len(association_map[mapping[1]]) == 0:
                    # Skip trying to associate objects if no objects of that type were present in the study.
                    continue
                DatasetMapper._populate_basic_mapping(
                    association_map, association_ro_crate_fields, attr_dict, mapping
                )

            # Handle more complex case of biosample
            biosample_reference: str = attr_dict["biosample"]
            specimen_reference: str = attr_dict["specimen"]

            biosample_map = association_map[ro_crate_models.BioSample]
            roc_bio_sample_id = (
                biosample_map.get(f"{biosample_reference}{specimen_reference}")
                or biosample_map[biosample_reference]
            )

            if roc_bio_sample_id:
                id = {"@id": roc_bio_sample_id}
                if id not in association_ro_crate_fields["associatedBiologicalEntity"]:
                    association_ro_crate_fields["associatedBiologicalEntity"].append(id)

        return association_ro_crate_fields

    @staticmethod
    def _populate_basic_mapping(
        association_map, association_ro_crate_fields, attr_dict, mapping
    ):
        association_reference = attr_dict.get(mapping[0])
        if association_reference and isinstance(association_reference, str):
            association_ro_crate_reference = {
                "@id": association_map[mapping[1]][association_reference]
            }

            if (
                association_ro_crate_reference
                not in association_ro_crate_fields[mapping[2]]
            ):
                association_ro_crate_fields[mapping[2]].append(
                    association_ro_crate_reference
                )

    def _create_root_dataset_for_submission(self, submission: Submission):
        section_name = "Default template. No Study Components"
        id = f"#{quote(section_name)}"

        # Use more specific section fields, fall back to base fields
        root_attributes = attributes_to_dict(submission.attributes)
        base_section_attributes = attributes_to_dict(submission.section.attributes)

        model_dict = {
            "@id": id,
            "@type": ["Dataset", "bia:Dataset"],
            "name": base_section_attributes.get("title") or root_attributes["title"],
            "description": base_section_attributes.get("description")
            or root_attributes["description"],
            "hasPart": [],
            "associationFileMetadata": None,
        }

        self.generated_dataset = ro_crate_models.Dataset(**model_dict)
