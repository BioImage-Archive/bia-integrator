"""
Utility functions to create models

This module attempts to create models starting from the outer nodes (leaves) of the model dependency graph
"""

import json
from typing import Dict, List
from pathlib import Path
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_ingest_sm.conversion.utils import dict_to_uuid, filter_model_dictionary


accession_id = "S-BIADTEST"

def get_test_annotation_method() -> List[bia_data_model.AnnotationMethod]:
    # For UUID
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
        "annotation_criteria",
        "annotation_coverage",
        "method_type",
        "source_dataset",
    ]
    annotation_method_info = [
        {
            "accno": "Annotations-29",
            "accession_id": accession_id,
            "title_id": "Segmentation masks",
            "protocol_description": "Test annotation overview 1",
            "annotation_criteria": "Test annotation criteria 1",
            "annotation_coverage": "",
            "method_type": "other",
            "source_dataset": [],
            "version": 1,
        },
    ]

    annotation_method = []
    for annotation_method_dict in annotation_method_info:
        annotation_method_dict["uuid"] = dict_to_uuid(
            annotation_method_dict, attributes_to_consider
        )
        annotation_method_dict = filter_model_dictionary(
            annotation_method_dict, bia_data_model.AnnotationMethod
        )
        annotation_method.append(
            bia_data_model.AnnotationMethod.model_validate(annotation_method_dict)
        )
    return annotation_method


def get_test_specimen_growth_protocol() -> List[bia_data_model.SpecimenGrowthProtocol]:
    # For UUID
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
    ]
    protocol_info = [
        {
            "accno": "Specimen-1",
            "accession_id": accession_id,
            "title_id": "Test specimen 1",
            "protocol_description": "Test growth protocol 1",
            "version": 1,
        },
        {
            "accno": "Specimen-2",
            "accession_id": accession_id,
            "title_id": "Test specimen 2",
            "protocol_description": "Test growth protocol 2",
            "version": 1,
        },
    ]

    protocol = []
    for protocol_dict in protocol_info:
        protocol_dict["uuid"] = dict_to_uuid(protocol_dict, attributes_to_consider)
        protocol_dict = filter_model_dictionary(
            protocol_dict, bia_data_model.SpecimenGrowthProtocol
        )
        protocol.append(
            bia_data_model.SpecimenGrowthProtocol.model_validate(protocol_dict)
        )
    return protocol


def get_test_specimen_imaging_preparation_protocol() -> (
    List[bia_data_model.SpecimenImagingPrepartionProtocol]
):
    # For UUID
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
    ]
    protocol_info = [
        {
            "accno": "Specimen-1",
            "accession_id": accession_id,
            "title_id": "Test specimen 1",
            "protocol_description": "Test sample preparation protocol 1",
            "signal_channel_information": [],
            "version": 1,
        },
        {
            "accno": "Specimen-2",
            "accession_id": accession_id,
            "title_id": "Test specimen 2",
            "protocol_description": "Test sample preparation protocol 2",
            "signal_channel_information": [],
            "version": 1,
        },
    ]

    protocol = []
    for protocol_dict in protocol_info:
        protocol_dict["uuid"] = dict_to_uuid(protocol_dict, attributes_to_consider)
        protocol_dict = filter_model_dictionary(
            protocol_dict, bia_data_model.SpecimenImagingPrepartionProtocol
        )
        protocol.append(
            bia_data_model.SpecimenImagingPrepartionProtocol.model_validate(
                protocol_dict
            )
        )
    return protocol


