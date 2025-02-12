from pathlib import Path
import pytest
from bia_test_data.data_to_api import add_objects_to_api, get_client_with_retries
from bia_export.settings import Settings
from bia_shared_datamodels.uuid_creation import create_study_uuid
from pathlib import Path
import json
import os
from glob import glob


def pytest_configure(config: pytest.Config):
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




@pytest.fixture(scope="session")
def api_studies_in_expected_order():
    setttings = Settings()

    base_study = Path(__file__).parent / "input_data" / "study" / "S-BIADTEST" / "a2fdbd58-ee11-4cd9-bc6a-f3d3da7fff71.json"

    with open(base_study, "r") as object_file:
        base_study_dict: dict = json.load(object_file)
    
    object_list = []

    study_1 = base_study_dict.copy() | {
            "accession_id": "S-BIADTEST1",
            "uuid": str(create_study_uuid("S-BIADTEST111")),
            "release_date": "2024-01-01"
        }
    object_list.append(study_1)

    study_2 = base_study_dict.copy() | {
            "accession_id": "S-BIADTEST22",
            "uuid": str(create_study_uuid("S-BIADTEST22")),
            "release_date": "2024-01-01"
        }
    object_list.append(study_2)
    
    study_3 = base_study_dict.copy() | {
            "accession_id": "S-BIADTEST333",
            "uuid": str(create_study_uuid("S-BIADTEST333")),
            "release_date": "2024-01-03"
        }
    object_list.append(study_3)

    
    study_4 = base_study_dict.copy() | {
        "accession_id": "S-BIADTEST4444",
        "uuid": str(create_study_uuid("S-BIADTEST4444")),
        "release_date": "2024-01-02"
    }
    object_list.append(study_4)

    private_client = get_client_with_retries(setttings.api_base_url)

    add_objects_to_api(private_client, object_list)

    expected_order_of_studies = [study_3, study_4, study_2, study_1]

    return expected_order_of_studies
