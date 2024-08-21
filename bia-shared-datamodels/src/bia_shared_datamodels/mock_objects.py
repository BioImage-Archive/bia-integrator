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
    taxon = {}
    if completeness == Completeness.COMPLETE:
        taxon |= {
            "common_name": "Test Common Name",
            "scientific_name": "Test Scientific Name",
            "ncbi_id": "Test_NCBI_ID",
        }
    return taxon


def get_channel_dict(completeness=Completeness.COMPLETE) -> dict:
    channel = {
        "colormap_start": 0.0,
        "colormap_end": 1.0,
    }
    if completeness == Completeness.COMPLETE:
        channel |= {
            "scale_factor": 1.0,
            "label": "Template label",
        }
    return channel


def get_rendered_view_dict(completeness=Completeness.COMPLETE) -> dict:
    rendered_view = {}
    if completeness == Completeness.COMPLETE:
        rendered_view |= {
            "z": "Template z position",
            "t": "Template t position",
            "channel_information": [
                get_channel_dict(Completeness.COMPLETE),
            ],
        }
    return rendered_view


def get_signal_channel_information_dict(completeness=Completeness.COMPLETE) -> dict:
    signal_channel_information = {}
    if completeness == Completeness.COMPLETE:
        signal_channel_information |= {
            "signal_contrast_mechanism_description": "Test description",
            "channel_content_description": "Test description",
            "channel_biological_entity": "Test Entity",
        }
    return signal_channel_information