def get_test_biosample() -> List[bia_data_model.BioSample]:
    # For UUID
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "organism_classification",
        "biological_entity_description",
        "intrinsic_variable_description",
        "extrinsic_variable_description",
        "experimental_variable_description",
    ]
    taxon1 = semantic_models.Taxon.model_validate(
        {
            "common_name": "human",
            "scientific_name": "Homo sapiens",
            "ncbi_id": None,
        }
    )
    taxon2 = semantic_models.Taxon.model_validate(
        {
            "common_name": "mouse",
            "scientific_name": "Mus musculus",
            "ncbi_id": None,
        }
    )
    biosample_info = [
        {
            "accno": "Biosample-1",
            "accession_id": accession_id,
            "title_id": "Test Biosample 1",
            "organism_classification": [
                taxon1.model_dump(),
            ],
            "biological_entity_description": "Test biological entity 1",
            "experimental_variable_description": [
                "Test experimental entity 1",
            ],
            "extrinsic_variable_description": [
                "Test extrinsic variable 1",
            ],
            "intrinsic_variable_description": [
                "Test intrinsic variable 1\nwith escaped character",
            ],
            "version": 1,
        },
        {
            "accno": "Biosample-2",
            "accession_id": accession_id,
            "title_id": "Test Biosample 2 ",
            "organism_classification": [
                taxon2.model_dump(),
            ],
            "biological_entity_description": "Test biological entity 2",
            "experimental_variable_description": [
                "Test experimental entity 2",
            ],
            "extrinsic_variable_description": [
                "Test extrinsic variable 2",
            ],
            "intrinsic_variable_description": [
                "Test intrinsic variable 2",
            ],
            "version": 1,
        },
    ]

    biosample = []
    for biosample_dict in biosample_info:
        biosample_dict["uuid"] = dict_to_uuid(biosample_dict, attributes_to_consider)
        biosample_dict = filter_model_dictionary(
            biosample_dict, bia_data_model.BioSample
        )
        biosample.append(bia_data_model.BioSample.model_validate(biosample_dict))
    return biosample


def get_test_image_acquisition() -> List[bia_data_model.ImageAcquisition]:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
        "imaging_instrument_description",
        "imaging_method_name",
        "fbbi_id",
    ]
    image_acquisition_info = [
        {
            "accno": "Image acquisition-3",
            "accession_id": accession_id,
            "title_id": "Test Primary Screen Image Acquisition",
            "protocol_description": "Test image acquisition parameters 1",
            "imaging_instrument_description": "Test imaging instrument 1",
            "imaging_method_name": "confocal microscopy",
            "fbbi_id": [],
            "version": 1,
        },
        {
            "accno": "Image acquisition-7",
            "accession_id": accession_id,
            "title_id": "Test Secondary Screen Image Acquisition",
            "protocol_description": "Test image acquisition parameters 2",
            "imaging_instrument_description": "Test imaging instrument 2",
            "imaging_method_name": "fluorescence microscopy",
            "fbbi_id": [],
            "version": 1,
        },
    ]
    image_acquisition = []
    for image_acquisition_dict in image_acquisition_info:
        image_acquisition_dict["uuid"] = dict_to_uuid(
            image_acquisition_dict, attributes_to_consider
        )
        image_acquisition_dict = filter_model_dictionary(
            image_acquisition_dict, bia_data_model.ImageAcquisition
        )
        image_acquisition.append(
            bia_data_model.ImageAcquisition.model_validate(image_acquisition_dict)
        )
    return image_acquisition


def get_test_image_analysis_method() -> semantic_models.ImageAnalysisMethod:
    return semantic_models.ImageAnalysisMethod.model_validate(
        {
            "protocol_description": "Test image analysis",
            "features_analysed": "Test image analysis overview",
        }
    )


def get_test_image_correlation_method() -> semantic_models.ImageCorrelationMethod:
    return semantic_models.ImageCorrelationMethod.model_validate(
        {
            "protocol_description": "Template Analysis method",
            "fiducials_used": "Template fiducials used",
            "transformation_matrix": "Template transformation matrix",
        }
    )


def get_test_file_list_data(file_list_name) -> List[Dict[str, int | str]]:
    """Return file list contents as dict

    """
    
    file_list_path = Path(__file__).parent / "data" / file_list_name
    file_list_data = json.loads(file_list_path.read_text())
    return file_list_data

def get_test_file_reference_data() -> List[Dict[str, str]]:
    """Return file reference data for study component 2

       Return file reference data for study component 2. This is the same
       data in ./data/file_list_study_component_2.json
    """
    
    submission_dataset_uuids = [s.uuid for s in get_test_experimental_imaging_dataset()]
    uri_template = "https://www.ebi.ac.uk/biostudies/files/{accession_id}/{file_path}"
    file_list_data = get_test_file_list_data("file_list_study_component_2.json")

    file_reference_data = []

    for fl_data in file_list_data:
        file_reference_data.append({
            "accession_id": accession_id,
            "file_path": fl_data["path"],
            "format": fl_data["type"],
            "size_in_bytes": fl_data["size"],
            "uri": uri_template.format(accession_id=accession_id, file_path=fl_data["path"]),
            "attribute": { a["name"]: a["value"] for a in fl_data["attributes"]},
            "submission_dataset_uuid": submission_dataset_uuids[1],
        })

    return file_reference_data

