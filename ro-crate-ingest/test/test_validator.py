import pytest
import logging
import pytest_check as check

from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest

runner = CliRunner()


def get_test_ro_crate_path(accession_id) -> Path:
    return Path(__file__).parent / "validator" / "input_ro_crate" / accession_id


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
    ],
)
def test_ro_crate_context_validation_error_messages(
    accession_id, expected_result, messages, caplog
):

    caplog.set_level(logging.ERROR)

    crate_path = get_test_ro_crate_path(accession_id)

    arguments = ["validate", "-c", crate_path]
    result = runner.invoke(ro_crate_ingest, arguments)
    assert result.exit_code == expected_result

    captured_messages = [
        (record.levelname, record.message) for record in caplog.records
    ]

    for message_position, message in enumerate(captured_messages):
        severity, error_message = message
        for expected_message_snippet in messages[message_position]:
            check.is_in(expected_message_snippet, error_message)
