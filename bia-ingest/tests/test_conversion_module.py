"""Test using conversion module to create API models

"""

from bia_ingest.conversion import (
    find_and_convert_biosamples,
    extract_specimen_dicts,
    convert_specimen_to_api_model,
    extract_image_acquisition_dicts,
    convert_image_acquisition_to_api_model,
)


def test_read_biosample(submission, expected_biosample):
    extracted_biosamples = find_and_convert_biosamples(submission)

    assert len(extracted_biosamples) == 1
    assert extracted_biosamples[0] == expected_biosample


def test_read_specimen(submission, expected_specimen):
    extracted_specimen_dicts = extract_specimen_dicts(submission)
    assert len(extracted_specimen_dicts) == 1

    extracted_specimen_dicts[0]["biosample_uuid"] = expected_specimen.biosample_uuid
    extracted_specimen = convert_specimen_to_api_model(extracted_specimen_dicts[0])
    assert extracted_specimen == expected_specimen


def test_image_acquisition(submission, expected_image_acquisition):
    extracted_image_acquisition_dicts = extract_image_acquisition_dicts(submission)

    assert len(extracted_image_acquisition_dicts) == 2
    extracted_image_acquisition_dicts[0][
        "specimen_uuid"
    ] = expected_image_acquisition.specimen_uuid
    extracted_image_acquisition = convert_image_acquisition_to_api_model(
        extracted_image_acquisition_dicts[0]
    )
    assert extracted_image_acquisition == expected_image_acquisition