# This returns the expected FileReference models for study component 2
def get_test_file_reference() -> List [bia_data_model.FileReference]:
    
    file_reference_data = get_test_file_reference_data()
    file_reference_uuids = get_test_file_reference_uuid(file_reference_data)
    file_references = []
    for file_reference_dict, uuid in zip(file_reference_data, file_reference_uuids):
        file_reference_dict["uuid"] = uuid
        file_reference_dict["version"] = 1
        file_reference_dict = filter_model_dictionary(file_reference_dict, bia_data_model.FileReference)
        file_references.append(bia_data_model.FileReference.model_validate(file_reference_dict))

    return file_references

# TODO: Create ExperimentallyCapturedImage
def get_test_experimental_imaging_dataset() -> (
    bia_data_model.ExperimentalImagingDataset
):
    study_uuid = dict_to_uuid(
        {
            "accession_id": accession_id,
        },
        attributes_to_consider=[
            "accession_id",
        ],
    )

    experimental_imaging_dataset_dict = {
        "title_id": "Study Component 1",
        "submitted_in_study_uuid": study_uuid,
        "analysis_method": [
            get_test_image_analysis_method().model_dump(),
        ],
        "correlation_method": [
            # get_template_image_correlation_method().model_dump(),
        ],
        "example_image_uri": [],
        "description": "Description of study component 1",
        "version": 1,
        "attribute": {
            "associations": [
                {
                    "image_analysis": "Test image analysis",
                    "image_correlation": None,
                    "biosample": "Test Biosample 1",
                    "image_acquisition": "Test Primary Screen Image Acquisition",
                    "specimen": "Test specimen 1",
                },
                {
                    "image_analysis": "Test image analysis",
                    "image_correlation": None,
                    "biosample": "Test Biosample 2 ",
                    "image_acquisition": "Test Secondary Screen Image Acquisition",
                    "specimen": "Test specimen 1",
                },
            ]
        },
    }
    experimental_imaging_dataset_uuid = dict_to_uuid(
        experimental_imaging_dataset_dict,
        [
            "title_id",
            "submitted_in_study_uuid",
        ],
    )
    experimental_imaging_dataset_dict["uuid"] = experimental_imaging_dataset_uuid
    experimental_imaging_dataset_dict = filter_model_dictionary(
        experimental_imaging_dataset_dict, bia_data_model.ExperimentalImagingDataset
    )
    experimental_imaging_dataset1 = (
        bia_data_model.ExperimentalImagingDataset.model_validate(
            experimental_imaging_dataset_dict
        )
    )

    experimental_imaging_dataset_dict = {
        "title_id": "Study Component 2",
        "submitted_in_study_uuid": study_uuid,
        "analysis_method": [
            get_test_image_analysis_method().model_dump(),
        ],
        "correlation_method": [
            # get_template_image_correlation_method().model_dump(),
        ],
        "example_image_uri": [],
        "description": "Description of study component 2",
        "version": 1,
        "attribute": {
            "associations": [
                {
                    "image_analysis": "Test image analysis",
                    "image_correlation": None,
                    "biosample": "Test Biosample 2 ",
                    "image_acquisition": "Test Primary Screen Image Acquisition",
                    "specimen": "Test specimen 2",
                }
            ]
        },
    }
    experimental_imaging_dataset_uuid = dict_to_uuid(
        experimental_imaging_dataset_dict,
        [
            "title_id",
            "submitted_in_study_uuid",
        ],
    )
    experimental_imaging_dataset_dict["uuid"] = experimental_imaging_dataset_uuid
    experimental_imaging_dataset2 = (
        bia_data_model.ExperimentalImagingDataset.model_validate(
            experimental_imaging_dataset_dict
        )
    )
    return [experimental_imaging_dataset1, experimental_imaging_dataset2]


def get_test_affiliation() -> Dict[str, semantic_models.Affiliation]:
    affiliation1 = semantic_models.Affiliation.model_validate(
        {
            "display_name": "Test College 1",
            "rorid": None,
            "address": None,
            "website": None,
        }
    )
    affiliation2 = semantic_models.Affiliation.model_validate(
        {
            "display_name": "Test College 2",
            "rorid": None,
            "address": None,
            "website": None,
        }
    )
    return {
        "o1": affiliation1,
        "o2": affiliation2,
    }


