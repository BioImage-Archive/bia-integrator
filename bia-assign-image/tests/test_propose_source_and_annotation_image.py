from bia_assign_image.propose import (
    write_convertible_source_annotation_file_refs_for_acc_id,
    read_proposals,
)
from pathlib import Path
from typing import List, Dict

import pytest


@pytest.fixture
def test_accession_id() -> str:
    return "S-BIAD-TEST-PROPOSE-SOURCE-AND-ANNOTATION-IMAGE"


@pytest.fixture
def expected_proposal_details(test_accession_id) -> List[Dict]:
    return [
        {
            "accession_id": test_accession_id,
            "study_uuid": "bee3ebf2-73c7-4089-a9dd-c62998810921",
            "dataset_uuid": "07b9ca05-f14a-442d-8798-88bdfcfcc4cc",
            "name": "source_image_1.tif",
            "file_reference_uuid": "4d3d16b1-0f0c-45d5-b399-9c4af0b27eed",
            "size_in_bytes": 100,
            "size_human_readable": "100.0B",
        },
        {
            "accession_id": test_accession_id,
            "study_uuid": "bee3ebf2-73c7-4089-a9dd-c62998810921",
            "dataset_uuid": "ea203990-166b-4658-bbe3-cead4f4778d0",
            "name": "annotation_image_2_for_source_image_1.tif",
            "file_reference_uuid": "b17bac3c-4a4d-4d18-8fd9-9fdc2a900c86",
            "size_in_bytes": 100,
            "size_human_readable": "100.0B",
            "source_image_uuid": ["283440f8-d18d-416b-bda7-54375fa25d84"],
            "source_image": "source_image_1.tif",
        },
        {
            "accession_id": test_accession_id,
            "study_uuid": "bee3ebf2-73c7-4089-a9dd-c62998810921",
            "dataset_uuid": "ea203990-166b-4658-bbe3-cead4f4778d0",
            "name": "annotation_image_1_for_source_image_1.tif",
            "file_reference_uuid": "fd66d5e2-a87b-400a-9182-6ea649853726",
            "size_in_bytes": 100,
            "size_human_readable": "100.0B",
            "source_image_uuid": ["283440f8-d18d-416b-bda7-54375fa25d84"],
            "source_image": "source_image_1.tif",
        },
    ]


def test_propose(test_accession_id, tmp_path, expected_proposal_details):
    output_path = Path(tmp_path) / "test_output.yaml"

    n_source__annotations = write_convertible_source_annotation_file_refs_for_acc_id(
        test_accession_id,
        output_path,
        "local",
        append=False,
        check_image_creation_prerequisites=False,
    )
    proposal_details = read_proposals(output_path)
    assert proposal_details == expected_proposal_details

    n_source_images = n_source__annotations[0]
    assert n_source_images == 1

    n_annotations = n_source__annotations[1]
    assert n_annotations == 2
