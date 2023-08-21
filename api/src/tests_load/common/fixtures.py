from common.api_user_base import APIUserBase
from .util import get_uuid

COLLECTION_NAME = "locust_tests"
COLLECTION_UUID = "00000000-0000-0000-0000-000000000001"

def img_alias_from_uuid(uuid):
    return f"alias_{uuid}"

def study_accno_from_uuid(uuid):
    return f"accno_{uuid}"

def make_collection_payload():
    collection = {
        "uuid": COLLECTION_UUID,
        "version": 0,
        "name": COLLECTION_NAME,
        "title": COLLECTION_NAME,
        "subtitle": "",
        "study_uuids": []
    }
    return collection

def get_test_collection(locust_user: APIUserBase):
    rsp = locust_user.client.get(f"api/collections/{COLLECTION_UUID}")
    if rsp.status_code == 404:
        return None

    assert rsp.status_code == 200, rsp.json()

    return rsp.json()

def make_study_payload():
    uuid = get_uuid()
    study = {
        "uuid": uuid,
        "version": 0,
        "accession_id": study_accno_from_uuid(uuid),
        "title": "Locust test study",
        "description": "Locust test study",
        "authors": [{
            "name": "First Author"
        }, {
            "name": "Second Author"
        }],
        "organism": "test",
        "release_date": "test"
    }

    return study

def get_test_study(locust_user: APIUserBase):
    collection = get_test_collection(locust_user)
    return collection['study_uuids'][0]

def make_fileref_payload(study_uuid, n_filerefs):
    filerefs = [{
        "uuid": get_uuid(),
        "version": 0,
        "type": "file",
        "study_uuid": study_uuid,
        "name": "test",
        "uri": "https://test.com/test",
        "size_bytes": 100
    } for _ in range(n_filerefs)]
    return filerefs

def get_test_filerefs(locust_user: APIUserBase, n_filerefs):
    study_uuid = get_test_study(locust_user)
    rsp = locust_user.client.get(f"api/studies/{study_uuid}/file_references?limit={n_filerefs}")
    assert rsp.status_code == 200
    
    filerefs = rsp.json()
    assert len(filerefs) == n_filerefs, f"Study {study_uuid} has {len(filerefs)} file references, but {n_filerefs} were requested."

    return filerefs

def make_image_payload(study_uuid, n_images):
    images = []
    
    for _ in range(n_images):
        uuid = get_uuid()
        images.append({
            "uuid": uuid,
            "version": 0,
            "study_uuid": study_uuid,
            "name": "image_name_value",
            "original_relpath": "/home/test/image_path_value",
            "alias": {
                "name": img_alias_from_uuid(uuid)
            }
        })
    return images

def get_test_images(locust_user: APIUserBase, n_images):
    study_uuid = get_test_study(locust_user)
    rsp = locust_user.client.get(f"api/studies/{study_uuid}/images?limit={n_images}")
    assert rsp.status_code == 200
    
    images = rsp.json()
    assert len(images) == n_images, f"Study {study_uuid} has {len(images)} file references, but {n_images} were requested."

    return images
