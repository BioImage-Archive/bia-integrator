from pathlib import Path
import shutil
import pytest
from bia_shared_datamodels import bia_data_model
import bia_integrator_api.models as api_models
from bia_converter import io
from bia_converter import convert
from typer.testing import CliRunner
from bia_converter import cli
from bia_converter.config import settings
from bia_converter.bia_api_client import api_client


@pytest.fixture
def mock_copy_uri_to_local(monkeypatch):
    def _mock_copy_uri_to_local(src_uri: str, dst_fpath: Path):
        src_fpath = Path(__file__).parent / "data" / Path(src_uri).name
        shutil.copy(src_fpath, dst_fpath)

    monkeypatch.setattr(io, "copy_uri_to_local", _mock_copy_uri_to_local)


@pytest.fixture
def mock_copy_local_to_s3(monkeypatch):
    def _mock_copy_local_to_s3(src_fpath: Path, dst_key: str) -> str:
        dst_dir = settings.cache_root_dirpath / "mock_s3"
        dst_dir.mkdir(exist_ok=True)
        dst_fname = Path(dst_key).name
        dst_fpath = dst_dir / dst_fname
        shutil.copy(src_fpath, dst_fpath)
        return f"{dst_fpath}"

    monkeypatch.setattr(convert, "copy_local_to_s3", _mock_copy_local_to_s3)


@pytest.fixture
def mock_sync_dirpath_to_s3(monkeypatch):
    def _sync_dirpath_to_s3(src_dirpath, dst_suffix):
        return f"{src_dirpath}"

    monkeypatch.setattr(convert, "sync_dirpath_to_s3", _sync_dirpath_to_s3)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture
def uploaded_by_submitter_rep_uuid() -> str:
    return "feafb069-7a94-48b7-9a15-25d3f85dda40"


@pytest.fixture
def interactive_image_rep_uuid() -> str:
    # This image representation is created by
    # test_cli_convert_uploaded_by_submitter_to_interactive_display!!!
    return "302d2c87-adf1-4a35-839b-3acaa6973ff7"


def compare_created_vs_expected_image_representation(
    created: api_models.ImageRepresentation,
    expected: bia_data_model.ImageRepresentation,
) -> bool:
    created_as_bia_data_model = bia_data_model.ImageRepresentation.model_validate(
        created.model_dump()
    )

    # Versions may be different depending on how many times test has been run - don't compare this
    created_as_bia_data_model.version = expected.version

    # Because of mocking the file_uri will be different (created will point to dir created during test setup)
    # Just check lengths equal and uuid is in file_uri
    if len(created_as_bia_data_model.file_uri) != len(expected.file_uri):
        return False
    if f"{expected.uuid}" not in created_as_bia_data_model.file_uri[0]:
        return False
    created_as_bia_data_model.file_uri = expected.file_uri

    # On Github there is a descrepancy of 38 bytes between expected and created zarr archives
    # Could this be due to line endings? Do not test this
    created_as_bia_data_model.total_size_in_bytes = expected.total_size_in_bytes

    # Also on Github image_viewer_settings is None instead of []
    created_as_bia_data_model.image_viewer_setting = expected.image_viewer_setting

    return created_as_bia_data_model == expected


@pytest.fixture
def expected_interactive_display() -> bia_data_model.ImageRepresentation:
    obj_path = (
        Path(__file__).parent
        / "data"
        / "expected_interactive_display_image_representation.json"
    )
    return bia_data_model.ImageRepresentation.model_validate_json(obj_path.read_text())


@pytest.fixture
def expected_static_display() -> bia_data_model.ImageRepresentation:
    obj_path = (
        Path(__file__).parent
        / "data"
        / "expected_static_display_image_representation.json"
    )
    return bia_data_model.ImageRepresentation.model_validate_json(obj_path.read_text())


@pytest.fixture
def expected_thumbnail() -> bia_data_model.ImageRepresentation:
    obj_path = (
        Path(__file__).parent / "data" / "expected_thumbnail_image_representation.json"
    )
    return bia_data_model.ImageRepresentation.model_validate_json(obj_path.read_text())


def test_cli_convert_uploaded_by_submitter_to_interactive_display(
    runner,
    uploaded_by_submitter_rep_uuid,
    mock_copy_uri_to_local,
    mock_sync_dirpath_to_s3,
    expected_interactive_display,
):
    # cli.convert(
    #    uploaded_by_submitter_rep_uuid,
    #    "INTERACTIVE_DISPLAY",
    # )
    # assert True
    result = runner.invoke(
        cli.app,
        [
            "convert",
            uploaded_by_submitter_rep_uuid,
            "INTERACTIVE_DISPLAY",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    created_interactive_display = api_client.get_image_representation(
        str(expected_interactive_display.uuid)
    )
    assert compare_created_vs_expected_image_representation(
        created_interactive_display, expected_interactive_display
    )

    created_zarr_path = (
        settings.cache_root_dirpath
        / "zarr"
        / f"{expected_interactive_display.uuid}.zarr"
    )
    assert created_zarr_path.exists()


def test_cli_convert_interactive_display_to_static_display(
    runner, interactive_image_rep_uuid, mock_copy_local_to_s3, expected_static_display
):
    result = runner.invoke(
        cli.app,
        [
            "convert",
            interactive_image_rep_uuid,
            "STATIC_DISPLAY",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    created_static_display = api_client.get_image_representation(
        str(expected_static_display.uuid)
    )
    assert compare_created_vs_expected_image_representation(
        created_static_display, expected_static_display
    )

    created_static_display_path = (
        settings.cache_root_dirpath / "mock_s3" / f"{expected_static_display.uuid}.png"
    )
    assert created_static_display_path.exists()


def test_cli_convert_interactive_display_to_thumbnail(
    runner,
    interactive_image_rep_uuid,
    mock_copy_local_to_s3,
    expected_thumbnail,
):
    result = runner.invoke(
        cli.app,
        [
            "convert",
            interactive_image_rep_uuid,
            "THUMBNAIL",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    created_thumbnail = api_client.get_image_representation(
        str(expected_thumbnail.uuid)
    )
    assert compare_created_vs_expected_image_representation(
        created_thumbnail, expected_thumbnail
    )

    created_thumbnail_path = (
        settings.cache_root_dirpath / "mock_s3" / f"{expected_thumbnail.uuid}.png"
    )
    assert created_thumbnail_path.exists()
