"""
Example script that creates and gets some objects. Please see the api client readme for details
"""

from bia_integrator_api.util import get_client_private
from bia_integrator_api.models import Study, Licence, Contributor, Dataset, Provenance
from datetime import date
from bia_integrator_api import exceptions as api_exceptions
from pydantic import ValidationError
from uuid import uuid4

def get_uuid() -> str:
    """
    @return example "06c19696-00e8-4c2e-a27f-23587aedb782"
    """
    generated = uuid4()

    return str(generated)


api_base_url = "http://api:8080"
client = get_client_private(
    username="test@example.com",
    password="test",
    api_base_url=api_base_url
)

# Example create/get - equivalent for every object
study = Study(
    uuid=get_uuid(),
    object_creator=Provenance.BIA_INGEST,
    version=0,
    accession_id="test",
    licence=Licence.HTTPS_COLON_SLASH_SLASH_CREATIVECOMMONS_DOT_ORG_SLASH_LICENSES_SLASH_BY_MINUS_NC_MINUS_SA_SLASH_2_DOT_0_SLASH,
    author=[Contributor(
        display_name="test",
        affiliation=[]
    )],
    title = "test",
    release_date = date.today(),
    description = "test",
    additional_metadata = []
)
client.post_study(study)

study_fetched = client.get_study(study.uuid)
assert study_fetched.uuid == study.uuid

# attach a dataset to a study, and get all datasets for the study
dataset = Dataset(
    uuid = get_uuid(),
    title="test",
    object_creator=Provenance.BIA_INGEST,
    version = 0,
    example_image_uri = [],
    submitted_in_study_uuid = study.uuid
)
client.post_dataset(dataset)

study_datasets = client.get_dataset_linking_study(study.uuid, page_size=100)
assert len(study_datasets) == 1
assert study_datasets[0].uuid == dataset.uuid

"""
Example errors
"""
try:
    # create a client instance, remove the authentication token and try to make a request to a private endpoint
    client_unauthenticated = get_client_private(
        username="test@example.com",
        password="test",
        api_base_url=api_base_url
    )

    client_unauthenticated.api_client.configuration.access_token = ""
    client_unauthenticated.post_study(study)
except api_exceptions.UnauthorizedException:
    pass
else:
    assert False, "UnauthorizedException should have been raised"

try:
    # authenticate with bad credentials
    get_client_private(
        username="does_not_exist_user_test@example.com",
        password="test",
        api_base_url=api_base_url
    )
except api_exceptions.UnauthorizedException:
    pass
else:
    assert False, "UnauthorizedException should have been raised"

try:
    # mistyped parameter - NOTE pydantic exception, not api exception
    client.post_study("")
except ValidationError:
    pass
else:
    assert False, "ValidationError should have been raised"

try:
    # mistyped attribute - NOTE pydantic exception, not api exception
    client.post_study(Study(uuid=123))
except ValidationError:
    pass
else:
    assert False, "ValidationError should have been raised"

#! "foreign key" links (all fields typed UUID that are not uuid) are validated
try:
    dataset.submitted_in_study_uuid = dataset.uuid
    client.post_dataset(dataset)
except api_exceptions.NotFoundException:
    pass
else:
    assert False, "NotFoundException should have been raised"