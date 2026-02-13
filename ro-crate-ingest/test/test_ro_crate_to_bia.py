import json
from pathlib import Path

import deepdiff
import pytest
import pytest_check as check
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_specimen_uuid,
    create_bio_sample_uuid,
)
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_study_uuid,
    create_file_reference_uuid,
    create_image_uuid,
    create_specimen_uuid as generate_specimen_uuid_from_image,
)
from typer.testing import CliRunner

from ro_crate_ingest.cli import ro_crate_ingest

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


def accession_id_from_path(ro_crate_path: Path) -> str:
    return ro_crate_path.name


def get_expected_files(accession_id) -> list[Path]:
    expected_out_dir = Path(__file__).parent / "ro_crate_to_bia" / "output_data"

    expected_files = [f for f in expected_out_dir.rglob(f"*/{accession_id}/*.json")]

    return expected_files


def test_basic_ROCrate_local(tmp_bia_data_dir):
    ro_crate_path = get_test_ro_crate_path("typical_ro_crate")

    ingest_local_test("S-TEST123", tmp_bia_data_dir, ro_crate_path)


def test_basic_ROCrate_api(get_bia_api_client):
    ro_crate_path = get_test_ro_crate_path("typical_ro_crate")

    ingest_api_test("S-TEST123", get_bia_api_client, ro_crate_path)


@pytest.mark.parametrize(
    "ro_crate_path,url_prefix",
    [
        # (
        #     get_biostudies_to_ro_crate_path("S-BIADTEST_AUTHOR_AFFILIATION"),
        #     "biostudies",
        # ),
        # (get_biostudies_to_ro_crate_path("S-BIADTEST_COMPLEX_BIOSAMPLE"), "biostudies"),
        # (get_biostudies_to_ro_crate_path("S-BIADTEST_PROTOCOL_STUDY"), "biostudies"),
        # (get_mock_ro_crate_path("S-BIAD1494"), None),
        # (get_mock_ro_crate_path("S-BIAD843"), None),
        # (get_mock_ro_crate_path("S-BIADWITHFILELIST"), None),
        # (get_empiar_to_ro_crate_path("EMPIAR-IMAGEPATTERNTEST"), "empiar"),
        # (get_empiar_to_ro_crate_path("EMPIAR-STARFILETEST"), "empiar"),
        # (get_empiar_to_ro_crate_path("EMPIAR-SPECIMENTEST"), "empiar"),
    ],
)
class TestGenericROCrateToAPI:

    def test_ingest_local(self, ro_crate_path, url_prefix, tmp_bia_data_dir):
        accession_id = accession_id_from_path(ro_crate_path)

        ingest_local_test(
            accession_id,
            tmp_bia_data_dir,
            ro_crate_path,
            file_ref_url_prefix=url_prefix,
        )

    def test_ingest_api(self, ro_crate_path, url_prefix, get_bia_api_client):
        accession_id = accession_id_from_path(ro_crate_path)

        ingest_api_test(
            accession_id,
            get_bia_api_client,
            ro_crate_path,
            file_ref_url_prefix=url_prefix,
        )


