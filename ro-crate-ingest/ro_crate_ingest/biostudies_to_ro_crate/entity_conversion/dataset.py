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
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion.file_list import (
    generate_relative_filelist_path,
    get_filelist_name_from_dataset,
)

logger = logging.getLogger("__main__." + __name__)


def get_datasets_by_accno(
    submission: Submission,
    association_map: dict[type, dict[str, str]],
) -> dict[str, ro_crate_models.Dataset]:

    study_comp_sections = find_sections_recursive(
        submission.section, ["Study Component"], []
    )

    annotation_sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    generic_section_with_filelist = find_sections_with_filelists_recursive(
        submission.section, ignore_types=["Study Component", "Annotations"]
    )

    datasets_by_accno = {}
    for section in study_comp_sections:
        association_dict = get_association_fields(
            section=section,
            association_map=association_map,
        )
        datasets_by_accno[section.accno] = get_dataset_from_study_component(
            section, association_dict
        )

    for section in annotation_sections:
        datasets_by_accno[section.accno] = get_dataset_from_annotation_component(
            section, association_map
        )

    for section in generic_section_with_filelist:
        datasets_by_accno[section.accno] = get_dataset_from_generic_filelist_section(
            section, association_map
        )

    return datasets_by_accno


def get_dataset_from_study_component(
    section: Section,
    association_dict: dict[type, dict[str, str]],
):

    roc_id = f"#{quote(section.accno)}"

    attr_dict = attributes_to_dict(section.attributes)

    model_dict = association_dict | {
        "@id": roc_id,
        "@type": ["Dataset", "bia:Dataset"],
        "name": attr_dict["name"],
        "description": attr_dict["description"],
    }

    return ro_crate_models.Dataset(**model_dict)


def get_dataset_from_annotation_component(
    section: Section, association_map: dict[type, dict[str, str]]
):
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
    return ro_crate_models.Dataset(**model_dict)


def get_dataset_from_generic_filelist_section(
    section: Section, association_map: dict[str, dict[type, str]]
):
    roc_id = f"#{quote(section.accno)}"

    attr_dict = attributes_to_dict(section.attributes)

    # Handle older submission formats (prior to v4 template submission) by creating protocols for the subsections.
    protocol_subsections_ids = [
        protocol.accno for protocol in find_sections_recursive(section, ["Protocol"])
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

    return ro_crate_models.Dataset(**model_dict)


def get_association_fields(
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

        # Handle more complex case of biosample
        biosample_reference: str = attr_dict["biosample"]
        specimen_reference: str = attr_dict["specimen"]

        biosample_map = association_map[ro_crate_models.BioSample]
        roc_bio_sample_id = (
            biosample_map.get(f"{biosample_reference}{specimen_reference}")
            or biosample_map[biosample_reference]
        )

        if roc_bio_sample_id:
            association_ro_crate_fields["associatedBiologicalEntity"].append(
                {"@id": roc_bio_sample_id}
            )

    return association_ro_crate_fields


def get_filelist_reference(dataset_id: str, dataset_section: Section):
    file_list_name = get_filelist_name_from_dataset(dataset_section)
    return generate_relative_filelist_path(dataset_id, file_list_name)
