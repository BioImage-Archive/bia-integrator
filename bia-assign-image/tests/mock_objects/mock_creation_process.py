from bia_shared_datamodels import uuid_creation
from copy import deepcopy
from bia_shared_datamodels import bia_data_model
# Importing mock image and mock_specimen to use uuids generated there.
# Care is needed if importing this module to others to avoid circular
# imports
from . import mock_image, mock_specimen

basic_creation_process_dict = {
    "version": 0,
}

def get_creation_process_with_one_file_reference() -> bia_data_model.CreationProcess:
    creation_process_dict = deepcopy(basic_creation_process_dict)

    image_uuid = mock_image.get_image_with_one_file_reference().uuid
    creation_process_dict["uuid"] = uuid_creation.create_creation_process_uuid(image_uuid)

    specimen = mock_specimen.get_specimen_for_image_with_one_file_reference()
    creation_process_dict["subject_specimen_uuid"] = specimen.uuid

    return bia_data_model.CreationProcess.model_validate(creation_process_dict)