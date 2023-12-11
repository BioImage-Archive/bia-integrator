"""
Final invariants about the object (annotations not applied when they shouldn't be, applied when they should) should hold for any possible way an object could be persisted (created, updated, something else?)
    pass a parameterised flag (update) to fixture-creating method to decide which case to run
    @FIXME: Note that test function is parameterised with a param intended for the fixture - this is to have named params. Fixtures with named params / parameterised fixtures with autowiring not supported now
    Basically what is needed is to have "different fixtures with the same name" for a study * all_possible_ways_to_change_a_study
"""

import pytest
from fastapi.testclient import TestClient
from .util import *
from ..models.repository import Repository
import uuid as uuid_lib

@pytest.mark.asyncio
class TestStudyAnnotations(DBTestMixin):
    @pytest.fixture
    def field_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "organism",
            "value": "overwritten",
            "state": "active"
        }

    @pytest.fixture
    def attribute_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "test_attribute",
            "value": "overwritten",
            "state": "active"
        }

    @pytest.fixture
    def study_initial(self):
        study = get_template_study(add_uuid=True)
        study["attributes"] = {
            "test_attribute": "initial"
        }

        return study

    @pytest.fixture
    def study(self, api_client: TestClient, study_initial: dict, field_annotation: dict, attribute_annotation: dict, update: bool):
        study_initial["annotations"] = [field_annotation, attribute_annotation]

        rsp = api_client.post('private/studies', json=study_initial)
        assert rsp.status_code == 201, rsp.json()

        if update:
            study_initial['version'] += 1
            study_initial["attributes"]["updated_attribute"] = "updated_value"
            rsp = api_client.patch('private/studies', json=study_initial)
            assert rsp.status_code == 201, rsp.json()

        rsp = api_client.get(f"studies/{study_initial['uuid']}")
        assert rsp.status_code == 200

        return rsp.json()
    
    @pytest.mark.parametrize('update', [False, True])
    async def test_annotations_not_applied_when_fetching(self, study_initial: dict, study: dict):
        assert study_initial == study
    
    @pytest.mark.parametrize('update', [False, True])
    async def test_annotations_not_applied_when_persisted(self, db: Repository, study: dict, study_initial: dict, field_annotation: dict, attribute_annotation: dict):
        study_in_db = await db.find_study_by_uuid(study['uuid'])
        study_in_db = study_in_db.model_dump() # just to simplify

        assert study_in_db[field_annotation['key']] == study_initial[field_annotation['key']]
        assert study_in_db[field_annotation['key']] != field_annotation['value']

        assert study_in_db['attributes'][attribute_annotation['key']] == study_initial['attributes'][attribute_annotation['key']]
        assert study_in_db['attributes'][attribute_annotation['key']] != attribute_annotation['value']

    @pytest.mark.parametrize('update', [False, True])
    async def test_annotations_applied_flag_not_persisted(self, db: Repository, study):
        study_in_db = await db.find_study_by_uuid(study['uuid'])
        study_in_db = study_in_db.model_dump() # just to simplify

        assert "annotations_applied" in study, "Checking that something is absent below. Ensure it existed in the first place, or the test isn't useful (so fails if we rename the attribute)"
        assert "annotations_applied" not in study_in_db

    @pytest.mark.parametrize('update', [False, True])
    def test_annotations_applied_when_explicit(self, study: dict, api_client: TestClient, study_initial: dict, field_annotation: dict, attribute_annotation: dict):
        rsp = api_client.get(f"studies/{study_initial['uuid']}?apply_annotations=true")
        assert rsp.status_code == 200

        study_with_annotations = rsp.json()
        assert study_with_annotations[field_annotation["key"]] == field_annotation["value"]
        assert study_with_annotations["attributes"][attribute_annotation["key"]] == attribute_annotation["value"]
        assert study_with_annotations["annotations_applied"] == True, "annotations_applied field should always be set to True if annotations were applied"

    @pytest.mark.parametrize('update', [False, True])
    def test_annotations_not_applied_when_explicit(self, study: dict, api_client: TestClient, study_initial: dict):
        rsp = api_client.get(f"studies/{study_initial['uuid']}?apply_annotations=false")
        assert rsp.status_code == 200

        study_without_annotations = rsp.json()
        assert study_without_annotations == study
        assert study_without_annotations == study_initial
        assert study_without_annotations["annotations_applied"] == False, "annotations_applied field should always be set to False if annotations were applied"
    
    def test_object_fetch_sets_annotations_applied_flag_even_if_no_annotations_set(self, study_initial: dict, api_client: TestClient):
        assert study_initial["annotations"] == [], "This test assumes the object has no annotations"

        rsp = api_client.post('private/studies', json=study_initial)
        assert rsp.status_code == 201, rsp.json()

        rsp = api_client.get(f"studies/{study_initial['uuid']}?apply_annotations=true")
        assert rsp.status_code == 200
        study_fetched = rsp.json()

        assert study_fetched["annotations_applied"] == True, "Study doesn't have annotations, but was fetched with apply_annotations=true"

        del study_fetched["annotations_applied"]
        del study_initial["annotations_applied"]
        assert study_fetched == study_initial, "No annotations should have been applied (there are none), so the object should be unchanged"

    @pytest.mark.parametrize('update', [False, True])
    def test_search_annotations_applied_when_explicit(self, study: dict, api_client: TestClient):
        study_uuid = uuid_lib.UUID(study['uuid'])
        prev_study_uuid = uuid_lib.UUID(
            int=study_uuid.int-1
        )

        rsp = api_client.get(f"search/studies", params={
            "apply_annotations": True,
            "start_uuid": str(prev_study_uuid),
            "limit": 1
        })
        assert rsp.status_code == 200
        assert len(rsp.json()) == 1
        study_fetched = rsp.json()[0]

        # if annotations_applied, then all annotations applied correctly (tested separately)
        assert study_fetched['annotations_applied'] == True

    @pytest.mark.parametrize('update', [False, True])
    def test_accession_to_objectinfo_no_apply_annotations(self, study: dict, api_client: TestClient):
        rsp = api_client.get(f"object_info_by_accessions?apply_annotations=true", params={
            'accessions': [study['uuid']]
        })
        study_annotated = rsp.json()

        rsp = api_client.get(f"object_info_by_accessions", params={
            'accessions': [study['uuid']]
        })
        study_not_annotated = rsp.json()

        assert study_annotated == study_not_annotated

    def test_object_create_annotations_applied_rejected(self, study_initial: dict, api_client: TestClient):
        study_initial['annotations_applied'] = True

        rsp = api_client.post('private/studies', json=study_initial)
        assert rsp.status_code == 422, rsp.json()

        # double-check object not created
        rsp = api_client.get(f"studies/{study_initial['uuid']}")
        assert rsp.status_code == 404

    @pytest.mark.parametrize('update', [False, True])
    def test_object_update_annotations_applied_rejected(self, study: dict, api_client: TestClient):
        study["annotations_applied"] = True
        study["version"] += 1

        rsp = api_client.patch('private/studies', json=study)
        assert rsp.status_code == 422, rsp.json()

        # double-check object not updated
        rsp = api_client.get(f"studies/{study['uuid']}")
        assert rsp.status_code == 200
        assert rsp.json()['version'] == study['version']-1

