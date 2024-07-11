"""Utility functions to create models

    This module attempts to create models starting from the outer nodes (leaves) of the 
    model dependency graph

"""

from pathlib import Path
import sys

base_path = Path(__file__).parent
sys.path.append(f"{base_path.parent / 'src'}")
sys.path.append(f"{base_path.parent / 'src' / 'bia_models'}")
from bia_models import bia_data_model, semantic_models
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


def get_template_specimen_preparation_protocol() -> (
    bia_data_model.SpecimenPrepartionProtocol
):
    specimen_preparation_protocol = (
        bia_data_model.SpecimenPrepartionProtocol.model_validate(
            {
                "uuid": uuid4(),
                "title_id": "Test specimen preparation protocol",
                "protocol_description": "Test description",
                "signal_channel_information": [
                    get_template_signal_channel_information()
                ],
            }
        )
    )
    return specimen_preparation_protocol


def get_template_specimen_growth_protocol() -> (
    bia_data_model.SpecimenGrowthProtocol
):
    specimen_growth_protocol = bia_data_model.SpecimenGrowthProtocol.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Test specimen preparation protocol",
            "protocol_description": "Test description",
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
            "description": "Test biosample description",
            "experimental_variable_description": [
                "Description of experimental variable",
            ],
            "extrinsic_variable_description": [
                "Description of external treatment",
            ],
            "intrinsic_variable_description": [
                "Description of internal treatment",
            ],
        }
    )
    return biosample


# Depends on:
#   bia_data_model.BioSample
#   bia_data_model.SpecimenPreparationProtocol
def get_template_specimen() -> bia_data_model.Specimen:
    specimen = bia_data_model.Specimen.model_validate(
        {
            "imaging_preparation_protocol": [
                get_template_specimen_preparation_protocol().uuid,
            ],
            "sample_of": [
                get_template_biosample().uuid,
            ],
            "growth_protocol": [
                get_template_specimen_growth_protocol().uuid,
            ],
        }
    )
    return specimen


# Depends on ExperimentalImagingDataset
def get_template_annotation_method() -> bia_data_model.AnnotationMethod:
    annotation_method = bia_data_model.AnnotationMethod.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Template annotation method",
            "source_dataset": [],  # ExperimentalImagingDataset.uuid or url
            "protocol_description": "Template annotation method description",
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
            "creation_process": [get_template_annotation_method().uuid],
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
#   bia_data_model.AnnotationMethod
def get_template_image_annotation_dataset() -> bia_data_model.ImageAnnotationDataset:
    image_annotation_dataset = bia_data_model.ImageAnnotationDataset.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Template image annotation dataset",
            "annotation_method": [get_template_annotation_method().uuid],
            "file_reference_count": 0,
            "image_count": 0,
            "example_image_uri": ["https://dummy.url.org"],
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
            "parameters_description": "Template parameters description",
            "fbbi_id": [
                "Test FBBI ID",
            ],
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


# Depends on:
#   bia_data_model.SpecimenPreparationProtocol
#   bia_data_model.ImageAcquisition
#   bia_data_model.BioSample
#   bia_data_model.SpecimenGrowthProtocol
def get_template_experimental_imaging_dataset() -> (
    bia_data_model.ExperimentalImagingDataset
):
    experimental_imaging_dataset = bia_data_model.ExperimentalImagingDataset.model_validate(
        {
            "uuid": uuid4(),
            "title_id": "Template experimental image dataset",
            "specimen_imaging_preparation_protocol": [
                get_template_specimen_preparation_protocol().uuid,
            ],
            "acquisition_process": [
                get_template_image_acquisition().uuid,
            ],
            "biological_entity": [
                get_template_biosample().uuid,
            ],
            "specimen_growth_protocol": [
                get_template_specimen_growth_protocol().uuid,
            ],
            "analysis_method": [
                get_template_image_analysis_method().model_dump(),
            ],
            "correlation_method": [
                get_template_image_correlation_method().model_dump(),
            ],
            "file_reference_count": 0,
            "image_count": 0,
            "example_image_uri": ["https://dummy.url.org"],
        }
    )
    return experimental_imaging_dataset


# Depends on:
#   bia_data_model.ImageAnnotationDataset
#   bia_data_model.ExperimentalImagingDataset (circular)
def get_template_annotation_file_reference() -> bia_data_model.AnnotationFileReference:
    return bia_data_model.AnnotationFileReference.model_validate(
        {
            "uuid": uuid4(),
            "file_path": "Dummy file path",
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
            "creation_process": [get_template_annotation_method().uuid],
        }
    )


# Depends on:
#   bia_data_model.ImageAnnotationDataset
#   or
#   bia_data_model.ExperimentalImagingDataset
#   the latter is tested here.
def get_template_file_reference() -> bia_data_model.FileReference:
    file_reference = bia_data_model.FileReference.model_validate(
        {
            "uuid": uuid4(),
            "file_path": "Dummy file path",
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


def get_template_affiliation() -> semantic_models.Affiliation:
    affiliation = semantic_models.Affiliation.model_validate(
        {
            "display_name": "Template Affiliation Organisation",
            "rorid": "None",
            "address": "None",
            "website": "https://www.none.com",
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
            "orcid": "None",
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
            "experimental_imaging_component": [
                uuid4(),
            ],
            "annotation_component": [
                uuid4(),
            ],
            "description": "Template description",
        }
    )
    return study
