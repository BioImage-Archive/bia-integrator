from bia_shared_datamodels import uuid_creation
from copy import deepcopy
from bia_shared_datamodels import bia_data_model
from bia_test_data.mock_objects import mock_dataset
from .mock_object_constants import study_uuid

# Importing mock image and mock_specimen to use uuids generated there.
# Care is needed if importing this module to others to avoid circular
# imports
from . import mock_image, mock_specimen

basic_creation_process_dict = {
    "version": 0,
    "object_creator": "bia_ingest",
}


def get_creation_process_with_one_file_reference() -> bia_data_model.CreationProcess:
    creation_process_dict = deepcopy(basic_creation_process_dict)

    output_image_uuid = mock_image.get_image_with_one_file_reference().uuid
    creation_process_dict["uuid"] = uuid_creation.create_creation_process_uuid(
        study_uuid,
        output_image_uuid,
    )

    specimen = mock_specimen.get_specimen_for_image_with_one_file_reference()
    creation_process_dict["subject_specimen_uuid"] = specimen.uuid

    dataset = mock_dataset.get_dataset()[1]
    attribute_names = (
        (
            "image_acquisition_protocol_uuid",
            "image_acquisition_protocol_uuid",
        ),
    )
    for attribute_name, mapped_name in attribute_names:
        creation_process_dict[mapped_name] = next(
            (
                attribute.value[attribute_name]
                for attribute in dataset.additional_metadata
                if attribute.name == attribute_name
            ),
            [],
        )

    "additional_metadata": [
      {
        "provenance": "bia_ingest",
        "name": "uuid_unique_input",
        "value": {
          "uuid_unique_input": output_image_uuid,
        }
      }
    ],
    # TODO: Do we want tests to include a test protocol?
    # TODO: Do we want tests to include a test annotation method?

    return bia_data_model.CreationProcess.model_validate(creation_process_dict)
