from locust import task

from common.api_user_base import APIUserBase
from locust.exception import ResponseError

class APIUser(APIUserBase):
    _config = {
        # keep this up to date as a template, even though it's overwritten
        'study_uuid': None,
        'study_accession': None,
        'image_uuid': None,
        'image_alias': None
    }

    @task
    def get_study(self):
        with self.client.get(f"api/studies/{self._config['study_uuid']}", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 600:
                raise ResponseError("Took too long")

    @task
    def get_image(self):
        with self.client.get(f"api/images/{self._config['image_uuid']}", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 600:
                raise ResponseError("Took too long")

    @task
    def resolve_study_objinfo(self):
        with self.client.get(f"api/object_info_by_accessions?accessions={self._config['study_accession']}", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 600:
                raise ResponseError("Took too long")

    @task
    def image_by_alias(self):
        with self.client.get(f"api/studies/{self._config['study_uuid']}/images_by_aliases?aliases={self._config['image_alias']}", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 600:
                raise ResponseError("Took too long")
