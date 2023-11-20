from bia_integrator_api.util import simple_client, uuid_from_str
from bia_integrator_api import models as api_models
import os

rw_client = simple_client(
    api_base_url = "https://bia-cron-1.ebi.ac.uk:8080",
    # FIXME: Re-enable and remove this flag once api is on publicly accessible infra
    disable_ssl_host_check = True
)

search_result = rw_client.search_images_exact_match(
    api_models.SearchImageFilter(
        annotations_any=[api_models.SearchAnnotation(
            key="dimension_order",
            value="XYZCT"
        )],
        image_representations_any=[api_models.SearchFileRepresentation(
            type="thumbnail",
            size_bounds_lte=1000000000
        )],
        study_uuid="00000000-0000-0000-0006-09b5dbf57bdf",
        limit=10
    )
)

#print(search_result)

search_result = rw_client.search_images_exact_match(
    api_models.SearchImageFilter(
        attr=[api_models.SearchAnnotation(
            key="_neuroglancer_link"
        )],
        limit=10
    )
)
if len(search_result):
    print(search_result[0].attributes['_neuroglancer_link'])
else:
    print("No images found for the query")