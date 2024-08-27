from bia_integrator_api.util import get_client_private
from bia_integrator_api.models import Study, LicenceType, Contributor
from datetime import date

client = get_client_private(
    username="test@example.com",
    password="test"
)

# @TODO: Re-use shared minimal/maximal to make sure field typing / metadata gets transferred through to client
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
    attribute = {},
    model=None
)
client.post_study(study)

study = client.get_study(study.uuid)
print(study)