from fastapi.testclient import TestClient
from .util import *

def test_create_collection(api_client: TestClient, uuid: str):
    # @TODO: Does deleting a study inside a collection cascade/invalidate the collection/something else?
    
    study_uuids = [
        make_study(api_client)['uuid']
        for _ in range(3)
    ]
    collection = {
        "uuid": uuid,
        "version": 0,
        "name": "test_collection_name",
        "title": "test_collection_title",
        "subtitle": "",
        "study_uuids": study_uuids
    }

    rsp = api_client.post(f"/api/private/collections", json=collection)
    assert rsp.status_code == 201, rsp.json()
