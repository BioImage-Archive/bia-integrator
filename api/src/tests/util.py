from fastapi.testclient import TestClient

from .. import app
import uuid as uuid_lib
from typing import List
from ..models.repository import repository_create, Repository

from ..api.auth import create_user, get_user
import asyncio
import pytest_asyncio
import os


class DBTestMixin:
    @pytest_asyncio.fixture
    async def db(self) -> Repository:
        return await repository_create(init=True)


def create_user_if_missing(email: str, password: str):
    """
    Exception from the general rule used in this project, of tests being as high-level as possible
    Just to avoid compromising on security for easy test user creation / the logistics of a seed db
    """
    loop = asyncio.get_event_loop()

    async def create_test_user_if_missing():
        db = await repository_create(init=True)

        if not await get_user(db, email):
            await create_user(db, email, password)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_test_user_if_missing())


def authenticate_client(api_client: TestClient):
    user_details = {
        "username": "test@example.com",
        "password": "test",
    }
    create_user_if_missing(user_details["username"], user_details["password"])

    rsp = api_client.post("auth/token", data=user_details)

    assert rsp.status_code == 200
    token = rsp.json()

    api_client.headers["Authorization"] = f"Bearer {token['access_token']}"


def get_collection(
    api_client: TestClient, collection_uuid: str, assert_status_code=200
):
    rsp = api_client.get(f"collections/{collection_uuid}")
    assert rsp.status_code == assert_status_code

    return rsp.json()


def make_collection(api_client: TestClient, collection_attributes_override={}):
    collection = get_template_collection(add_uuid=True)
    collection |= collection_attributes_override

    rsp = api_client.post("private/collections", json=collection)
    assert rsp.status_code == 201, rsp.json()

    return get_collection(api_client, collection["uuid"])


def get_template_study(add_uuid=False):
    study_uuid = None if not add_uuid else get_uuid()
    return {
        "uuid": study_uuid,
        "version": 0,
        "model": {"type_name": "BIAStudy", "version": 1},
        "accession_id": study_uuid,
        "title": "Test BIA study",
        "description": "description",
        "attributes": {},
        "example_image_annotation_uri": "",
        "example_image_uri": "",
        "imaging_type": None,
        "authors": [],
        "tags": [],
        "organism": "test",
        "release_date": "test",
        "file_references_count": 0,
        "images_count": 0,
        "annotations_applied": False,
        "annotations": [],
        "@context": f"file://{os.path.join( package_base(), 'models/jsonld/1.0/StudyContext.jsonld')}",
    }


def get_template_biosample(add_uuid=False):
    biosample_uuid = None if not add_uuid else get_uuid()
    return {
        "uuid": biosample_uuid,
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
        "@context": f"file://{os.path.join(package_base(), 'models/jsonld/1.0/BiosampleContext.jsonld')}",
    }


def get_template_specimen(existing_biosample, add_uuid=False):
    specimen_uuid = None if not add_uuid else get_uuid()
    return {
        "uuid": specimen_uuid,
        "version": 0,
        "biosample_uuid": existing_biosample["uuid"],
        "title": "placeholder_title",
        "sample_preparation_protocol": "placeholder_sample_preparation_protocol",
        "growth_protocol": "placeholder_growth_protocol",
        "@context": f"file://{os.path.join(package_base(), 'models/jsonld/1.0/SpecimenContext.jsonld')}",
    }


def get_template_image_acquisition(existing_specimen, add_uuid=False):
    image_acquisition_uuid = None if not add_uuid else get_uuid()
    return {
        "uuid": image_acquisition_uuid,
        "version": 0,
        "specimen_uuid": existing_specimen["uuid"],
        "title": "placeholder_title",
        "imaging_instrument": "placeholder_imaging_instrument",
        "image_acquisition_parameters": "placeholder_image_acquisition_parameters",
        "imaging_method": "placeholder_imaging_method",
        "@context": f"file://{os.path.join(package_base(), 'models/jsonld/1.0/ImageAcquisitionContext.jsonld')}",
    }


def make_study(api_client: TestClient, study_attributes_override={}):
    study = get_template_study(add_uuid=True)
    study |= study_attributes_override

    rsp = api_client.post("private/studies", json=study)
    assert rsp.status_code == 201, rsp.json()

    return get_study(api_client, study["uuid"])


def make_biosample(api_client: TestClient, biosample_attributes_override={}):
    biosample = get_template_biosample(add_uuid=True)
    biosample |= biosample_attributes_override

    rsp = api_client.post("private/biosamples", json=biosample)
    assert rsp.status_code == 201, rsp.json()

    return get_biosample(api_client, biosample["uuid"])


def make_specimen(
    api_client: TestClient, existing_biosample: dict, specimen_attributes_override={}
):
    specimen = get_template_specimen(existing_biosample, add_uuid=True)
    specimen |= specimen_attributes_override

    rsp = api_client.post("private/specimens", json=specimen)
    assert rsp.status_code == 201, rsp.json()

    return get_specimen(api_client, specimen["uuid"])


def make_image_acquisition(
    api_client: TestClient,
    existing_specimen: dict,
    image_acquisition_attributes_override={},
):
    image_acquisition = get_template_image_acquisition(existing_specimen, add_uuid=True)
    image_acquisition |= image_acquisition_attributes_override

    rsp = api_client.post("private/image_acquisitions", json=image_acquisition)
    assert rsp.status_code == 201, rsp.json()

    return get_image_acquisition(api_client, image_acquisition["uuid"])


