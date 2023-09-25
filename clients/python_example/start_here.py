"""
Useful docs:
API endpoints reference https://github.com/BioImage-Archive/bia-integrator/tree/biaint-api-backend/clients/python#documentation-for-api-endpoints
API models reference https://github.com/BioImage-Archive/bia-integrator/tree/biaint-api-backend/clients/python#documentation-for-models
"""

from openapi_client.util import simple_client
from openapi_client import models as api_models, exceptions as api_exceptions
from util import get_uuid

# This replaces the generated 'getting started' and any concern for authentication
rw_client = simple_client(
    "http://127.0.0.1:8080",
    "test@example.com",
    "test"
)
# Known issue of being unable to have multiple api client instances
#ro_client = simple_client("production:8080")

##  Create a study
# always provide version=0 and a uuid when creating objects
study_uuid = get_uuid()
my_study = api_models.BIAStudy(
    uuid = study_uuid,
    version = 0,
    title = "Study title",
    description = "Study description",
    release_date = "@TODO: Check format",
    accession_id = f"accessions_must_be_unique_{study_uuid}",
    organism = "test"
)
rw_client.create_study(my_study)


##  Updating an object
# Always bump the version before updating an object
my_study.title = "Study title amended"
try:
    rw_client.update_study(my_study)
except api_exceptions.NotFoundException:
    # This is really a conflict, but the point is that the study is not accepted
    pass

# this works
my_study.version += 1
rw_client.update_study(my_study)


## Some objects are nested in others
# This creates an Image (toplevel object), then updates it to add an annotation
#   Note that the whole image is pushed back in the update, not the annotation (like for the Study example above)
image_uuid = get_uuid()
my_image = api_models.BIAImage(
    uuid = image_uuid,
    version = 0,
    study_uuid = study_uuid,
    original_relpath = ""
)
rw_client.create_images([my_image])

annotation = api_models.ImageAnnotation(
    author_email = "test",
    key = "test",
    value = "test",
    state = api_models.AnnotationState.ACTIVE
)
my_image.annotations = [annotation]
my_image.version += 1

# Note the entire image being pushed, there is no way to update just the nested annotation yet
rw_client.update_image(my_image)


## Study stats need to be explicitly calculated
# The study in this example has an image, but it isn't counted untill we explicitly ask the api to do so 
my_study = rw_client.get_study(my_study.uuid)
my_image = rw_client.get_image(my_image.uuid)
assert my_study.images_count == 0

rw_client.study_refresh_counts(my_study.uuid)
my_study = rw_client.get_study(my_study.uuid)
assert my_study.images_count == 1


### For really large studies, use the study counts to paginate
max_image_list_size = 10
last_image_uuid = None
for chunk_idx in range(my_study.images_count // max_image_list_size):
    for img in rw_client.get_study_images(my_study.uuid, last_image_uuid, max_image_list_size):
        last_image_uuid = img.uuid

# Otherwise, to just fetch all images
rw_client.get_study_images(my_study.uuid, limit=1000000000)
