from pathlib import Path
import pytest
from bia_test_data.data_to_api import add_objects_to_api, get_client_with_retries
from bia_export.settings import Settings
from pathlib import Path
import json
import os
from glob import glob


def pytest_configure(config: pytest.Config):
    if not os.environ.get("API_BASE_URL", None):
        os.environ.setdefault("API_BASE_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def data_in_api():
    setttings = Settings()

    input_file_dir = Path(__file__).parent / "input_data" / "**" / "*.json"
    file_path_list = glob(str(input_file_dir), recursive=True)

    object_list = []
    for path in file_path_list:
        if os.path.isfile(path):
            with open(path, "r") as object_file:
                json_dict = json.load(object_file)
                object_list.append(json_dict)


    private_client = get_client_with_retries(setttings.api_base_url)

    add_objects_to_api(private_client, object_list)
