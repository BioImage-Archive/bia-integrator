from typing import Dict
from copy import deepcopy
from bia_shared_datamodels import bia_data_model, uuid_creation, semantic_models
from bia_test_data.mock_objects import mock_file_reference
from bia_test_data.mock_objects.mock_object_constants import accession_id


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
        # "use_type": to be added by template user,
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
    }

    return deepcopy(dict_template)


def get_image_representation_of_uploaded_by_submitter(
    with_file_uri_set=True,
) -> bia_data_model.ImageRepresentation:
    representation_dict = representation_dict_template()
    representation_dict["use_type"] = (
        semantic_models.ImageRepresentationUseType.UPLOADED_BY_SUBMITTER
    )
    representation_dict["image_format"] = ".png"
    if with_file_uri_set:
        representation_dict["file_uri"] = [
            file_reference.uri,
        ]
    representation_dict["total_size_in_bytes"] = file_reference.size_in_bytes
    representation_dict["uuid"] = uuid_creation.create_image_representation_uuid(
        image_uuid,
        representation_dict["image_format"],
        # Note that using the Enum ImageRepresentation gives a different UUID than using its value
        representation_dict["use_type"].value,
    )
    model = bia_data_model.ImageRepresentation.model_validate(representation_dict)

    file_pattern_attribute_dict = {
        "name": "file_pattern",
        "provenance": semantic_models.AttributeProvenance.bia_conversion,
        "value": {
            "file_pattern": file_reference.file_path,
        },
    }
    model.attribute = [
        semantic_models.Attribute.model_validate(file_pattern_attribute_dict),
    ]

    return model


def get_image_representation_of_thumbnail(
    with_file_uri_set=True,
) -> bia_data_model.ImageRepresentation:
    representation_dict = representation_dict_template()
    representation_dict.update(
        {
            "use_type": semantic_models.ImageRepresentationUseType.THUMBNAIL,
            "image_format": ".png",
        }
    )
    # TODO: create actual image and get the size
    #       However, on initial creation of representation we would not
    #       normally know this - except if we already have the thumbnail
    # representation_dict["total_size_in_bytes"] =
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image_uuid,
        representation_dict["image_format"],
        representation_dict["use_type"].value,
    )
    # File uri should be set after image conversion
    if with_file_uri_set:
        representation_dict["file_uri"] = [
            f"{file_uri_base}/{accession_id}/{image_uuid}/{image_representation_uuid}.png"
        ]

    representation_dict.update(
        {
            "uuid": image_representation_uuid,
        }
    )
    return bia_data_model.ImageRepresentation.model_validate(representation_dict)


def get_image_representation_of_static_display(
    with_file_uri_set=True,
) -> bia_data_model.ImageRepresentation:
    representation_dict = representation_dict_template()
    representation_dict.update(
        {
            "use_type": semantic_models.ImageRepresentationUseType.STATIC_DISPLAY,
            "image_format": ".png",
        }
    )
    # TODO: create actual image and get the size
    # representation_dict["total_size_in_bytes"] =
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image_uuid,
        representation_dict["image_format"],
        representation_dict["use_type"].value,
    )
    # File uri should be set after image conversion
    if with_file_uri_set:
        representation_dict["file_uri"] = [
            f"{file_uri_base}/{accession_id}/{image_uuid}/{image_representation_uuid}.png"
        ]

    representation_dict.update(
        {
            "uuid": image_representation_uuid,
        }
    )
    return bia_data_model.ImageRepresentation.model_validate(representation_dict)


def get_image_representation_of_interactive_display(
    with_file_uri_set=True,
) -> bia_data_model.ImageRepresentation:
    representation_dict = representation_dict_template()
    representation_dict.update(
        {
            "use_type": semantic_models.ImageRepresentationUseType.INTERACTIVE_DISPLAY,
            "image_format": ".ome.zarr",
        }
    )
    # TODO: create actual image and get the size
    # representation_dict["total_size_in_bytes"] =
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image_uuid,
        representation_dict["image_format"],
        representation_dict["use_type"].value,
    )
    # File uri should be set after image conversion
    if with_file_uri_set:
        representation_dict["file_uri"] = [
            f"{file_uri_base}/{accession_id}/{image_uuid}/{image_representation_uuid}.png"
        ]

    representation_dict.update(
        {
            "uuid": image_representation_uuid,
        }
    )
    representation_dict["uuid"] = image_representation_uuid
    return bia_data_model.ImageRepresentation.model_validate(representation_dict)
