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


async def bulk_index_in_chunks(client, bulk_file_path, chunk_lines=100):
    """Index data in chunks to avoid circuit breaker limits.
    
    Args:
        client: Elasticsearch client
        bulk_file_path: Path to the bulk file
        chunk_lines: Number of lines to read per chunk (must be even, default 100 = 50 docs)
    """
    # Ensure chunk_lines is even (bulk format requires pairs of lines)
    if chunk_lines % 2 != 0:
        chunk_lines = chunk_lines - 1
    
    with open(bulk_file_path, 'r') as f:
        while True:
            # Read chunk_lines (even number) of lines
            lines = []
            for _ in range(chunk_lines):
                line = f.readline()
                if not line:  # End of file
                    break
                lines.append(line)
            
            if not lines:
                break  # No more data
            
            # Join lines and ensure it ends with newline for bulk format
            chunk_data = ''.join(lines)
            if chunk_data and not chunk_data.endswith('\n'):
                chunk_data += '\n'
            
            if chunk_data.strip():  # Only process non-empty chunks
                response = await client.bulk(body=chunk_data)
                assert not response.body["errors"], response.body


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

    # Index study metadata in chunks
    study_bulk_path = (
        pathlib.Path(__file__).parent / "test_data" / "bia-study-metadata.json.bulk"
    )
    await bulk_index_in_chunks(el.client, study_bulk_path, chunk_lines=100)

    # Index image metadata in chunks
    image_bulk_path = (
        pathlib.Path(__file__).parent / "test_data" / "bia-image-metadata.json.bulk"
    )
    await bulk_index_in_chunks(el.client, image_bulk_path, chunk_lines=100)

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
