# Writing this as a load test to reuse credential passing, auth handling
#   ! Depends on a test user manually being created
from locust import task

from common.api_user_base import APIUserBase
import common.fixtures as fixtures
from common.util import batch_response_status_all

class FixturesUser(APIUserBase):
    _config = {
        'username': None,
        'password': None,
    }
    def on_start(self):
        super().on_start()

        study = fixtures.make_study_payload()
        rsp = self.client.post("api/private/studies", json=study)
        assert rsp.status_code == 201, rsp.json()

        collection = fixtures.make_collection_payload()
        collection['study_uuids'].append(study['uuid'])
        rsp = self.client.post("api/private/collections", json=collection)
        assert rsp.status_code == 201, rsp.json()

        file_references = fixtures.make_fileref_payload(study['uuid'], 1000)
        rsp = self.client.post("api/private/file_references", json=file_references, headers={"Accept-Encoding":"gzip, deflate"})
        assert batch_response_status_all(rsp.json()['items'], 201)

        images = fixtures.make_image_payload(study['uuid'], 1000)
        rsp = self.client.post("api/private/images", json=images, headers={"Accept-Encoding":"gzip, deflate"})
        assert batch_response_status_all(rsp.json()['items'], 201)

        # prevent locust from starting new users once this one finishes
        exit()

    @task
    def _(self):
        # Nothing to do here - this is not an actual test
        pass
