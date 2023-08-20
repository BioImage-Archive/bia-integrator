from locust import task

from common.util import batch_response_status_all, make_fileref_payload
from common.api_user_base import APIUserBase
from locust.exception import ResponseError

class APIUser(APIUserBase):
    _config = {
        # keep this up to date as a template, even though it's overwritten
        'study_uuid': None,
        'n_img_count': None,
        'username': None,
        'password': None
    }

    @task
    def batch_create_image(self):
        payload = make_fileref_payload(self._config['study_uuid'], self._config['n_img_count'])

        with self.client.post("api/private/file_references", json=payload, headers={"Accept-Encoding":"gzip, deflate"}, catch_response=True) as rsp:
            rsp_json = rsp.json()
            if not batch_response_status_all(rsp_json['items'], 201):
                raise ResponseError("Unexpected status code")
            if rsp.request_meta["response_time"] > 10000:
                raise ResponseError("Took too long")
