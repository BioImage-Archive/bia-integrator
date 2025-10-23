from bia_assign_image.propose import (
    get_first_n_convertible_file_references,
)
import pytest


@pytest.fixture
def test_accession_id() -> str:
    return "S-BIAD-TEST-PROPOSE-SOURCE-AND-ANNOTATION-IMAGE"


@pytest.fixture
def expected_proposal_details(test_accession_id) -> list[dict]:
    return [
        {
            "4d3d16b1-0f0c-45d5-b399-9c4af0b27eed" : {
                "accession_id": test_accession_id,
                "study_uuid": "bee3ebf2-73c7-4089-a9dd-c62998810921",
                "dataset_uuid": "07b9ca05-f14a-442d-8798-88bdfcfcc4cc",
                "name": "source_image_1.tif",
                "file_reference_uuid": "4d3d16b1-0f0c-45d5-b399-9c4af0b27eed",
                "size_in_bytes": 100,
                "size_human_readable": "100.0B",
            },
        }, {
            "b17bac3c-4a4d-4d18-8fd9-9fdc2a900c86":
            {
                "accession_id": test_accession_id,
                "study_uuid": "bee3ebf2-73c7-4089-a9dd-c62998810921",
                "dataset_uuid": "ea203990-166b-4658-bbe3-cead4f4778d0",
                "name": "annotation_image_2_for_source_image_1.tif",
                "file_reference_uuid": "b17bac3c-4a4d-4d18-8fd9-9fdc2a900c86",
                "size_in_bytes": 100,
                "size_human_readable": "100.0B",
            },
        }, {
            "f4c4df4b-f44b-4b24-9fbc-b350034cf323":
            {
                "accession_id": test_accession_id,
                "study_uuid": "bee3ebf2-73c7-4089-a9dd-c62998810921",
                "dataset_uuid": "ea203990-166b-4658-bbe3-cead4f4778d0",
                "name": "annotation_image_no_source_image.tif",
                "file_reference_uuid": "f4c4df4b-f44b-4b24-9fbc-b350034cf323",
                "size_in_bytes": 200,
                "size_human_readable": "200.0B",
            },
        }, {
            "fd66d5e2-a87b-400a-9182-6ea649853726":
            {
                "accession_id": test_accession_id,
                "study_uuid": "bee3ebf2-73c7-4089-a9dd-c62998810921",
                "dataset_uuid": "ea203990-166b-4658-bbe3-cead4f4778d0",
                "name": "annotation_image_1_for_source_image_1.tif",
                "file_reference_uuid": "fd66d5e2-a87b-400a-9182-6ea649853726",
                "size_in_bytes": 100,
                "size_human_readable": "100.0B",
            },
        },
    ]


@pytest.mark.parametrize("n_to_propose", [1, 2, 3, 4])
def test_get_first_n_convertible_file_references(
    test_accession_id,
    expected_proposal_details,
    n_to_propose,
):
    proposal_details = get_first_n_convertible_file_references(
        test_accession_id,
        "local",
        n_to_propose=n_to_propose,
        check_image_creation_prerequisites=False,
    )

    assert len(proposal_details) == n_to_propose
    assert all(
        [
            {k: v} in expected_proposal_details for k, v in proposal_details.items()
        ]
    )