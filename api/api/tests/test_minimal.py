"""
WIP minimal tests
tl;dr avoid importing get_uuid to make sure we reuse mocks
"""

from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid


def test_get_created_study(api_client: TestClient, existing_study):
    rsp = api_client.get(f"study/{existing_study['uuid']}")
    assert rsp.status_code == 200, rsp.text
    assert rsp.json() == existing_study


def test_get_study_datasets(
    api_client: TestClient, existing_study, existing_experimental_imaging_dataset
):
    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset",
        params={"page_size": 100},
    )
    assert rsp.status_code == 200, rsp.json()
    assert rsp.json() == [existing_experimental_imaging_dataset]


def test_get_biosample_specimens(
    api_client: TestClient, existing_biosample, existing_specimen
):
    rsp = api_client.get(
        f"bio_sample/{existing_biosample['uuid']}/specimen",
        params={"page_size": 100},
    )
    assert rsp.status_code == 200, rsp.json()
    assert rsp.json() == [existing_specimen]


def test_create_object_missing_dependency_fails(
    api_client: TestClient, existing_specimen: dict
):
    """
    overwrite uuid and sample uuid on an existing specimen to get a new specimen with a missing sample uuid
    """
    specimen = existing_specimen.copy()
    specimen["uuid"] = get_uuid()
    specimen["sample_of_uuid"] = [get_uuid()]

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 404, rsp.json()

    # Error should mention the uuid referenced in sample_of_uuid that doesn't exist
    rsp_body = rsp.json()
    assert specimen["sample_of_uuid"][0] in rsp_body["detail"]


def test_create_object_mistyped_dependency_fails(
    api_client: TestClient, existing_specimen: dict, existing_study: dict
):
    specimen = existing_specimen.copy()
    specimen["uuid"] = get_uuid()
    specimen["imaging_preparation_protocol_uuid"] = [existing_study["uuid"]]

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 404, rsp.json()

    # Error message should mention the referenced uuid that doesn't exist
    rsp_body = rsp.json()
    assert specimen["imaging_preparation_protocol_uuid"][0] in rsp_body["detail"]


def test_create_object_duplicate_dependency_fails(
    api_client: TestClient, existing_specimen: dict
):
    """
    accidental feature of the dependency check implementation
       if a list of referenced objects contains duplicates (presumably there by accident), object creation should fail
    except the error is "Not found" instead of something to do with duplicates
    """

    specimen = existing_specimen.copy()
    specimen["uuid"] = get_uuid()
    specimen["sample_of_uuid"] = specimen["sample_of_uuid"] + specimen["sample_of_uuid"]

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 404, rsp.json()

    # Error message should mention the referenced uuid that doesn't exist
    rsp_body = rsp.json()
    assert specimen["sample_of_uuid"][0] in rsp_body["detail"]


#   TODO - when we add indices
# def test_duplicate_uuid_fails(
#    api_client: TestClient, existing_specimen: dict, existing_study: dict
# ):
#    """
#    ! Should fail (maybe with a different status code)
#    Needs indices
#    """
#    specimen = existing_specimen.copy()
#    specimen["uuid"] = existing_study["uuid"]

#    rsp = api_client.post(
#        "private/specimen",
#        json=specimen,
#    )
#    assert rsp.status_code == 404, rsp.json()


def test_optional_link_unset_passes(
    api_client: TestClient, existing_image_representation: dict
):
    image_representation = existing_image_representation.copy()

    image_representation["uuid"] = get_uuid()
    del image_representation["original_file_reference_uuid"]

    rsp = api_client.post(
        "private/image_representation",
        json=image_representation,
    )
    assert rsp.status_code == 201, rsp.json()


def test_optional_reverse_link(
    api_client: TestClient, existing_image_representation: dict
):
    rsp = api_client.get(
        f"file_reference/{existing_image_representation['original_file_reference_uuid'][0]}/image_representation",
        params={"page_size": 100},
    )
    assert rsp.status_code == 200, rsp.json()
    assert rsp.json() == [existing_image_representation]


