"""Load details from biostudies submission into API Biosample model

"""
from bia_ingest.conversion import (
    find_and_convert_biosamples,
    extract_specimen_dicts,
    convert_specimen_to_api_model,
    extract_image_acquisition_dicts,
    convert_image_acquisition_to_api_model,
)


def test_find_and_convert_biosamples(submission, expected_biosample):
    extracted_biosample = find_and_convert_biosamples(submission)[-1]

    assert extracted_biosample == expected_biosample


def test_find_and_convert_specimens(submission, expected_specimen):
    extracted_specimen_dicts = extract_specimen_dicts(submission)
    assert len(extracted_specimen_dicts) == 1
    extracted_specimen_dict = extracted_specimen_dicts[0]
    extracted_specimen_dict["biosample_uuid"] = expected_specimen.biosample_uuid
    extracted_specimen = convert_specimen_to_api_model(extracted_specimen_dict)
    assert extracted_specimen == expected_specimen


def test_find_and_convert_image_acquisitions(submission, expected_image_acquisition):
    extracted_image_acquisition_dicts = extract_image_acquisition_dicts(submission)
    assert len(extracted_image_acquisition_dicts) == 2
    extracted_image_acquisition_dict = [
        im_acq
        for im_acq in filter(
            lambda i: i["title"] == expected_image_acquisition.title,
            extracted_image_acquisition_dicts,
        )
    ][0]
    extracted_image_acquisition_dict[
        "specimen_uuid"
    ] = expected_image_acquisition.specimen_uuid
    extracted_image_acquisition = convert_image_acquisition_to_api_model(
        extracted_image_acquisition_dict
    )
    assert extracted_image_acquisition == expected_image_acquisition
