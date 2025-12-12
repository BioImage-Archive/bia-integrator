import hashlib
from uuid import UUID

import pytest
from bia_integrator_api.models.study import Study
from bia_shared_datamodels import bia_data_model, mock_objects

from persistance.bia_api_client import BIAAPIClient


@pytest.fixture()
def study_object(request) -> Study:
    study_shared_model = bia_data_model.Study(**mock_objects.get_study_dict())

    # Make a test-specific uuid
    hexdigest = hashlib.md5(str(request.node.nodeid).encode("utf-8")).hexdigest()
    study_shared_model.uuid = UUID(version=4, hex=hexdigest)

    study_object = Study(**study_shared_model.model_dump(mode="json"))
    return study_object


def test_put_object(bia_api_client: BIAAPIClient, study_object: Study):

    bia_api_client.put_object(study_object)

    response = bia_api_client.get_study(study_object.uuid)
    assert response == study_object


def test_put_object_exisiting_same(bia_api_client: BIAAPIClient, study_object: Study):

    bia_api_client.put_object(study_object)

    bia_api_client.put_object(study_object)

    # check version is not changed
    response = bia_api_client.get_study(study_object.uuid)
    assert response == study_object


def test_put_object_exisiting_different(
    bia_api_client: BIAAPIClient, study_object: Study
):

    bia_api_client.put_object(study_object)
    starting_study = bia_api_client.get_study(study_object.uuid)

    updated_desciption = f"{starting_study.description} With updated!"
    study_object.description = updated_desciption
    bia_api_client.put_object(study_object)

    # check study was update
    response = bia_api_client.get_study(study_object.uuid)
    assert response.version == starting_study.version + 1
    assert response.description == updated_desciption