def get_template_file_reference(existing_study: dict, add_uuid=False):
    return {
        "uuid": None if not add_uuid else get_uuid(),
        "version": 0,
        "study_uuid": existing_study["uuid"],
        "model": {"type_name": "FileReference", "version": 1},
        "name": "test",
        "uri": "https://test.com/test",
        "size_in_bytes": 2,
        "attributes": {},
        "annotations": [],
        "annotations_applied": False,
        "type": "file",
        "@context": f"file://{os.path.join(package_base(), 'models/jsonld/1.0/StudyFileReferenceContext.jsonld')}",
    }


def get_template_collection(add_uuid=False):
    return {
        "uuid": None if not add_uuid else get_uuid(),
        "version": 0,
        "model": {"type_name": "BIACollection", "version": 1},
        "name": "template_collection_name",
        "title": "template_collection_title",
        "subtitle": "template_collection_subtitle",
        "description": "template_collection_description",
        "study_uuids": [],
        "attributes": {},
        "annotations": [],
        "annotations_applied": False,
        "@context": f"file://{os.path.join(package_base(), 'models/jsonld/1.0/CollectionContext.jsonld')}",
    }


def get_template_image(existing_study: dict, add_uuid=False):
    return {
        "uuid": None if not add_uuid else get_uuid(),
        "version": 0,
        "study_uuid": existing_study["uuid"],
        "model": {"type_name": "BIAImage", "version": 2},
        "name": f"image_name_value",
        "original_relpath": f"/home/test/image_path_value",
        "attributes": {
            "k": "v",
        },
        "annotations": [],
        "annotations_applied": False,
        "dimensions": None,
        "alias": None,
        "representations": [],
        "image_acquisition_methods_uuid": [],
        "@context": f"file://{os.path.join(package_base(), 'models/jsonld/1.0/ImageContext.jsonld')}",
    }


def make_images(
    api_client: TestClient,
    existing_study: dict,
    n: int,
    image_template=None,
    expect_status=201,
):
    if image_template is None:
        image_template = get_template_image(existing_study)

    images = []
    for i in range(n):
        img = image_template.copy()
        if not img["uuid"]:
            img["uuid"] = get_uuid()
            img["name"] += str(i)

        images.append(img)

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == expect_status, rsp.json()

    return images


def make_file_references(
    api_client: TestClient, existing_study: dict, n: int, file_reference_template=None
):
    if file_reference_template is None:
        file_reference_template = get_template_file_reference(existing_study)

    file_references = []
    for i in range(n):
        file_ref = file_reference_template.copy()
        if not file_ref["uuid"]:
            file_ref["uuid"] = get_uuid()
            file_ref["name"] += str(i)

        file_references.append(file_ref)

    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    return file_references


def get_study(api_client: TestClient, study_uuid: str, assert_status_code=200):
    rsp = api_client.get(f"studies/{study_uuid}")
    assert rsp.status_code == assert_status_code

    return rsp.json()


def get_biosample(api_client: TestClient, biosample_uuid: str, assert_status_code=200):
    rsp = api_client.get(f"biosamples/{biosample_uuid}")
    assert rsp.status_code == assert_status_code

    return rsp.json()


def get_specimen(api_client: TestClient, specimen_uuid: str, assert_status_code=200):
    rsp = api_client.get(f"specimens/{specimen_uuid}")
    assert rsp.status_code == assert_status_code

    return rsp.json()


def get_image_acquisition(
    api_client: TestClient, image_acquisition_uuid: str, assert_status_code=200
):
    rsp = api_client.get(f"image_acquisitions/{image_acquisition_uuid}")
    assert rsp.status_code == assert_status_code

    return rsp.json()


TEST_SERVER_BASE_URL = "http://localhost.com/api/v1"


def get_client(**kwargs) -> TestClient:
    from fastapi.responses import JSONResponse
    from fastapi import Request
    import traceback

    @app.app.exception_handler(Exception)
    def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=traceback.format_exception(exc, value=exc, tb=exc.__traceback__),
        )

    return TestClient(app.app, base_url=TEST_SERVER_BASE_URL, **kwargs)


def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.uuid4()

    return str(generated)


def unorderd_lists_equality(list1: list[dict], list2: list[dict]) -> bool:
    # verbose equality check to compare lists of dictionaries created from json objects
    if len(list1) == len(list2):
        for elem1 in list1:
            if list1.count(elem1) != list2.count(elem1):
                return False
        return True
    return False


def assert_bulk_response_items_correct(
    api_client: TestClient,
    bulk_create_payload: List[dict],
    bulk_create_response: dict,
    single_item_get_path: str,
):
    for response_item in bulk_create_response["items"]:
        created_item = bulk_create_payload[response_item["idx_in_request"]]
        rsp = api_client.get(f"{single_item_get_path}/{created_item['uuid']}")

        if response_item["status"] == 201:
            assert rsp.status_code == 200
            fetched_item = rsp.json()
            assert fetched_item == created_item
        elif response_item["status"] == 400:
            if response_item["message"].startswith(
                "E11000 duplicate key error collection"
            ):
                # clashing with existing document
                # check that the other document exists and is different from the attempted insert
                assert rsp.status_code == 200

                # only check the attributes in the request item, to avoid the check always passing due to model changes
                existing_item = rsp.json()
                existing_item_shaped_as_request = {
                    k: existing_item[k] for k in created_item.keys()
                }
                assert existing_item_shaped_as_request != created_item
            else:
                # if there was no clash but the insert was rejected, the object shouldn't exist at all
                assert rsp.status_code == 404


def package_base() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
