import os
import pytest
from dotenv import dotenv_values
from pathlib import Path


def pytest_configure(config: pytest.Config):
    env_settings = dotenv_values(str(Path(__file__).parents[1] / ".env_template"))
    os.environ["bia_api_basepath"] = env_settings["local_bia_api_basepath"]
    os.environ["bia_api_username"] = env_settings["local_bia_api_username"]
    os.environ["bia_api_password"] = env_settings["local_bia_api_password"]
