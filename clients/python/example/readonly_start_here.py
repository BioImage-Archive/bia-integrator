from bia_integrator_api.util import get_client

client = get_client()

for study in client.search_studies(limit=10):
    print(study.uuid)


