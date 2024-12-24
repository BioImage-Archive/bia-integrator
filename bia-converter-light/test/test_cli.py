import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock

from bia_shared_datamodels import bia_data_model
from bia_test_data.mock_objects.mock_object_constants import accession_id
from bia_test_data.mock_objects import (
    mock_image_representation,
    mock_image,
    mock_dataset,
)
from bia_ingest.persistence_strategy import (
    persistence_strategy_factory,
    PersistenceStrategy,
)
from bia_converter_light import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture
def output_dir_base(tmpdir):
    return tmpdir


@pytest.fixture
def persister(output_dir_base) -> PersistenceStrategy:
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=str(output_dir_base),
        accession_id=accession_id,
    )
    return persister


@pytest.fixture
def mock_api_client(monkeypatch, persister):
    """Mock api_client functions for getting and saving model objects used in test"""

    def mock_get_image(uuid):
        return persister.fetch_by_uuid(
            [
                uuid,
            ],
            bia_data_model.Image,
        )[0]

    def mock_get_image_representation(uuid):
        return persister.fetch_by_uuid(
            [
                uuid,
            ],
            bia_data_model.ImageRepresentation,
        )[0]

    def mock_get_dataset(uuid):
        return persister.fetch_by_uuid(
            [
                uuid,
            ],
            bia_data_model.Dataset,
        )[0]

    def mock_post_object(obj):
        persister.persist(
            [
                obj,
            ]
        )

    mock_api_client_object = MagicMock()
    mock_api_client_object.get_image_representation = mock_get_image_representation
    mock_api_client_object.get_dataset = mock_get_dataset
    mock_api_client_object.get_image = mock_get_image
    mock_api_client_object.post_dataset = mock_post_object
    monkeypatch.setattr(
        cli,
        "api_client",
        mock_api_client_object,
    )
    return mock_api_client_object


def test_cli_convert_image(runner):
    # image_representation = (
    #    mock_image_representation.get_image_representation_of_interactive_display()
    # )

    result = runner.invoke(
        cli.app,
        [
            "convert-image",
            # "S-BIADTEST",
            # str(image_representation.uuid),
            "S-BIAD1005",
            "98cd36b1-cd9f-4bd5-83a0-ad89f21808b1",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0


def test_cli_update_example_image_uri_for_dataset(
    runner, mock_api_client, output_dir_base, persister, monkeypatch
):
    image_representation = (
        mock_image_representation.get_image_representation_of_static_display()
    )
    persister.persist(
        [
            image_representation,
        ]
    )

    bia_image = mock_image.get_image_with_one_file_reference()
    persister.persist(
        [
            bia_image,
        ]
    )

    dataset = mock_dataset.get_dataset()[1]
    persister.persist(
        [
            dataset,
        ]
    )

    monkeypatch.setattr(cli.settings, "bia_data_dir", str(output_dir_base))
    monkeypatch.setattr(cli, "api_client", mock_api_client)
    result = runner.invoke(
        cli.app,
        [
            "update-example-image-uri-for-dataset",
            str(image_representation.uuid),
            # "--help"
        ],
    )

    assert result.exit_code == 0
    # cli.update_example_image_uri_for_dataset(image_representation.uuid)
    modified_dataset = persister.fetch_by_uuid(
        [
            dataset.uuid,
        ],
        bia_data_model.Dataset,
    )[0]
    assert dataset.example_image_uri == []
    assert modified_dataset.example_image_uri == image_representation.file_uri
