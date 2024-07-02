from pathlib import Path
import json
import pytest
from bia_ingest_sm.biostudies import Submission

@pytest.fixture
def base_path() -> Path:
    """Return full path to test directory

    """
    return Path(__file__).parent

@pytest.fixture
def test_submission(base_path: Path) -> Submission:
    submission_path = base_path / "data" / "S-BIADTEST.json"
    json_data = json.loads(submission_path.read_text())
    submission = Submission.model_validate(json_data)
    return submission
    
