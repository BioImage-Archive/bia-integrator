"""Test assigning images with patterns from CLI directly and from CLI with proposal yaml

Test with CLI directly uses pattern for 1 channel
Test with CLI using proposal yaml uses pattern for 2 channels

"""

from typing import Type
from pydantic import BaseModel
from pydantic.alias_generators import to_snake
from pathlib import Path
from typer.testing import CliRunner
from ruamel.yaml import YAML

import pytest
from bia_shared_datamodels import bia_data_model
from bia_assign_image import cli
from bia_assign_image.api_client import get_api_client

accession_id = "S-BIAD-TEST-ASSIGN-IMAGE-WITH-PATTERN"
pattern_2channels = "image_01_channel_{c:d}_slice_{z:d}_time{t:d}.tiff"
pattern_1channel = "image_01_channel_00_slice_{z:d}_time{t:d}.tiff"


def get_expected_object(object_type: str, uuid: str) -> Type[BaseModel]:
    object_path = (
        Path(__file__).parent
        / "test_data"
        / to_snake(object_type)
        / accession_id
        / f"{uuid}.json"
    )
    obj = getattr(bia_data_model, object_type)
    return obj.model_validate_json(object_path.read_text())


@pytest.fixture()
def expected_bia_image_2channels() -> bia_data_model.Image:
    return get_expected_object("Image", "1fa56584-27be-45a6-8aed-96387f171024")


@pytest.fixture()
def expected_bia_image_1channel() -> bia_data_model.Image:
    return get_expected_object("Image", "451e042f-a4f1-4eb7-8d85-285a75bd9aa9")


@pytest.fixture()
def expected_uploaded_by_submitter_representation_2channels() -> (
    bia_data_model.ImageRepresentation
):
    return get_expected_object(
        "ImageRepresentation", "7def833e-0640-4251-84c5-ed759d78d9d2"
    )


@pytest.fixture()
def expected_uploaded_by_submitter_representation_1channel() -> (
    bia_data_model.ImageRepresentation
):
    return get_expected_object(
        "ImageRepresentation", "2dba82c4-db6d-4649-8a70-5d839b6356c2"
    )


@pytest.fixture
def file_reference_uuids_2channels(expected_bia_image_2channels) -> str:
    return " ".join(
        [
            str(f_uuid)
            for f_uuid in expected_bia_image_2channels.original_file_reference_uuid
        ]
    )


@pytest.fixture
def file_reference_uuids_1channel(expected_bia_image_1channel) -> str:
    return " ".join(
        [
            str(f_uuid)
            for f_uuid in expected_bia_image_1channel.original_file_reference_uuid
        ]
    )


@pytest.fixture
def assign_from_proposal_input_path_yaml(
    tmpdir, file_reference_uuids_2channels
) -> Path:
    """Return path to a yaml file with proposal details to create mock image"""

    proposal_details_for_input = {
        "accession_id": accession_id,
        "study_uuid": "dummy_study_uuid",
        "dataset_uuid": "dummy_dataset_uuid",
        "name": "dummy_name",
        "file_reference_uuid": file_reference_uuids_2channels,
        "pattern": pattern_2channels,
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


# TODO: When use of RO crate complete also check CreationProcess and Specimen in all tests below
def test_cli_assign_from_proposal_command(
    test_api_client,
    data_in_api,
    assign_from_proposal_input_path_yaml,
    expected_bia_image_2channels,
    expected_uploaded_by_submitter_representation_2channels,
):
    # This implicitly tests the 'assign' and 'create' commands
    runner = CliRunner()

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
        str(expected_bia_image_2channels.uuid)
    ).model_dump()
    created_bia_image = bia_data_model.Image.model_validate(created_bia_image_dict)
    assert created_bia_image == expected_bia_image_2channels

    created_uploaded_by_submitter_representation_dict = (
        test_api_client.get_image_representation(
            str(expected_uploaded_by_submitter_representation_2channels.uuid)
        ).model_dump()
    )
    created_uploaded_by_submitter_representation = (
        bia_data_model.ImageRepresentation.model_validate(
            created_uploaded_by_submitter_representation_dict
        )
    )
    assert (
        created_uploaded_by_submitter_representation
        == expected_uploaded_by_submitter_representation_2channels
    )


def test_cli_assign_command_with_pattern(
    test_api_client,
    data_in_api,
    file_reference_uuids_1channel,
    expected_bia_image_1channel,
    expected_uploaded_by_submitter_representation_1channel,
):
    # This implicitly tests the 'assign' and 'create' commands
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "assign",
            "--api",
            "local",
            "--pattern",
            pattern_1channel,
            accession_id,
            file_reference_uuids_1channel,
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
        str(expected_bia_image_1channel.uuid)
    ).model_dump()
    created_bia_image = bia_data_model.Image.model_validate(created_bia_image_dict)
    assert created_bia_image == expected_bia_image_1channel

    created_uploaded_by_submitter_representation_dict = (
        test_api_client.get_image_representation(
            str(expected_uploaded_by_submitter_representation_1channel.uuid)
        ).model_dump()
    )
    created_uploaded_by_submitter_representation = (
        bia_data_model.ImageRepresentation.model_validate(
            created_uploaded_by_submitter_representation_dict
        )
    )
    assert (
        created_uploaded_by_submitter_representation
        == expected_uploaded_by_submitter_representation_1channel
    )
