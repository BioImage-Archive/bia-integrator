from pathlib import Path
from typer.testing import CliRunner
from ruamel.yaml import YAML
from pydantic.alias_generators import to_snake
import pytest
from bia_integrator_api import models as api_models
from bia_assign_image import cli
from .conftest import get_expected_object
from csv import DictWriter

from bia_assign_image.api_client import get_api_client


# TODO: Create separate study with separate accession ID for this test
# ACCESSION_ID = "S-BIAD-TEST-ASSIGN-IMAGE-CLI"
ACCESSION_ID = "S-BIAD-TEST-ASSIGN-IMAGE"
EXPECTED_OBJECT_BASE_PATH = Path(__file__).parent / "test_data"

rembi_file_ref_uuid = "278ffc50-3924-4b8a-bad6-d017c503e5dd"
annotation_file_ref_uuid = "c252f796-fd5c-416b-bfaa-3c2554492b68"


def proposal_input_path_tsv(root_path, proposal_contents) -> Path:
    """Return path to a tsv file with proposal details to create mock image"""

    header_row = list(proposal_contents[0].keys())

    proposal_path_tsv = Path(root_path) / "proposal_details.tsv"
    with open(proposal_path_tsv, "w") as tsv:
        writer = DictWriter(tsv, header_row, delimiter="\t")
        writer.writeheader()
        for row in proposal_contents:
            writer.writerow(row)

    return proposal_path_tsv.absolute()


def proposal_input_path_yaml(root_path, proposal_contents) -> Path:
    """Return path to a yaml file with proposal details to create mock image"""

    yaml = YAML(typ="safe")
    proposal_path = Path(root_path) / "proposal_details.yaml"
    yaml.dump(
        proposal_contents,
        proposal_path,
    )

    return proposal_path.absolute()


@pytest.fixture
def expected_objects(request: pytest.FixtureRequest):
    # Map of starting FileReference uuid to all the uuid of all the objects (and their types) expected to be created by Image Assignment.
    expected_objects = {
        "278ffc50-3924-4b8a-bad6-d017c503e5dd": [
            ("97456be4-fd3b-4303-bff3-02b93d00bd8e", "Image"),
            ("a0fbc4fd-2e52-424f-b8e7-6f9fd5109513", "ImageRepresentation"),
            ("94394b72-823e-4565-8131-e4c5e60d45a7", "Specimen"),
            ("f154164e-7e6e-42f9-943e-c6d1ff0a5ba2", "CreationProcess"),
        ],
        "c252f796-fd5c-416b-bfaa-3c2554492b68": [
            ("b912bebc-8386-47cc-a0fe-0af500d63a8a", "Image"),
            ("4fd4c5c3-7d43-44fb-b38a-3d16f6b0c2eb", "ImageRepresentation"),
            ("18fc18d2-f3e0-4b7c-a89d-c62e6b354e26", "CreationProcess"),
        ],
    }
    return expected_objects[request.param]


@pytest.fixture()
def proposal_path_yaml_and_tsv(tmpdir, request: pytest.FixtureRequest):

    proposal_contents = [
        {
            "accession_id": ACCESSION_ID,
            "study_uuid": "dummy_study_uuid",
            "dataset_uuid": "dummy_dataset_uuid",
            "name": "dummy_name",
            "file_reference_uuid": request.param,
            "size_in_bytes": "0",
            "size_human_readable": "dummy_size_human_readable",
        },
    ]

    return {
        "tsv": proposal_input_path_tsv(tmpdir, proposal_contents),
        "yaml": proposal_input_path_yaml(tmpdir, proposal_contents),
    }


@pytest.fixture
def test_api_client():
    return get_api_client("local")


@pytest.mark.parametrize(
    "proposal_path_yaml_and_tsv, expected_objects",
    (
        [rembi_file_ref_uuid, rembi_file_ref_uuid],
        [annotation_file_ref_uuid, annotation_file_ref_uuid],
    ),
    indirect=True,
)
def test_cli_assign_from_proposal_command(
    test_api_client,
    proposal_path_yaml_and_tsv,
    expected_objects,
):

    run_cli_and_check_output(
        test_api_client, proposal_path_yaml_and_tsv["tsv"], expected_objects
    )
    run_cli_and_check_output(
        test_api_client, proposal_path_yaml_and_tsv["yaml"], expected_objects
    )


def run_cli_and_check_output(test_api_client, proposal_input_path, expected_object):

    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "assign-from-proposal",
            str(proposal_input_path),
            "--api",
            "local",
        ],
    )

    assert result.exit_code == 0

    for object_uuid, type_name in expected_object:
        expected_object = get_expected_object(
            EXPECTED_OBJECT_BASE_PATH, type_name, ACCESSION_ID, object_uuid
        )
        api_class = getattr(api_models, type_name)
        expected_object = api_class.model_validate_json(
            expected_object.model_dump_json()
        )

        model_name_snake = to_snake(type_name)
        get_func_name = "get_" + model_name_snake
        get_function = getattr(test_api_client, get_func_name)
        object_from_api = get_function(object_uuid)

        assert object_from_api == expected_object
