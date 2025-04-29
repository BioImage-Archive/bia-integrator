from pathlib import Path
from typer.testing import CliRunner
from ruamel.yaml import YAML

import pytest
from bia_shared_datamodels import bia_data_model
from bia_assign_image import cli
from bia_assign_image.api_client import get_api_client

accession_id = "S-BIAD-BIA-ASSIGN-IMAGE-WITH-PATTERN-TEST"


@pytest.fixture()
def expected_bia_image() -> bia_data_model.Image:
    dir = Path(__file__).parent / "data" / "image" / accession_id
    image_path = next(dir.glob("*.json"))
    return bia_data_model.Image.model_validate_json(image_path.read_text())


@pytest.fixture()
def expected_uploaded_by_submitter_representation() -> (
    bia_data_model.ImageRepresentation
):
    dir = Path(__file__).parent / "data" / "image_representation" / accession_id
    object_path = next(dir.glob("*.json"))
    return bia_data_model.ImageRepresentation.model_validate_json(
        object_path.read_text()
    )


@pytest.fixture
def assign_from_proposal_input_path_yaml(tmpdir, expected_bia_image) -> Path:
    """Return path to a yaml file with proposal details to create mock image"""

    file_reference_uuids = " ".join(
        [str(f_uuid) for f_uuid in expected_bia_image.original_file_reference_uuid]
    )
    proposal_details_for_input = {
        "accession_id": accession_id,
        "study_uuid": "dummy_study_uuid",
        "dataset_uuid": "dummy_dataset_uuid",
        "name": "dummy_name",
        "file_reference_uuid": file_reference_uuids,
        "pattern": "image_01_channel{%d}_slice{%d}_time{%d}",
    }
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


def test_cli_assign_from_proposal_command(
    data_in_api,
    test_api_client,
    assign_from_proposal_input_path_yaml,
    expected_bia_image,
    expected_uploaded_by_submitter_representation,
):
    # This implicitly tests the 'assign' and 'create' commands
    runner = CliRunner(mix_stderr=False)

    # result = cli.assign_from_proposal(
    #       Path(assign_from_proposal_input_path),
    #       "local",
    # )

    result = runner.invoke(
        cli.app,
        [
            "assign-from-proposal",
            f"{assign_from_proposal_input_path_yaml}",
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
