from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
import json
import pytest
import pytest_check as check
import deepdiff

runner = CliRunner()


def get_mock_ro_crate_path(accession_id) -> Path:
    return (
        Path(__file__).parents[2]
        / "bia-shared-datamodels"
        / "src"
        / "bia_shared_datamodels"
        / "mock_ro_crate"
        / accession_id
    )


def get_test_ro_crate_path(accession_id) -> Path:
    return Path(__file__).parent / "ro_crate_to_bia" / "input_ro_crate" / accession_id


def get_biostudies_to_ro_crate_path(accession_id) -> Path:
    return (
        Path(__file__).parent / "biostudies_to_ro_crate" / "output_data" / accession_id
    )


def get_empiar_to_ro_crate_path(accession_id) -> Path:
    return Path(__file__).parent / "empiar_to_ro_crate" / "output_data" / accession_id


def get_expected_files(accession_id) -> list[Path]:
    expected_out_dir = Path(__file__).parent / "ro_crate_to_bia" / "output_data"

    expected_files = [f for f in expected_out_dir.rglob(f"*/{accession_id}/*.json")]

    return expected_files


@pytest.mark.parametrize(
    "accession_id", ["S-BIAD1494", "S-BIAD843", "S-BIADWITHFILELIST"]
)
def test_ingest_mock_ro_crate_metadata(accession_id: str, tmp_bia_data_dir: Path):

    crate_path = get_mock_ro_crate_path(accession_id)

    ingest_local_test(accession_id, tmp_bia_data_dir, crate_path)


@pytest.mark.parametrize(
    "accession_id", ["S-BIAD1494", "S-BIAD843", "S-BIADWITHFILELIST"]
)
def test_ingest_mock_ro_crate_metadata_with_api(accession_id: str, get_bia_api_client):

    crate_path = get_mock_ro_crate_path(accession_id)

    ingest_api_test(accession_id, get_bia_api_client, crate_path)


@pytest.mark.parametrize(
    "accession_id",
    [
        "S-BIADTEST_AUTHOR_AFFILIATION",
        "S-BIADTEST_COMPLEX_BIOSAMPLE",
        "S-BIADTEST_PROTOCOL_STUDY",
    ],
)
def test_ingest_biostudies_ro_crate_metadata(accession_id: str, tmp_bia_data_dir: Path):

    crate_path = get_biostudies_to_ro_crate_path(accession_id)

    ingest_local_test(
        accession_id, tmp_bia_data_dir, crate_path, file_ref_url_prefix="biostudies"
    )


@pytest.mark.parametrize(
    "accession_id",
    [
        "S-BIADTEST_AUTHOR_AFFILIATION",
        "S-BIADTEST_COMPLEX_BIOSAMPLE",
        "S-BIADTEST_PROTOCOL_STUDY",
    ],
)
def test_ingest_biostudies_ro_crate_metadata_with_api(
    accession_id: str, get_bia_api_client
):

    crate_path = get_biostudies_to_ro_crate_path(accession_id)

    ingest_api_test(
        accession_id, get_bia_api_client, crate_path, file_ref_url_prefix="biostudies"
    )


@pytest.mark.parametrize(
    "accession_id", ["EMPIAR-IMAGEPATTERNTEST", "EMPIAR-STARFILETEST"]
)
def test_ingest_empiar_ro_crate_metadata(accession_id: str, tmp_bia_data_dir: Path):

    crate_path = get_empiar_to_ro_crate_path(accession_id)

    ingest_local_test(
        accession_id, tmp_bia_data_dir, crate_path, file_ref_url_prefix="empiar"
    )


@pytest.mark.parametrize(
    "accession_id", ["EMPIAR-IMAGEPATTERNTEST", "EMPIAR-STARFILETEST"]
)
def test_ingest_empiar_ro_crate_metadata_with_api(
    accession_id: str, get_bia_api_client
):

    crate_path = get_empiar_to_ro_crate_path(accession_id)

    ingest_api_test(
        accession_id, get_bia_api_client, crate_path, file_ref_url_prefix="empiar"
    )


def ingest_local_test(
    accession_id: str,
    tmp_bia_data_dir: Path,
    crate_path: Path,
    file_ref_url_prefix: str = None,
):

    arguments = ["ingest", "-c", crate_path]
    if file_ref_url_prefix:
        arguments.extend(["-u", file_ref_url_prefix])
    result = runner.invoke(ro_crate_ingest, arguments)

    assert result.exit_code == 0

    files_written = sorted(
        [f for f in tmp_bia_data_dir.rglob(f"*/{accession_id}/*.json")]
    )

    expected_files = sorted(get_expected_files(accession_id))

    assert len(files_written) == len(expected_files)

    for file in expected_files:
        relative_file_path = Path(file).parts[-3:]
        expected_path_of_written_file = tmp_bia_data_dir / Path(*relative_file_path)

        check.is_true(expected_path_of_written_file.exists())

        with open(expected_path_of_written_file, "r") as f:
            cli_out = json.load(f)

        with open(file, "r") as f:
            expected_out = json.load(f)

        diff = deepdiff.DeepDiff(expected_out, cli_out, ignore_order=True, verbose_level=2)

        check.is_true(
            not diff,
            f"Missmatch in object: {'/'.join(expected_path_of_written_file.parts[-3:])}:\n{diff.pretty()}",
        )