def get_test_contributor() -> Dict[str, semantic_models.Contributor]:
    affiliations = get_test_affiliation()
    contributor1 = semantic_models.Contributor.model_validate(
        {
            "display_name": "Test Author1",
            "contact_email": "test_author1@ebi.ac.uk",
            "role": "corresponding author",
            "affiliation": [
                affiliations["o1"],
            ],
            "rorid": None,
            "address": None,
            "website": None,
            "orcid": "0000-0000-0000-0000",
        }
    )
    contributor2 = semantic_models.Contributor.model_validate(
        {
            "display_name": "Test Author2",
            "contact_email": "test_author2@ebi.ac.uk",
            "role": "first author",
            "affiliation": [
                affiliations["o2"],
            ],
            "rorid": None,
            "address": None,
            "website": None,
            "orcid": "1111-1111-1111-1111",
        }
    )

    return [
        contributor1,
        contributor2,
    ]


def get_test_publication() -> List[semantic_models.Publication]:
    publication1 = semantic_models.Publication.model_validate(
        {
            "pubmed_id": "38381674",
            "title": "Test publication 1",
            # TODO: No release date -> ST only collects Year
            "release_date": "2024",
            # TODO: Author is a string here.
            "author": "Test Author11, Test Author12.",
        }
    )
    publication2 = semantic_models.Publication.model_validate(
        {
            "pubmed_id": "38106175",
            "doi": "10.1101/2023.12.07.570699",
            "title": "Test publication 2",
            # TODO: Author is a string here.
            "author": "Test Author21, Test Author22",
            "release_date": "2023",
        }
    )
    return [
        publication1,
        publication2,
    ]


def get_test_external_reference() -> List[semantic_models.ExternalReference]:
    link1 = semantic_models.ExternalReference.model_validate(
        {
            "link": "https://www.test.link1.com/",
            "description": "Test link 1.",
        }
    )
    link2 = semantic_models.ExternalReference.model_validate(
        {
            "link": "ERP116793",
            "description": "Test ENA link",
            "Type": "ENA",
        }
    )
    return [
        link1,
        link2,
    ]


def get_test_grant() -> List[semantic_models.Grant]:
    funding_body1 = semantic_models.FundingBody.model_validate(
        {
            "display_name": "Test funding body1",
        }
    )
    funding_body2 = semantic_models.FundingBody.model_validate(
        {
            "display_name": "Test funding body2",
        }
    )

    grant1 = semantic_models.Grant.model_validate(
        {
            "id": "TESTFUNDS1",
            "funder": [
                funding_body1,
            ],
        }
    )
    grant2 = semantic_models.Grant.model_validate(
        {
            "id": "TESTFUNDS2",
            "funder": [
                funding_body2,
            ],
        }
    )
    return [
        grant1,
        grant2,
    ]


def get_test_study() -> bia_data_model.Study:
    contributor = get_test_contributor()
    grant = get_test_grant()
    study_dict = {
        "accession_id": accession_id,
        "title": "A test submission with title greater than 25 characters",
        "description": "A test submission to allow testing without retrieving from bia server",
        "release_date": "2024-02-13",
        "licence": semantic_models.LicenceType.CC0,
        "acknowledgement": "We thank you",
        "funding_statement": "This work was funded by the EBI",
        "attribute": {},
        "related_publication": [],
        "author": [c.model_dump() for c in contributor],
        "keyword": [
            "Test keyword1",
            "Test keyword2",
            "Test keyword3",
        ],
        "grant": [g.model_dump() for g in grant],
        "version": 1,
    }
    study_uuid = dict_to_uuid(
        study_dict,
        [
            "accession_id",
        ],
    )
    study_dict["uuid"] = study_uuid
    study = bia_data_model.Study.model_validate(study_dict)
    return study


def get_test_file_reference_uuid(file_references: List[Dict[str, str]]) -> List[str]:
    attributes_to_consider = [
        "accession_id",
        "file_path",
        "size_in_bytes",
    ]
    return [
        dict_to_uuid(file_reference, attributes_to_consider)
        for file_reference in file_references
    ]
