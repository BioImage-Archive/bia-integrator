import pytest
import logging
import pytest_check as check

from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest

runner = CliRunner()


def get_test_ro_crate_path(accession_id, test_folder="validator") -> Path:
    return Path(__file__).parent / test_folder / "input_ro_crate" / accession_id


@pytest.mark.parametrize(
    "accession_id,expected_result,messages",
    [
        (
            "test_invalid_ro_crate",
            1,
            [
                ("field_not_included_in_context",),
                (
                    "At ro-crate object with @id: ./",
                    "description",
                ),
                (
                    "At ro-crate object with @id: ./",
                    "MUST be linked to either File or Directory instances",
                ),
                (
                    "does not include",
                    "data2_missing_folder",
                ),
                (
                    "At ro-crate object with @id: ./data1FailedReference/",
                    "http://schema.org/hasPart",
                ),
                (
                    "At ro-crate object with @id: ./missing_has_part.tiff",
                    "http://schema.org/hasPart",
                ),
            ],
        ),
        (
            "test_invalid_redefined_context_term",
            1,
            [
                (
                    "At accessionId",
                    "Term has been remapped in context",
                ),
            ],
        ),
        (
            "test_invalid_ro_crate_object_ids",
            1,
            [
                (
                    "At ro-crate object with @id: _:RepeatedBiosample1",
                    "Two objects with the same @id",
                ),
            ],
        ),
        (
            "test_invalid_ro_crate_objects",
            1,
            [
                (
                    "At ro-crate object with @id: data2/",
                    "@type of object does not contain any BIA classes.",
                ),
                (
                    "At ro-crate object with @id: data2/groupedImage/",
                    "@type of object contains multiple BIA classes",
                ),
                (
                    "At ro-crate object with @id: _:SpecimenPreparation:",
                    "1 validation error for SpecimenImagingPreparationProtocol",
                ),
                (
                    "At ro-crate object with @id: _:ImageAcquisitionProtocol1",
                    "1 validation error for ImageAcquisitionProtocol",
                ),
            ],
        ),
        (
            "test_invalid_ro_crate_object_references",
            1,
            [
                (
                    "At ro-crate object with @id: Biosample1",
                    "contains references to Non-existant growth protocol",
                    "not defined",
                ),
                (
                    "At ro-crate object with @id: Biosample2",
                    "contains references to Biosample1",
                    "not of the expected type",
                ),
            ],
        ),
        (
            "test_invalid_ro_crate_with_file_list_without_path_column",
            1,
            [
                ("No column has been assigned csvw:propertyUrl http://bia/filePath",),
                (
                    "At ro-crate TableSchema object with @id: ts0",
                    "Missing column with required property: http://bia/filePath",
                ),
            ],
        ),
        (
            "test_invalid_file_list_references",
            1,
            [
                (
                    "filelist: data1/file_list_with_missing_references.tsv",
                    "row: example_file_1.tiff",
                    "NCBI:txid9606",
                    "unexpected type",
                ),
                (
                    "filelist: data1/file_list_with_missing_references.tsv",
                    "row: example_file_2.tiff",
                    "_:not_present",
                    "does not exist",
                ),
            ],
        ),
        (
            "test_minimal_valid_ro_crate",
            0,
            [],
        ),
    ],
)
def test_ro_crate_context_validation_error_messages(
    accession_id, expected_result, messages, caplog
):
    """
    See parametrisation above for test expectations.

    Structure of test paraters are tuples with:
    - Accesion id of the ro-crate to test
    - Expected result code (0 for no validation issues, 1 otherwise)
    - List of tuples of strings to check in each error message. E.g.

    [
        (
            "At ro-crate object with @id: data2/",
            "@type of object does not contain any BIA classes.",
        ),
        (
            "At ro-crate object with @id: data2/groupedImage/",
            "@type of object contains multiple BIA classes",
        ),
    ]
    Would result in a check that the validator returned 2 messages, and that each message contained all (2) expected substrings
    """

    caplog.set_level(logging.ERROR)

    crate_path = get_test_ro_crate_path(accession_id)

    arguments = ["validate", str(crate_path)]
    result = runner.invoke(ro_crate_ingest, arguments)
    assert result.exit_code == expected_result

    captured_messages = [
        (record.levelname, record.message) for record in caplog.records
    ]

    assert len(messages) == len(captured_messages)

    # check that no duplicate messages were created
    unique_error_messages = set(
        severity_message[1] for severity_message in captured_messages
    )
    assert len(unique_error_messages) == len(messages)

    for message_position, message in enumerate(captured_messages):
        severity, error_message = message
        for expected_message_snippet in messages[message_position]:
            check.is_in(expected_message_snippet, error_message)


@pytest.mark.parametrize(
    "accession_id",
    ["S-TEST_specimen", "S-TEST_overlapping_file_list_and_ro_crate_info"],
)
def test_valid_ro_crate(accession_id, caplog):
    """
    Check that the ro-crates that get used to test our ingest pipeline are valid
    """

    caplog.set_level(logging.ERROR)

    crate_path = get_test_ro_crate_path(accession_id, "ro_crate_to_bia")

    arguments = ["validate", str(crate_path)]
    result = runner.invoke(ro_crate_ingest, arguments)
    assert result.exit_code == 0
    assert len(caplog.records) == 0
