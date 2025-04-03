from pathlib import Path
import pytest
from bia_test_data.data_to_api import add_objects_to_api, get_object_creation_client
import json
import os
from glob import glob


def data_in_api():
    private_client = get_object_creation_client("http://localhost:8080")
    input_file_dir = Path(__file__).parent / "input_data" / "**" / "*.json"
    file_path_list = glob(str(input_file_dir), recursive=True)

    object_list = []
    for path in file_path_list:
        if os.path.isfile(path):
            with open(path, "r") as object_file:
                json_dict = json.load(object_file)
                object_list.append(json_dict)

    add_objects_to_api(private_client, object_list)


def pytest_sessionstart(session):
    """Set up environment variables before any test modules are loaded."""

    base_temp = session.config._tmp_path_factory.getbasetemp()
    cache_root_dirpath = base_temp / "temp_cache"
    cache_root_dirpath.mkdir(exist_ok=True)
    os.environ["cache_root_dirpath"] = f"{cache_root_dirpath}"


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Runs before test modules are imported."""
    data_in_api()
