import bia_integrator_api.models as api_models
import pytest
from bia_integrator_api import exceptions
from bia_shared_datamodels import bia_data_model, mock_objects
from persistence.bia_api_client import BIAAPIClient
from persistence.utils import create_test_user, set_dev_settings_to_local

from curation.settings import get_settings


def pytest_configure(config: pytest.Config):
    set_dev_settings_to_local()


@pytest.fixture(scope="session")
def private_client() -> BIAAPIClient:
    settings = get_settings()
    create_test_user(settings)
    return BIAAPIClient(settings)


@pytest.fixture(scope="session")
def any_api_object(private_client: BIAAPIClient) -> api_models.Study:
    study_dict = mock_objects.get_study_dict()
    study_object = api_models.Study.model_validate_json(
        bia_data_model.Study(**study_dict).model_dump_json()
    )
    try:
        private_client.post_study(study_object)
    except exceptions.ApiException as e:
        if e.reason == "Conflict":
            api_copy = private_client.get_study(str(study_object.uuid))
            study_object.version = api_copy.version + 1
            private_client.post_study(study_object)
        else:
            raise e
    return study_object
