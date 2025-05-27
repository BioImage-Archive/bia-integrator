from typing import Dict
from copy import deepcopy
from bia_shared_datamodels import (
    bia_data_model,
    uuid_creation,
    semantic_models,
    attribute_models,
)
from bia_test_data.mock_objects import mock_file_reference
from bia_test_data.mock_objects.mock_object_constants import accession_id, study_uuid


file_uri_base = "https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data"
# We are using image im06.png from study component 2
file_reference = mock_file_reference.get_file_reference()[0]
image_uuid = uuid_creation.create_image_uuid(
    [
        file_reference.uuid,
    ]
)


def representation_dict_template() -> Dict:
    dict_template = {
        "image_format": "",
        "file_uri": [],
        "representation_of_uuid": image_uuid,
        "total_size_in_bytes": 0,  # overwrite by template user if necessary
        # "physical_size_x": 0,
        # "physical_size_y": 0,
        # "physical_size_z": 0,
        "size_x": None,  # overwrite by template user if necessary
        "size_y": None,  # overwrite by template user if necessary
        "size_z": None,  # overwrite by template user if necessary
        "size_c": None,  # overwrite by template user if necessary
        "size_t": None,  # overwrite by template user if necessary
        "version": 0,
        "object_creator": semantic_models.Provenance("bia_ingest"),
    }

    return deepcopy(dict_template)


def get_image_representation_of_uploaded_by_submitter(
    with_file_uri_set=True,
) -> bia_data_model.ImageRepresentation:
    representation_dict = representation_dict_template()
    unique_string = image_uuid
    representation_dict["image_format"] = ".png"
    if with_file_uri_set:
        representation_dict["file_uri"] = [
            file_reference.uri,
        ]
    representation_dict["total_size_in_bytes"] = file_reference.size_in_bytes
    representation_dict["uuid"] = uuid_creation.create_image_representation_uuid(
        study_uuid,
        unique_string,
    )
    model = bia_data_model.ImageRepresentation.model_validate(representation_dict)

    file_pattern_attribute_dict = {
        "name": "file_pattern",
        "provenance": semantic_models.AttributeProvenance.bia_conversion,
        "value": {
            "file_pattern": file_reference.file_path,
        },
    }
    uuid_unique_input_dict = {
        "provenance": semantic_models.Provenance("bia_ingest"),
        "name": "uuid_unique_input",
        "value": {
            "uuid_unique_input": unique_string,
        },
    }
    model.additional_metadata = [
        attribute_models.Attribute.model_validate(file_pattern_attribute_dict),
        attribute_models.DatasetAssociatedUUIDAttribute.model_validate(
            uuid_unique_input_dict
        ),
    ]

    return model


def get_image_representation_of_interactive_display(
    with_file_uri_set=True,
) -> bia_data_model.ImageRepresentation:
    representation_dict = representation_dict_template()
    representation_dict.update(
        {
            "image_format": ".ome.zarr",
        }
    )
    unique_string = '{"conversion_function": "bioformats2raw"}'
    # TODO: create actual image and get the size
    # representation_dict["total_size_in_bytes"] =
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        study_uuid,
        unique_string,
    )
    # File uri should be set after image conversion
    if with_file_uri_set:
        representation_dict["file_uri"] = [
            f"{file_uri_base}/{accession_id}/{image_uuid}/{image_representation_uuid}.png"
        ]

    representation_dict["uuid"] = image_representation_uuid

    uuid_unique_input_dict = {
        "provenance": semantic_models.Provenance("bia_ingest"),
        "name": "uuid_unique_input",
        "value": {
            "uuid_unique_input": unique_string,
        },
    }
    representation_dict["additional_metadata"] = [
        uuid_unique_input_dict,
    ]
    return bia_data_model.ImageRepresentation.model_validate(representation_dict)
