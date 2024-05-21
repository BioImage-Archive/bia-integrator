import pytest

from pathlib import Path
import json

from bia_ingest.biostudies import Submission

from .utils import (
    create_expected_biosample,
    create_expected_specimen,
    create_expected_image_acquisition,
)


@pytest.fixture
def base_path():
    return Path(__file__).parent


@pytest.fixture
def accession_id():
    return "S-BIADTEST"


@pytest.fixture
def submission_from_json(base_path, accession_id):
    submission_path = base_path / "data" / f"{accession_id}.json"
    return json.loads(submission_path.read_text())


@pytest.fixture
def submission(submission_from_json):
    return Submission(**submission_from_json)


@pytest.fixture
def expected_biosample(accession_id):
    """ Create Biosample

    """
    return create_expected_biosample(accession_id)


@pytest.fixture
def expected_biosample_uuid(expected_biosample):
    return expected_biosample.uuid


@pytest.fixture
def expected_specimen(accession_id, expected_biosample_uuid):
    """Create Specimen

    """
    return create_expected_specimen(accession_id, expected_biosample_uuid)


@pytest.fixture
def expected_specimen_uuid(expected_specimen):
    return expected_specimen.uuid


@pytest.fixture
def expected_image_acquisition(accession_id, expected_specimen_uuid):
    """ Create Image Acquisition object directly as we do not need its dict

    """
    return create_expected_image_acquisition(accession_id, expected_specimen_uuid)
