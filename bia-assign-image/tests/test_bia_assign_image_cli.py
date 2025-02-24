from pathlib import Path
from typer.testing import CliRunner
import pytest
from bia_shared_datamodels import bia_data_model
from bia_assign_image import cli
from bia_test_data.mock_objects.mock_object_constants import accession_id
from bia_test_data.mock_objects import (
    mock_image,
    mock_image_representation,
)
from bia_assign_image.api_client import get_api_client


@pytest.fixture()
def expected_bia_image() -> bia_data_model.Image:
    return mock_image.get_image_with_one_file_reference()


@pytest.fixture
def expected_uploaded_by_submitter_representation() -> (
    bia_data_model.ImageRepresentation
):
    return mock_image_representation.get_image_representation_of_uploaded_by_submitter()


@pytest.fixture
def assign_from_proposal_input_path(tmpdir, expected_bia_image) -> Path:
    """Return path to a tsv file with proposal details to create mock image"""

    header_row = "\t".join(
        [
            "accession_id",
            "study_uuid",
            "dataset_uuid",
            "name",
            "file_reference_uuid",
            "size_in_bytes",
            "size_human_readable",
        ]
    )
    values = "\t".join(
        [
            accession_id,
            "dummy_study_uuid",
            "dummy_dataset_uuid",
            "dummy_name",
            f"{expected_bia_image.original_file_reference_uuid[0]}",
            "0",
            "dummy_size_human_readable",
        ]
    )

    proposal_path = Path(tmpdir) / "proposal_details.tsv"
    proposal_path.write_text(f"{header_row}\n{values}")

    return proposal_path


@pytest.fixture
def test_api_client():
    return get_api_client("local")


def test_cli_propose_images_command(data_in_api, tmpdir):
    max_items = 2
    propose_output_path = Path(tmpdir) / "propose_S-BIAD1522.tsv"

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            "propose-images",
            accession_id,
            "--api",
            "local",
            "--check-image-creation-prerequisites",
            "--max-items",
            f"{max_items}",
            "--no-append",
            f"{propose_output_path}",
        ],
    )
    assert result.exit_code == 0
    proposed_output = propose_output_path.read_text().strip("\n").split("\n")
    assert len(proposed_output) == max_items + 1


def test_cli_assign_from_proposal_command(
    data_in_api,
    test_api_client,
    assign_from_proposal_input_path,
    expected_bia_image,
    expected_uploaded_by_submitter_representation,
):
    # This implicitly tests the 'assign' and 'create' commands
    runner = CliRunner(mix_stderr=False)

    # result = cli.assign_from_proposal(
    #        assign_from_proposal_input_path,
    #        "local",
    # )
    result = runner.invoke(
        cli.app,
        [
            "assign-from-proposal",
            f"{assign_from_proposal_input_path}",
            "--api",
            "local",
        ],
    )

    assert result.exit_code == 0

    # Check BIA image and UPLOADED_BY_SUBMITTER representation objects created.
    #
    # TODO: Investigate issue commented on below.
    # At time of writing test (21/02/2025), there are subtle differences in
    # API models and bia_data_models (e.g. Pydantic serializer warnings around type of
    # AttributeProvenance which may be leading to:
    #     <AttributeProvenance.bia_conversion: 'bia_conversion' (bia_data_model) vs
    #     <AttributeProvenance.BIA_CONVERSION: 'bia_conversion' (api)
    # so convert returned value to bia_data_model.* before comparison)
    created_bia_image_dict = test_api_client.get_image(
        str(expected_bia_image.uuid)
    ).model_dump()
    created_bia_image = bia_data_model.Image.model_validate(created_bia_image_dict)
    assert created_bia_image == expected_bia_image

    created_uploaded_by_submitter_representation_dict = (
        test_api_client.get_image_representation(
            str(expected_uploaded_by_submitter_representation.uuid)
        ).model_dump()
    )
    created_uploaded_by_submitter_representation = (
        bia_data_model.ImageRepresentation.model_validate(
            created_uploaded_by_submitter_representation_dict
        )
    )
    assert (
        created_uploaded_by_submitter_representation
        == expected_uploaded_by_submitter_representation
    )
