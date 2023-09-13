from locust import task

from common.api_user_base import APIUserBase
import common.fixtures as fixtures
from locust.exception import ResponseError
import random

class APIUser(APIUserBase):
    _file_reference = None

    def on_start(self):
        super().on_start()

        # new users created only when the tests ramp up, afterwards the same user instances are used
        #   overhead acceptable to getting the filerefs in on_init
        file_references = fixtures.get_test_filerefs(self, 1000)
        fileref_idx = random.randint(0, len(file_references)-1)
        self._file_reference = file_references[fileref_idx]

    @task
    def update_file_reference(self):
        self._file_reference['version'] += 1
        self._file_reference['size_in_bytes'] += 1

        with self.client.patch(f"api/private/file_references/single", json=self._file_reference, catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 150:
                raise ResponseError("Took too long")
