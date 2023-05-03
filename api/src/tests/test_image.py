from fastapi.testclient import TestClient
from .util import *

def test_create_images(api_client: TestClient, existing_study):
    images = [
        {
            "uuid": get_uuid(),
            "version": 0,
            "study_id": existing_study['uuid'],
            "name": f"image_{i}",
            "original_relpath": f"/home/test/{i}",
            "attributes": {
                "image_idx": i
            }
        }
        for i in range(10)
    ]
    rsp = api_client.post("/api/private/images", json=images)
    assert rsp == 201, rsp.json()