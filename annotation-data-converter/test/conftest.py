import os
import pytest
import json
import glob

from dotenv import dotenv_values
from pathlib import Path
from bia_test_data.data_to_api import add_objects_to_api, get_object_creation_client
from annotation_data_converter.settings import get_settings


def pytest_configure(config: pytest.Config):
    env_settings = dotenv_values(str(Path(__file__).parents[1] / ".env_template"))
    os.environ["bia_api_basepath"] = env_settings["local_bia_api_basepath"]
    os.environ["bia_api_username"] = env_settings["local_bia_api_username"]
    os.environ["bia_api_password"] = env_settings["local_bia_api_password"]


@pytest.fixture(scope="session")
def private_client():
    setttings = get_settings()
    return get_object_creation_client(setttings.local_bia_api_basepath)


@pytest.fixture(scope="session")
def data_in_api(private_client):

    input_file_dir = Path(__file__).parent / "input_data" / "**" / "*.json"
    file_path_list = glob.glob(str(input_file_dir), recursive=True)

    object_list = []
    for path in file_path_list:
        if os.path.isfile(path):
            with open(path, "r") as object_file:
                json_dict = json.load(object_file)
                object_list.append(json_dict)

    add_objects_to_api(private_client, object_list)
