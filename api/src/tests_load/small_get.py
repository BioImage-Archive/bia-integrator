from locust import task

from common.api_user_base import APIUserBase
import common.fixtures as fixtures
from locust.exception import ResponseError

class APIUser(APIUserBase):
    study_uuid = None
    study_accession = None
    image_uuid = None
    image_alias = None

    def on_start(self):
        super().on_start()

        self.study_uuid = fixtures.get_test_study(self)
        self.study_accession = fixtures.study_accno_from_uuid(self.study_uuid)
        self.image_uuid = fixtures.get_test_images(self, 1)[0]['uuid']
        self.image_alias = fixtures.img_alias_from_uuid(self.image_uuid)

    @task
    def get_study(self):
        with self.client.get(f"api/studies/{self.study_uuid}", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 600:
                raise ResponseError("Took too long")

    @task
    def get_image(self):
        with self.client.get(f"api/images/{self.image_uuid}", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 600:
                raise ResponseError("Took too long")

    @task
    def resolve_study_objinfo(self):
        with self.client.get(f"api/object_info_by_accessions?accessions={self.study_accession}", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 600:
                raise ResponseError("Took too long")

    @task
    def image_by_alias(self):
        with self.client.get(f"api/studies/{self.study_accession}/images_by_aliases?aliases={self.image_alias}", catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 600:
                raise ResponseError("Took too long")