@pytest.mark.asyncio
class TestImageAnnotations(DBTestMixin):
    @pytest.fixture
    def field_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "original_relpath",
            "value": "overwritten",
            "state": "active"
        }

    @pytest.fixture
    def attribute_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "test_attribute",
            "value": "overwritten",
            "state": "active"
        }

    @pytest.fixture
    def img_initial(self, existing_study):
        img = get_template_image(existing_study, add_uuid=True)
        img["attributes"] = {
            "test_attribute": "initial"
        }

        return img

    @pytest.fixture
    def image(self, api_client: TestClient, img_initial: dict, field_annotation: dict, attribute_annotation: dict, update: bool):
        img_initial["annotations"] = [field_annotation, attribute_annotation]

        rsp = api_client.post('private/images', json=[img_initial])
        assert rsp.status_code == 201, rsp.json()

        if update:
            img_initial['version'] += 1
            img_initial["attributes"]["updated_attribute"] = "updated_value"
            rsp = api_client.patch('private/images/single', json=img_initial)
            assert rsp.status_code == 200, rsp.json()

        rsp = api_client.get(f"images/{img_initial['uuid']}")
        assert rsp.status_code == 200

        return rsp.json()
    
    @pytest.mark.parametrize('update', [False, True])
    async def test_annotations_not_applied_when_fetching(self, img_initial: dict, image: dict):
        assert img_initial == image
    
    @pytest.mark.parametrize('update', [False, True])
    async def test_annotations_not_applied_when_persisted(self, db: Repository, image: dict, img_initial: dict, field_annotation: dict, attribute_annotation: dict):
        img_in_db = await db.find_image_by_uuid(image['uuid'])
        img_in_db = img_in_db.model_dump() # just to simplify

        assert img_in_db[field_annotation['key']] == img_in_db[field_annotation['key']]
        assert img_in_db[field_annotation['key']] != field_annotation['value']

        assert img_in_db['attributes'][attribute_annotation['key']] == img_initial['attributes'][attribute_annotation['key']]
        assert img_in_db['attributes'][attribute_annotation['key']] != attribute_annotation['value']

    @pytest.mark.parametrize('update', [False, True])
    def test_annotations_applied_when_explicit(self, image: dict):
        raise Exception("TODO")

