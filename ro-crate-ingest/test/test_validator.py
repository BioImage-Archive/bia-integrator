
from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
import pytest
import logging

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
                (
                    "ERROR",
                    'The 1 occurrence of the JSON-LD key "field_not_included_in_context" is not allowed in the compacted format because it is not present in the @context of the document',
                ),
                (
                    "ERROR",
                    "At ro-crate object with @id: ./:\nThe Root Data Entity MUST have a `description` property (as specified by schema.org)",
                ),
                (
                    "ERROR",
                    "At ro-crate object with @id: ./:\nThe Root Data Entity MUST be linked to either File or Directory instances, nothing else",
                ),
                (
                    "ERROR",
                    "The RO-Crate does not include the Data Entity 'data2_missing_folder/' as part of its payload",
                ),
                (
                    "ERROR",
                    "At ro-crate object with @id: ./data1FailedReference/:\nLess than 1 values on <file://.//data1FailedReference/>->[ sh:inversePath <http://schema.org/hasPart> ]",
                ),
                (
                    "ERROR",
                    "At ro-crate object with @id: ./missing_has_part.tiff:\nLess than 1 values on <file://.//missing_has_part.tiff>->[ sh:inversePath <http://schema.org/hasPart> ]",
                ),
            ],
        ),
        (
            "test_invalid_ro_crate_objects",
            1,
            [
                (
                    "ERROR",
                    "At ro-crate object with @id: data2/:\n@type of object does not contain any BIA classes. @type contains: Dataset",
                ),
                (
                    "ERROR",
                    "At ro-crate object with @id: data2/groupedImage/:\n@type of object contains multiple BIA classes. @type contains: http://bia/Dataset, http://bia/Image",
                ),
                (
                    "ERROR",
                    'At ro-crate object with @id: _:SpecimenPreparation:\n1 validation error for SpecimenImagingPreparationProtocol\nprotocolDescription\n  Input should be a valid string [type=string_type, input_value=["ERROR This shouldn\'t be a list"], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.11/v/string_type',
                ),
                (
                    "ERROR",
                    "At ro-crate object with @id: _:ImageAcquisitionProtocol1:\n1 validation error for ImageAcquisitionProtocol\nprotocolDescription\n  Field required [type=missing, input_value={'@id': '_:ImageAcquisiti...: ['obo:FBbi_00000246']}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
                ),
                (
                    "ERROR",
                    "At ro-crate object with @id: _:RepeatedBiosample1:\nTwo objects with the same @id: @id should be unique.",
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

    assert captured_messages == messages
