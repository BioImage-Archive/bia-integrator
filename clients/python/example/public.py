"""
Assumed internal use, tests ran on local (to generate dummy data)
private_api more complete
"""

from bia_integrator_api.util import get_client

client = get_client()

study_searched = client.search_study_by_accession("S-BIADTEST")
print(study_searched.title)

study_missing = client.search_study_by_accession("S-BIAD")
print(study_missing)

image_representations_searched = client.search_image_representation_by_file_uri("https://")
print(len(image_representations_searched))