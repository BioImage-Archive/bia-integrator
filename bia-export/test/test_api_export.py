from typer.testing import CliRunner
from bia_shared_datamodels.uuid_creation import create_study_uuid
from pathlib import Path
from bia_export.cli import (
    app,
    DEFAULT_WEBSITE_STUDY_FILE_NAME,
    DEFAULT_WEBSITE_IMAGE_FILE_NAME,
    DEFAULT_WEBSITE_DATASET_FOR_IMAGE_FILE_NAME,
)
import json
import os
from bia_test_data.data_to_api import add_objects_to_api

runner = CliRunner()


# Note that pytest fixture data_in_api is unused in test code,
# but requested in order to guarentee that data is in the test api before running the test
def test_cli_export_export_all_data_contains_at_least_expected_objects(
    tmp_path: Path, data_in_api
):

    outpath = tmp_path.resolve()

    result = runner.invoke(
        app,
        [
            "website",
            "all",
            "-o",
            outpath,
        ],
    )

    assert result.exit_code == 0
    assert len(os.listdir(tmp_path)) == 3

    def check_file_contains_expected_object(outfile: Path, expected_output: Path):
        with open(outfile, "r") as f:
            json_result = json.load(f)

        with open(expected_output) as f:
            json_expected = json.load(f)

        for key, value in json_expected.items():
            assert key in json_result
            assert value == json_result[key]

    check_file_contains_expected_object(
        outpath.joinpath(DEFAULT_WEBSITE_STUDY_FILE_NAME),
        Path(__file__).parent.joinpath("output_data/bia-study-metadata.json"),
    )

    check_file_contains_expected_object(
        outpath.joinpath(DEFAULT_WEBSITE_IMAGE_FILE_NAME),
        Path(__file__).parent.joinpath("output_data/bia-image-metadata.json"),
    )

    check_file_contains_expected_object(
        outpath.joinpath(DEFAULT_WEBSITE_DATASET_FOR_IMAGE_FILE_NAME),
        Path(__file__).parent.joinpath(
            "output_data/bia-dataset-metadata-for-images.json"
        ),
    )


# Note that pytest fixture data_in_api is unused in test code,
# but requested in order to guarentee that data is in the test api before running the test
def test_cli_export_website_studies(tmp_path: Path, data_in_api):
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-study-metadata.json"
    )
    outfile = tmp_path.joinpath("bia-dataset-metadata.json").resolve()

    result = runner.invoke(
        app,
        [
            "website",
            "study",
            "S-BIADTEST",
            "-o",
            outfile,
        ],
    )

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected


# Note that pytest fixture data_in_api is unused in test code,
# but requested in order to guarentee that data is in the test api before running the test
def test_cli_export_website_images(tmp_path: Path, data_in_api):
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-image-metadata.json"
    )
    outfile = tmp_path.joinpath("bia-image-metadata.json").resolve()

    result = runner.invoke(app, ["website", "image", "S-BIADTEST", "-o", outfile])

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected


# Note that pytest fixture data_in_api is unused in test code,
# but requested in order to guarentee that data is in the test api before running the test
def test_cli_export_dataset_for_website_images(tmp_path: Path, data_in_api):
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-dataset-metadata-for-images.json"
    )
    outfile = tmp_path.joinpath("bia-dataset-metadata.json").resolve()

    result = runner.invoke(
        app,
        ["website", "image-dataset", "S-BIADTEST", "-o", outfile],
    )

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected


def test_cli_export_study_ordering(
    tmp_path: Path, api_studies_in_expected_order: list[dict], private_client
):
    # Note these tests are grouped so as to use the output of one as the input of the next
    # This adds data to the api during tests, so is not as neat as bundling all pre-test set up prior to running tests.

    def check_order(ordered_acc_id_list: list[str], result_file: Path):
        with open(result_file, "r") as f:
            json_result: dict = json.load(f)

        it = iter(json_result.keys())
        return all(acc_id in it for acc_id in ordered_acc_id_list)

    # Test 1. studies are ordered correctly when they're all exported (i.e. no accession ids provided)
    expected_study_acc_id_order = [
        study["accession_id"] for study in api_studies_in_expected_order
    ]

    outfile_all = tmp_path.joinpath("all.json").resolve()
    result = runner.invoke(
        app,
        [
            "website",
            "study",
            "-o",
            outfile_all,
        ],
    )

    assert result.exit_code == 0
    assert check_order(expected_study_acc_id_order, outfile_all)

    # Test 2. studies are ordered correctly when specific ones are exported
    # Skipping expected_study_acc_id_order[2] to set up starting point for test3.
    specific_study_acc_id_order = (
        expected_study_acc_id_order[0:2] + expected_study_acc_id_order[3:]
    )

    outfile_specific = tmp_path.joinpath("specific.json").resolve()
    result = runner.invoke(
        app,
        [
            "website",
            "study",
            *specific_study_acc_id_order,
            "-o",
            outfile_specific,
        ],
    )

    assert result.exit_code == 0
    assert check_order(specific_study_acc_id_order, outfile_specific)

    # Test 3. export with the update_file flag results in the same order of studies
    outfile_specific_update = tmp_path.joinpath("specific-update.json").resolve()
    result = runner.invoke(
        app,
        [
            "website",
            "study",
            *specific_study_acc_id_order,
            "-o",
            outfile_specific_update,
            "-u",
            outfile_specific,
        ],
    )
    assert result.exit_code == 0
    assert check_order(specific_study_acc_id_order, outfile_specific_update)

    # Test 4. export with the update_file flag of a new study results in the correct order of studies
    # Uses results of test 2 to check expected_study_acc_id_order[2] is inserted in the right place
    outfile_new_study_update = tmp_path.joinpath("new-study-update.json").resolve()
    result = runner.invoke(
        app,
        [
            "website",
            "study",
            expected_study_acc_id_order[2],
            "-o",
            outfile_new_study_update,
            "-u",
            outfile_specific,
        ],
    )

    assert result.exit_code == 0
    assert check_order(expected_study_acc_id_order, outfile_new_study_update)

    # Test 5. export with the update_file flag for an existing study with new data results in a new order
    # Changing release date of most recently released study to be released before all others, so it now appears last
    study_to_move = api_studies_in_expected_order.pop(0)
    study_to_move |= {
        "release_date": "2000-02-01",
    }
    api_studies_in_expected_order.append(study_to_move)
    add_objects_to_api(private_client, [study_to_move], auto_update_version=True)
    reoreded_acc_id_order = [
        study["accession_id"] for study in api_studies_in_expected_order
    ]
    outfile_reordered = tmp_path.joinpath("update-after-data-change.json").resolve()
    result = runner.invoke(
        app,
        [
            "website",
            "study",
            study_to_move["accession_id"],
            "-o",
            outfile_reordered,
            "-u",
            outfile_all,
        ],
    )

    assert result.exit_code == 0
    assert check_order(reoreded_acc_id_order, outfile_reordered)
