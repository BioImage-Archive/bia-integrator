from pathlib import Path
from typing import Dict
from typer.testing import CliRunner
from ruamel.yaml import YAML

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
def proposal_details_for_input(expected_bia_image) -> Dict:
    return {
        "accession_id": accession_id,
        "study_uuid": "dummy_study_uuid",
        "dataset_uuid": "dummy_dataset_uuid",
        "name": "dummy_name",
        "file_reference_uuid": f"{expected_bia_image.original_file_reference_uuid[0]}",
        "size_in_bytes": "0",
        "size_human_readable": "dummy_size_human_readable",
    }


@pytest.fixture
def assign_from_proposal_input_path_tsv(tmpdir, proposal_details_for_input) -> Path:
    """Return path to a tsv file with proposal details to create mock image"""

    header_row = "\t".join(list(proposal_details_for_input.keys()))
    values = "\t".join(list(proposal_details_for_input.values()))

    proposal_path = Path(tmpdir) / "proposal_details.tsv"
    proposal_path.write_text(f"{header_row}\n{values}")

    return proposal_path


@pytest.fixture
def assign_from_proposal_input_path_yaml(tmpdir, proposal_details_for_input) -> Path:
    """Return path to a yaml file with proposal details to create mock image"""

    yaml = YAML(typ="safe")
    proposal_path = Path(tmpdir) / "proposal_details.yaml"
    yaml.dump(
        [
            proposal_details_for_input,
        ],
        proposal_path,
    )

    return proposal_path


@pytest.fixture
def test_api_client():
    return get_api_client("local")


@pytest.mark.parametrize("format", ("tsv", "yaml"))
def test_cli_propose_images_command(format, tmpdir):
    max_items = 2
    propose_output_path = Path(tmpdir) / f"propose_S-BIADTEST.{format}"

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
    if format == "tsv":
        proposed_output = propose_output_path.read_text().strip("\n").split("\n")
        assert len(proposed_output) == max_items + 1
    elif format == "yaml":
        yaml = YAML(typ="safe")
        proposed_output = yaml.load(propose_output_path)
        assert len(proposed_output) == max_items


@pytest.mark.parametrize(
    "format",
    (
        "tsv",
        "yaml",
    ),
)
def test_cli_assign_from_proposal_command(
    test_api_client,
    format,
    assign_from_proposal_input_path_tsv,
    assign_from_proposal_input_path_yaml,
    expected_bia_image,
    expected_uploaded_by_submitter_representation,
):
    # This implicitly tests the 'assign' and 'create' commands
    runner = CliRunner(mix_stderr=False)

    if format == "tsv":
        assign_from_proposal_input_path = f"{assign_from_proposal_input_path_tsv}"
    elif format == "yaml":
        assign_from_proposal_input_path = f"{assign_from_proposal_input_path_yaml}"

    result = runner.invoke(
        cli.app,
        [
            "assign-from-proposal",
            assign_from_proposal_input_path,
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
