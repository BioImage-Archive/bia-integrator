import os
from pathlib import Path

import pytest
from dotenv import dotenv_values

from persistance.bia_api_client import BIAAPIClient
from persistance.settings import get_settings


def pytest_configure(config: pytest.Config):
    # Should be the setting by default, but re-setting prior to test running to avoid accidentally updating actual DBs during test runs
    env_settings = dotenv_values(str(Path(__file__).parents[1] / ".env_template"))
    os.environ["bia_api_basepath"] = env_settings["local_bia_api_basepath"]
    os.environ["bia_api_username"] = env_settings["local_bia_api_username"]
    os.environ["bia_api_password"] = env_settings["local_bia_api_password"]


@pytest.fixture(scope="session")
def bia_api_client() -> BIAAPIClient:
    setttings = get_settings()
    return BIAAPIClient(setttings)
