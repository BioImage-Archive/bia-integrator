from unittest.mock import Mock
from typing import Dict
from pathlib import Path
import json
import pytest
from bia_ingest.biostudies.api import Submission, SubmissionTable, requests
from bia_test_data.mock_objects.mock_object_constants import (
    accession_id,
    accession_id_biostudies_default,
)
from bia_ingest.cli_logging import IngestionResult
from bia_test_data import bia_test_data_dir
from bia_ingest.biostudies.api import SearchPage

from bia_ingest.biostudies.biostudies_processing_version import (
    BioStudiesProcessingVersion,
)
from bia_integrator_api.util import get_client
import os
from dotenv.main import dotenv_values


def pytest_configure(config: pytest.Config):
    env_settings = dotenv_values(str(Path(__file__).parents[1] / ".env_template"))
    os.environ["bia_api_basepath"] = env_settings["local_bia_api_basepath"]
    os.environ["bia_api_username"] = env_settings["local_bia_api_username"]
    os.environ["bia_api_password"] = env_settings["local_bia_api_password"]


@pytest.fixture
def test_submission() -> Submission:
    submission_path = bia_test_data_dir / "biad_v4" / "S-BIADTEST.json"
    json_data = json.loads(submission_path.read_text())
    submission = Submission.model_validate(json_data)
    return submission


@pytest.fixture
def test_submission_biostudies_default_direct_files() -> Submission:
    submission_path = (
        bia_test_data_dir / "default_biostudies" / "S-BSSTTEST_files_direct.json"
    )
    json_data = json.loads(submission_path.read_text())
    submission = Submission.model_validate(json_data)
    return submission


@pytest.fixture
def test_submission_table() -> SubmissionTable:
    submission_path = bia_test_data_dir / "biad_v4" / "S-BIADTEST_INFO.json"
    json_data = json.loads(submission_path.read_text())
    submission = SubmissionTable.model_validate(json_data)
    return submission


@pytest.fixture
def ingestion_result_summary():
    result_summary = {accession_id: IngestionResult()}
    return result_summary


@pytest.fixture
def ingestion_result_summary_biostudies_default():
    result_summary = {}
    result_summary[accession_id_biostudies_default] = IngestionResult()
    result_summary[
        accession_id_biostudies_default
    ].ProcessingVersion = BioStudiesProcessingVersion.BIOSTUDIES_DEFAULT
    return result_summary


@pytest.fixture
def mock_request_get(monkeypatch):
    """Requests.get mocked to read file from disk"""

    def _mock_request_get(flist_url: str, stream: bool = True) -> Dict[str, str]:
        path_to_load = bia_test_data_dir / "biad_v4" / Path(flist_url).name
        return_value = Mock()
        return_value.status_code = 200
        return_value.content = path_to_load.read_text()
        return return_value

    monkeypatch.setattr(requests.Session, "get", _mock_request_get)


@pytest.fixture
def mock_search_result():
    """Requests.get mocked to read file from disk"""

    mock_result = {
        "page": 1,
        "pageSize": 1,
        "totalHits": 1,
        "isTotalHitsExact": True,
        "sortBy": "release_date",
        "sortOrder": "descending",
        "hits": [
            {
                "accession": "S-BIADNotYetInAPI",
                "type": "study",
                "title": "Test Title",
                "author": "Test Authors",
                "links": 0,
                "files": 0,
                "release_date": "2025-01-01",
                "views": 0,
                "isPublic": True,
            }
        ],
        "query": None,
        "facets": None,
    }
    search_result = SearchPage(**mock_result)

    return search_result


@pytest.fixture()
def get_bia_api_client():
    return get_client(os.environ.get("bia_api_basepath"))


@pytest.fixture()
def tmp_bia_data_dir(tmp_path):
    os.environ["bia_data_dir"] = str(tmp_path)
    return tmp_path
