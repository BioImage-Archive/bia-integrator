from dotenv import load_dotenv
from pathlib import Path
import pytest
from bia_test_data.test_api.test_api import TestAPI, create_objects
from bia_export.settings import Settings
from pathlib import Path
import json


def pytest_configure(config: pytest.Config):
    test_env = str(Path(__file__).parent / "test.env_export")
    load_dotenv(test_env, override=True)


@pytest.fixture(scope="session")
def docker_api():
    setttings = Settings()
    api = TestAPI()
    api.start()

    input_file_dir = Path(__file__).parent / "input_data"

    # Note order is *very* important due to uuid references needing to exist.
    file_path_list = [
        # Studies don't depend on anything
        input_file_dir
        / "study"
        / "S-BIADTEST"
        / "a2fdbd58-ee11-4cd9-bc6a-f3d3da7fff71.json",
        # Datasets only depend on studies
        input_file_dir
        / "dataset"
        / "S-BIADTEST"
        / "47a4ab60-c76d-4424-bfaa-c2a024de720c.json",
        input_file_dir
        / "dataset"
        / "S-BIADTEST"
        / "850a1ca3-9681-4a8a-b625-477936fcb954.json",
        input_file_dir
        / "dataset"
        / "S-BIADTEST"
        / "21999a9f-6f16-45d4-91c9-ed46cbfe015c.json",
        # File references only depend on Datasets
        input_file_dir
        / "file_reference"
        / "S-BIADTEST"
        / "4bb8c5a4-d39f-4d9e-a112-334e859a5c22.json",
        input_file_dir
        / "file_reference"
        / "S-BIADTEST"
        / "42cdf779-56c5-4a9e-9813-840f49071f79.json",
        input_file_dir
        / "file_reference"
        / "S-BIADTEST"
        / "ed89fa57-46a4-4ace-8d01-cc4504eb98e1.json",
        input_file_dir
        / "file_reference"
        / "S-BIADTEST"
        / "fe7b5598-d089-4624-bbd6-21e68a0fe506.json",
        # Biosample can require protocol. Specimen Requires Biosample & specimen_imaging_preparation_protocol
        input_file_dir
        / "protocol"
        / "S-BIADTEST"
        / "a2ce3950-3b28-40b3-a6a5-23c4f7864912.json",
        input_file_dir
        / "bio_sample"
        / "S-BIADTEST"
        / "64a67727-4e7c-469a-91c4-6219ae072e99.json",
        input_file_dir
        / "bio_sample"
        / "S-BIADTEST"
        / "6950718c-4917-47a1-a807-11b874e80a23.json",
        input_file_dir
        / "specimen_imaging_preparation_protocol"
        / "S-BIADTEST"
        / "7199d730-29f1-4ad8-b599-e9089cbb2d7b.json",
        input_file_dir
        / "image_acquisition_protocol"
        / "S-BIADTEST"
        / "c2e44a1b-a43c-476e-8ddf-8587f4c955b3.json",
        input_file_dir
        / "specimen"
        / "S-BIADTEST"
        / "dcc18482-fa1a-468f-878f-c00f9cd46376.json",
        input_file_dir
        / "annotation_method"
        / "S-BIADTEST"
        / "ef019f5d-d3e0-4122-89ae-1d1d07d2830f.json",
        # Creation processes can depend on images & images depend on creation processes, so this order is most important to get right.
        input_file_dir
        / "creation_process"
        / "S-BIADTEST"
        / "2447db96-dd23-44eb-ad47-1086c9be1cba.json",
        input_file_dir
        / "image"
        / "S-BIADTEST"
        / "e7322131-8e27-455d-b9fc-8add0719af70.json",
        input_file_dir
        / "creation_process"
        / "S-BIADTEST"
        / "8444ff28-e32b-4c6f-9677-d9ff597b0c29.json",
        input_file_dir
        / "image"
        / "S-BIADTEST"
        / "7966aa52-e3db-4ce3-801e-44c524b73ee3.json",
        # Image representations just depend on Images
        input_file_dir
        / "image_representation"
        / "S-BIADTEST"
        / "8bfef1ff-18ec-4de7-8a10-2c19d552c150.json",
        input_file_dir
        / "image_representation"
        / "S-BIADTEST"
        / "570a177d-de5d-4bee-bbd1-fd2dcbec9e2a.json",
        input_file_dir
        / "image_representation"
        / "S-BIADTEST"
        / "677d5571-8ca3-4478-9e9f-cfeb3b012703.json",
    ]

    object_list = []
    for file_path in file_path_list:
        with open(file_path, "r") as object_file:
            json_dict = json.load(object_file)
            try:
                json_dict["model"]["type_name"]
            except KeyError:
                continue
            object_list.append(json_dict)

    create_objects(setttings.api_base_url, object_list)

    yield api
    api.stop()
