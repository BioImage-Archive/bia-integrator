import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.api import (
    Submission,
    Section,
)
from typing import Optional
from bia_shared_datamodels import ro_crate_models


logger = logging.getLogger("__main__." + __name__)


def get_datasets(
    submission: Submission,
    image_aquisition_protocols: dict[str, ro_crate_models.ImageAcquisitionProtocol],
    specimen_imaging_preparation_protocols: dict[
        str, ro_crate_models.SpecimenImagingPreparationProtocol
    ],
    annotation_methods: dict[str, ro_crate_models.AnnotationMethod],
    image_analysis_methods: dict[str, ro_crate_models.ImageAnyalysisMethod],
    image_correlation_method: dict[str, ro_crate_models.ImageCorrelationMethod],
    bio_samples_association: dict[str, dict[Optional[str], str]],
) -> dict[str, ro_crate_models.Dataset]:

    study_comp_sections = find_sections_recursive(
        submission.section, ["Study Component"], []
    )

    annotation_sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    datasets = []
    for section in study_comp_sections:
        association_dict = get_association_field_from_associations(
            section=section,
            image_aquisition_protocols=image_aquisition_protocols,
            specimen_imaging_preparation_protocols=specimen_imaging_preparation_protocols,
            bio_samples_association=bio_samples_association,
            image_analysis_methods=image_analysis_methods,
            image_correlation_method=image_correlation_method,
        )
        datasets.append(get_dataset_from_study_component(section, association_dict))

    for section in annotation_sections:
        datasets.append(
            get_dataset_from_annotation_component(section, annotation_methods)
        )

    return datasets


def get_dataset_from_study_component(
    section: Section,
    association_dict: dict[str, dict[str, str]],
):

    attr_dict = attributes_to_dict(section.attributes)

    model_dict = association_dict | {
        "@id": f"./{section.accno}",
        "@type": ["Dataset", "bia:Dataset"],
        "title": attr_dict["name"],
        "desciption": attr_dict["description"],
    }

    return ro_crate_models.Dataset(**model_dict)


def get_dataset_from_annotation_component(
    section: Section, annotation_methods: dict[str, ro_crate_models.AnnotationMethod]
):

    attr_dict = attributes_to_dict(section.attributes)

    model_dict = {
        "@id": f"./{section.accno}",
        "@type": ["Dataset", "bia:Dataset"],
        "title": attr_dict["title"],
        "desciption": attr_dict.get("annotation overview", None),
        "associatedAnnotationMethod": [
            {"@id": annotation_methods[attr_dict["title"]].id}
        ],
    }
    return ro_crate_models.Dataset(**model_dict)


def get_association_field_from_associations(
    section,
    image_aquisition_protocols: dict[str, ro_crate_models.ImageAcquisitionProtocol],
    specimen_imaging_preparation_protocols: dict[
        str, ro_crate_models.SpecimenImagingPreparationProtocol
    ],
    image_analysis_methods: dict[str, ro_crate_models.ImageAnyalysisMethod],
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

    # Assocations will only come up for REMBI components
    associations = find_sections_recursive(section, ["Associations"], [])
    for association in associations:
        attr_dict = attributes_to_dict(association.attributes)

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

        for mapping in rembi_component_mapping:
            title = attr_dict.get(mapping[0], None)
            if title:
                association_dict[mapping[2]].append({"@id": mapping[1][title].id})

        biosample_title = attr_dict.get("biosample", None)
        specimen_title = attr_dict.get("specimen", None)

        if specimen_title in bio_samples_association[biosample_title]:
            association_dict["associatedBiologicalEntity"].append(
                {"@id": bio_samples_association[biosample_title][specimen_title]}
            )
        else:
            association_dict["associatedBiologicalEntity"].append(
                {"@id": bio_samples_association[biosample_title][None]}
            )

    return association_dict
