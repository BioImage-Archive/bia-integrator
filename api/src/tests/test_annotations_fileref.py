from src.models.repository import Repository
from src.tests.util import DBTestMixin, get_template_file_reference


import pytest
from fastapi.testclient import TestClient


class TestFilerefAnnotations(DBTestMixin):
    @pytest.fixture
    def field_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "name",
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
    def fileref_initial(self, existing_study):
        fileref = get_template_file_reference(existing_study, add_uuid=True)
        fileref["attributes"] = {
            "test_attribute": "initial",
        }

        return fileref

    @pytest.fixture
    def fileref(
        self,
        api_client: TestClient,
        fileref_initial: dict,
        field_annotation: dict,
        attribute_annotation: dict,
        update: bool,
    ):
        fileref_initial["annotations"] = [field_annotation, attribute_annotation]

        rsp = api_client.post("private/file_references", json=[fileref_initial])
        assert rsp.status_code == 201, rsp.json()

        if update:
            fileref_initial["version"] += 1
            fileref_initial["attributes"]["updated_attribute"] = "updated_value"
            rsp = api_client.patch(
                "private/file_references/single", json=fileref_initial
            )
            assert rsp.status_code == 200, rsp.json()

        rsp = api_client.get(f"file_references/{fileref_initial['uuid']}")
        assert rsp.status_code == 200

        return rsp.json()

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_not_applied_when_fetching(
        self, fileref_initial: dict, fileref: dict
    ):
        assert fileref_initial == fileref

    @pytest.mark.asyncio
    @pytest.mark.parametrize("update", [False, True])
    async def test_annotations_not_applied_when_persisted(
        self,
        db: Repository,
        fileref: dict,
        fileref_initial: dict,
        field_annotation: dict,
        attribute_annotation: dict,
    ):
        fileref_in_db = await db.find_fileref_by_uuid(fileref["uuid"])
        fileref_in_db = fileref_in_db.model_dump()  # just to simplify

        assert (
            fileref_in_db[field_annotation["key"]]
            == fileref_in_db[field_annotation["key"]]
        )
        assert fileref_in_db[field_annotation["key"]] != field_annotation["value"]

        assert (
            fileref_in_db["attributes"][attribute_annotation["key"]]
            == fileref_initial["attributes"][attribute_annotation["key"]]
        )
        assert (
            fileref_in_db["attributes"][attribute_annotation["key"]]
            != attribute_annotation["value"]
        )

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_applied_when_explicit(
        self,
        api_client: TestClient,
        fileref: dict,
        attribute_annotation: dict,
        field_annotation: dict,
    ):
        rsp = api_client.get(
            f"file_references/{fileref['uuid']}",
            params={
                "apply_annotations": True,
            },
        )
        assert rsp.status_code == 200
        fileref_fetched = rsp.json()

        assert fileref_fetched["annotations_applied"] == True
        assert (
            fileref_fetched["attributes"][attribute_annotation["key"]]
            == attribute_annotation["value"]
        )
        assert fileref_fetched[field_annotation["key"]] == field_annotation["value"]
