"""
Example script that creates and gets some objects. Please see the api client readme for details
"""

from bia_integrator_api.util import get_client_private
from bia_integrator_api.models import Study, LicenceType, Contributor, ExperimentalImagingDataset
from datetime import date
from bia_integrator_api import exceptions as api_exceptions
from pydantic import ValidationError

api_base_url = "https://wwwdev.ebi.ac.uk/bioimage-archive/api"
client = get_client_private(
    username="test@example.com",
    password="test",
    api_base_url=api_base_url
)

# Example create/get - equivalent for every object
study = Study(
    uuid="06c19696-00e8-4c2e-a27f-23587aedb782",
    version=0,
    accession_id="test",
    licence=LicenceType.CC0,
    author=[Contributor(
        display_name="test",
        affiliation=[]
    )],
    title = "test",
    release_date = date.today(),
    description = "test",
    attribute = {}
)
client.post_study(study)

study = client.get_study(study.uuid)
print(study)

# attach a dataset to a study, and get all datasets for the study

dataset = ExperimentalImagingDataset(
    uuid = "06c19696-00e8-4c2e-a27f-23587aedb780",
    title_id = "test",
    version = 0,
    attribute = {},
    example_image_uri = [],
    submitted_in_study_uuid = study.uuid
)
client.post_experimental_imaging_dataset(dataset)

study_datasets = client.get_experimental_imaging_dataset_in_study(study.uuid)

# NOTE same dataset
print(study_datasets)

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

try:
    # authenticate with bad credentials
    get_client_private(
        username="does_not_exist_user_test@example.com",
        password="test",
        api_base_url=api_base_url
    )
except api_exceptions.UnauthorizedException:
    pass

try:
    # mistyped parameter - NOTE pydantic exception, not api exception
    client.post_study("")
except ValidationError:
    pass

try:
    # mistyped attribute - NOTE pydantic exception, not api exception
    client.post_study(Study(uuid=123))
except ValidationError:
    pass

#! "foreign key" links (all fields typed UUID that are not uuid) are validated
try:
    dataset.submitted_in_study_uuid = dataset.uuid
    client.post_experimental_imaging_dataset(dataset)
except api_exceptions.NotFoundException:
    pass