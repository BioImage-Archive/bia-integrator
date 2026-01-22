from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid

def test_create_embedding_no_doc(api_client: TestClient):
    embedding = {
        'uuid': get_uuid(),
        'vector': [0.1]*1024,
        'for_document_uuid': get_uuid(),
        'additional_metadata': {},
        'embedding_model': 'test/test',
        'model': {'type_name': 'Embedding', "version": 1},
        'version': 0
    }
    rsp = api_client.post(
        "private/embedding",
        json=embedding,
    )
    assert rsp.status_code == 404, rsp.json()

def test_create_embedding_existing_doc(api_client: TestClient, existing_study):
    embedding = {
        'uuid': get_uuid(),
        'vector': [0.1]*1024,
        'for_document_uuid': existing_study['uuid'],
        'additional_metadata': {},
        'embedding_model': 'test/test',
        'model': {'type_name': 'Embedding', "version": 1},
        'version': 0
    }
    rsp = api_client.post(
        "private/embedding",
        json=embedding,
    )
    assert rsp.status_code == 201, rsp.json()

def test_create_embedding_not_a_study(api_client: TestClient, existing_dataset):
    """
    Ensure we always do the cross-collection checks so we know perf impact
    """
    embedding = {
        'uuid': get_uuid(),
        'vector': [0.1]*1024,
        'for_document_uuid': existing_dataset['uuid'],
        'additional_metadata': {},
        'embedding_model': 'test/test',
        'model': {'type_name': 'Embedding', "version": 1},
        'version': 0
    }
    rsp = api_client.post(
        "private/embedding",
        json=embedding,
    )
    assert rsp.status_code == 404, rsp.json()

def test_get_embedding_for_study(api_client: TestClient, existing_embedding):
    rsp = api_client.get(f"search/embedding/study/{existing_embedding['for_document_uuid']}")
    assert rsp.status_code == 200, rsp.json()

    assert rsp.json() == existing_embedding