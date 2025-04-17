"""
Functions to create example dictionaries that satisfy various degrees of completeness of BIA models
"""

from bia_shared_datamodels import semantic_models, uuid_creation
from uuid import uuid4
from enum import Enum
import datetime
from pydantic import AnyUrl


class Completeness(str, Enum):
    COMPLETE = "COMPLETE"
    MINIMAL = "MINIMAL"


#######################################################################################################
# Subgraph 1: Studies and links to external information (publications, grants etc)
#######################################################################################################


def get_study_dict(completeness=Completeness.COMPLETE) -> dict:
    accession_id = "S-BIADTEST"

    study_dict = {
        "uuid": uuid_creation.create_study_uuid(accession_id),
        "accession_id": accession_id,
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
            "website": AnyUrl("https://www.none.com/"),
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
            "website": AnyUrl("https://www.none.com/"),
        }
    return affiliation


#######################################################################################################
# Subgraph 3: Dataset, File References
#######################################################################################################


def get_dataset_dict(
    completeness=Completeness.COMPLETE,
) -> dict:
    title = "Template experimental image dataset"
    study_uuid = get_study_dict()["uuid"]

    dataset = {
        "uuid": uuid_creation.create_dataset_uuid(title, study_uuid),
        "submitted_in_study_uuid": study_uuid,
        "title": title,
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
    study_uuid = get_study_dict()["uuid"]
    file_path = "Dummy file path"

    file_reference = {
        "uuid": uuid_creation.create_file_reference_uuid(file_path, study_uuid),
        "file_path": file_path,
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
    # TODO: update UUID generation
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
    # TODO: update UUID generation
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
            "model": {"type_name": "ImageRepresentation", "version": 3},
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
            "attribute": [get_attribute_dict()],
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
            "attribute": [get_attribute_dict()],
        }
    return channel


def get_annotation_data_dict(completeness=Completeness.COMPLETE) -> dict:
    # TODO: update UUID generation
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
    # TODO: update UUID generation
    process = {
        "uuid": uuid4(),
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        process |= {
            "model": {"type_name": "CreationProcess", "version": 2},
            "subject_specimen_uuid": get_specimen_dict()["uuid"],
            "image_acquisition_protocol_uuid": [
                get_image_acquisition_protocol_dict()["uuid"]
            ],
            "input_image_uuid": [
                uuid4()  # Can't call get_image_dict() otherwise we loop endlessly
            ],
            "protocol_uuid": [get_protocol_dict()["uuid"]],
            "annotation_method_uuid": [get_annotation_method_dict()["uuid"]],
            "attribute": [get_attribute_dict()],
        }

    return process


def get_protocol_dict(completeness=Completeness.COMPLETE) -> dict:
    study_uuid = get_study_dict()["uuid"]
    title = "Template image acquisition"

    protocol = {
        "uuid": uuid_creation.create_protocol_uuid(title, study_uuid),
        "title": title,
        "protocol_description": "Template method description",
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        protocol |= {
            "model": {"type_name": "Protocol", "version": 2},
            "attribute": [get_attribute_dict()],
        }

    return protocol


def get_image_acquisition_protocol_dict(completeness=Completeness.COMPLETE) -> dict:
    study_uuid = get_study_dict()["uuid"]
    title = "Template image acquisition"

    image_acquisition_protocol = {
        "uuid": uuid_creation.create_image_acquisition_protocol_uuid(title, study_uuid),
        "title": title,
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
            "attribute": [get_attribute_dict()],
            "model": {"type_name": "ImageAcquisitionProtocol", "version": 2},
        }
    return image_acquisition_protocol


def get_annotation_method_dict(completeness=Completeness.COMPLETE) -> dict:
    study_uuid = get_study_dict()["uuid"]
    title = "Template annotation method"

    annotation_method = {
        "uuid": uuid_creation.create_annotation_method_uuid(title, study_uuid),
        "title": title,
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
            "attribute": [get_attribute_dict()],
            "model": {"type_name": "AnnotationMethod", "version": 3},
        }
    return annotation_method


def get_image_analysis_method_dict(completeness=Completeness.COMPLETE) -> dict:
    image_analysis_method = {
        "protocol_description": "Template Analysis method",
        "title": "Template analysis method title",
    }
    if completeness == Completeness.COMPLETE:
        image_analysis_method |= {
            "attribute": [get_attribute_dict()],
            "features_analysed": "Template features analysed",
        }
    return image_analysis_method


def get_image_correlation_method_dict(completeness=Completeness.COMPLETE) -> dict:
    image_correlation_method = {
        "protocol_description": "Template Analysis method",
        "title": "Template correlation method title",
    }
    if completeness == Completeness.COMPLETE:
        image_correlation_method |= {
            "attribute": [get_attribute_dict()],
            "fiducials_used": "Template fiducials used",
            "transformation_matrix": "Template transformation matrix",
        }
    return image_correlation_method


#######################################################################################################
# Subgraph 6: Specimen, Biosample etc
#######################################################################################################


def get_specimen_dict(completeness=Completeness.COMPLETE) -> dict:
    # TODO: update specimen uuid generation
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
            "model": {"type_name": "Specimen", "version": 2},
            "attribute": [get_attribute_dict()],
        }
    return specimen


def get_specimen_imaging_preparation_protocol_dict(
    completeness=Completeness.COMPLETE,
) -> dict:
    study_uuid = get_study_dict()["uuid"]
    title = "Test specimen preparation protocol"
    specimen_imaging_preparation_protocol = {
        "uuid": uuid_creation.create_specimen_imaging_preparation_protocol_uuid(
            title, study_uuid
        ),
        "title": title,
        "protocol_description": "Test description",
        "version": 1,
    }
    if completeness == Completeness.COMPLETE:
        specimen_imaging_preparation_protocol |= {
            "signal_channel_information": [
                get_signal_channel_information_dict(Completeness.COMPLETE)
            ],
            "attribute": [get_attribute_dict()],
            "model": {
                "type_name": "SpecimenImagingPreparationProtocol",
                "version": 2,
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
            "attribute": [get_attribute_dict()],
        }
    return signal_channel_information


def get_biosample_dict(completeness=Completeness.COMPLETE) -> dict:
    study_uuid = get_study_dict()["uuid"]
    title = "Template BioSample"
    biosample = {
        "uuid": uuid_creation.create_bio_sample_uuid(title, study_uuid),
        "title": title,
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
            "attribute": [get_attribute_dict()],
            "model": {"type_name": "BioSample", "version": 3},
        }
    return biosample


def get_taxon_dict(completeness=Completeness.COMPLETE) -> dict:
    taxon = {}
    if completeness == Completeness.COMPLETE:
        taxon |= {
            "common_name": "Test Common Name",
            "scientific_name": "Test Scientific Name",
            "ncbi_id": "Test_NCBI_ID",
            "attribute": [get_attribute_dict()],
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


def get_dataset_associated_uuid_attribute(completeness=Completeness.COMPLETE) -> dict:
    attribute = {
        "provenance": semantic_models.AttributeProvenance.bia_ingest,
        "name": "protocol_uuid",
        "value": {"protocol_uuid": [str(get_protocol_dict()["uuid"])]},
    }
    return attribute


def get_dataset_associatation_attribute(completeness=Completeness.COMPLETE) -> dict:
    attribute = {
        "provenance": semantic_models.AttributeProvenance.bia_ingest,
        "name": "associations",
        "value": {"associations": []},
    }
    if completeness == Completeness.COMPLETE:
        attribute |= {
            "value": {
                "associations": [
                    {
                        "image_analysis": "image_analysis_title",
                        "image_correlation": "image_correlation_title",
                        "biosample": "biosample_title",
                        "image_acquisition": "biosample_title",
                        "specimen": "specimen_title",
                    }
                ]
            }
        }
    return attribute
