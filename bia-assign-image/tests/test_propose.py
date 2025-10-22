from bia_assign_image.propose import (
    write_convertible_file_references_for_accession_id,
    read_proposals,
)
from pathlib import Path
from typing import List, Dict

import pytest


@pytest.fixture
def test_accession_id() -> str:
    return "S-BIAD-TEST-PROPOSE"


@pytest.fixture
def expected_proposal_details(test_accession_id) -> List[Dict]:
    return [
        {
            "accession_id": test_accession_id,
            "study_uuid": "c2cf7af2-36a7-4249-9e69-a6ba565e94a2",
            "dataset_uuid": "63e33342-2390-49e1-af69-2652f7c97296",
            "name": "F3/2E2.tif",
            "file_reference_uuid": "9cebfb9d-8bfa-4d61-ba38-e56a6cf731d8",
            "size_in_bytes": 206050081,
            "size_human_readable": "196.5MiB",
        },
        {
            "accession_id": test_accession_id,
            "study_uuid": "c2cf7af2-36a7-4249-9e69-a6ba565e94a2",
            "dataset_uuid": "63e33342-2390-49e1-af69-2652f7c97296",
            "name": "study_component2/im06.png",
            "file_reference_uuid": "10628322-8051-4e6a-a569-c5dbaf7a4cec",
            "size_in_bytes": 24649,
            "size_human_readable": "24.1KiB",
        },
    ]


@pytest.fixture
def expected_proposal_details_for_append_flag_set_to_true(
    expected_proposal_details,
) -> List[Dict]:
    details = []
    details.extend(expected_proposal_details)
    details.extend(expected_proposal_details)
    return details


@pytest.mark.parametrize("format", ("tsv", "yaml"))
def test_propose_works_with_supported_file_formats(
    test_accession_id, format, tmp_path, expected_proposal_details
):
    output_path = Path(tmp_path) / f"test_output.{format}"

    write_convertible_file_references_for_accession_id(
        test_accession_id,
        output_path,
        "local",
        append=False,
        propose_strategy="size_stratified_sampling",
    )
    proposal_details = read_proposals(output_path)
    assert proposal_details == expected_proposal_details


@pytest.mark.parametrize("format", ("tsv", "yaml"))
def test_propose_append_flag(
    test_accession_id,
    format,
    tmp_path,
    expected_proposal_details_for_append_flag_set_to_true,
):
    output_path = Path(tmp_path) / f"test_output.{format}"

    # Do two writes appending on second
    write_convertible_file_references_for_accession_id(
        test_accession_id,
        output_path,
        "local",
        append=False,
        propose_strategy="size_stratified_sampling",
    )
    write_convertible_file_references_for_accession_id(
        test_accession_id,
        output_path,
        "local",
        append=True,
        propose_strategy="size_stratified_sampling",
    )

    # We should have duplicate records
    proposal_details = read_proposals(output_path)
    assert proposal_details == expected_proposal_details_for_append_flag_set_to_true
