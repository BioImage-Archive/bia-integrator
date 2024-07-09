"""Utility functions to create models

    This module attempts to create models starting from the outer nodes (leaves) of the 
    model dependency graph

"""

from typing import Dict, List
from src.bia_models import bia_data_model, semantic_models
from bia_ingest_sm.conversion.utils import dict_to_uuid
from uuid import uuid4

template_taxon = semantic_models.Taxon.model_validate(
    {
        "common_name": "Test Common Name",
        "scientific_name": "Test Scientific Name",
        "ncbi_id": "Test_NCBI_ID",
    }
)


def get_template_channel() -> semantic_models.Channel:
    return semantic_models.Channel.model_validate(
        {
            "colormap_start": 0.0,
            "colormap_end": 1.0,
            "scale_factor": 1.0,
            "label": "Template label",
        }
    )


def get_template_rendered_view() -> semantic_models.RenderedView:
    return semantic_models.RenderedView.model_validate(
        {
            "z": "Template z position",
            "t": "Template t position",
            "channel_information": [
                get_template_channel(),
            ],
        }
    )


def get_template_specimen_preparation_protocol() -> (
    bia_data_model.SpecimenPrepartionProtocol
):
    specimen_preparation_protocol = (
        bia_data_model.SpecimenPrepartionProtocol.model_validate(
            {
                "uuid": uuid4(),
                "title_id": "Test specimen preparation protocol",
                "method_description": "Test description",
                "signal_contrast_mechanism_description": "Test description",
                "growth_protocol_description": "Test description",
                "channel_content_description": "Test description",
                "channel_biological_entity": "Test Entity",
            }
        )
    )
    return specimen_preparation_protocol


def get_test_biosample() -> List[bia_data_model.BioSample]:
    # For UUID
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "organism_classification",
        "description",
        # TODO: Discuss including below in semantic_models.BioSample
        #"biological_entity",
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
            "accession_id": "S-BIADTEST",
            "title_id": "Test Biosample 1",
            "organism_classification": [
                taxon1.model_dump(),
            ],
            "description": "Test description 1 (\"with some escaped chars\") ",
            "experimental_variable_description": [
                "Test experimental entity 1",
            ],
            "extrinsic_variable_description": [
                "Test extrinsic variable 1",
            ],
            "intrinsic_variable_description": [
                "Test intrinsic variable 1\nwith escaped character",
            ],
         }, {
            "accno": "Biosample-2",
            "accession_id": "S-BIADTEST",
            "title_id": "Test Biosample 2 ",
            "organism_classification": [
                taxon2.model_dump(),
            ],
            "description": "Test description 2",
            "experimental_variable_description": [
                "Test experimental entity 2",
            ],
            "extrinsic_variable_description": [
                "Test extrinsic variable 2",
            ],
            "intrinsic_variable_description": [
                "Test intrinsic variable 2",
            ],
        },
    ]
    
    biosample = []
    for biosample_dict in biosample_info:
        biosample_dict["uuid"] = dict_to_uuid(biosample_dict, attributes_to_consider)
        biosample.append(bia_data_model.BioSample.model_validate(biosample_dict))
    return biosample


# Depends on:
#   bia_data_model.BioSample
#   bia_data_model.SpecimenPreparationProtocol
def get_template_specimen() -> bia_data_model.Specimen:
    specimen = bia_data_model.Specimen.model_validate(
        {
            "preparation_method": [
                get_template_specimen_preparation_protocol().uuid,
            ],
            "sample_of": [
                biosample.uuid for biosample in get_test_biosample()
            ],
        }
    )
    return specimen


# Depends on ExperimentalImagingDataset (circular)
def get_template_annotation_method() -> bia_data_model.AnnotationMethod:
    annotation_method = bia_data_model.AnnotationMethod.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Template annotation method",
            "source_dataset": [],  # ExperimentalImagingDataset.uuid or url
            "method_description": "Template annotation method description",
            "annotation_criteria": "Template annotation criteria",
            "annotation_coverage": "Template annotation coverage",
            "method_type": semantic_models.AnnotationType.class_labels,
        }
    )
    return annotation_method


