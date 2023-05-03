from fastapi.testclient import TestClient

from .. import app
import uuid as uuid_lib
import time

import pytest

@pytest.fixture
def api_client() -> TestClient:
    return get_client(raise_server_exceptions=False)

@pytest.fixture(scope="function")
def uuid() -> str:
    return get_uuid()

@pytest.fixture(scope="function")
def existing_study(api_client: TestClient, uuid: str):
    study = {
        "uuid": uuid,
        "version": 0,
        "title": "Test BIA study",
        "description": "description",
        "authors": [{
            "name": "First Author"
        }, {
            "name": "Second Author"
        }],
        "organism": "test",
        "release_date": "test"
    }
    rsp = api_client.post('/api/private/study', json=study)
    assert rsp.status_code == 201, rsp.json()

    rsp = api_client.get(f'/api/{uuid}')
    assert rsp.status_code == 200

    return rsp.json()

def get_client(**kwargs) -> TestClient:
    from fastapi.responses import JSONResponse
    from fastapi import Request
    import traceback

    @app.app.exception_handler(Exception)
    def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__),
        )

    return TestClient(app.app, **kwargs)

def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.UUID(int=int(time.time()*1000000))

    return str(generated)
