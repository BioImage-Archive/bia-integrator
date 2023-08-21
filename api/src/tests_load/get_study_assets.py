from locust import task

from common.api_user_base import APIUserBase
from locust.exception import ResponseError

class APIUser(APIUserBase):
    @task
    def get_study_images(self):
        with self.client.get(f"api/studies/{ self._config['study_uuid'] }/images?limit=1000", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 2000:
                raise ResponseError("Took too long")

    @task
    def get_study_filerefs(self):
        with self.client.get(f"api/studies/{ self._config['study_uuid'] }/file_references?limit=1000", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 2000:
                raise ResponseError("Took too long")
