"""
Utility functions to create models

This module attempts to create models starting from the outer nodes (leaves) of the model dependency graph
"""

from pathlib import Path

from bia_shared_datamodels import semantic_models
from uuid import uuid4
from enum import Enum
import datetime
from pydantic_core import Url


class Completeness(str, Enum):
    COMPLETE = "COMPLETE"
    MINIMAL = "MINIMAL"


def get_taxon_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        taxon = {}
    elif completeness == Completeness.COMPLETE:
        taxon = {
            "common_name": "Test Common Name",
            "scientific_name": "Test Scientific Name",
            "ncbi_id": "Test_NCBI_ID",
        }
    return taxon


def get_channel_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        channel = {
            "colormap_start": 0.0,
            "colormap_end": 1.0,
        }
    elif completeness == Completeness.COMPLETE:
        channel = {
            "colormap_start": 0.0,
            "colormap_end": 1.0,
            "scale_factor": 1.0,
            "label": "Template label",
        }
    return channel


def get_rendered_view_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        rendered_view = {}
    elif completeness == Completeness.COMPLETE:
        rendered_view = {
            "z": "Template z position",
            "t": "Template t position",
            "channel_information": [
                get_channel_dict(Completeness.COMPLETE),
            ],
        }
    return rendered_view


def get_signal_channel_information_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        signal_channel_information = {}
    elif completeness == Completeness.COMPLETE:
        signal_channel_information = {
            "signal_contrast_mechanism_description": "Test description",
            "channel_content_description": "Test description",
            "channel_biological_entity": "Test Entity",
        }
    return signal_channel_information