def ingest_local_test(
    accession_id: str,
    tmp_bia_data_dir: Path,
    crate_path: Path,
    file_ref_url_prefix: str | None = None,
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

        diff = deepdiff.DeepDiff(
            expected_out, cli_out, ignore_order=True, verbose_level=2
        )

        check.is_true(
            not diff,
            f"Missmatch in object: {'/'.join(expected_path_of_written_file.parts[-3:])}:\n{diff.pretty()}",
        )


def ingest_api_test(
    accession_id: str,
    get_bia_api_client,
    crate_path: Path,
    file_ref_url_prefix: str | None = None,
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
            expected_object.model_dump(),
            api_obj.model_dump(),
            ignore_order=True,
            verbose_level=2,
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

    accession_id = "ro_crate_with_overlapping_associations"
    crate_path = get_test_ro_crate_path(accession_id)

    arguments = ["ingest", "-c", crate_path]
    result = runner.invoke(ro_crate_ingest, arguments)

    assert result.exit_code == 0

    image_folder_path = tmp_bia_data_dir / "image" / accession_id
    creation_process_folder_path = tmp_bia_data_dir / "creation_process" / accession_id
    specimen_folder_path = tmp_bia_data_dir / "specimen" / accession_id
    bio_sample_folder_path = tmp_bia_data_dir / "bio_sample" / accession_id

    result_data_files = list(image_folder_path.glob("*.json"))

    result_expectations: dict[str, dict[str, int | str | None]] = {
        "image using assigned specimen and its biosample": {
            "file_path": "data/image_1.tif",
            "file_size": 12,
            "subject_specimen_uuid_input": "#Specimen%20used%20by%20images",
            "biosample_uuid_input": "#Biosample%20used%20by%20specimen",
        },
        "image with generated specimen": {
            "file_path": "data/image_2.tif",
            "file_size": 12,
            "subject_specimen_uuid_input": "d52777fd-18e2-4ad9-a5f1-0462d4410425",
            "biosample_uuid_input": "#Biosample%20used%20by%20specimen",
        },
        "image without biosample or specimen": {
            "file_path": "data/image_3.tif",
            "file_size": 12,
            "subject_specimen_uuid_input": None,
            "biosample_uuid_input": None,
        },
    }

    assert len(result_data_files) == len(result_expectations)

    study_uuid = str(create_study_uuid(accession_id)[0])

    for image_label, lookup_info in result_expectations.items():
        # Created expected UUIDS for all objects
        expected_file_reference_uuid: str = str(
            create_file_reference_uuid(
                study_uuid, str(lookup_info["file_path"]), lookup_info["file_size"]
            )[0]
        )
        expected_image_uuid: str = str(
            create_image_uuid(
                study_uuid, [expected_file_reference_uuid], provenance="bia_ingest"
            )[0]
        )

        specimen_uuid_input = lookup_info["subject_specimen_uuid_input"]
        expected_specimen_uuid: str | None = None
        if specimen_uuid_input and str(specimen_uuid_input).startswith("#"):
            expected_specimen_uuid = str(
                create_specimen_uuid(study_uuid, str(specimen_uuid_input))[0]
            )
        elif specimen_uuid_input:
            expected_specimen_uuid = str(
                generate_specimen_uuid_from_image(
                    study_uuid,
                    str(specimen_uuid_input),
                    provenance="bia_ingest",
                )[0]
            )
        else:
            expected_specimen_uuid = None
        expected_bio_sample_uuid: str | None = (
            str(
                create_bio_sample_uuid(
                    study_uuid, str(lookup_info["biosample_uuid_input"])
                )[0]
            )
            if lookup_info["biosample_uuid_input"]
            else None
        )

        # Follow uuid links and check they correspond
        image_path = image_folder_path / f"{expected_image_uuid}.json"
        with open(image_path, "r") as f:
            image_data = json.load(f)
        check.equal(image_data["label"], image_label)

        creation_process_uuid = image_data["creation_process_uuid"]
        with open(
            creation_process_folder_path / f"{creation_process_uuid}.json", "r"
        ) as f:
            creation_process = json.load(f)
        check.equal(
            expected_specimen_uuid,
            creation_process["subject_specimen_uuid"],
            f"creation process -> specimen UUID mismatch for {image_label}",
        )

        if expected_specimen_uuid:
            specimen_path = specimen_folder_path / f"{expected_specimen_uuid}.json"
            with open(specimen_path, "r") as f:
                specimen = json.load(f)

            check.equal(
                expected_bio_sample_uuid,
                specimen["sample_of_uuid"][0],
                "specimen -> biosample UUID mismatch for {image_label}",
            )

            biosample_file = bio_sample_folder_path / f"{expected_bio_sample_uuid}.json"
            check.is_true(
                biosample_file.is_file(),
                f"For {image_label} biosample file does not exist: {biosample_file}",
            )
