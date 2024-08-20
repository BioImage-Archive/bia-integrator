from bia_integrator_api.util import simple_client
from bia_integrator_api import models as api_models, exceptions as api_exceptions
from util import get_uuid

rw_client = simple_client(
    "http://127.0.0.1:8080",
    "test@example.com",
    "test",
    # FIXME: Re-enable and remove this flag once api is on publicly accessible infra
    disable_ssl_host_check=True
)

study_uuid = get_uuid()
my_study = api_models.BIAStudy(
    uuid = study_uuid,
    version = 0,
    title = "Study title",
    description = "Study description",
    release_date = "@TODO: Check format",
    accession_id = f"accessions_must_be_unique_{study_uuid}",
    organism = "test",
    authors = [
        api_models.Author(name="Study Author 1"),
        api_models.Author(name="Study Author 2")
    ]
)
rw_client.create_study(my_study)

"""
Note the image dependencies being created ahead of the image.
Doing this might be useful so that everything gets created in a single pass, and also the bulk operations can be used.
There is also the option of creating the image with image_acquisitions_uuid = [] first,
    then creating the dependencies, and then updating each image to include its corresponding image_acquisitions 
"""

my_biosample = api_models.Biosample(
    uuid = get_uuid(),
    version = 0,
    title = "A known cell line",
    organism_scientific_name = "Mus musculus",
    organism_common_name = "Mouse",
    organism_ncbi_taxon = "10090",
    description = "",
    biological_entity = "liver",
    experimental_variables = ["example"],
    extrinsic_variables = ["example"],
    intrinsic_variables = ["example"]
)
rw_client.create_biosample(my_biosample)

my_specimen = api_models.Specimen(
    uuid = get_uuid(),
    version = 0,
    title = "Specimen brief description",
    sample_preparation_protocol = "",
    growth_protocol = "",
    biosample_uuid = my_biosample.uuid
)
rw_client.create_specimen(my_specimen)


my_image_acquisition = api_models.ImageAcquisition(
    uuid = get_uuid(),
    version = 0,
    title = "An Image Acquisition that's possibly shared across multiple Images",
    imaging_instrument = "Instrument description, model, etc",
    image_acquisition_parameters = "",
    imaging_method = "Text value of the FBBI term if it exists",
    specimen_uuid = my_specimen.uuid
)
rw_client.create_image_acquisition(my_image_acquisition)


my_image = api_models.BIAImage(
    uuid = get_uuid(),
    version = 0,
    study_uuid = study_uuid,
    original_relpath = "",
    image_acquisitions_uuid=[
        my_image_acquisition.uuid
    ]
)
rw_client.create_images([my_image])
