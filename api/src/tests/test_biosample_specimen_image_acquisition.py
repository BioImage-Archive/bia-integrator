"""
ImageAcquisition depends on nothing but Specimen - not even Image or Study!
Specimen depends on nothing but Biosample
Biosample depends on nothing (at all)

So they were grouped in the same test file
"""

from fastapi.testclient import TestClient
from .util import *


def test_biosample_create_retrieve_update(api_client: TestClient, uuid: str):
    # Note that this actually doesn't depend on any study
    biosample = {
        "uuid": uuid,
        "version": 0,
        "title": "placeholder_title",
        "organism_scientific_name": "placeholder_organism_scientific_name",
        "organism_common_name": "placeholder_organism_common_name",
        "organism_ncbi_taxon": "placeholder_organism_ncbi_taxon",
        "description": "placeholder_description",
        "biological_entity": "placeholder_biological_entity",
        "experimental_variables": ["placeholder_experimental_variable"],
        "extrinsic_variables": ["placeholder_extrinsic_variable"],
        "intrinsic_variables": ["placeholder_intrinsic_variable"],
    }
    rsp = api_client.post(f"private/biosamples", json=biosample)
    assert rsp.status_code == 201, rsp.json()

    rsp = api_client.get(f"biosamples/{uuid}")
    biosample_fetched = rsp.json()
    del biosample_fetched["model"]
    assert biosample_fetched == biosample

    biosample["title"] = "title_updated"
    biosample["version"] += 1
    rsp = api_client.patch(f"private/biosamples", json=biosample)
    assert rsp.status_code == 200, rsp.json()

    rsp = api_client.get(f"biosamples/{uuid}")
    biosample_fetched = rsp.json()
    del biosample_fetched["model"]
    assert biosample_fetched == biosample


def test_specimen_create_retrieve_update(
    api_client: TestClient, uuid: str, existing_biosample
):
    specimen = {
        "uuid": uuid,
        "version": 0,
        "biosample_uuid": existing_biosample["uuid"],
        "title": "placeholder_title",
        "sample_preparation_protocol": "placeholder_sample_preparation_protocol",
        "growth_protocol": "placeholder_growth_protocol",
    }
    rsp = api_client.post(f"private/specimens", json=specimen)
    assert rsp.status_code == 201, rsp.json()

    rsp = api_client.get(f"specimens/{uuid}")
    specimen_fetched = rsp.json()
    del specimen_fetched["model"]
    assert specimen_fetched == specimen

    specimen["title"] = "title_updated"
    specimen["version"] += 1
    rsp = api_client.patch(f"private/specimens", json=specimen)
    assert rsp.status_code == 200, rsp.json()

    rsp = api_client.get(f"specimens/{uuid}")
    specimen_fetched = rsp.json()
    del specimen_fetched["model"]
    assert specimen_fetched == specimen


def test_image_acquisition_create_retrieve_update(
    api_client: TestClient, uuid: str, existing_specimen
):
    image_acquisition = {
        "uuid": uuid,
        "version": 0,
        "specimen_uuid": existing_specimen["uuid"],
        "title": "placeholder_title",
        "imaging_instrument": "placeholder_imaging_instrument",
        "image_acquisition_parameters": "placeholder_image_acquisition_parameters",
        "imaging_method": "placeholder_imaging_method",
    }
    rsp = api_client.post(f"private/image_acquisitions", json=image_acquisition)
    assert rsp.status_code == 201, rsp.json()

    rsp = api_client.get(f"image_acquisitions/{uuid}")
    specimen_fetched = rsp.json()
    del specimen_fetched["model"]
    assert specimen_fetched == image_acquisition

    image_acquisition["title"] = "title_updated"
    image_acquisition["version"] += 1
    rsp = api_client.patch(f"private/image_acquisitions", json=image_acquisition)
    assert rsp.status_code == 200, rsp.json()

    rsp = api_client.get(f"image_acquisitions/{uuid}")
    specimen_fetched = rsp.json()
    del specimen_fetched["model"]
    assert specimen_fetched == image_acquisition


def test_image_add_image_acquisition(
    api_client: TestClient, existing_image, existing_image_acquisition
):
    existing_image["version"] += 1
    existing_image["image_acquisition_methods_uuid"].append(
        existing_image_acquisition["uuid"]
    )

    rsp = api_client.patch(f"private/images/single", json=existing_image)
    assert rsp.status_code == 200, rsp.json()


def test_image_add_study_as_image_acquisition(
    api_client: TestClient, existing_image, existing_study
):
    """
    This test fails on purpose! We need _uuid field type validation
    """
    existing_image["version"] += 1
    existing_image["image_acquisition_methods_uuid"].append(existing_study["uuid"])

    rsp = api_client.patch(f"private/images/single", json=existing_image)
    assert rsp.status_code == 400, rsp.json()
