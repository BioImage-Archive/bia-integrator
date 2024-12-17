from pathlib import Path
import pytest
from typer.testing import CliRunner

from bia_test_data.mock_objects.mock_object_constants import accession_id
from bia_test_data.mock_objects import (
    mock_image_representation,
    mock_image,
    mock_dataset,
)
from bia_ingest.persistence_strategy import persistence_strategy_factory
from bia_converter_light.cli import app, settings


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


def test_cli_convert_image(runner):
    # image_representation = (
    #    mock_image_representation.get_image_representation_of_interactive_display()
    # )

    result = runner.invoke(
        app,
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


def test_cli_update_example_image_uri_for_dataset(runner, tmpdir, monkeypatch):
    output_dir_base = tmpdir
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=str(output_dir_base),
        accession_id=accession_id,
    )
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

    created_image_path = Path(output_dir_base) / "image"
    if created_image_path.exists():
        for p in created_image_path.rglob("*.json"):
            p.unlink()
        for d in created_image_path.rglob("*"):
            if d.is_dir():
                d.rmdir()
        created_image_path.rmdir()

    monkeypatch.setattr(settings, "bia_data_dir", str(output_dir_base))
    result = runner.invoke(
        app,
        [
            "update-example-image-uri-for-dataset",
            accession_id,
            str(dataset.uuid),
            str(image_representation.uuid),
            # "--help"
        ],
    )

    assert result.exit_code == 0
    modified_dataset = persister.fetch_by_uuid(dataset.uuid, dataset.__name__)
    assert dataset.example_image_uri == []
    assert modified_dataset.example_image_uri == image_representation.file_uri