def get_specimen_imaging_preparation_protocol_dict(
    completeness=Completeness.COMPLETE,
) -> dict:
    if completeness == Completeness.MINIMAL:
        specimen_imaging_preparation_protocol = {
            "uuid": uuid4(),
            "title_id": "Test specimen preparation protocol",
            "protocol_description": "Test description",
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        specimen_imaging_preparation_protocol = {
            "uuid": uuid4(),
            "title_id": "Test specimen preparation protocol",
            "protocol_description": "Test description",
            "signal_channel_information": [
                get_signal_channel_information_dict(Completeness.COMPLETE)
            ],
            "version": 1,
            "model": {
                "type_name": "SpecimenImagingPrepartionProtocol",
                "version": 1,
            },
        }
    return specimen_imaging_preparation_protocol


def get_specimen_growth_protocol_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        specimen_growth_protocol = {
            "uuid": uuid4(),
            "title_id": "Test specimen preparation protocol",
            "protocol_description": "Test description",
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        specimen_growth_protocol = {
            "uuid": uuid4(),
            "title_id": "Test specimen preparation protocol",
            "protocol_description": "Test description",
            "version": 1,
            "model": {"type_name": "SpecimenGrowthProtocol", "version": 1},
        }
    return specimen_growth_protocol


def get_biosample_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        biosample = {
            "uuid": uuid4(),
            "title_id": "Template BioSample",
            "biological_entity_description": "Test biological entity description",
            "version": 1,
            "organism_classification": [],
        }
    elif completeness == Completeness.COMPLETE:
        biosample = {
            "uuid": uuid4(),
            "title_id": "Template BioSample",
            "organism_classification": [
                get_taxon_dict(Completeness.COMPLETE),
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
            "model": {"type_name": "BioSample", "version": 1},
        }
    return biosample


def get_specimen_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        specimen = {
            "uuid": uuid4(),
            "imaging_preparation_protocol_uuid": [
                get_specimen_imaging_preparation_protocol_dict()["uuid"],
            ],
            "sample_of_uuid": [
                get_biosample_dict()["uuid"],
            ],
            "growth_protocol_uuid": [],
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        specimen = {
            "uuid": uuid4(),
            "imaging_preparation_protocol_uuid": [
                get_specimen_imaging_preparation_protocol_dict()["uuid"],
            ],
            "sample_of_uuid": [
                get_biosample_dict()["uuid"],
            ],
            "growth_protocol_uuid": [
                get_specimen_growth_protocol_dict()["uuid"],
            ],
            "version": 1,
            "model": {"type_name": "Specimen", "version": 1},
        }
    return specimen


def get_annotation_method_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        annotation_method = {
            "uuid": uuid4(),
            "title_id": "Template annotation method",
            "protocol_description": "Template annotation method description",
            "method_type": semantic_models.AnnotationType.class_labels,
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        annotation_method = {
            "uuid": uuid4(),
            "title_id": "Template annotation method",
            "protocol_description": "Template annotation method description",
            "annotation_criteria": "Template annotation criteria",
            "annotation_coverage": "Template annotation coverage",
            "method_type": semantic_models.AnnotationType.class_labels,
            "version": 1,
            "model": {"type_name": "AnnotationMethod", "version": 1},
        }
    return annotation_method


def get_experimentally_captured_image_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        experimentally_captured_image = {
            "uuid": uuid4(),
            "acquisition_process_uuid": [],
            "subject_uuid": get_specimen_dict()["uuid"],
            "submission_dataset_uuid": get_experimental_imaging_dataset_dict()["uuid"],
            "version": 1,
            "attribute": {},
        }
    elif completeness == Completeness.COMPLETE:
        experimentally_captured_image = {
            "uuid": uuid4(),
            "acquisition_process_uuid": [get_image_acquisition_dict()["uuid"]],
            "submission_dataset_uuid": get_experimental_imaging_dataset_dict()["uuid"],
            "subject_uuid": get_specimen_dict()["uuid"],
            "attribute": {},
            "version": 1,
            "model": {"type_name": "ExperimentallyCapturedImage", "version": 1},
        }
    return experimentally_captured_image


def get_derived_image_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        derived_image = {
            "uuid": uuid4(),
            "source_image_uuid": [],
            "submission_dataset_uuid": get_image_annotation_dataset_dict()["uuid"],
            "creation_process_uuid": [],
            "attribute": {},
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        derived_image = {
            "uuid": uuid4(),
            "source_image_uuid": [
                get_image_representation_dict()["uuid"],
            ],
            "submission_dataset_uuid": get_image_annotation_dataset_dict()["uuid"],
            "creation_process_uuid": [get_annotation_method_dict()["uuid"]],
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "attribute": {},
            "version": 1,
            "model": {"type_name": "DerivedImage", "version": 1},
        }
    return derived_image


def get_image_annotation_dataset_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        image_annotation_dataset = {
            "uuid": uuid4(),
            "submitted_in_study_uuid": get_study_dict()["uuid"],
            "title_id": "Template image annotation dataset",
            "example_image_uri": [],
            "version": 1,
            "attribute": {},
        }
    elif completeness == Completeness.COMPLETE:
        image_annotation_dataset = {
            "uuid": uuid4(),
            "submitted_in_study_uuid": get_study_dict()["uuid"],
            "title_id": "Template image annotation dataset",
            "example_image_uri": ["https://dummy.url.org"],
            "description": "Template description",
            "version": 1,
            "model": {"type_name": "ImageAnnotationDataset", "version": 1},
            "attribute": {},
        }
    return image_annotation_dataset


def get_image_acquisition_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        image_acquisition = {
            "uuid": uuid4(),
            "title_id": "Template image acquisition",
            "protocol_description": "Template method description",
            "imaging_instrument_description": "Template imaging instrument",
            "imaging_method_name": "Template imaging method name",
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        image_acquisition = {
            "uuid": uuid4(),
            "title_id": "Template image acquisition",
            "protocol_description": "Template method description",
            "imaging_instrument_description": "Template imaging instrument",
            "imaging_method_name": "Template imaging method name",
            "fbbi_id": [
                "Test FBBI ID",
            ],
            "version": 1,
            "model": {"type_name": "ImageAcquisition", "version": 1},
        }
    return image_acquisition


def get_image_analysis_method_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        image_analysis_method = {
            "protocol_description": "Template Analysis method",
            "features_analysed": "Template features analysed",
        }
    elif completeness == Completeness.COMPLETE:
        image_analysis_method = {
            "protocol_description": "Template Analysis method",
            "features_analysed": "Template features analysed",
        }
    return image_analysis_method


def get_image_correlation_method_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        image_correlation_method = {
            "protocol_description": "Template Analysis method",
            "fiducials_used": "Template fiducials used",
            "transformation_matrix": "Template transformation matrix",
        }
    elif completeness == Completeness.COMPLETE:
        image_correlation_method = {
            "protocol_description": "Template Analysis method",
            "fiducials_used": "Template fiducials used",
            "transformation_matrix": "Template transformation matrix",
        }
    return image_correlation_method


def get_experimental_imaging_dataset_dict(
    completeness=Completeness.COMPLETE,
) -> dict:
    if completeness == Completeness.MINIMAL:
        experimental_imaging_dataset = {
            "uuid": uuid4(),
            "submitted_in_study_uuid": get_study_dict()["uuid"],
            "title_id": "Template experimental image dataset",
            "example_image_uri": [],
            "version": 1,
            "attribute": {},
        }
    elif completeness == Completeness.COMPLETE:
        experimental_imaging_dataset = {
            "uuid": uuid4(),
            "submitted_in_study_uuid": get_study_dict()["uuid"],
            "title_id": "Template experimental image dataset",
            "description": "Template description",
            "analysis_method": [
                get_image_analysis_method_dict(),
            ],
            "correlation_method": [
                get_image_correlation_method_dict(),
            ],
            "example_image_uri": ["https://dummy.url.org"],
            "version": 1,
            "model": {"type_name": "ExperimentalImagingDataset", "version": 1},
            "attribute": {},
        }
    return experimental_imaging_dataset


def get_annotation_file_reference_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        annotation_file_reference = {
            "uuid": uuid4(),
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "attribute": {},
            "source_image_uuid": [],
            "creation_process_uuid": [],
            "submission_dataset_uuid": get_image_annotation_dataset_dict()["uuid"],
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        annotation_file_reference = {
            "uuid": uuid4(),
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "attribute": {},
            "submission_dataset_uuid": get_image_annotation_dataset_dict()["uuid"],
            "source_image_uuid": [
                get_image_representation_dict()["uuid"],
            ],
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "creation_process_uuid": [get_annotation_method_dict()["uuid"]],
            "version": 1,
            "model": {"type_name": "AnnotationFileReference", "version": 1},
        }
    return annotation_file_reference


def get_file_reference_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        file_reference = {
            "uuid": uuid4(),
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "attribute": {},
            "submission_dataset_uuid": get_experimental_imaging_dataset_dict()["uuid"],
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        file_reference = {
            "uuid": uuid4(),
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "attribute": {},
            "submission_dataset_uuid": get_experimental_imaging_dataset_dict()["uuid"],
            "version": 1,
            "model": {"type_name": "FileReference", "version": 1},
        }
    return file_reference


def get_image_representation_dict(completeness=Completeness.COMPLETE) -> dict:
    if completeness == Completeness.MINIMAL:
        image_representation = {
            "uuid": uuid4(),
            "representation_of_uuid": get_experimentally_captured_image_dict()["uuid"],
            "original_file_reference_uuid": [],
            "image_format": "Template image format",
            "attribute": {},
            "total_size_in_bytes": 0,
            "file_uri": [],
            "version": 1,
        }
    elif completeness == Completeness.COMPLETE:
        image_representation = {
            "uuid": uuid4(),
            "representation_of_uuid": get_experimentally_captured_image_dict()["uuid"],
            "original_file_reference_uuid": [
                get_file_reference_dict()["uuid"],
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
                get_rendered_view_dict(),
            ],
            "attribute": {},
            "version": 1,
            "model": {"type_name": "ImageRepresentation", "version": 1},
        }
    return image_representation


def get_affiliation_dict(
    completeness=Completeness.COMPLETE,
) -> dict:

    if completeness == Completeness.MINIMAL:
        affiliation = {
            "display_name": "Template Affiliation Organisation",
        }
    elif completeness == Completeness.COMPLETE:
        affiliation = {
            "display_name": "Template Affiliation Organisation",
            "rorid": "None",
            "address": "None",
            "website": Url("https://www.none.com"),
        }
    return affiliation


def get_contributor_dict(
    completeness=Completeness.COMPLETE,
) -> dict:

    if completeness == Completeness.MINIMAL:
        contributor_dict = {"display_name": "Contributor1", "affiliation": []}
    elif completeness == Completeness.COMPLETE:
        contributor_dict = {
            "display_name": "Contributor1",
            "contact_email": "contributor1@org1.ac.uk",
            "role": "contributing author",
            "affiliation": [
                get_affiliation_dict(Completeness.COMPLETE),
            ],
            "rorid": "None",
            "address": "None",
            "website": Url("https://www.none.com"),
            "orcid": "None",
        }
    return contributor_dict


def get_study_dict(completeness=Completeness.COMPLETE) -> dict:

    if completeness == Completeness.MINIMAL:
        study_dict = {
            "uuid": uuid4(),
            "accession_id": "S-BIADTEST",
            "licence": semantic_models.LicenceType.CC0,
            "author": [get_contributor_dict(Completeness.MINIMAL)],
            "attribute": {},
            "title": "Test publication",
            "release_date": "2024-06-23",
            "version": 1,
            "description": "Template description",
        }

    elif completeness == Completeness.COMPLETE:
        study_dict = {
            "uuid": uuid4(),
            "accession_id": "S-BIADTEST",
            "licence": semantic_models.LicenceType.CC0,
            "attribute": {},
            "related_publication": [],
            "author": [get_contributor_dict(Completeness.COMPLETE)],
            "acknowledgement": "Template acknowledgement",
            "funding_statement": "Template funding statement",
            "grant": [],
            "title": "Test publication",
            "release_date": datetime.date(2024, 6, 23),
            "see_also": [],
            "keyword": [
                "Template keyword1",
                "Template keyword2",
            ],
            "description": "Template description",
            "version": 1,
            "model": {"type_name": "Study", "version": 1},
        }

    return study_dict
