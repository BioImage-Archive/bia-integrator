from unittest.mock import Mock
from typing import Dict
from pathlib import Path
import json
import pytest
from bia_ingest.ingest.biostudies.api import Submission, SubmissionTable, requests
from .utils import accession_id
from bia_ingest.cli_logging import IngestionResult


@pytest.fixture
def base_path() -> Path:
    """Return full path to test directory"""
    return Path(__file__).parent


@pytest.fixture
def test_submission(base_path: Path) -> Submission:
    submission_path = base_path / "data" / "S-BIADTEST.json"
    json_data = json.loads(submission_path.read_text())
    submission = Submission.model_validate(json_data)
    return submission


@pytest.fixture
def test_submission_table(base_path: Path) -> SubmissionTable:
    submission_path = base_path / "data" / "S-BIADTEST_INFO.json"
    json_data = json.loads(submission_path.read_text())
    submission = SubmissionTable.model_validate(json_data)
    return submission


@pytest.fixture
def ingestion_result_summary():
    return {accession_id: IngestionResult()}


@pytest.fixture
def mock_request_get(monkeypatch):
    """Requests.get mocked to read file from disk"""

    def _mock_request_get(flist_url: str) -> Dict[str, str]:
        data_dir = Path(__file__).parent / "data"
        path_to_load = data_dir / Path(flist_url).name
        return_value = Mock()
        return_value.status_code = 200
        return_value.content = path_to_load.read_text()
        return return_value

    monkeypatch.setattr(requests, "get", _mock_request_get)