# Depends on:
#   bia_data_model.ExperimentalImagingDataset (circular dependency)
#   bia_data_model.ImageAcquisition
#   bia_data_model.ImageRepresentation
#   bia_data_model.Specimen
def get_template_experimentally_captured_image() -> (
    bia_data_model.ExperimentallyCapturedImage
):
    return bia_data_model.ExperimentallyCapturedImage.model_validate(
        {
            "uuid": uuid4(),
            "acquisition_process": [get_template_image_acquisition().uuid],
            "representation": [
                get_template_image_representation().uuid,
            ],
            "submission_dataset": get_template_experimental_imaging_dataset().uuid,
            "subject": get_template_specimen(),
            "attribute": {},
        }
    )


# Depends on:
#   bia_data_model.ImageAnnotationDataset (circular dependency)
#   bia_data_model.AnnotationMethod
#   bia_data_model.ImageRepresentation
def get_template_derived_image() -> bia_data_model.DerivedImage:
    derived_image = bia_data_model.DerivedImage.model_validate(
        {
            "uuid": uuid4(),
            "source_image": [
                get_template_image_representation().uuid,
            ],
            "submission_dataset": get_template_image_annotation_dataset().uuid,
            "creation_process": get_template_annotation_method().uuid,
            "representation": [
                get_template_image_representation().uuid,
            ],
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "attribute": {},
        }
    )
    return derived_image


# Depends on:
#   bia_data_model.DerivedImage
#   bia_data_model.FileReference (this is a circular dependence!)
#   bia_data_model.Study
#   bia_data_model.AnnotationFileReference (this is a circular dependence!)
#   bia_data_model.AnnotationMethod
#
# TODO: Verify that in practice, the Datasets are created then the
#       FileReference instances are added. So here we have empty lists
#       for the dataset
def get_template_image_annotation_dataset() -> bia_data_model.ImageAnnotationDataset:
    image_annotation_dataset = bia_data_model.ImageAnnotationDataset.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Template image annotation dataset",
            "image": [
                get_template_image_representation().uuid,
            ],
            "file": [],  # This should be a list of FileReference UUIDs ...
            "annotation_file": [],  # This should be a list of AnnotationFileReference UUIDs ...
            "submitted_in_study": get_template_study().uuid,
            "annotation_method": get_template_annotation_method().uuid,
            "file_reference_count": 0,
            "image_count": 0,
            "example_image_uri": ["https://dummy.url.org"],
        }
    )
    return image_annotation_dataset


def get_test_image_acquisition() -> List[bia_data_model.ImageAcquisition]:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "method_description",
        "imaging_instrument_description",
        "image_acquisition_parameters",
        "fbbi_id",
    ]
    image_acquisition_info = [
        {
            "accno": "Image acquisition-3",
            "accession_id": "S-BIADTEST",
            "title_id": "Test Primary Screen Image Acquisition",
            "method_description": "confocal microscopy",
            "imaging_instrument_description": "Test imaging instrument 1",
            "image_acquisition_parameters": "Test image acquisition parameters 1",
            "fbbi_id": [],
        }, {
            "accno": "Image acquisition-7",
            "accession_id": "S-BIADTEST",
            "title_id": "Test Secondary Screen Image Acquisition",
            "method_description": "flourescence microscopy",
            "imaging_instrument_description": "Test imaging instrument 2",
            "image_acquisition_parameters": "Test image acquisition parameters 2",
            "fbbi_id": [],
        },
    ]
    image_acquisition = []
    for image_acquisition_dict in image_acquisition_info:
        image_acquisition_dict["uuid"] = dict_to_uuid(image_acquisition_dict, attributes_to_consider)
        image_acquisition.append(bia_data_model.ImageAcquisition.model_validate(image_acquisition_dict))
    return image_acquisition


def get_test_image_analysis_method() -> semantic_models.ImageAnalysisMethod:
    return semantic_models.ImageAnalysisMethod.model_validate(
        {
            "method_description": "Test image analysis",
            "features_analysed": "Test image analysis overview",
        }
    )


def get_template_image_correlation_method() -> semantic_models.ImageCorrelationMethod:
    return semantic_models.ImageCorrelationMethod.model_validate(
        {
            "method_description": "Template Analysis method",
            "fiducials_used": "Template fiducials used",
            "transformation_matrix": "Template transformation matrix",
        }
    )


