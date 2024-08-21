from bia_integrator_api.util import get_client

client = get_client()

study = client.get_study("06c19696-00e8-4c2e-a27f-23587aedb782")
print(study)