def ingest_api_test(
    accession_id: str,
    get_bia_api_client,
    crate_path: Path,
    file_ref_url_prefix: str = None,
):
    arguments = ["ingest", "-c", crate_path, "-p", "local_api"]
    if file_ref_url_prefix:
        arguments.extend(["-u", file_ref_url_prefix])
    result = runner.invoke(ro_crate_ingest, arguments)

    assert result.exit_code == 0

    expected_files = get_expected_files(accession_id)

    for file in expected_files:
        relative_file_path = Path(file).parts[-3:]

        with open(file, "r") as f:
            expected_out = json.load(f)

        expected_type = relative_file_path[0]
        expected_uuid = expected_out["uuid"]

        api_get_method = f"get_{expected_type}"
        api_obj = getattr(get_bia_api_client, api_get_method)(str(expected_uuid))

        api_obj_type = api_obj.__class__
        expected_object = api_obj_type.model_validate(expected_out)

        diff = deepdiff.DeepDiff(
            expected_object.model_dump(), api_obj.model_dump(), ignore_order=True, verbose_level=2
        )

        check.is_true(
            not diff,
            f"Missmatch in object: {'/'.join(relative_file_path)}:\n{diff.pretty()}",
        )


def test_overlapping_image_data(
    tmp_bia_data_dir: Path,
):
    """
    Tests situation where there are:
    1. Images described in the ro-crate-metadata
    2. Images described in the file-list
    3. Images that are not described, but are in a dataset with associatations
    4. AnnotationData described in the ro-crate-metadata that reference an image that is only described in the file-list
    And includes situation where the images descriptions overlap & contradict one another in order to make sure a certain heirarchy of infomation is followed.
    """

    accession_id = "S-TEST_overlapping_file_list_and_ro_crate_info"
    crate_path = get_test_ro_crate_path(accession_id)

    arguments = ["ingest", "-c", crate_path]
    result = runner.invoke(ro_crate_ingest, arguments)

    assert result.exit_code == 0

    image_folder_path = tmp_bia_data_dir / "image" / accession_id
    annotation_data_folder_path = tmp_bia_data_dir / "annotation_data" / accession_id
    creation_process_folder_path = tmp_bia_data_dir / "creation_process" / accession_id
    file_reference_folder_path = tmp_bia_data_dir / "file_reference" / accession_id
    result_data_files = list(image_folder_path.glob("*.json"))
    result_data_files.extend(list(annotation_data_folder_path.glob("*.json")))

    assert len(result_data_files) == 4

    result_field_length_expectations = {
        "data/annotation_data_in_ro_crate_refs_file_list_file.tsv": {
            "subject_specimen_uuid": 0,
            "image_acquisition_protocol_uuid": 0,
            "input_image_uuid": 1,
            "protocol_uuid": 0,
            "annotation_method_uuid": 1,
        },
        "data/image_1_use_ro_crate_info.tiff": {
            "subject_specimen_uuid": 1,
            "image_acquisition_protocol_uuid": 1,
            "input_image_uuid": 0,
            "protocol_uuid": 0,
            "annotation_method_uuid": 0,
        },
        "data/image_2_use_file_list_info.tiff": {
            "subject_specimen_uuid": 1,
            "image_acquisition_protocol_uuid": 1,
            "input_image_uuid": 1,
            "protocol_uuid": 0,
            "annotation_method_uuid": 0,
        },
        "data/image3_not_referenced_gets_dataset_associations.tiff": {
            "subject_specimen_uuid": 1,
            "image_acquisition_protocol_uuid": 1,
            "input_image_uuid": 0,
            "protocol_uuid": 0,
            "annotation_method_uuid": 1,
        },
    }

    for result_data_path in result_data_files:

        with open(result_data_path, "r") as f:
            result_data = json.load(f)

        creation_process_uuid = result_data["creation_process_uuid"]

        with open(
            creation_process_folder_path / f"{creation_process_uuid}.json", "r"
        ) as f:
            creation_process = json.load(f)

        file_reference_uuid = result_data["original_file_reference_uuid"][0]

        with open(file_reference_folder_path / f"{file_reference_uuid}.json", "r") as f:
            file_reference = json.load(f)

        original_file_path = file_reference["file_path"]

        for field, expected_length in result_field_length_expectations[
            original_file_path
        ].items():
            field_value = creation_process[field]
            if isinstance(field_value, list):
                assert len(field_value) == expected_length
            elif expected_length == 0:
                assert field_value == None
            elif expected_length == 1:
                assert field_value
