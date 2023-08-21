from locust import task

from common.util import batch_response_status_all
import common.fixtures as fixtures
from common.api_user_base import APIUserBase
from locust.exception import ResponseError

class APIUser(APIUserBase):
    study_uuid = None
    n_img_count = None

    def on_start(self):
        super().on_start()

        self.study_uuid = fixtures.get_test_study(self)
        self.n_img_count = self.test_config['n_img_count']

    @task
    def batch_create_image(self):
        payload = fixtures.make_fileref_payload(self.study_uuid, self.n_img_count)

        with self.client.post("api/private/file_references", json=payload, headers={"Accept-Encoding":"gzip, deflate"}, catch_response=True) as rsp:
            rsp_json = rsp.json()
            if not batch_response_status_all(rsp_json['items'], 201):
                raise ResponseError("Unexpected status code")
            if rsp.request_meta["response_time"] > 10000:
                raise ResponseError("Took too long")
