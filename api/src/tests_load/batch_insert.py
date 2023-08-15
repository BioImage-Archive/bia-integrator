from locust import task

from common.util import batch_response_status_all, make_image_payload
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
        payload = make_image_payload(self._config['study_uuid'], self._config['n_img_count'])

        with self.client.post("api/private/images", json=payload, catch_response=True, headers={"Accept-Encoding":"gzip, deflate"}) as rsp:
            rsp_json = rsp.json()
            if not batch_response_status_all(rsp_json['items'], 201):
                raise ResponseError("Unexpected status code")
            if rsp.elapsed.total_seconds() > 10:
                raise ResponseError("Took too long")
