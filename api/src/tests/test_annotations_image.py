from src.models.repository import Repository
from src.tests.util import DBTestMixin, get_template_image


import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
class TestImageAnnotations(DBTestMixin):
    @pytest.fixture
    def field_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "original_relpath",
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
    def img_initial(self, existing_study):
        img = get_template_image(existing_study, add_uuid=True)
        img["attributes"] = {
            "test_attribute": "initial",
        }

        return img

    @pytest.fixture
    def image(
        self,
        api_client: TestClient,
        img_initial: dict,
        field_annotation: dict,
        attribute_annotation: dict,
        update: bool,
    ):
        img_initial["annotations"] = [field_annotation, attribute_annotation]

        rsp = api_client.post("private/images", json=[img_initial])
        assert rsp.status_code == 201, rsp.json()

        if update:
            img_initial["version"] += 1
            img_initial["attributes"]["updated_attribute"] = "updated_value"
            rsp = api_client.patch("private/images/single", json=img_initial)
            assert rsp.status_code == 200, rsp.json()

        rsp = api_client.get(f"images/{img_initial['uuid']}")
        assert rsp.status_code == 200

        return rsp.json()

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_not_applied_when_fetching(
        self, img_initial: dict, image: dict
    ):
        assert img_initial == image

    @pytest.mark.parametrize("update", [False, True])
    async def test_annotations_not_applied_when_persisted(
        self,
        db: Repository,
        image: dict,
        img_initial: dict,
        field_annotation: dict,
        attribute_annotation: dict,
    ):
        img_in_db = await db.find_image_by_uuid(image["uuid"])
        img_in_db = img_in_db.model_dump()  # just to simplify

        assert img_in_db[field_annotation["key"]] == img_in_db[field_annotation["key"]]
        assert img_in_db[field_annotation["key"]] != field_annotation["value"]

        assert (
            img_in_db["attributes"][attribute_annotation["key"]]
            == img_initial["attributes"][attribute_annotation["key"]]
        )
        assert (
            img_in_db["attributes"][attribute_annotation["key"]]
            != attribute_annotation["value"]
        )

    @pytest.mark.parametrize("update", [False, True])
    def test_annotations_applied_when_explicit(
        self,
        api_client: TestClient,
        image: dict,
        attribute_annotation: dict,
        field_annotation: dict,
    ):
        rsp = api_client.get(
            f"images/{image['uuid']}",
            params={
                "apply_annotations": True,
            },
        )
        assert rsp.status_code == 200
        img_fetched = rsp.json()

        assert img_fetched["annotations_applied"] == True
        assert (
            img_fetched["attributes"][attribute_annotation["key"]]
            == attribute_annotation["value"]
        )
        assert img_fetched[field_annotation["key"]] == field_annotation["value"]
