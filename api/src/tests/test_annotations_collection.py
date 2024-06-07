from src.tests.util import DBTestMixin, get_template_collection


import pytest
from fastapi.testclient import TestClient


class TestCollectionAnnotation(DBTestMixin):
    @pytest.fixture
    def field_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "title",
            "value": "overwritten",
            "state": "active",
        }

    @pytest.fixture
    def attribute_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "test_attribute",
            "value": "new_attribute",
            "state": "active",
        }

    @pytest.fixture
    def collection_initial(self):
        collection = get_template_collection(add_uuid=True)
        collection["attributes"] = {
            "test_attribute": "initial",
        }

        return collection

    @pytest.fixture
    def collection(
        self,
        api_client: TestClient,
        collection_initial: dict,
        field_annotation: dict,
        attribute_annotation: dict,
        update: bool,
    ):
        collection_initial["annotations"] = [field_annotation, attribute_annotation]

        rsp = api_client.post("private/collections", json=collection_initial)
        assert rsp.status_code == 201, rsp.json()

        if update:
            collection_initial["version"] += 1
            collection_initial["attributes"]["updated_attribute"] = "updated_value"
            rsp = rsp = api_client.post("private/collections", json=collection_initial)
            assert rsp.status_code == 201, rsp.json()

        rsp = api_client.get(f"collections/{collection_initial['uuid']}")
        assert rsp.status_code == 200

        return rsp.json()

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_not_applied_implicit(self, collection: dict):
        assert collection["annotations_applied"] == False

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_applied_when_explicit(
        self,
        collection: dict,
        api_client: TestClient,
        field_annotation: dict,
        attribute_annotation: dict,
    ):
        rsp = api_client.get(
            f"collections/{collection['uuid']}",
            params={
                "apply_annotations": True,
            },
        )
        assert rsp.status_code == 200

        collection_fetched = rsp.json()
        assert collection_fetched["annotations_applied"] == True
        assert collection_fetched[field_annotation["key"]] == field_annotation["value"]

        assert (
            collection_fetched["attributes"][attribute_annotation["key"]]
            == attribute_annotation["value"]
        )
