from locust import task

from common.api_user_base import APIUserBase
from locust.exception import ResponseError

class APIUser(APIUserBase):
    _config = {
        # keep this up to date as a template, even though it's overwritten
        'study_uuid': None
    }

    @task
    def batch_create_image(self):
        with self.client.get(f"api/studies/{ self._config['study_uuid'] }/images?limit=1000", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 2000:
                raise ResponseError("Took too long")
