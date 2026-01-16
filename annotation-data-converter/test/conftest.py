import os
import pytest
import json
import glob

from dotenv import dotenv_values
from pathlib import Path
from bia_test_data.data_to_api import add_objects_to_api, get_object_creation_client
from annotation_data_converter.settings import get_settings


def pytest_configure(config: pytest.Config):
    """s3 bucket name has no default, so it is set here for testing"""
    os.environ["s3_bucket_name"] = "testbucket"


@pytest.fixture(scope="session")
def private_client():
    settings = get_settings()
    settings.set_to_local_api()
    return get_object_creation_client(settings.local_bia_api_basepath)


@pytest.fixture(scope="session")
def tmp_bia_data_dir(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("bia_data_dir")
    os.environ["bia_data_dir"] = str(tmp_dir)
    return tmp_dir


@pytest.fixture(scope="session")
def data_in_api(private_client):

    input_file_dir = (
        Path(__file__).parent / "input_data" / "api_objects" / "**" / "*.json"
    )
    file_path_list = glob.glob(str(input_file_dir), recursive=True)

    object_list = []
    for path in file_path_list:
        if os.path.isfile(path):
            with open(path, "r") as object_file:
                json_dict = json.load(object_file)
                object_list.append(json_dict)

    add_objects_to_api(private_client, object_list)
