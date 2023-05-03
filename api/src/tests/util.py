from fastapi.testclient import TestClient

from .. import app
import uuid as uuid_lib
import time

import pytest

@pytest.fixture
def api_client() -> TestClient:
    return _get_client(raise_server_exceptions=False)

@pytest.fixture(scope="function")
def uuid() -> str:
    return _get_uuid()

def _get_client(**kwargs) -> TestClient:
    return TestClient(app.app, **kwargs)

def _get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.UUID(int=int(time.time()*1000))

    return str(generated)
