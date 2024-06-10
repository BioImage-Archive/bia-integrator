"""
ImageAcquisition depends on nothing but Specimen - not even Image or Study!
Specimen depends on nothing but Biosample
Biosample depends on nothing (at all)

So they were grouped in the same test file
"""

from fastapi.testclient import TestClient
from .util import (
    get_template_biosample,
    get_template_specimen,
    get_template_image_acquisition,
)
import pytest


def test_biosample_create_retrieve_update(api_client: TestClient, uuid: str):
    # Note that this actually doesn't depend on any study
    biosample = get_template_biosample() | {"uuid": uuid}
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
    api_client: TestClient, existing_biosample: dict, uuid: str
):
    specimen = get_template_specimen(existing_biosample) | {"uuid": uuid}
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
    api_client: TestClient, existing_specimen: dict, uuid: str
):
    image_acquisition = get_template_image_acquisition(existing_specimen) | {
        "uuid": uuid
    }
    rsp = api_client.post(f"private/image_acquisitions", json=image_acquisition)
    assert rsp.status_code == 201, rsp.json()

    rsp = api_client.get(f"image_acquisitions/{uuid}")
    image_acquisition_fetched = rsp.json()
    del image_acquisition_fetched["model"]
    assert image_acquisition_fetched == image_acquisition

    image_acquisition["title"] = "title_updated"
    image_acquisition["version"] += 1
    rsp = api_client.patch(f"private/image_acquisitions", json=image_acquisition)
    assert rsp.status_code == 200, rsp.json()

    rsp = api_client.get(f"image_acquisitions/{uuid}")
    image_acquisition_fetched = rsp.json()
    del image_acquisition_fetched["model"]
    assert image_acquisition_fetched == image_acquisition


def test_create_update_with_badly_typed_uuid(
    api_client: TestClient,
    existing_specimen: dict,
    existing_image_acquisition: dict,
    existing_study: dict,
    uuid: str,
):
    image_acquisition = get_template_image_acquisition(existing_study) | {"uuid": uuid}
    rsp = api_client.post(f"private/image_acquisitions", json=image_acquisition)
    assert rsp.status_code == 400, rsp.json()

    existing_image_acquisition["specimen_uuid"] = existing_study["uuid"]
    existing_image_acquisition["version"] += 1
    rsp = api_client.patch(
        f"private/image_acquisitions", json=existing_image_acquisition
    )
    assert rsp.status_code == 400, rsp.json()

    specimen = get_template_specimen(existing_study, add_uuid=True)
    rsp = api_client.post(f"private/specimens", json=specimen)
    assert rsp.status_code == 400, rsp.json()

    existing_specimen["biosample_uuid"] = existing_study["uuid"]
    existing_specimen["version"] += 1
    rsp = api_client.patch(f"private/specimens", json=existing_specimen)
    assert rsp.status_code == 400, rsp.json()


def test_image_add_image_acquisition(
    api_client: TestClient, existing_image: dict, existing_image_acquisition: dict
):
    existing_image["version"] += 1
    existing_image["image_acquisitions_uuid"].append(existing_image_acquisition["uuid"])

    rsp = api_client.patch(f"private/images/single", json=existing_image)
    assert rsp.status_code == 200, rsp.json()


def test_image_add_study_as_image_acquisition(
    api_client: TestClient, existing_image: dict, existing_study: dict
):
    existing_image["version"] += 1
    existing_image["image_acquisitions_uuid"].append(existing_study["uuid"])

    rsp = api_client.patch(f"private/images/single", json=existing_image)
    assert rsp.status_code == 400, rsp.json()
