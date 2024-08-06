"""
WIP minimal tests
"""

from fastapi.testclient import TestClient
import pytest
import uuid as uuid_lib


TEST_SERVER_BASE_URL = "http://localhost.com/v2"


def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.uuid4()

    return str(generated)


def get_client(**kwargs) -> TestClient:
    from fastapi.responses import JSONResponse
    from fastapi import Request
    import traceback

    from ..app import app

    @app.exception_handler(Exception)
    def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=traceback.format_exception(exc, value=exc, tb=exc.__traceback__),
        )

    return TestClient(app, base_url=TEST_SERVER_BASE_URL, **kwargs)


@pytest.fixture(scope="module")
def api_client() -> TestClient:
    client = get_client(raise_server_exceptions=False)
    # authenticate_client(client)  # @TODO: DELETEME

    return client


def test_create_study(api_client: TestClient):
    study_uuid = get_uuid()
    study = {
        "uuid": study_uuid,
        "version": 0,
        "release_date": "2023-01-31",
        "accession_id": study_uuid,
        "title": "Test BIA study",
        "description": "description",
        "licence": "CC_BY_4.0",
        "see_also": [],
        "model": {"type_name": "Study", "version": 1},
        "acknowledgement": "test",
        "funding_statement": "test",
        "grant": [],
        "keyword": [],
        "related_publication": [],
        "author": [
            {
                "address": None,
                "display_name": "Test name",
                "contact_email": "test_email@test.com",
                "orcid": None,
                "role": None,
                "rorid": None,
                "website": None,
                "affiliation": [
                    {
                        "display_name": "Test",
                        "address": None,
                        "rorid": None,
                        "website": None,
                    }
                ],
            }
        ],
        "attribute": {},
    }

    rsp = api_client.post("private/study", json=study)
    assert rsp.status_code == 201, rsp.json()

    rsp = api_client.get(f"study/{study['uuid']}")
    assert rsp.status_code == 200, rsp.text
    assert rsp.json() == study


def test_get_study_datasets(api_client: TestClient):
    study_uuid = get_uuid()
    study = {
        "uuid": study_uuid,
        "version": 0,
        "release_date": "2023-01-31",
        "accession_id": study_uuid,
        "title": "Test BIA study",
        "description": "description",
        "licence": "CC_BY_4.0",
        "see_also": [],
        "model": {"type_name": "Study", "version": 1},
        "acknowledgement": "test",
        "funding_statement": "test",
        "grant": [],
        "keyword": [],
        "related_publication": [],
        "author": [
            {
                "address": None,
                "display_name": "Test name",
                "contact_email": "test_email@test.com",
                "orcid": None,
                "role": None,
                "rorid": None,
                "website": None,
                "affiliation": [
                    {
                        "display_name": "Test",
                        "address": None,
                        "rorid": None,
                        "website": None,
                    }
                ],
            }
        ],
        "attribute": {},
    }

    rsp = api_client.post("private/study", json=study)
    assert rsp.status_code == 201, rsp.json()

    rsp = api_client.get(f"study/{study_uuid}/experimental_imaging_dataset")
    assert rsp.status_code == 200, rsp.json()
    assert rsp.json() == []
