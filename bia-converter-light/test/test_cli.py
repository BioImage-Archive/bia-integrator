from pathlib import Path
import shutil
import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock

from bia_integrator_api import PrivateApi
from bia_shared_datamodels import bia_data_model
from bia_test_data.mock_objects.mock_object_constants import accession_id
from bia_test_data.mock_objects import (
    mock_image_representation,
    mock_image,
    mock_dataset,
    mock_file_reference,
)
from bia_ingest.persistence_strategy import (
    persistence_strategy_factory,
    PersistenceStrategy,
)
from bia_converter_light import cli
from bia_converter_light.config import settings


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture
def output_dir_base(tmpdir, monkeypatch):
    odb = Path(tmpdir)

    monkeypatch.setattr(
        settings,
        "cache_root_dirpath",
        odb,
    )

    # Copy file to be convertered to cache so it does not need to be downloaded
    file_reference = mock_file_reference.get_file_reference()[0]
    src_path = (
        Path(__file__).parent / "data" / "test_files_for_study_component_2" / "im06.png"
    )
    dest_dir = odb / "files"
    if not dest_dir.is_dir():
        dest_dir.mkdir()
    dest_path = dest_dir / f"{file_reference.uuid}.png"
    shutil.copy(src_path, dest_path)

    return odb


@pytest.fixture
def persister(output_dir_base) -> PersistenceStrategy:
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=str(output_dir_base),
        accession_id=accession_id,
    )
    return persister


@pytest.fixture
def dataset(persister) -> bia_data_model.Dataset:
    ds = mock_dataset.get_dataset()[1]
    persister.persist(
        [
            ds,
        ]
    )

    return ds


@pytest.fixture
def image(persister) -> bia_data_model.Image:
    im = mock_image.get_image_with_one_file_reference()
    persister.persist(
        [
            im,
        ]
    )

    return im


@pytest.fixture
def file_reference(persister) -> bia_data_model.FileReference:
    file_ref = mock_file_reference.get_file_reference()[0]
    persister.persist(
        [
            file_ref,
        ]
    )

    return file_ref


@pytest.fixture
def conversion_details_path(output_dir_base, dataset, file_reference) -> Path:
    """Write tsv files with details of file references to convert"""

    path_to_conversion_details = output_dir_base / "file_references_to_convert.tsv"
    study_uuid = f"{dataset.submitted_in_study_uuid}"
    # Get details of file references in study component 2 of mock study
    size_human_readable = f"{file_reference.size_in_bytes}B"
    conversion_details = "\t".join(
        [
            accession_id,
            study_uuid,
            file_reference.file_path,
            f"{file_reference.uuid}",
            f"{file_reference.size_in_bytes}",
            size_human_readable,
        ]
    )
    path_to_conversion_details.write_text(conversion_details)
    return path_to_conversion_details


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

    def mock_get_file_reference(uuid):
        return persister.fetch_by_uuid(
            [
                uuid,
            ],
            bia_data_model.FileReference,
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
    mock_api_client_object.get_file_reference = mock_get_file_reference
    mock_api_client_object.get_image = mock_get_image
    mock_api_client_object.post_dataset = mock_post_object
    mock_api_client_object.__class__ = PrivateApi
    monkeypatch.setattr(
        cli,
        "api_client",
        mock_api_client_object,
    )
    return mock_api_client_object


def test_cli_convert_image(
    runner,
    output_dir_base,
    conversion_details_path,
    mock_api_client,
    image,
    file_reference,
):
    zarr_representation = (
        mock_image_representation.get_image_representation_of_interactive_display()
    )

    result = runner.invoke(
        cli.app,
        [
            "convert-image",
            "--accession-ids",
            accession_id,
            "--conversion-details-path",
            conversion_details_path,
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    # Check a zarr was created

    # Compare all output files vs expected?
    zarr_path = (
        output_dir_base / ".cache" / "zarr" / f"{zarr_representation.uuid}.ome.zarr"
    )
    assert zarr_path.is_dir()


def test_cli_update_example_image_uri_for_dataset(
    runner, mock_api_client, output_dir_base, persister, dataset
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

    result = runner.invoke(
        cli.app,
        [
            "update-example-image-uri-for-dataset",
            str(image_representation.uuid),
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
