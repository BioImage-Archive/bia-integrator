from api.settings import Settings
import pytest_asyncio
import pathlib
import asyncio
import pytest
from fastapi.testclient import TestClient


test_settings = Settings()
TEST_SERVER_BASE_URL = "http://localhost.com/v2"


@pytest.fixture(scope="session")
def event_loop():
    yield asyncio.get_event_loop()

    asyncio.get_event_loop().close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def elastic():
    from api.elastic import elastic_create

    el = await elastic_create(test_settings)
    if not el.client:
        yield
        return

    try:
        await el.client.indices.delete(index=[el.index_study, el.index_image])
    except:
        pass

    await el.configure(test_settings)

    test_data = (
        pathlib.Path(__file__).parent / "test_data" / "bia-study-metadata.json.bulk"
    ).read_text()
    response = await el.client.bulk(body=test_data)
    assert not response.body["errors"]

    test_data = (
        pathlib.Path(__file__).parent / "test_data" / "bia-image-metadata.json.bulk"
    ).read_text()
    response = await el.client.bulk(body=test_data)
    assert not response.body["errors"]

    await el.client.indices.refresh(index=[el.index_study, el.index_image])

    yield el

    await el.close()


def get_client():
    from fastapi.responses import JSONResponse
    from fastapi import Request
    import traceback

    from api.app import app

    @app.exception_handler(Exception)
    def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=traceback.format_exception(exc, value=exc, tb=exc.__traceback__),
        )

    client = TestClient(
        app, base_url=TEST_SERVER_BASE_URL, raise_server_exceptions=False
    )
    return client


@pytest.fixture(scope="session")
def api_client():
    client = get_client
    with get_client() as client:

        yield client
        client.close()
