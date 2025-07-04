from bia_shared_datamodels import uuid_creation
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_test_data.mock_objects import mock_dataset
from bia_test_data.mock_objects.mock_object_constants import study_uuid

# Importing mock image to use uuid generated there. Care is needed if
# importing this module to others to avoid circular imports
from . import mock_image

# We use the dataset of study component 2
dataset = mock_dataset.get_dataset()[1]


def get_specimen_for_image_with_one_file_reference() -> bia_data_model.Specimen:
    image = mock_image.get_image_with_one_file_reference()
    unique_string = f"{image.uuid}"

    specimen_dict = {
        "uuid": uuid_creation.create_specimen_uuid(study_uuid, unique_string),
        "version": 0,
        "object_creator": semantic_models.Provenance.bia_ingest,
        "additional_metadata": [
            {
                "provenance": semantic_models.Provenance.bia_ingest,
                "name": "uuid_unique_input",
                "value": {
                    "uuid_unique_input": unique_string,
                },
            },
        ],
    }

    attribute_names = (
        (
            "specimen_imaging_preparation_protocol_uuid",
            "imaging_preparation_protocol_uuid",
        ),
        (
            "bio_sample_uuid",
            "sample_of_uuid",
        ),
    )
    for attribute_name, mapped_name in attribute_names:
        specimen_dict[mapped_name] = next(
            (
                attribute.value[attribute_name]
                for attribute in dataset.additional_metadata
                if attribute.name == attribute_name
            ),
            [],
        )

    return bia_data_model.Specimen.model_validate(specimen_dict)
