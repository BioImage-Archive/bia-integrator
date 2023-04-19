from fastapi.testclient import TestClient

from ..api.api import app
import uuid
import time

client = TestClient(app.router)

def _get_uuid() -> str:
    generated = uuid.UUID(int=int(time.time()))

    return str(generated)

def test_create_everything():
    study_uuid = "123-123-123-123"

    rsp = client.post('/studies', json={
        "id": study_uuid,
        "title": "Test BIA study",
        "description": "description",
        "authors": [{
            "name": "First Author"
        }, {
            "name": "Second Author"
        }],
        "organism": "test",
        "release_date": "test"
    })
    assert rsp.status_code == 201, rsp.json()
    raise Exception("A")

    # IMAGES CREATE
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

    # FILE REFERENCES CREATE
    study_file_references = []
    for i in range(10):
        reference_uuid = f"456-456-456-45{i}"
        study_file_references.append({
            "id": reference_uuid,
            "study_id": study_uuid,
            "name": f"file_reference_name_{i}",
            "uri": f"https://www.google.com/file_reference/{i}",
            "size_bytes": 100 * (i+1),
            "attributes": {
                'first': 'attribute',
                'second': 'attribute'
            }
        })
    rsp = client.post('/file_references', json=study_file_references)
    
    rsp = client.post(f'/studies/{study_uuid}/refresh_counts')

def test_study_update():
    """
    Similar mechanism (provide version to overwrite) for everything: images, file references
    """

    study_uuid = "123-123-123-123"
    study = {
        "id": study_uuid,
        "title": "Test BIA study",
        "authors": [{
            "name": "First Author"
        }, {
            "name": "Second Author"
        }],
        "description": "description",
        "organism": "test",
        "release_date": "test"
    }
    client.post('/studies', json=study)

    study['title'] = "UPDATED_TITLE"

    # fails because object exists but version is missing from payload
    client.post('/studies', json=study)

    study_saved = client.get(f"/studies/{study_uuid}").json
    study['version'] = study_saved['version'] + 1

    # accepted now because version doesn't clash
    client.post('/studies', json=study)