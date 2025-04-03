from pathlib import Path
import shutil
import pytest
from bia_converter import io
from bia_converter import convert
from typer.testing import CliRunner
from bia_converter import cli


@pytest.fixture
def mock_copy_uri_to_local(monkeypatch):
    def _mock_copy_uri_to_local(src_uri: str, dst_fpath: Path):
        src_fpath = Path(__file__).parent / "data" / Path(src_uri).name
        shutil.copy(src_fpath, dst_fpath)

    monkeypatch.setattr(io, "copy_uri_to_local", _mock_copy_uri_to_local)


@pytest.fixture
def mock_sync_dir_path_to_s3(monkeypatch):
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


def test_cli_convert_uploaded_by_submitter_to_interactive_display(
    runner,
    uploaded_by_submitter_rep_uuid,
    mock_copy_uri_to_local,
    mock_sync_dir_path_to_s3,
    # data_in_api,
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


def test_cli_convert_interactive_display_to_static_display(
    runner,
    interactive_image_rep_uuid,
    mock_copy_uri_to_local,
    mock_sync_dir_path_to_s3,
    # data_in_api,
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


def test_cli_convert_interactive_display_to_thumbnail(
    runner,
    interactive_image_rep_uuid,
    mock_copy_uri_to_local,
    mock_sync_dir_path_to_s3,
    # data_in_api,
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
