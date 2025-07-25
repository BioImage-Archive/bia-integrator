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
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion.file_list import (
    generate_relative_filelist_path,
    get_filelist_name_from_dataset,
)
from urllib.parse import quote

logger = logging.getLogger("__main__." + __name__)


def get_datasets_by_accno(
    submission: Submission,
    image_aquisition_protocols: dict[str, ro_crate_models.ImageAcquisitionProtocol],
    specimen_imaging_preparation_protocols: dict[
        str, ro_crate_models.SpecimenImagingPreparationProtocol
    ],
    annotation_methods: dict[str, ro_crate_models.AnnotationMethod],
    image_analysis_methods: dict[str, ro_crate_models.ImageAnalysisMethod],
    image_correlation_method: dict[str, ro_crate_models.ImageCorrelationMethod],
    bio_samples_association: dict[str, dict[Optional[str], str]],
) -> dict[str, ro_crate_models.Dataset]:

    study_comp_sections = find_sections_recursive(
        submission.section, ["Study Component"], []
    )

    annotation_sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    datasets_by_accno = {}
    for section in study_comp_sections:
        association_dict = get_association_field_from_associations(
            section=section,
            image_aquisition_protocols=image_aquisition_protocols,
            specimen_imaging_preparation_protocols=specimen_imaging_preparation_protocols,
            bio_samples_association=bio_samples_association,
            image_analysis_methods=image_analysis_methods,
            image_correlation_method=image_correlation_method,
        )
        datasets_by_accno[section.accno] = get_dataset_from_study_component(
            section, association_dict
        )

    for section in annotation_sections:
        datasets_by_accno[section.accno] = get_dataset_from_annotation_component(
            section, annotation_methods
        )

    return datasets_by_accno


def get_dataset_from_study_component(
    section: Section,
    association_dict: dict[str, dict[str, str]],
):

    id = f"{quote(section.accno)}/"

    attr_dict = attributes_to_dict(section.attributes)
    filelist_id_ref = {"@id": get_filelist_reference(id, section)}

    model_dict = association_dict | {
        "@id": id,
        "@type": ["Dataset", "bia:Dataset"],
        "title": attr_dict["name"],
        "description": attr_dict["description"],
        "hasPart": [filelist_id_ref],
        "associationFileMetadata": filelist_id_ref,
    }

    return ro_crate_models.Dataset(**model_dict)


def get_dataset_from_annotation_component(
    section: Section, annotation_methods: dict[str, ro_crate_models.AnnotationMethod]
):
    id = f"{quote(section.accno)}/"

    attr_dict = attributes_to_dict(section.attributes)
    filelist_id_ref = {"@id": get_filelist_reference(id, section)}

    model_dict = {
        "@id": id,
        "@type": ["Dataset", "bia:Dataset"],
        "title": attr_dict["title"],
        "description": attr_dict.get("annotation overview", None),
        "associatedAnnotationMethod": [
            {"@id": annotation_methods[attr_dict["title"]].id}
        ],
        "hasPart": [filelist_id_ref],
        "associationFileMetadata": filelist_id_ref,
        "associationFileMetadata": filelist_id_ref,
    }
    return ro_crate_models.Dataset(**model_dict)


def get_association_field_from_associations(
    section,
    image_aquisition_protocols: dict[str, ro_crate_models.ImageAcquisitionProtocol],
    specimen_imaging_preparation_protocols: dict[
        str, ro_crate_models.SpecimenImagingPreparationProtocol
    ],
    image_analysis_methods: dict[str, ro_crate_models.ImageAnalysisMethod],
    image_correlation_method: dict[str, ro_crate_models.ImageCorrelationMethod],
    bio_samples_association: dict[str, dict[Optional[str], str]],
):

    association_dict = {
        "associatedBiologicalEntity": [],
        "associatedSpecimenImagingPreparationProtocol": [],
        "associatedImageAcquisitionProtocol": [],
        "associatedImageAnalysisMethod": [],
        "associatedImageCorrelationMethod": [],
        "associatedProtocol": [],
    }

    rembi_component_mapping = [
        (
            "image acquisition",
            image_aquisition_protocols,
            "associatedImageAcquisitionProtocol",
        ),
        (
            "specimen",
            specimen_imaging_preparation_protocols,
            "associatedSpecimenImagingPreparationProtocol",
        ),
        (
            "image correlation",
            image_correlation_method,
            "associatedImageCorrelationMethod",
        ),
        (
            "image analysis",
            image_analysis_methods,
            "associatedImageAnalysisMethod",
        ),
    ]

    # Assocations will only come up for REMBI components
    associations = find_sections_recursive(section, ["Associations"], [])
    for association in associations:
        attr_dict = attributes_to_dict(association.attributes)

        for mapping in rembi_component_mapping:
            title = attr_dict.get(mapping[0], None)
            if (
                title
                and {"@id": mapping[1][title].id} not in association_dict[mapping[2]]
            ):
                association_dict[mapping[2]].append({"@id": mapping[1][title].id})

        biosample_title = attr_dict.get("biosample", None)
        specimen_title = attr_dict.get("specimen", None)

        if (
            specimen_title in bio_samples_association[biosample_title]
            and {"@id": bio_samples_association[biosample_title][specimen_title]}
            not in association_dict["associatedBiologicalEntity"]
        ):
            association_dict["associatedBiologicalEntity"].append(
                {"@id": bio_samples_association[biosample_title][specimen_title]}
            )

        elif {
            "@id": bio_samples_association[biosample_title][None]
        } not in association_dict["associatedBiologicalEntity"]:
            association_dict["associatedBiologicalEntity"].append(
                {"@id": bio_samples_association[biosample_title][None]}
            )

    return association_dict


def get_filelist_reference(dataset_id: str, dataset_section: Section):
    file_list_name = get_filelist_name_from_dataset(dataset_section)
    return generate_relative_filelist_path(dataset_id, file_list_name)
