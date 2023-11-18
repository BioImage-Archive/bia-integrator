from bia_integrator_api.util import simple_client, uuid_from_str
from bia_integrator_api import models as api_models
import os

rw_client = simple_client(
    api_base_url = "https://bia-cron-1.ebi.ac.uk:8080/",
    # FIXME: Re-enable and remove this flag once api is on publicly accessible infra
    disable_ssl_host_check = True
)

rw_client.search_images_exact_match(
    
)

{
    "annotations_any": [{"dimension_order": "XYZCT"} ],
    "image_representations_any": [{"type": "thumbnail", "size_lte": 1000000000} ],
    "study_uuid": "00000000-0000-0000-0006-09b5dbf57bdf",
    "limit": 10
}
