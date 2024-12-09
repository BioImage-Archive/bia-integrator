from pathlib import Path
from bia_test_data.mock_objects.utils import accession_id
from typer.testing import CliRunner
from bia_assign_image import cli
from bia_test_data.mock_objects import mock_file_reference, mock_dataset
from .mock_objects import mock_image, mock_image_representation
from bia_ingest.persistence_strategy import persistence_strategy_factory


def test_bia_assign_cli(monkeypatch, tmpdir):
    runner = CliRunner()
    file_reference_uuids = " ".join(
        [str(f.uuid) for f in mock_file_reference.get_file_reference()]
    )

    output_dir_base = tmpdir
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=str(output_dir_base),
        accession_id=accession_id,
    )
    persister.persist(mock_file_reference.get_file_reference())
    persister.persist(mock_dataset.get_dataset())

    created_image_path = Path(output_dir_base) / "image"
    if created_image_path.exists():
        for p in created_image_path.rglob("*.json"):
            p.unlink()
        for d in created_image_path.rglob("*"):
            if d.is_dir():
                d.rmdir()
        created_image_path.rmdir()

    monkeypatch.setattr(cli.settings, "bia_data_dir", str(output_dir_base))
    result = runner.invoke(
        cli.app,
        [
            "assign",
            accession_id,
            file_reference_uuids,
        ],
    )
    print(result.stdout)
    assert result.exit_code == 0
    created = [p for p in created_image_path.rglob("*.json")]
    assert len(created) == 1


def test_bia_create_image_representation_cli(monkeypatch, tmpdir):
    runner = CliRunner(mix_stderr=False)

    output_dir_base = tmpdir
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=str(output_dir_base),
        accession_id=accession_id,
    )
    persister.persist(mock_file_reference.get_file_reference())
    persister.persist(
        [
            mock_image.get_image_with_one_file_reference(),
        ]
    )
    persister.persist(
        [
            mock_image_representation.get_image_representation_of_interactive_display(),
        ]
    )
    persister.persist(
        [
            mock_image_representation.get_image_representation_of_thumbnail(),
        ]
    )
    persister.persist(
        [
            mock_image_representation.get_image_representation_of_uploaded_by_submitter(),
        ]
    )
    persister.persist(
        [
            mock_image_representation.get_image_representation_of_static_display(),
        ]
    )

    image_uuid = mock_image.get_image_with_one_file_reference().uuid
    monkeypatch.setattr(cli.settings, "bia_data_dir", str(output_dir_base))
    result = runner.invoke(
        cli.app,
        [
            "representations",
            "create",
            accession_id,
            str(image_uuid),
        ],
    )
    print(result.stdout)
    assert result.exit_code == 0
    image_representations_path = Path(output_dir_base) / "image_representation"
    created = [p for p in image_representations_path.rglob("*.json")]
    assert len(created) == 4
    # TODO: Check actual results !!!
