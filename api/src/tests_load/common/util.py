from urllib.parse import urljoin

import requests
import uuid as uuid_lib
import time

def get_uuid():
    uuid = uuid_lib.UUID(int=int(time.time()*1000000))
    return str(uuid)

def authenticate(host, path, username, password):
    url = urljoin(host, path)
    response = requests.post(url, data={
        "username": username,
        "password": password
    })
    assert response.status_code == 200, response

    return response.json()['access_token']


def make_image_payload(study_uuid, n_images):
    images = [{
        "uuid": get_uuid(),
        "version": 0,
        "study_uuid": study_uuid,
        "name": "image_name_value",
        "original_relpath": "/home/test/image_path_value"
    } for _ in range(n_images)]
    return images

def batch_response_status_all(arr_batch_op_result, expected_status_code):
    return all([res['status'] == expected_status_code] for res in arr_batch_op_result)


