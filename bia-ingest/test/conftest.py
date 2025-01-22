from unittest.mock import Mock
from typing import Dict
from pathlib import Path
import json
import pytest
from bia_ingest.biostudies.api import Submission, SubmissionTable, requests
from bia_test_data.mock_objects.mock_object_constants import accession_id, accession_id_default
from bia_ingest.cli_logging import IngestionResult
from bia_test_data import bia_test_data_dir


@pytest.fixture
def test_submission() -> Submission:
    submission_path = bia_test_data_dir / "biad_v4" / "S-BIADTEST.json"
    json_data = json.loads(submission_path.read_text())
    submission = Submission.model_validate(json_data)
    return submission

@pytest.fixture
def test_default_submission_direct_files() -> Submission:
    submission_path = bia_test_data_dir / "default_biostudies" / "S-BSSTTEST_files_direct.json"
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
def ingestion_result_summary_default():
    result_summary = {accession_id_default: IngestionResult()}
    return result_summary

@pytest.fixture
def mock_request_get(monkeypatch):
    """Requests.get mocked to read file from disk"""

    def _mock_request_get(flist_url: str) -> Dict[str, str]:
        path_to_load = bia_test_data_dir / "biad_v4" / Path(flist_url).name
        return_value = Mock()
        return_value.status_code = 200
        return_value.content = path_to_load.read_text()
        return return_value

    monkeypatch.setattr(requests, "get", _mock_request_get)
