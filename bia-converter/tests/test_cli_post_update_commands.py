from pathlib import Path
import shutil
import pytest
import json
import bia_integrator_api.models as api_models
from bia_integrator_api.exceptions import NotFoundException
from bia_converter import convert
from typer.testing import CliRunner
from bia_converter import cli
from bia_converter.config import settings
from bia_converter.bia_api_client import api_client

accession_id = "S-BIAD-BIACONVERTER-TEST"
original_copy_local_to_s3 = convert.copy_local_to_s3


@pytest.fixture
def mock_copy_local_to_s3(monkeypatch):
    """Copy files to a temporary directory instead the s3 bucket specified in settings.bucket"""

    def _mock_copy_local_to_s3(src_fpath: Path, dst_key: str) -> str:
        # We call the original with dry_run=True to get the file_uri, but it will not copy
        file_uri = original_copy_local_to_s3(src_fpath, dst_key, dry_run=True)

        dst_dir = settings.cache_root_dirpath / "mock_s3"
        dst_dir.mkdir(exist_ok=True)
        dst_fname = Path(dst_key).name
        dst_fpath = dst_dir / dst_fname
        shutil.copy(src_fpath, dst_fpath)
        return file_uri

    monkeypatch.setattr(convert, "copy_local_to_s3", _mock_copy_local_to_s3)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def expected_thumbnail_uri_attribute(input_image_uuid) -> api_models.Attribute:
    file_uri = f"{settings.endpoint_url}/{settings.bucket_name}/{accession_id}/{input_image_uuid}/thumbnail_256_256.png"

    return api_models.Attribute.model_validate(
        {
            "provenance": "bia_image_conversion",
            "name": "image_thumbnail_uri",
            "value": {
                "256_256": file_uri,
                "size": [256, 256],
            },
        }
    )


@pytest.fixture
def expected_static_display_uri_attribute(input_image_uuid) -> api_models.Attribute:
    file_uri = f"{settings.endpoint_url}/{settings.bucket_name}/{accession_id}/{input_image_uuid}/static_display_512_512.png"

    return api_models.Attribute.model_validate(
        {
            "provenance": "bia_image_conversion",
            "name": "image_static_display_uri",
            "value": {
                "slice": {"uri": file_uri, "size": [512, 512],},
            },
        }
    )


def setup_input_image_and_return_uuid() -> str:
    input_image_path = (
        Path(__file__).parent / "data" / "input_image_for_creating_2d_views.json"
    )
    input_image_dict = json.loads(input_image_path.read_text())
    input_image = api_models.Image.model_validate(input_image_dict)
    input_image_uuid = f"{input_image.uuid}"

    try:
        api_version_of_input_image = api_client.get_image(input_image_uuid)
        input_image.version = api_version_of_input_image.version + 1
    except NotFoundException:
        pass
    api_client.post_image(input_image)

    return input_image_uuid


def setup_interactive_image_rep_and_return_uuid() -> str:
    interactive_image_rep_uuid = "841aaca8-633d-48f9-bfdb-6fe765aad109"
    try:
        interactive_image_rep = api_client.get_image_representation(
            interactive_image_rep_uuid
        )
    except NotFoundException:
        interactive_image_rep_path = (
            Path(__file__).parent
            / "data"
            / "interactive_image_representation_for_creating_2d_views.json"
        )
        interactive_image_rep_dict = json.loads(interactive_image_rep_path.read_text())
        interactive_image_rep = api_models.ImageRepresentation.model_validate(
            interactive_image_rep_dict
        )
        assert interactive_image_rep_uuid == interactive_image_rep.uuid

        # Ensure the file_uri points to the ome.zarr in tests/data
        file_uri_path = (
            Path(__file__).parent.absolute() / "data" / "im07.ome.zarr" / "0"
        )
        interactive_image_rep.file_uri = [f"file://{file_uri_path}"]

        api_client.post_image_representation(interactive_image_rep)

    return interactive_image_rep_uuid


@pytest.fixture
def input_image_uuid() -> str:
    return setup_input_image_and_return_uuid()


@pytest.fixture
def interactive_image_rep_uuid(input_image_uuid) -> str:
    # The input_image_uuid parameter in func declaration is used to ensure the input image
    # is setup before the interactive image representation which depends on it.
    return setup_interactive_image_rep_and_return_uuid()


def test_cli_convert_interactive_display_to_static_display(
    runner,
    interactive_image_rep_uuid,
    mock_copy_local_to_s3,
    expected_static_display_uri_attribute,
    input_image_uuid,
):
    result = runner.invoke(
        cli.app,
        [
            "create-static-display",
            interactive_image_rep_uuid,
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    updated_image = api_client.get_image(input_image_uuid)
    created_static_display_uri_attribute = next(
        a
        for a in updated_image.additional_metadata
        if a.name == "image_static_display_uri"
    )
    assert created_static_display_uri_attribute == expected_static_display_uri_attribute

    created_static_display_path = (
        settings.cache_root_dirpath / "mock_s3" / "static_display_512_512.png"
    )
    assert created_static_display_path.exists()


def test_cli_convert_interactive_display_to_thumbnail(
    runner,
    interactive_image_rep_uuid,
    mock_copy_local_to_s3,
    expected_thumbnail_uri_attribute,
    input_image_uuid,
):
    result = runner.invoke(
        cli.app,
        [
            "create-thumbnail",
            interactive_image_rep_uuid,
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    updated_image = api_client.get_image(input_image_uuid)
    created_thumbnail_uri_attribute = next(
        a for a in updated_image.additional_metadata if a.name == "image_thumbnail_uri"
    )
    assert created_thumbnail_uri_attribute == expected_thumbnail_uri_attribute

    created_thumbnail_path = (
        settings.cache_root_dirpath / "mock_s3" / "thumbnail_256_256.png"
    )
    assert created_thumbnail_path.exists()

def test_cli_update_recommended_vizarr_rep_for_image(
    runner,
    interactive_image_rep_uuid,
    input_image_uuid,
):
    result = runner.invoke(
        cli.app,
        [
            "update-recommended-vizarr-representation",
            interactive_image_rep_uuid,
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    updated_image = api_client.get_image(input_image_uuid)
    attr_name = "recommended_vizarr_representation"
    recommended_vizarr_rep_attribute = next(
        a for a in updated_image.additional_metadata if a.name == attr_name
    )
    recommended_vizarr_rep = recommended_vizarr_rep_attribute.value[attr_name]
    assert recommended_vizarr_rep == interactive_image_rep_uuid
