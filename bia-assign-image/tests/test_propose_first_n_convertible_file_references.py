from bia_assign_image.propose import (
    get_first_n_convertible_file_references,
)
from typing import List, Dict

import pytest


@pytest.fixture
def test_accession_id() -> str:
    return "S-BIAD-TEST-PROPOSE"


@pytest.fixture
def expected_proposal_details(test_accession_id) -> List[Dict]:
    return {
        "9cebfb9d-8bfa-4d61-ba38-e56a6cf731d8": {
            "accession_id": test_accession_id,
            "study_uuid": "c2cf7af2-36a7-4249-9e69-a6ba565e94a2",
            "dataset_uuid": "63e33342-2390-49e1-af69-2652f7c97296",
            "name": "F3/2E2.tif",
            "file_reference_uuid": "9cebfb9d-8bfa-4d61-ba38-e56a6cf731d8",
            "size_in_bytes": 206050081,
            "size_human_readable": "196.5MiB",
        },
        "10628322-8051-4e6a-a569-c5dbaf7a4cec": {
            "accession_id": test_accession_id,
            "study_uuid": "c2cf7af2-36a7-4249-9e69-a6ba565e94a2",
            "dataset_uuid": "63e33342-2390-49e1-af69-2652f7c97296",
            "name": "study_component2/im06.png",
            "file_reference_uuid": "10628322-8051-4e6a-a569-c5dbaf7a4cec",
            "size_in_bytes": 24649,
            "size_human_readable": "24.1KiB",
        },
    }


def test_get_first_n_convertible_file_references(
    test_accession_id,
    expected_proposal_details,
):
    proposal_details = get_first_n_convertible_file_references(
        test_accession_id,
        "local",
        n_to_propose=2,
        check_image_creation_prerequisites=True,
    )

    assert proposal_details == expected_proposal_details
