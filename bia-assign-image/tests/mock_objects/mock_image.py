from uuid import uuid4
from copy import deepcopy
from bia_shared_datamodels import bia_data_model
from . import mock_creation_process

# Experiment with using bia_ingest mock objects
import sys
from pathlib import Path
# TODO: Fix this by moving bia-ingest.test.mock_objects to shared location
bia_ingest_mock_objects_path = str(Path(__file__).parent.parent.parent.parent / "bia-ingest")
sys.path.insert(0,bia_ingest_mock_objects_path)
from test.mock_objects import mock_dataset

basic_image_dict = {
    "version": 0,
    #TODO: Get UUID from a predefined test dataset
    "submission_dataset_uuid": uuid4(),
    #TODO: Get UUID from a predefined test file reference
    "original_file_reference_uuid": [],
}

def get_image_with_one_file_reference() -> bia_data_model.Image:
    image_dict = deepcopy(basic_image_dict)

    image_dict["uuid"] = uuid4()
    creation_process_uuid = mock_creation_process.get_creation_process_with_one_file_reference().uuid
    image_dict["creation_process_uuid"] = creation_process_uuid

    return bia_data_model.Image.model_validate(image_dict)