def test_known_bug_should_not_pass_but_does_union_reference_typed_lists_not_exclusive(
    api_client: TestClient,
    existing_annotaton_file_reference: dict,
    existing_derived_image: dict,
    existing_experimentally_captured_image: dict,
):
    existing_annotaton_file_reference |= {
        "uuid": get_uuid(),
        "source_image_uuid": [
            # this should cause an error, because the source images aren't of the same type
            existing_derived_image["uuid"],
            existing_experimentally_captured_image["uuid"],
        ],
    }
    rsp = api_client.post(
        "private/annotation_file_reference",
        json=existing_annotaton_file_reference,
    )
    assert rsp.status_code == 201, "Fixed the bug!"


def test_cannot_resolve_reverse_union_link_from_mistyped_parent(
    api_client: TestClient,
    existing_annotaton_file_reference: dict,
    existing_experimentally_captured_image: dict,
):
    existing_annotaton_file_reference |= {
        "uuid": get_uuid(),
        "source_image_uuid": [
            # Note no derived_image anywhere
            existing_experimentally_captured_image["uuid"],
        ],
    }
    rsp = api_client.post(
        "private/annotation_file_reference",
        json=existing_annotaton_file_reference,
    )
    assert rsp.status_code == 201

    rsp = api_client.get(
        # existing_experimentally_captured_image exists but is not a derived_image
        f"derived_image/{existing_experimentally_captured_image['uuid']}/annotation_file_reference",
        params={"page_size": 100},
    )
    assert rsp.status_code == 404


def test_object_update_same_version_zero_rejected(
    api_client: TestClient, existing_study: dict
):
    rsp = api_client.post(
        "private/study",
        json=existing_study,
    )
    assert rsp.status_code == 409


def test_object_update_same_version_nonzero_rejected(
    api_client: TestClient, updated_study: dict
):
    rsp = api_client.post(
        "private/study",
        json=updated_study,
    )
    assert rsp.status_code == 409


def test_object_update_missing_uuid_rejected(
    api_client: TestClient, updated_study: dict
):
    updated_study["uuid"] = get_uuid()

    rsp = api_client.post(
        "private/study",
        json=updated_study,
    )
    assert rsp.status_code == 404


def test_object_update_bump_larger_than_one_rejected(
    api_client: TestClient, existing_study: dict
):
    existing_study["version"] = 2
    rsp = api_client.post(
        "private/study",
        json=existing_study,
    )
    assert rsp.status_code == 409


def test_create_object_negative_version(api_client: TestClient, existing_study: dict):
    new_study = existing_study.copy()

    new_study["version"] = -1
    new_study["uuid"] = get_uuid()

    rsp = api_client.post(
        "private/study",
        json=new_study,
    )
    assert rsp.status_code == 422


def test_create_object_nonzero_positive_version(
    api_client: TestClient, existing_study: dict
):
    new_study = existing_study.copy()

    new_study["version"] = 1
    new_study["uuid"] = get_uuid()

    rsp = api_client.post(
        "private/study",
        json=new_study,
    )
    assert rsp.status_code == 404


def test_db_timeout():
    """
    ! This is very flimsy and dependent on the test env. Maybe just delete it?
    """

    from pymongo.errors import ExecutionTimeout, NetworkTimeout
    import asyncio
    from api.models.repository import Repository
    from api.models.api import Pagination
    from api.settings import Settings

    loop = asyncio.get_event_loop()

    async def large_query():
        db = Repository()
        settings = Settings()
        settings.mongo_timeout_ms = 5
        
        db.configure(settings)

        await db._get_docs_raw(pagination=Pagination(page_size=100))

    try:
        loop.run_until_complete(large_query())
    except ExecutionTimeout as e:
        pass
    except NetworkTimeout as e:
        pass
    else:
        assert False


def test_get_studies(api_client: TestClient, existing_study: dict):
    # @TODO: page_size makes this test fail eventually!
    rsp = api_client.get("study", params={"page_size": 100000})
    assert rsp.status_code == 200

    studies = rsp.json()
    assert all([study["model"]["type_name"] == "Study" for study in studies])
    assert existing_study["uuid"] in [study["uuid"] for study in studies]
