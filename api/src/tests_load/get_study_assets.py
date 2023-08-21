from locust import task

from common.api_user_base import APIUserBase
import common.fixtures as fixtures
from locust.exception import ResponseError

class APIUser(APIUserBase):
    study_uuid = None

    def on_start(self):
        super().on_start()

        self.study_uuid = fixtures.get_test_study(self)

    @task
    def get_study_images(self):
        with self.client.get(f"api/studies/{ self.study_uuid }/images?limit=1000", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 1000:
                raise ResponseError("Took too long")

    @task
    def get_study_filerefs(self):
        with self.client.get(f"api/studies/{ self.study_uuid }/file_references?limit=1000", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 1000:
                raise ResponseError("Took too long")
