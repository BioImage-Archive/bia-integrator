import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
    find_sections_with_filelists_recursive,
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
    protocols: dict[str, ro_crate_models.Protocol],
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

    for section in generic_section_with_filelist:
        datasets_by_accno[section.accno] = get_dataset_from_generic_filelist_section(
            section, protocols
        )

    return datasets_by_accno


def get_dataset_from_study_component(
    section: Section,
    association_dict: dict[str, dict[str, str]],
):

    roc_id = f"{quote(section.accno)}/"

    attr_dict = attributes_to_dict(section.attributes)
    filelist_id_ref = {"@id": get_filelist_reference(roc_id, section)}

    model_dict = association_dict | {
        "@id": roc_id,
        "@type": ["Dataset", "bia:Dataset"],
        "name": attr_dict["name"],
        "description": attr_dict["description"],
        "hasPart": [filelist_id_ref],
        "associationFileMetadata": filelist_id_ref,
    }

    return ro_crate_models.Dataset(**model_dict)


def get_dataset_from_annotation_component(
    section: Section, annotation_methods: dict[str, ro_crate_models.AnnotationMethod]
):
    roc_id = f"{quote(section.accno)}/"

    attr_dict = attributes_to_dict(section.attributes)
    filelist_id_ref = {"@id": get_filelist_reference(roc_id, section)}

    model_dict = {
        "@id": roc_id,
        "@type": ["Dataset", "bia:Dataset"],
        "name": attr_dict["title"],
        "description": attr_dict.get("annotation overview", None),
        "associatedAnnotationMethod": [
            {"@id": annotation_methods[attr_dict["title"]].id}
        ],
        "hasPart": [filelist_id_ref],
        "associationFileMetadata": filelist_id_ref,
    }
    return ro_crate_models.Dataset(**model_dict)


def get_dataset_from_generic_filelist_section(
    section: Section, protocols: dict[str, ro_crate_models.Protocol]
):
    roc_id = f"{quote(section.accno)}/"

    attr_dict = attributes_to_dict(section.attributes)
    filelist_id_ref = {"@id": get_filelist_reference(roc_id, section)}

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
            {"@id": protocols[accno].id} for accno in protocol_subsections_ids
        ],
        "hasPart": [filelist_id_ref],
        "associationFileMetadata": filelist_id_ref,
    }

    return ro_crate_models.Dataset(**model_dict)


def get_association_field_from_associations(
    section: Section,
    image_aquisition_protocols: dict[str, ro_crate_models.ImageAcquisitionProtocol],
    specimen_imaging_preparation_protocols: dict[
        str, ro_crate_models.SpecimenImagingPreparationProtocol
    ],
    image_analysis_methods: dict[str, ro_crate_models.ImageAnalysisMethod],
    image_correlation_method: dict[str, ro_crate_models.ImageCorrelationMethod],
    bio_samples_association: dict[str, dict[str | None, str]],
) -> dict[str, list[dict[str, str]]]:
    """
    Function that fills in the association fields for an ro-crate BIA Dataset based on the associations of the BioSample Study Component.

        Parameters:
            section (Section):
                A dataset section which should have associations of the form:
                "subsections": [
                    {
                        "type": "Associations",
                        "attributes": [
                        {
                            "name": "Biosample",
                            "value": "Cell Lines"
                        },
                        {
                            "name": "Specimen",
                            "value": "Protocol"
                        },
                        {
                            "name": "Image acquisition",
                            "value": "Image Acquisition using CQ1 confocal imaging"
                        }
                        ]
                    }
                ]
                Where the value in the attribute corresponds to the title of other biostudies objects.

            image_aquisition_protocols (dict[str, ro_crate_models.ImageAcquisitionProtocol]):
                A map between the title of the ImageAcquisitionProtocol and the ImageAcquisitionProtocol in order to retrieve the ID

            specimen_imaging_preparation_protocols, image_analysis_methods, image_analysis_methods, image_correlation_method:
                These other parameters are the same as image_aquisition_protocols for their respective types

            bio_samples_association (dict[str, dict[str | None, str]]]):
                Essentially a tree to get to the correct ID of a ro-crate biosample. Unlikely the other objects, there is a 1 -> many
                relationship betwen Biostudies Biosample and ro-crate BioSamples. The correct ID to use depends on both a) the title
                of the biosample being present in the assoication (the key of the outer dict) and b) whether the association Specimen
                resulted in a Growth Protocol. In this case the correct id for the ro-crate BioSample will be under [Biosample Title]
                [Specimen title]. If no Growth protocol was needed the correct id for the BioSample is under [Biosample Title][None].
                See get_taxons_bio_samples_and_association_map in bio_sample.py for how this is created. See S-BIADTEST_COMPLEX_BIOSAMPLE 
                in the tests for an example of the expected end-to-end input-output.

            Returns:
                association_dict ( dict[str, list[dict[str, str]]]):
                    A dictionary which can be used as part of an BIA ro-crate Dataset object, containing all the association fields
                    for a non-annotation Study Component.
    """

    association_dict = {
        "associatedBiologicalEntity": [],
        "associatedSpecimenImagingPreparationProtocol": [],
        "associatedImageAcquisitionProtocol": [],
        "associatedImageAnalysisMethod": [],
        "associatedImageCorrelationMethod": [],
        "associatedProtocol": [],
    }

    # Mapping that groups the name of the association in the biostudies submission, the objects we have created in ro-crate,
    # and the field in the ro-crate dataset we want to put the object ID references into.
    # Does not include BioSamples, as that has different logic.
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

        # If no biosample and specimen, review Study
        biosample_title: str = attr_dict["biosample"]
        specimen_title: str = attr_dict["specimen"]
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
