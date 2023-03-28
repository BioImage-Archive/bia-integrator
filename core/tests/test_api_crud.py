from fastapi.testclient import TestClient

import bia_integrator_core.api.studies as api

client = TestClient(api.router)

def test_create_study():
    study_uuid = "123-123-123-123"

    rsp = client.post('/studies', json={
        "id": study_uuid,
        "title": "Test BIA study",
        "authors": [{
            "name": "First Author"
        }, {
            "name": "Second Author"
        }],
        "description": "description",
        "organism": "test",
        "release_date": "test",
        "imaging_type": None
    })
    assert rsp.status_code == 201, rsp.json()

    # FILE REFERENCES CREATE
    study_images = []
    for i in range(10):
        img_uuid = f"234-234-234-23{i}"
        study_images.append({
            "id": img_uuid,
            "study_id": study_uuid,
            "accession_id": img_uuid,
            "name": None,
            "original_relpath": f"S-BIAD1/my_dir/test-image{i}",
            # @TODO: Test mongo list item field indexing
            "representations": [{
                "accession_id": f"999-999-999-99{i}",
                "uri": ["https://www.google.com/1", "https://www.google.com/2"],
                "size": 1234,
                "type": None,
                "dimensions": None,
                "attributes": None,
                "rendering": None,
            }],
            "attributes": {
                "first": "first",
                "second": "second"
            },
            "annotations": [
                {
                    "first_annotation": "test"
                },
                {
                    "second_annotation": "test"
                }
            ]
        })
    rsp = client.post('/images', json=study_images)

    # re-issuing the request should do nothing
    rsp = client.post('/images', json=study_images)
    
    rsp = client.post(f'/studies/{study_uuid}/refresh_counts')