@pytest.mark.asyncio
class TestFilerefAnnotations(DBTestMixin):
    @pytest.fixture
    def field_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "name",
            "value": "overwritten",
            "state": "active"
        }

    @pytest.fixture
    def attribute_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "test_attribute",
            "value": "overwritten",
            "state": "active"
        }

    @pytest.fixture
    def fileref_initial(self, existing_study):
        fileref = get_template_file_reference(existing_study, add_uuid=True)
        fileref["attributes"] = {
            "test_attribute": "initial"
        }

        return fileref

    @pytest.fixture
    def fileref(self, api_client: TestClient, fileref_initial: dict, field_annotation: dict, attribute_annotation: dict, update: bool):
        fileref_initial["annotations"] = [field_annotation, attribute_annotation]

        rsp = api_client.post('private/file_references', json=[fileref_initial])
        assert rsp.status_code == 201, rsp.json()

        if update:
            fileref_initial['version'] += 1
            fileref_initial["attributes"]["updated_attribute"] = "updated_value"
            rsp = api_client.patch('private/file_references/single', json=fileref_initial)
            assert rsp.status_code == 200, rsp.json()

        rsp = api_client.get(f"file_references/{fileref_initial['uuid']}")
        assert rsp.status_code == 200

        return rsp.json()
    
    @pytest.mark.parametrize('update', [False, True])
    async def test_annotations_not_applied_when_fetching(self, fileref_initial: dict, fileref: dict):
        assert fileref_initial == fileref
    
    @pytest.mark.parametrize('update', [False, True])
    async def test_annotations_not_applied_when_persisted(self, db: Repository, fileref: dict, fileref_initial: dict, field_annotation: dict, attribute_annotation: dict):
        fileref_in_db = await db.find_fileref_by_uuid(fileref['uuid'])
        fileref_in_db = fileref_in_db.model_dump() # just to simplify

        assert fileref_in_db[field_annotation['key']] == fileref_in_db[field_annotation['key']]
        assert fileref_in_db[field_annotation['key']] != field_annotation['value']

        assert fileref_in_db['attributes'][attribute_annotation['key']] == fileref_initial['attributes'][attribute_annotation['key']]
        assert fileref_in_db['attributes'][attribute_annotation['key']] != attribute_annotation['value']

    @pytest.mark.parametrize('update', [False, True])
    def test_annotations_applied_when_explicit(self, fileref: dict):
        raise Exception("TODO")

@pytest.mark.asyncio
class TestCollectionAnnotation(DBTestMixin):
    @pytest.fixture
    def field_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "title",
            "value": "overwritten",
            "state": "active"
        }

    @pytest.fixture
    def attribute_annotation(self):
        return {
            "author_email": "test@ebi.ac.uk",
            "key": "test_attribute",
            "value": "new_attribute",
            "state": "active"
        }

    @pytest.fixture
    def collection_initial(self):
        collection = get_template_collection(add_uuid=True)
        collection["attributes"] = {
            "test_attribute": "initial"
        }

        return collection

    @pytest.fixture
    def collection(self, api_client: TestClient, collection_initial: dict, field_annotation: dict, attribute_annotation: dict, update: bool):
        collection_initial["annotations"] = [field_annotation, attribute_annotation]

        rsp = api_client.post("private/collections", json=collection_initial)
        assert rsp.status_code == 201, rsp.json()

        if update:
            collection_initial['version'] += 1
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
    def test_annotations_applied_explicit(self, collection: dict, api_client: TestClient, field_annotation: dict, attribute_annotation: dict):
        rsp = api_client.get(f"collections/{collection['uuid']}", params={
            "apply_annotations": True
        })
        assert rsp.status_code == 200

        collection_fetched = rsp.json()
        assert collection_fetched["annotations_applied"] == True
        assert collection_fetched[field_annotation["key"]] == field_annotation["value"]

        assert collection_fetched["attributes"][attribute_annotation["key"]] == attribute_annotation["value"]