from src.models.repository import Repository
from src.tests.util import DBTestMixin, get_template_study


import pytest
from fastapi.testclient import TestClient


import uuid as uuid_lib


@pytest.mark.asyncio
class TestStudyAnnotations(DBTestMixin):
    @pytest.fixture
    def field_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "organism",
            "value": "overwritten",
            "state": "active",
        }

    @pytest.fixture
    def attribute_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "test_attribute",
            "value": "overwritten",
            "state": "active",
        }

    @pytest.fixture
    def study_initial(self):
        study = get_template_study(add_uuid=True)
        study["attributes"] = {
            "test_attribute": "initial",
        }

        return study

    @pytest.fixture
    def study(
        self,
        api_client: TestClient,
        study_initial: dict,
        field_annotation: dict,
        attribute_annotation: dict,
        update: bool,
    ):
        study_initial["annotations"] = [field_annotation, attribute_annotation]

        rsp = api_client.post("private/studies", json=study_initial)
        assert rsp.status_code == 201, rsp.json()

        if update:
            study_initial["version"] += 1
            study_initial["attributes"]["updated_attribute"] = "updated_value"
            rsp = api_client.patch("private/studies", json=study_initial)
            assert rsp.status_code == 200, rsp.json()

        rsp = api_client.get(f"studies/{study_initial['uuid']}")
        assert rsp.status_code == 200

        return rsp.json()

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_not_applied_when_fetching(
        self, study_initial: dict, study: dict
    ):
        assert study_initial == study

    @pytest.mark.parametrize("update", [False, True])
    async def test_annotations_not_applied_when_persisted(
        self,
        db: Repository,
        study: dict,
        study_initial: dict,
        field_annotation: dict,
        attribute_annotation: dict,
    ):
        study_in_db = await db.find_study_by_uuid(study["uuid"])
        study_in_db = study_in_db.model_dump()  # just to simplify

        assert (
            study_in_db[field_annotation["key"]]
            == study_initial[field_annotation["key"]]
        )
        assert study_in_db[field_annotation["key"]] != field_annotation["value"]

        assert (
            study_in_db["attributes"][attribute_annotation["key"]]
            == study_initial["attributes"][attribute_annotation["key"]]
        )
        assert (
            study_in_db["attributes"][attribute_annotation["key"]]
            != attribute_annotation["value"]
        )

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_applied_when_explicit(
        self,
        study: dict,
        api_client: TestClient,
        study_initial: dict,
        field_annotation: dict,
        attribute_annotation: dict,
    ):
        rsp = api_client.get(f"studies/{study_initial['uuid']}?apply_annotations=true")
        assert rsp.status_code == 200

        study_with_annotations = rsp.json()
        assert (
            study_with_annotations[field_annotation["key"]] == field_annotation["value"]
        )
        assert (
            study_with_annotations["attributes"][attribute_annotation["key"]]
            == attribute_annotation["value"]
        )
        assert (
            study_with_annotations["annotations_applied"] == True
        ), "annotations_applied field should always be set to True if annotations were applied"

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_not_applied_when_explicit(
        self, study: dict, api_client: TestClient, study_initial: dict
    ):
        rsp = api_client.get(f"studies/{study_initial['uuid']}?apply_annotations=false")
        assert rsp.status_code == 200

        study_without_annotations = rsp.json()
        assert study_without_annotations == study
        assert study_without_annotations == study_initial
        assert (
            study_without_annotations["annotations_applied"] == False
        ), "annotations_applied field should always be set to False if annotations were applied"

    def test_object_fetch_sets_annotations_applied_flag_even_if_no_annotations_set(
        self, study_initial: dict, api_client: TestClient
    ):
        assert (
            study_initial["annotations"] == []
        ), "This test assumes the object has no annotations"

        rsp = api_client.post("private/studies", json=study_initial)
        assert rsp.status_code == 201, rsp.json()

        rsp = api_client.get(f"studies/{study_initial['uuid']}?apply_annotations=true")
        assert rsp.status_code == 200
        study_fetched = rsp.json()

        assert (
            study_fetched["annotations_applied"] == True
        ), "Study doesn't have annotations, but was fetched with apply_annotations=true"

        del study_fetched["annotations_applied"]
        del study_initial["annotations_applied"]
        assert (
            study_fetched == study_initial
        ), "No annotations should have been applied (there are none), so the object should be unchanged"

    @pytest.mark.parametrize("update", [False, True])
    def test_search_annotations_applied_when_explicit(
        self, study: dict, api_client: TestClient
    ):
        study_uuid = uuid_lib.UUID(study["uuid"])
        prev_study_uuid = uuid_lib.UUID(int=study_uuid.int - 1)

        rsp = api_client.get(
            f"search/studies",
            params={
                "apply_annotations": True,
                "start_uuid": str(prev_study_uuid),
                "limit": 1,
            },
        )
        assert rsp.status_code == 200
        assert len(rsp.json()) == 1
        study_fetched = rsp.json()[0]

        # if annotations_applied, then all annotations applied correctly (tested separately)
        assert study_fetched["annotations_applied"] == True

    @pytest.mark.parametrize("update", [False, True])
    def test_accession_to_objectinfo_no_apply_annotations(
        self, study: dict, api_client: TestClient
    ):
        rsp = api_client.get(
            f"object_info_by_accessions?apply_annotations=true",
            params={
                "accessions": [study["uuid"]],
            },
        )
        study_annotated = rsp.json()

        rsp = api_client.get(
            f"object_info_by_accessions",
            params={
                "accessions": [study["uuid"]],
            },
        )
        study_not_annotated = rsp.json()

        assert study_annotated == study_not_annotated

    def test_object_create_annotations_applied_rejected(
        self, study_initial: dict, api_client: TestClient
    ):
        study_initial["annotations_applied"] = True

        rsp = api_client.post("private/studies", json=study_initial)
        assert rsp.status_code == 422, rsp.json()

        # double-check object not created
        rsp = api_client.get(f"studies/{study_initial['uuid']}")
        assert rsp.status_code == 404

    @pytest.mark.parametrize("update", [False, True])
    def test_object_update_annotations_applied_rejected(
        self, study: dict, api_client: TestClient
    ):
        study["annotations_applied"] = True
        study["version"] += 1

        rsp = api_client.patch("private/studies", json=study)
        assert rsp.status_code == 422, rsp.json()

        # double-check object not updated
        rsp = api_client.get(f"studies/{study['uuid']}")
        assert rsp.status_code == 200
        assert rsp.json()["version"] == study["version"] - 1