# TODO: Create FileReferences and ExperimentallyCapturedImage 
def get_test_experimental_imaging_dataset() -> (
    bia_data_model.ExperimentalImagingDataset
):
    study_uuid = dict_to_uuid(
        {"accession_id": "S-BIADTEST",},
        attributes_to_consider=["accession_id",]
    )
    # Create first study component
    file_references = [{
            "accession_id": "S-BIADTEST",
            "file_name": "study_component1/im06.png",
            "size_in_bytes": 3,
        },{
            "accession_id": "S-BIADTEST",
            "file_name": "study_component1/im08.png",
            "size_in_bytes": 123,
        },{
            "accession_id": "S-BIADTEST",
            "file_name": "study_component1/ann01-05",
            "size_in_bytes": 11,
        },{
            "accession_id": "S-BIADTEST",
            "file_name": "study_component1/ann06-10.json",
            "size_in_bytes": 12,
        },
    ]
    file_reference_uuids = get_test_file_reference_uuid(file_references)

    experimental_imaging_dataset_dict = {
        "title_id": "Study Component 1",
        "image": [],  # This should be a list of Experimentally captured image UUIDs
        "file": file_reference_uuids,
        "submitted_in_study": study_uuid,
        "specimen_preparation_method": [
            #get_template_specimen_preparation_protocol().uuid,
        ],
        "acquisition_method": [
            #get_test_image_acquisition()[0].uuid,
        ],
        # This study component uses both biosamples
        "biological_entity": [
            biosample.uuid for biosample in get_test_biosample()
        ],
        "analysis_method": [
            get_test_image_analysis_method().model_dump(),
        ],
        "correlation_method": [
            #get_template_image_correlation_method().model_dump(),
        ],
        "file_reference_count": 4,
        "image_count": 0,
        "example_image_uri": [],
    }
    experimental_imaging_dataset_uuid = dict_to_uuid(experimental_imaging_dataset_dict, ["title_id", "submitted_in_study",])
    experimental_imaging_dataset_dict["uuid"] = experimental_imaging_dataset_uuid
    experimental_imaging_dataset1 = bia_data_model.ExperimentalImagingDataset.model_validate(experimental_imaging_dataset_dict)

    # Create second study component
    file_references = [{
            "accession_id": "S-BIADTEST",
            "file_name": "study_component2/im06.png",
            "size_in_bytes": 3,
        },{
            "accession_id": "S-BIADTEST",
            "file_name": "study_component2/im08.png",
            "size_in_bytes": 123,
        },{
            "accession_id": "S-BIADTEST",
            "file_name": "study_component2/ann01-05",
            "size_in_bytes": 11,
        },
    ]
    file_reference_uuids = get_test_file_reference_uuid(file_references)

    experimental_imaging_dataset_dict = {
        "title_id": "Study Component 2",
        "image": [],  # This should be a list of Experimentally captured image UUIDs
        "file": file_reference_uuids,
        "submitted_in_study": study_uuid,
        "specimen_preparation_method": [
            #get_template_specimen_preparation_protocol().uuid,
        ],
        "acquisition_method": [
            #get_test_image_acquisition()[1].uuid,
        ],
        # This study component uses only second biosample
        "biological_entity": [
            get_test_biosample()[1].uuid,
        ],
        "analysis_method": [
            get_test_image_analysis_method().model_dump(),
        ],
        "correlation_method": [
            #get_template_image_correlation_method().model_dump(),
        ],
        "file_reference_count": 3,
        "image_count": 0,
        "example_image_uri": [],
    }
    experimental_imaging_dataset_uuid = dict_to_uuid(experimental_imaging_dataset_dict, ["title_id", "submitted_in_study",])
    experimental_imaging_dataset_dict["uuid"] = experimental_imaging_dataset_uuid
    experimental_imaging_dataset2 = bia_data_model.ExperimentalImagingDataset.model_validate(experimental_imaging_dataset_dict)
    return [experimental_imaging_dataset1, experimental_imaging_dataset2]


# Depends on:
#   bia_data_model.ImageAnnotationDataset (circular)
#   bia_data_model.ExperimentalImagingDataset (circular)
def get_template_annotation_file_reference() -> bia_data_model.AnnotationFileReference:
    return bia_data_model.AnnotationFileReference.model_validate(
        {
            "uuid": uuid4(),
            "file_name": "Dummy file name",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "attribute": {},
            "submission_dataset": get_template_image_annotation_dataset().uuid,
            "source_image": [
                get_template_image_representation().uuid,
            ],
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "creation_process": get_template_annotation_method().uuid,
        }
    )


