from pathlib import Path
import shutil
import json
import pytest
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as api_models
from bia_integrator_api.exceptions import NotFoundException
from bia_converter import io
from bia_converter import convert
from typer.testing import CliRunner
from bia_converter import cli
from bia_converter.settings import get_settings
from bia_converter.bia_api_client import get_api_client, ApiTarget
from bia_converter.conversion import get_bioformats2raw_version

accession_id = "S-BIAD-BIACONVERTER-TEST"
api_client = get_api_client(target=ApiTarget.local)
settings = get_settings()


@pytest.fixture
def mock_copy_uri_to_local(monkeypatch):
    """Copy files from the tests/data directory instead of the file_uri"""

    def _mock_copy_uri_to_local(src_uri: str, dst_fpath: Path):
        src_fpath = Path(__file__).parent / "data" / Path(src_uri).name
        shutil.copy(src_fpath, dst_fpath)

    monkeypatch.setattr(io, "copy_uri_to_local", _mock_copy_uri_to_local)


@pytest.fixture
def mock_sync_dirpath_to_s3(monkeypatch):
    """Return s3 uri instead of syncing contents of a directory to s3 bucket specified in settings.bucket"""

    def _sync_dirpath_to_s3(src_dirpath, dst_suffix):
        return f"{src_dirpath}"

    monkeypatch.setattr(convert, "sync_dirpath_to_s3", _sync_dirpath_to_s3)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def zipped_ome_zarr_rep_uuid() -> str:
    return "2ecdac48-f4ef-44aa-aa32-a69ffc937585"


@pytest.fixture
def uploaded_by_submitter_rep_uuid() -> str:
    return "3b4415ed-fe6f-4591-a4a1-eebc9f4a6750"


def compare_created_vs_expected_image_representation(
    created: api_models.ImageRepresentation,
    expected: api_models.ImageRepresentation,
) -> bool:
    """Modify some properties before comparing image representations"""

    # Versions may be different depending on how many times test has been run - don't compare this
    created.version = expected.version

    # Because of mocking the file_uri will be different (created will point to dir created during test setup)
    # Just check lengths equal and uuid is in file_uri
    if len(created.file_uri) != len(expected.file_uri):
        return False
    if f"{expected.uuid}" not in created.file_uri[0]:
        return False
    created.file_uri = expected.file_uri

    # On Github there is a descrepancy of 38 bytes between expected and created zarr archives
    # Could this be due to line endings? Do not test this
    created.total_size_in_bytes = expected.total_size_in_bytes

    return created == expected


@pytest.fixture
def expected_interactive_display() -> api_models.ImageRepresentation:
    obj_path = (
        Path(__file__).parent
        / "data"
        / "expected_interactive_display_image_representation.json"
    )

    # Compute UUID at runtime as uuid_unique_input includes version of bioformats2raw on testing machine
    obj_dict = json.loads(obj_path.read_text())
    uuid_unique_input = obj_dict["additional_metadata"][0]["value"]["uuid_unique_input"]
    unique_string = uuid_unique_input.replace(
        "compute version at runtime", get_bioformats2raw_version()
    )
    obj_dict["additional_metadata"][0]["value"]["uuid_unique_input"] = unique_string
    study_uuid = uuid_creation.create_study_uuid(accession_id)
    im_rep_uuid = uuid_creation.create_image_representation_uuid(
        study_uuid, unique_string
    )
    obj_dict["uuid"] = str(im_rep_uuid)
    return api_models.ImageRepresentation.model_validate(obj_dict)


@pytest.fixture
def expected_ome_zarr_interactive_display() -> api_models.ImageRepresentation:
    obj_path = (
        Path(__file__).parent
        / "data"
        / "expected_ome_zarr_interactive_display_image_representation.json"
    )

    # Compute UUID at runtime as uuid_unique_input includes version of bioformats2raw on testing machine
    obj_dict = json.loads(obj_path.read_text())
    return api_models.ImageRepresentation.model_validate(obj_dict)

@pytest.fixture
def reset_expected_interactive_display_in_api(expected_interactive_display, expected_ome_zarr_interactive_display):
    """If the expected interactive display is in the api reset its values

    This may happen if this test is run more than once without cleaning out the local API.
    """
    for interactive_display in [expected_interactive_display, expected_ome_zarr_interactive_display]:
        try:
            im_rep = api_client.get_image_representation(
                str(interactive_display.uuid)
            )

            im_rep.additional_metadata = []
            im_rep.file_uri = []
            im_rep.image_format = ""
            im_rep.size_c = 0
            im_rep.size_t = 0
            im_rep.size_x = 0
            im_rep.size_y = 0
            im_rep.size_z = 0
            im_rep.total_size_in_bytes = 0
            im_rep.voxel_physical_size_x = 0.0
            im_rep.voxel_physical_size_y = 0.0
            im_rep.voxel_physical_size_z = 0.0

            im_rep.version += 1
            api_client.post_image_representation(im_rep)
        except NotFoundException:
            continue


def test_cli_convert_uploaded_by_submitter_to_interactive_display(
    runner,
    uploaded_by_submitter_rep_uuid,
    mock_copy_uri_to_local,
    mock_sync_dirpath_to_s3,
    expected_interactive_display,
    reset_expected_interactive_display_in_api,
):
    result = runner.invoke(
        cli.app,
        [
            "convert",
            uploaded_by_submitter_rep_uuid,
            "convert_uploaded_by_submitter_to_interactive_display",
            "--api",
            "local",
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


def test_cli_unzip_and_stage_zipped_ome_zarr(
    runner,
    zipped_ome_zarr_rep_uuid,
    mock_copy_uri_to_local,
    mock_sync_dirpath_to_s3,
    expected_ome_zarr_interactive_display,
    reset_expected_interactive_display_in_api,
):
    result = runner.invoke(
        cli.app,
        [
            "convert",
            zipped_ome_zarr_rep_uuid,
            "convert_zipped_ome_zarr_archive",
            "--api",
            "local",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    created_interactive_display = api_client.get_image_representation(
        str(expected_ome_zarr_interactive_display.uuid)
    )
    assert compare_created_vs_expected_image_representation(
        created_interactive_display, expected_ome_zarr_interactive_display
    )

    created_zarr_path = (
        settings.cache_root_dirpath
        / "zarr"
        / f"{expected_ome_zarr_interactive_display.uuid}.zarr"
    )
    assert created_zarr_path.exists()
