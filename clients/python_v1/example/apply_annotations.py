from bia_integrator_api.util import simple_client, uuid_from_str
from bia_integrator_api import models as api_models
import os

ro_client = simple_client(
    api_base_url = "https://bia-cron-1:8080",
    # FIXME: Re-enable and remove this flag once api is on publicly accessible infra
    disable_ssl_host_check = True
)

study_uuid = "1bf87852-3a3c-4d47-8c4d-06e078b18d6e"
study_without_annotations_applied = ro_client.get_study(study_uuid=study_uuid)

assert study_without_annotations_applied.annotations_applied == False
assert study_without_annotations_applied.attributes == {} # no attributes because annotations were not applied

study_with_annotations_applied = ro_client.get_study(study_uuid=study_uuid)
assert study_with_annotations_applied.annotations_applied == True # This study can't be pushed back to the api as an update
assert study_with_annotations_applied.attributes != {}
assert "study_size" in study_with_annotations_applied.attributes
