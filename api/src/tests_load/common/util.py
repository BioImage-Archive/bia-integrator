from urllib.parse import urljoin

import requests
import uuid as uuid_lib
import time


def get_uuid():
    uuid = uuid_lib.UUID(int=int(time.time() * 1000000))
    return str(uuid)


def authenticate(host, path, username, password):
    url = urljoin(host, path)
    response = requests.post(
        url,
        data={
            "username": username,
            "password": password,
        },
        verify=False,
    )
    assert response.status_code == 200, response

    return response.json()["access_token"]


def batch_response_status_all(arr_batch_op_result, expected_status_code):
    return all([res["status"] == expected_status_code] for res in arr_batch_op_result)


def get_study_filerefs(host, study_uuid, n_filerefs=100):
    url = (
        urljoin(host, f"/api/studies/{study_uuid}/file_references")
        + f"?limit={n_filerefs}"
    )
    rsp = requests.get(url, verify=False)

    assert rsp.status_code == 200

    filerefs = rsp.json()
    assert (
        len(filerefs) == n_filerefs
    ), f"Study has only {len(filerefs)} filerefs, but {n_filerefs} were expected."

    return filerefs