# Depends on:
#   bia_data_model.ImageAnnotationDataset (circular)
#   bia_data_model.ExperimentalImagingDataset (circular)
def get_template_file_reference() -> bia_data_model.FileReference:
    file_reference = bia_data_model.FileReference.model_validate(
        {
            "uuid": uuid4(),
            "file_name": "Dummy file name",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "attribute": {},
            "submission_dataset": get_template_experimental_imaging_dataset().uuid,
        }
    )
    return file_reference


# Depends on:
#   bia_data_model.FileReference (
def get_template_image_representation() -> bia_data_model.ImageRepresentation:
    return bia_data_model.ImageRepresentation.model_validate(
        {
            "uuid": uuid4(),
            "original_file_reference": [
                get_template_file_reference().uuid,
            ],
            "image_format": "Template image format",
            "file_uri": [
                "https://dummy.uri.org",
            ],
            "total_size_in_bytes": 0,
            "physical_size_x": 1,
            "physical_size_y": 1,
            "physical_size_z": 1,
            "size_x": 1,
            "size_y": 1,
            "size_z": 1,
            "size_c": 1,
            "size_t": 1,
            "image_viewer_setting": [
                get_template_rendered_view().model_dump(),
            ],
            "attribute": {},
        }
    )


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
    return { "o1": affiliation1, "o2": affiliation2, }


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

    return [contributor1, contributor2,]

def get_test_publication() -> List[semantic_models.Publication]:
    publication1 = semantic_models.Publication.model_validate({
        "pubmed_id": "38381674",
        "title": "Test publication 1",
        # TODO: No release date -> ST only collects Year
        "release_date": "2024",
        # TODO: Author is a string here.
        "author": "Test Author11, Test Author12.",
    })
    publication2 = semantic_models.Publication.model_validate({
        "pubmed_id": "38106175",
        "doi": "10.1101/2023.12.07.570699",
        "title": "Test publication 2",
        # TODO: Author is a string here.
        "author": "Test Author21, Test Author22",
        "release_date": "2023",
    })
    return [publication1, publication2,]

def get_test_external_reference() -> List[semantic_models.ExternalReference]:
    link1 = semantic_models.ExternalReference.model_validate({
        "link": "https://www.test.link1.com/",
        "description": "Test link 1.",
    })
    link1 = semantic_models.ExternalReference.model_validate({
        "link": "ERP116793",
        "description": "Test ENA link",
        "Type": "ENA",
    })
    return [link1, link2,]


def get_test_grant() -> List[semantic_models.Grant]:
    funding_body1 = semantic_models.FundingBody.model_validate({
        "display_name": "Test funding body1",
    })
    funding_body2 = semantic_models.FundingBody.model_validate({
        "display_name": "Test funding body2",
    })

    grant1 = semantic_models.Grant.model_validate({
        "id": "TESTFUNDS1",
        "funder": [funding_body1,],
    })
    grant2 = semantic_models.Grant.model_validate({
        "id": "TESTFUNDS2",
        "funder": [funding_body2,],
    })
    return [grant1, grant2,]

def get_test_study() -> bia_data_model.Study:
    contributor = get_test_contributor()
    grant = get_test_grant()
    study_dict = {
        "accession_id": "S-BIADTEST",
        "title": "A test submission with title greater than 25 characters",
        "description": "A test submission to allow testing without retrieving from bia server",
        "release_date": "2024-02-13",
        "licence": semantic_models.LicenceType.CC0,
        "acknowledgement": "We thank you",
        "funding_statement": "This work was funded by the EBI",
        "attribute": {

        },
        "related_publication": [],
        "author": [ c.model_dump() for c in contributor ],
        "keyword": [
            "Test keyword1",
            "Test keyword2",
            "Test keyword3",
        ],
        "grant": [ g.model_dump() for g in grant ],
        "experimental_imaging_component": [e.uuid for e in get_test_experimental_imaging_dataset()],
        "annotation_component": [],
    }
    study_uuid = dict_to_uuid(study_dict, ["accession_id", ])
    study_dict["uuid"] = study_uuid
    study = bia_data_model.Study.model_validate(study_dict)
    return study

def get_test_file_reference_uuid(file_references: List[Dict[str, str]]) -> List[str]:
    attributes_to_consider = [
        "accession_id",
        "file_name",
        "size_in_bytes",
    ]
    return [
        dict_to_uuid(file_reference, attributes_to_consider) for file_reference in file_references
    ]
