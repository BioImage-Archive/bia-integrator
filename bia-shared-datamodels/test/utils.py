"""
Utility functions to create models

This module attempts to create models starting from the outer nodes (leaves) of the model dependency graph
"""

from pathlib import Path

base_path = Path(__file__).parent
from bia_shared_datamodels import bia_data_model, semantic_models
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


def get_template_signal_channel_information() -> (
    semantic_models.SignalChannelInformation
):
    return semantic_models.SignalChannelInformation.model_validate(
        {
            "signal_contrast_mechanism_description": "Test description",
            "channel_content_description": "Test description",
            "channel_biological_entity": "Test Entity",
        }
    )


def get_template_specimen_imaging_preparation_protocol() -> (
    bia_data_model.SpecimenImagingPrepartionProtocol
):
    specimen_imaging_preparation_protocol = (
        bia_data_model.SpecimenImagingPrepartionProtocol.model_validate(
            {
                "uuid": uuid4(),
                "title_id": "Test specimen preparation protocol",
                "protocol_description": "Test description",
                "signal_channel_information": [
                    get_template_signal_channel_information()
                ],
                "version": 1,
                "model": {
                "type_name": "SpecimenImagingPrepartionProtocol", 
                "version": 1
            }
            }
        )
    )
    return specimen_imaging_preparation_protocol


def get_template_specimen_growth_protocol() -> bia_data_model.SpecimenGrowthProtocol:
    specimen_growth_protocol = bia_data_model.SpecimenGrowthProtocol.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Test specimen preparation protocol",
            "protocol_description": "Test description",
            "version": 1,
            "model": {
                "type_name": "SpecimenGrowthProtocol", 
                "version": 1
            }
        }
    )
    return specimen_growth_protocol


def get_template_biosample() -> bia_data_model.BioSample:
    biosample = bia_data_model.BioSample.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Template BioSample",
            "organism_classification": [
                template_taxon.model_dump(),
            ],
            "biological_entity_description": "Test biological entity description",
            "experimental_variable_description": [
                "Description of experimental variable",
            ],
            "extrinsic_variable_description": [
                "Description of external treatment",
            ],
            "intrinsic_variable_description": [
                "Description of internal treatment",
            ],
            "version": 1,
            "model": {
                "type_name": "BioSample", 
                "version": 1
            }
        }
    )
    return biosample


def get_template_specimen() -> bia_data_model.Specimen:
    specimen = bia_data_model.Specimen.model_validate(
        {
            "uuid": uuid4(),
            "imaging_preparation_protocol_uuid": [
                get_template_specimen_imaging_preparation_protocol().uuid,
            ],
            "sample_of_uuid": [
                get_template_biosample().uuid,
            ],
            "growth_protocol_uuid": [
                get_template_specimen_growth_protocol().uuid,
            ],
            "version": 1,
            "model": {
                "type_name": "Specimen", 
                "version": 1
            }
        }
    )
    return specimen


def get_template_annotation_method() -> bia_data_model.AnnotationMethod:
    annotation_method = bia_data_model.AnnotationMethod.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Template annotation method",
            "protocol_description": "Template annotation method description",
            "annotation_criteria": "Template annotation criteria",
            "annotation_coverage": "Template annotation coverage",
            "method_type": semantic_models.AnnotationType.class_labels,
            "version": 1,
            "model": {
                "type_name": "AnnotationMethod", 
                "version": 1
            }
        }
    )
    return annotation_method


def get_template_experimentally_captured_image() -> (
    bia_data_model.ExperimentallyCapturedImage
):
    return bia_data_model.ExperimentallyCapturedImage.model_validate(
        {
            "uuid": uuid4(),
            "acquisition_process_uuid": [get_template_image_acquisition().uuid],
            "submission_dataset_uuid": get_template_experimental_imaging_dataset().uuid,
            "subject_uuid": get_template_specimen().uuid,
            "attribute": {},
            "version": 1,
            "model": {
                "type_name": "ExperimentallyCapturedImage", 
                "version": 1
            }
        }
    )


def get_template_derived_image() -> bia_data_model.DerivedImage:
    derived_image = bia_data_model.DerivedImage.model_validate(
        {
            "uuid": uuid4(),
            "source_image_uuid": [
                get_template_image_representation().uuid,
            ],
            "submission_dataset_uuid": get_template_image_annotation_dataset().uuid,
            "creation_process_uuid": [get_template_annotation_method().uuid],
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "attribute": {},
            "version": 1,
            "model": {
                "type_name": "DerivedImage", 
                "version": 1
            }
        }
    )
    return derived_image



