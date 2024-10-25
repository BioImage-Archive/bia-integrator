"""
Functions to create example dictionaries that satisfy various degrees of completeness of BIA models
"""

from bia_shared_datamodels import semantic_models
from uuid import uuid4
from enum import Enum
import datetime
from pydantic_core import Url


class Completeness(str, Enum):
    COMPLETE = "COMPLETE"
    MINIMAL = "MINIMAL"


#######################################################################################################
# Subgraph 1: Studies and links to external information (publications, grants etc)
#######################################################################################################


def get_study_dict(completeness=Completeness.COMPLETE) -> dict:
    study_dict = {
        "uuid": uuid4(),
        "accession_id": "S-BIADTEST",
        "licence": semantic_models.LicenceType.CC0,
        "author": [get_contributor_dict(Completeness.MINIMAL)],
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
            "model": {"type_name": "Study", "version": 2},
            "attribute": [get_attribute_dict()],
        }

    return study_dict


#######################################################################################################
# Subgraph 2: Contributors & their affiliations
#######################################################################################################


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


#######################################################################################################
# Subgraph 3: Dataset, File References
#######################################################################################################


def get_dataset_dict(
    completeness=Completeness.COMPLETE,
) -> dict:
    dataset = {
        "uuid": uuid4(),
        "submitted_in_study_uuid": get_study_dict()["uuid"],
        "title_id": "Template experimental image dataset",
        "example_image_uri": [],
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        dataset |= {
            "description": "Template description",
            "analysis_method": [
                get_image_analysis_method_dict(),
            ],
            "correlation_method": [
                get_image_correlation_method_dict(),
            ],
            "example_image_uri": ["https://dummy.url.org"],
            "model": {"type_name": "Dataset", "version": 1},
            "attribute": [get_attribute_dict()],
        }
    return dataset


def get_file_reference_dict(completeness=Completeness.COMPLETE) -> dict:
    file_reference = {
        "uuid": uuid4(),
        "file_path": "Dummy file path",
        "format": "Dummy format",
        "size_in_bytes": 10,
        "uri": "https://dummy.uri.co",
        "submission_dataset_uuid": get_dataset_dict()["uuid"],
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        file_reference |= {
            "model": {"type_name": "FileReference", "version": 2},
            "attribute": [get_attribute_dict()],
        }
    return file_reference


#######################################################################################################
# Subgraph 4: Images & representations
#######################################################################################################


def get_image_dict(completeness=Completeness.COMPLETE) -> dict:
    image = {
        "uuid": uuid4(),
        "creation_process_uuid": get_creation_process_dict()["uuid"],
        "submission_dataset_uuid": get_dataset_dict()["uuid"],
        "original_file_reference_uuid": [],
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        image |= {
            "model": {"type_name": "Image", "version": 1},
            "attribute": [get_attribute_dict()],
            "original_file_reference_uuid": [
                get_file_reference_dict()["uuid"],
            ],
        }
    return image


def get_image_representation_dict(completeness=Completeness.COMPLETE) -> dict:
    image_representation = {
        "uuid": uuid4(),
        "representation_of_uuid": get_image_dict()["uuid"],
        "use_type": "UPLOADED_BY_SUBMITTER",
        "image_format": "Template image format",
        "total_size_in_bytes": 0,
        "file_uri": [],
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        image_representation |= {
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
            "model": {"type_name": "ImageRepresentation", "version": 2},
            "attribute": [get_attribute_dict()],
        }
    return image_representation


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


def get_annotation_data_dict(completeness=Completeness.COMPLETE) -> dict:
    annotation_data = {
        "uuid": uuid4(),
        "creation_process_uuid": get_creation_process_dict()["uuid"],
        "submission_dataset_uuid": get_dataset_dict()["uuid"],
        "original_file_reference_uuid": [],
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        annotation_data |= {
            "model": {"type_name": "AnnotationData", "version": 1},
            "attribute": [get_attribute_dict()],
            "original_file_reference_uuid": [
                get_file_reference_dict()["uuid"],
            ],
        }
    return annotation_data


#######################################################################################################
# Subgraph 5: Process & Protocols
#######################################################################################################


def get_creation_process_dict(completeness=Completeness.COMPLETE) -> dict:
    process = {
        "uuid": uuid4(),
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        process |= {
            "model": {"type_name": "CreationProcess", "version": 1},
            "subject_specimen_uuid": get_specimen_dict()["uuid"],
            "image_acquisition_protocol_uuid": [
                get_image_acquisition_protocol_dict()["uuid"]
            ],
            "input_image_uuid": [
                uuid4()  # Can't call get_image_dict() otherwise we loop endlessly
            ],
            "protocol_uuid": [get_protocol_dict()["uuid"]],
            "annotation_method_uuid": [get_annotation_method_dict()["uuid"]],
        }

    return process


def get_protocol_dict(completeness=Completeness.COMPLETE) -> dict:
    protocol = {
        "uuid": uuid4(),
        "protocol_description": "Template method description",
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        protocol |= {
            "model": {"type_name": "Protocol", "version": 1},
        }

    return protocol


def get_image_acquisition_protocol_dict(completeness=Completeness.COMPLETE) -> dict:
    image_acquisition_protocol = {
        "uuid": uuid4(),
        "title_id": "Template image acquisition",
        "protocol_description": "Template method description",
        "imaging_instrument_description": "Template imaging instrument",
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        image_acquisition_protocol |= {
            "fbbi_id": [
                "Test FBBI ID",
            ],
            "imaging_method_name": [
                "Template imaging method name",
            ],
            "model": {"type_name": "ImageAcquisitionProtocol", "version": 1},
        }
    return image_acquisition_protocol


def get_annotation_method_dict(completeness=Completeness.COMPLETE) -> dict:
    annotation_method = {
        "uuid": uuid4(),
        "title_id": "Template annotation method",
        "protocol_description": "Template annotation method description",
        "method_type": [],
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        annotation_method |= {
            "annotation_criteria": "Template annotation criteria",
            "annotation_coverage": "Template annotation coverage",
            "transformation_description": "Template transformation description",
            "spatial_information": "Template spatial information",
            "method_type": [semantic_models.AnnotationMethodType.class_labels],
            "annotation_source_indicator": semantic_models.AnnotationSourceIndicator.metadata_file,
            "model": {"type_name": "AnnotationMethod", "version": 2},
        }
    return annotation_method


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


#######################################################################################################
# Subgraph 6: Specimen, Biosample etc
#######################################################################################################


def get_specimen_dict(completeness=Completeness.COMPLETE) -> dict:
    specimen = {
        "uuid": uuid4(),
        "imaging_preparation_protocol_uuid": [
            get_specimen_imaging_preparation_protocol_dict()["uuid"],
        ],
        "sample_of_uuid": [
            get_biosample_dict()["uuid"],
        ],
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        specimen |= {
            "model": {"type_name": "Specimen", "version": 1},
        }
    return specimen


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


def get_signal_channel_information_dict(completeness=Completeness.COMPLETE) -> dict:
    signal_channel_information = {}
    if completeness == Completeness.COMPLETE:
        signal_channel_information |= {
            "signal_contrast_mechanism_description": "Test description",
            "channel_content_description": "Test description",
            "channel_biological_entity": "Test Entity",
        }
    return signal_channel_information


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
            "growth_protocol_uuid": get_protocol_dict()["uuid"],
            "model": {"type_name": "BioSample", "version": 2},
        }
    return biosample


def get_taxon_dict(completeness=Completeness.COMPLETE) -> dict:
    taxon = {}
    if completeness == Completeness.COMPLETE:
        taxon |= {
            "common_name": "Test Common Name",
            "scientific_name": "Test Scientific Name",
            "ncbi_id": "Test_NCBI_ID",
        }
    return taxon


#######################################################################################################
# Other
#######################################################################################################


def get_attribute_dict(completeness=Completeness.COMPLETE) -> dict:
    attribute = {
        "provenance": semantic_models.AttributeProvenance.submittor,
        "name": "file_list_columns",
        "value": {},
    }
    return attribute