def get_specimen_imaging_preparation_protocol_dict(
    completeness=Completeness.COMPLETE,
) -> dict:
    specimen_imaging_preparation_protocol = {
        "uuid": uuid4(),
        "title_id": "Test specimen preparation protocol",
        "protocol_description": "Test description",
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        specimen_imaging_preparation_protocol |= {
            "signal_channel_information": [
                get_signal_channel_information_dict(Completeness.COMPLETE)
            ],
            "model": {
                "type_name": "SpecimenImagingPreparationProtocol",
                "version": 1,
            },
        }
    return specimen_imaging_preparation_protocol


def get_specimen_growth_protocol_dict(completeness=Completeness.COMPLETE) -> dict:
    specimen_growth_protocol = {
        "uuid": uuid4(),
        "title_id": "Test specimen preparation protocol",
        "protocol_description": "Test description",
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        specimen_growth_protocol |= {
            "model": {"type_name": "SpecimenGrowthProtocol", "version": 1},
        }
    return specimen_growth_protocol


def get_biosample_dict(completeness=Completeness.COMPLETE) -> dict:
    biosample = {
        "uuid": uuid4(),
        "title_id": "Template BioSample",
        "biological_entity_description": "Test biological entity description",
        "version": 1,
        "organism_classification": [],
    }
    if completeness == Completeness.COMPLETE:
        biosample |= {
            "organism_classification": [
                get_taxon_dict(Completeness.COMPLETE),
            ],
            "experimental_variable_description": [
                "Description of experimental variable",
            ],
            "extrinsic_variable_description": [
                "Description of external treatment",
            ],
            "intrinsic_variable_description": [
                "Description of internal treatment",
            ],
            "model": {"type_name": "BioSample", "version": 1},
        }
    return biosample


def get_specimen_dict(completeness=Completeness.COMPLETE) -> dict:
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
    if completeness == Completeness.COMPLETE:
        specimen |= {
            "growth_protocol_uuid": [
                get_specimen_growth_protocol_dict()["uuid"],
            ],
            "model": {"type_name": "Specimen", "version": 1},
        }
    return specimen


def get_annotation_method_dict(completeness=Completeness.COMPLETE) -> dict:
    annotation_method = {
        "uuid": uuid4(),
        "title_id": "Template annotation method",
        "protocol_description": "Template annotation method description",
        "method_type": semantic_models.AnnotationType.class_labels,
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        annotation_method |= {
            "annotation_criteria": "Template annotation criteria",
            "annotation_coverage": "Template annotation coverage",
            "model": {"type_name": "AnnotationMethod", "version": 1},
        }
    return annotation_method


def get_experimentally_captured_image_dict(completeness=Completeness.COMPLETE) -> dict:
    experimentally_captured_image = {
        "uuid": uuid4(),
        "acquisition_process_uuid": [],
        "subject_uuid": get_specimen_dict()["uuid"],
        "submission_dataset_uuid": get_experimental_imaging_dataset_dict()["uuid"],
        "version": 1,
        "attribute": {},
    }
    if completeness == Completeness.COMPLETE:
        experimentally_captured_image |= {
            "acquisition_process_uuid": [get_image_acquisition_dict()["uuid"]],
            "model": {"type_name": "ExperimentallyCapturedImage", "version": 1},
        }
    return experimentally_captured_image


def get_derived_image_dict(completeness=Completeness.COMPLETE) -> dict:
    derived_image = {
        "uuid": uuid4(),
        "source_image_uuid": [],
        "submission_dataset_uuid": get_image_annotation_dataset_dict()["uuid"],
        "creation_process_uuid": [],
        "attribute": {},
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        derived_image |= {
            "source_image_uuid": [
                get_image_representation_dict()["uuid"],
            ],
            "creation_process_uuid": [get_annotation_method_dict()["uuid"]],
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "model": {"type_name": "DerivedImage", "version": 1},
        }
    return derived_image


def get_image_annotation_dataset_dict(completeness=Completeness.COMPLETE) -> dict:
    image_annotation_dataset = {
        "uuid": uuid4(),
        "submitted_in_study_uuid": get_study_dict()["uuid"],
        "title_id": "Template image annotation dataset",
        "example_image_uri": [],
        "version": 1,
        "attribute": {},
    }
    if completeness == Completeness.COMPLETE:
        image_annotation_dataset |= {
            "example_image_uri": ["https://dummy.url.org"],
            "description": "Template description",
            "model": {"type_name": "ImageAnnotationDataset", "version": 1},
        }
    return image_annotation_dataset


def get_image_acquisition_dict(completeness=Completeness.COMPLETE) -> dict:
    image_acquisition = {
        "uuid": uuid4(),
        "title_id": "Template image acquisition",
        "protocol_description": "Template method description",
        "imaging_instrument_description": "Template imaging instrument",
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        image_acquisition |= {
            "fbbi_id": [
                "Test FBBI ID",
            ],
            "imaging_method_name": [
                "Template imaging method name",
            ],
            "model": {"type_name": "ImageAcquisition", "version": 1},
        }
    return image_acquisition


def get_image_analysis_method_dict(completeness=Completeness.COMPLETE) -> dict:
    image_analysis_method = {
        "protocol_description": "Template Analysis method",
        "features_analysed": "Template features analysed",
    }
    if completeness == Completeness.COMPLETE:
        image_analysis_method |= {}
    return image_analysis_method


def get_image_correlation_method_dict(completeness=Completeness.COMPLETE) -> dict:
    image_correlation_method = {
        "protocol_description": "Template Analysis method",
        "fiducials_used": "Template fiducials used",
        "transformation_matrix": "Template transformation matrix",
    }
    if completeness == Completeness.COMPLETE:
        image_correlation_method |= {}
    return image_correlation_method


def get_experimental_imaging_dataset_dict(
    completeness=Completeness.COMPLETE,
) -> dict:
    experimental_imaging_dataset = {
        "uuid": uuid4(),
        "submitted_in_study_uuid": get_study_dict()["uuid"],
        "title_id": "Template experimental image dataset",
        "example_image_uri": [],
        "version": 1,
        "attribute": {},
    }
    if completeness == Completeness.COMPLETE:
        experimental_imaging_dataset |= {
            "description": "Template description",
            "analysis_method": [
                get_image_analysis_method_dict(),
            ],
            "correlation_method": [
                get_image_correlation_method_dict(),
            ],
            "example_image_uri": ["https://dummy.url.org"],
            "model": {"type_name": "ExperimentalImagingDataset", "version": 1},
        }
    return experimental_imaging_dataset


def get_annotation_file_reference_dict(completeness=Completeness.COMPLETE) -> dict:
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
    if completeness == Completeness.COMPLETE:
        annotation_file_reference |= {
            "source_image_uuid": [
                get_image_representation_dict()["uuid"],
            ],
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "creation_process_uuid": [get_annotation_method_dict()["uuid"]],
            "model": {"type_name": "AnnotationFileReference", "version": 1},
        }
    return annotation_file_reference


def get_file_reference_dict(completeness=Completeness.COMPLETE) -> dict:
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
    if completeness == Completeness.COMPLETE:
        file_reference |= {
            "model": {"type_name": "FileReference", "version": 1},
        }
    return file_reference


def get_image_representation_dict(completeness=Completeness.COMPLETE) -> dict:
    image_representation = {
        "uuid": uuid4(),
        "representation_of_uuid": get_experimentally_captured_image_dict()["uuid"],
        "image_format": "Template image format",
        "attribute": {},
        "total_size_in_bytes": 0,
        "file_uri": [],
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        image_representation |= {
            "original_file_reference_uuid": [
                get_file_reference_dict()["uuid"],
            ],
            "file_uri": [
                "https://dummy.uri.org",
            ],
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
            "model": {"type_name": "ImageRepresentation", "version": 1},
        }
    return image_representation


def get_affiliation_dict(
    completeness=Completeness.COMPLETE,
) -> dict:

    affiliation = {
        "display_name": "Template Affiliation Organisation",
    }
    if completeness == Completeness.COMPLETE:
        affiliation |= {
            "rorid": "None",
            "address": "None",
            "website": Url("https://www.none.com"),
        }
    return affiliation


def get_contributor_dict(
    completeness=Completeness.COMPLETE,
) -> dict:

    contributor_dict = {"display_name": "Contributor1", "affiliation": []}
    if completeness == Completeness.COMPLETE:
        contributor_dict |= {
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

    if completeness == Completeness.COMPLETE:
        study_dict |= {
            "release_date": datetime.date(2024, 6, 23),
            "author": [get_contributor_dict(Completeness.COMPLETE)],
            "related_publication": [],
            "acknowledgement": "Template acknowledgement",
            "funding_statement": "Template funding statement",
            "grant": [],
            "see_also": [],
            "keyword": [
                "Template keyword1",
                "Template keyword2",
            ],
            "model": {"type_name": "Study", "version": 1},
        }

    return study_dict
