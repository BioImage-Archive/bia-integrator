from locust import task, events, runners

from common.api_user_base import APIUserBase
from common.util import get_study_filerefs
from locust.exception import ResponseError
import random

class APIUser(APIUserBase):
    _config = {
        # keep this up to date as a template, even though it's overwritten
        'study_uuid': None
    }
    _file_reference = None

    def on_start(self):
        super().on_start()

        # workaround to avoid synchronising multiple users
        global file_references
        fileref_idx = random.randint(0, len(file_references)-1)
        self._file_reference = file_references[fileref_idx]

    @task
    def update_file_reference(self):
        self._file_reference['version'] += 1
        self._file_reference['size_bytes'] += 1

        with self.client.patch(f"api/private/file_references/single", json=self._file_reference, catch_response=True) as rsp:
            if rsp.request_meta["response_time"] > 2000:
                raise ResponseError("Took too long")

@events.init.add_listener
def on_locust_init(environment, **_kwargs):    
    global file_references
    file_references = get_study_filerefs(
        environment.parsed_options.host,
        APIUserBase._config['study_uuid'],
        1000
    )
