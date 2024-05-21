"""Test the script runs OK - kind of an integration test

"""

from unittest.mock import Mock, MagicMock
import logging
import json
from pathlib import Path
from scripts.assign_image_acquisitions_to_images import app, api_client
from scripts import assign_image_acquisitions_to_images
from bia_ingest.biostudies import Submission
from bia_ingest.conversion import dict_to_uuid

from .utils import (
    create_expected_biosample,
    create_expected_specimen,
    create_expected_image_acquisition,
)

from typer.testing import CliRunner

N_TEST_IMAGES = 3
TEST_IMAGE_UUID = "test_image_uuid"
accession_id = "S-BIADTEST"


def mock_get_object_info_by_accession():
    study = Mock()
    study.uuid = "test_study_uuid"
    return study


api_client.get_object_info_by_accession = MagicMock(
    return_value=[mock_get_object_info_by_accession(),]
)

test_filerefs = []
for i in range(N_TEST_IMAGES):
    fileref = Mock()
    fileref.path = f"test_fileref_path_{i}"
    fileref.size = (i + 1) * 100
    fileref.uuid = dict_to_uuid(
        {"accession_id": accession_id, "path": fileref.path, "size": fileref.size,},
        ["accession_id", "path", "size"],
    )
    test_filerefs.append(fileref)


def mock_get_study_images():
    images = []
    for i in range(N_TEST_IMAGES):
        image_rep = Mock()
        image_rep.attributes = {"fileref_ids": [test_filerefs[i].uuid,]}
        image_rep.type = "fire_object"
        image = Mock()
        image.uuid = TEST_IMAGE_UUID
        image.version = 0
        image.image_acquisitions_uuid = None
        image.representations = [
            image_rep,
        ]
        images.append(image)
    return images


api_client.get_study_images = MagicMock(return_value=mock_get_study_images())
api_client.update_image = MagicMock(return_value=True)


def mock_load_submission():
    submission_path = Path(__file__).parent / "data" / f"{accession_id}.json"
    submission_dict = json.loads(submission_path.read_text())
    return Submission(**submission_dict)


assign_image_acquisitions_to_images.load_submission = MagicMock(
    return_value=mock_load_submission()
)

assign_image_acquisitions_to_images.flist_from_flist_fname = MagicMock(
    return_value=test_filerefs
)

api_client.get_biosample = MagicMock(create_expected_biosample(accession_id))
api_client.create_biosample = MagicMock(create_expected_biosample(accession_id))

api_client.get_specimen = MagicMock(create_expected_specimen(accession_id))
api_client.create_specimen = MagicMock(create_expected_specimen(accession_id))

api_client.get_image_acquisition = MagicMock(
    create_expected_image_acquisition(accession_id)
)
api_client.create_image_acquisition = MagicMock(
    create_expected_image_acquisition(accession_id)
)

api_client.get_biosample = MagicMock(create_expected_biosample(""))
api_client.create_biosample = MagicMock(create_expected_biosample(""))


def test_assign_image_acquisitions_to_images_script_runs_ok(caplog):
    caplog.set_level(
        logging.INFO, logger=assign_image_acquisitions_to_images.logger.name
    )
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(app, [accession_id,], catch_exceptions=False)

    if result.exception is not None:
        print(result.exception)

    assert result.exception is None
    assert result.exit_code == 0

    expected_messages = [
        "Retrieved biosample with uuid",
        "Retrieved specimen with uuid",
        "Retrieved image_acquisition with uuid",
        "Found 3 fileref to image_acquisition relationships",
    ]
    caplog_messages = " ".join(caplog.messages)
    for expected_message in expected_messages:
        assert expected_message in caplog_messages

    image_acquisition_assigned_substr = (
        f"Setting image {TEST_IMAGE_UUID} image_acquisitions_uuid to :"
    )
    assert caplog_messages.count(image_acquisition_assigned_substr) == 3
