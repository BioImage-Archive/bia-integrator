from typing import Type
from pathlib import Path
from pydantic import BaseModel
from pydantic.alias_generators import to_snake
import pytest
from bia_shared_datamodels import bia_data_model
from bia_test_data.data_to_api import add_objects_to_api, get_object_creation_client
from bia_assign_image.settings import settings
import json
import os
from glob import glob


def get_expected_object(
    base_path: Path, object_type: str, accession_id: str, uuid: str
) -> Type[BaseModel]:
    """Return bia_data_model from json"""
    object_path = base_path / to_snake(object_type) / accession_id / f"{uuid}.json"
    obj = getattr(bia_data_model, object_type)
    return obj.model_validate_json(object_path.read_text())


@pytest.fixture(scope="session")
def private_client():
    return get_object_creation_client(settings.local_bia_api_basepath)


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
    """Set up environment variables before any test modules are loaded.

    Use sessionstart instead of fixtures to ensure the env vars are
    set before any modules are loaded, so the values for config.settings
    are picked up from environment variables using pydantic settings wiring
    """

    os.environ["api_base_url"] = "http://localhost:8080"
    os.environ["bia_api_username"] = "test@example.com"
    os.environ["bia_api_password"] = "test"


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Runs before test modules are imported."""
    data_in_api()
