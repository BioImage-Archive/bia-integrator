"""
Assumed internal use, tests ran on local (to generate dummy data)
private_api more complete
"""

from bia_integrator_api.util import get_client

api_base_url = "http://api:8080"
client = get_client(
    api_base_url=api_base_url
)

study_searched = client.search_study_by_accession("test")
print(study_searched.title)

study_missing = client.search_study_by_accession("S-BIAD")
print(study_missing)

all_representations = []
image_representations_searched = client.search_image_representation_by_file_uri("https://", page_size=10)
all_representations += image_representations_searched
while len(image_representations_searched) == 10:
    image_representations_searched = client.search_image_representation_by_file_uri(
        "https://",
        start_from_uuid=image_representations_searched[-1].uuid,
        page_size=10
    )
    all_representations += image_representations_searched

print(len(all_representations))