def get_template_image_annotation_dataset() -> bia_data_model.ImageAnnotationDataset:
    image_annotation_dataset = bia_data_model.ImageAnnotationDataset.model_validate(
        {
            "uuid": uuid4(),
            "submitted_in_study_uuid": get_template_study().uuid,
            "title_id": "Template image annotation dataset",
            "example_image_uri": ["https://dummy.url.org"],
            "version": 1,
            "model": {
                "type_name": "ImageAnnotationDataset", 
                "version": 1
            },
            "attribute": {},
        }
    )
    return image_annotation_dataset


def get_template_image_acquisition() -> bia_data_model.ImageAcquisition:
    image_acquisition = bia_data_model.ImageAcquisition.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Template image acquisition",
            "protocol_description": "Template method description",
            "imaging_instrument_description": "Template imaging instrument",
            "imaging_method_name": "Template imaging method name",
            "fbbi_id": [
                "Test FBBI ID",
            ],
            "version": 1,
            "model": {
                "type_name": "ImageAcquisition", 
                "version": 1
            }
        }
    )
    return image_acquisition


def get_template_image_analysis_method() -> semantic_models.ImageAnalysisMethod:
    return semantic_models.ImageAnalysisMethod.model_validate(
        {
            "protocol_description": "Template Analysis method",
            "features_analysed": "Template features analysed",
        }
    )


def get_template_image_correlation_method() -> semantic_models.ImageCorrelationMethod:
    return semantic_models.ImageCorrelationMethod.model_validate(
        {
            "protocol_description": "Template Analysis method",
            "fiducials_used": "Template fiducials used",
            "transformation_matrix": "Template transformation matrix",
        }
    )


def get_template_experimental_imaging_dataset() -> (
    bia_data_model.ExperimentalImagingDataset
):
    experimental_imaging_dataset = (
        bia_data_model.ExperimentalImagingDataset.model_validate(
            {
                "uuid": uuid4(),
                "submitted_in_study_uuid": get_template_study().uuid,
                "title_id": "Template experimental image dataset",
                "analysis_method": [
                    get_template_image_analysis_method().model_dump(),
                ],
                "correlation_method": [
                    get_template_image_correlation_method().model_dump(),
                ],
                "example_image_uri": ["https://dummy.url.org"],
                "version": 1,
                "model": {"type_name": "ExperimentalImagingDataset", "version": 1},
                "attribute": {}
            }
        )
    )
    return experimental_imaging_dataset


def get_template_annotation_file_reference() -> bia_data_model.AnnotationFileReference:
    return bia_data_model.AnnotationFileReference.model_validate(
        {
            "uuid": uuid4(),
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "attribute": {},
            "submission_dataset_uuid": get_template_image_annotation_dataset().uuid,
            "source_image_uuid": [
                get_template_image_representation().uuid,
            ],
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "creation_process_uuid": [get_template_annotation_method().uuid],
            "version": 1,
            "model": {"type_name": "AnnotationFileReference", "version": 1},
        }
    )


def get_template_file_reference() -> bia_data_model.FileReference:
    file_reference = bia_data_model.FileReference.model_validate(
        {
            "uuid": uuid4(),
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "attribute": {},
            "submission_dataset_uuid": get_template_experimental_imaging_dataset().uuid,
            "version": 1,
            "model": {"type_name": "FileReference", "version": 1},
        }
    )
    return file_reference



def get_template_image_representation() -> bia_data_model.ImageRepresentation:
    return bia_data_model.ImageRepresentation.model_validate(
        {
            "uuid": uuid4(),
            "representation_of_uuid": get_template_experimentally_captured_image().uuid,
            "original_file_reference_uuid": [
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
            "version": 1,
            "model": {"type_name": "ImageRepresentation", "version": 1},
        }
    )


def get_template_affiliation() -> semantic_models.Affiliation:
    affiliation = semantic_models.Affiliation.model_validate(
        {
            "display_name": "Template Affiliation Organisation",
            "rorid": "None",
            "address": "None",
            "website": "https://www.none.com"
        }
    )
    return affiliation


def get_template_contributor() -> semantic_models.Contributor:
    contributor = semantic_models.Contributor.model_validate(
        {
            "display_name": "Contributor1",
            "contact_email": "contributor1@org1.ac.uk",
            "role": "contributing author",
            "affiliation": [
                get_template_affiliation(),
            ],
            "rorid": "None",
            "address": "None",
            "website": "https://www.none.com",
            "orcid": "None"
        }
    )
    return contributor


def get_template_study() -> bia_data_model.Study:
    contributor = get_template_contributor()
    study = bia_data_model.Study.model_validate(
        {
            "uuid": uuid4(),
            "accession_id": "S-BIADTEST",
            "licence": semantic_models.LicenceType.CC0,
            "attribute": {},
            "related_publication": [],
            "author": [
                contributor.model_dump(),
            ],
            "title": "Test publication",
            "release_date": "2024-06-23",
            "keyword": [
                "Template keyword1",
                "Template keyword2",
            ],
            "description": "Template description",
            "version": 1,
            "model": {"type_name": "Study", "version": 1},
        },
    )
    return study
