import pytest

from persistence.bia_api_client import BIAAPIClient
from persistence.settings import get_settings
from persistence.utils import create_test_user, set_dev_settings_to_local


def pytest_configure(config: pytest.Config):
    set_dev_settings_to_local()


@pytest.fixture(scope="session")
def bia_api_client() -> BIAAPIClient:
    settings = get_settings()
    create_test_user(settings)
    return BIAAPIClient(settings)
