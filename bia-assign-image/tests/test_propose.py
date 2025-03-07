from bia_assign_image.propose import (
    write_convertible_file_references_for_accession_id,
    read_proposals,
)
from pathlib import Path
from typing import List, Dict

import pytest


@pytest.fixture
def test_accession_id() -> str:
    return "S-BIADTEST"


@pytest.fixture
def expected_proposal_details(test_accession_id) -> List[Dict]:
    return [
        {
            "accession_id": test_accession_id,
            "study_uuid": "a2fdbd58-ee11-4cd9-bc6a-f3d3da7fff71",
            "dataset_uuid": "47a4ab60-c76d-4424-bfaa-c2a024de720c",
            "name": "F3/2E2.tif",
            "file_reference_uuid": "4bb8c5a4-d39f-4d9e-a112-334e859a5c22",
            "size_in_bytes": 206050081,
            "size_human_readable": "196.5MiB",
        },
        {
            "accession_id": test_accession_id,
            "study_uuid": "a2fdbd58-ee11-4cd9-bc6a-f3d3da7fff71",
            "dataset_uuid": "660b3420-3f2e-4887-850a-7850e3b50ff5",
            "name": "study_component2/im06.png",
            "file_reference_uuid": "4f1278b7-539a-44cb-9fa7-d8327aa308a5",
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
    )
    write_convertible_file_references_for_accession_id(
        test_accession_id,
        output_path,
        "local",
        append=True,
    )

    # We should have duplicate records
    proposal_details = read_proposals(output_path)
    assert proposal_details == expected_proposal_details_for_append_flag_set_to_true
