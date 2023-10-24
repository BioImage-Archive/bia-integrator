from bia_integrator_api.util import simple_client, uuid_from_str
from bia_integrator_api import models as api_models
import os

rw_client = simple_client(
    api_base_url = "http://127.0.0.1:8080",
    username = "test@example.com",
    password = "test",
    # FIXME: Re-enable and remove this flag once api is on publicly accessible infra
    disable_ssl_host_check = True
)

###
# Fetch the image to update first, to:
#   * get the study uuid
#   * ensure the pipeline input starfile is a BIAImageRepresentation of the image
###

# Assumes the image uuid is fetched from elsewhere (or can get_study_images_by_alias if alias and study accession are known)
image_uuid = "0000-0000-0000-0000"

image = rw_client.get_image(image_uuid)
pipeline_study_uuid = image.study_uuid

assert image.representations, "Cannot annotate images with no representations"
image_star_files = [img_repr for img_repr in image.representations if img_repr.uri.endsWith('.star')]
assert len(image_star_files) == 1, "Found multiple starfiles per image"
pipeline_input_starfile = image_star_files.pop().uri

###
# Create file reference pointing at a generated file
###
pipeline_output_file_uri = "https://ftp.ebi.ac.uk/example.txt"
fileref = api_models.FileReference(
    uuid = uuid_from_str(pipeline_output_file_uri),
    version = 0,
    study_uuid = pipeline_study_uuid,
    name = os.path.basename(pipeline_output_file_uri),
    uri = pipeline_output_file_uri,
    size_in_bytes = 0, # probably not
    type = "fire_object",
    attributes = {
        "source image": pipeline_input_starfile
    }
)

rsp = rw_client.create_file_references([fileref])
assert rsp.items.pop().status == 201, rsp