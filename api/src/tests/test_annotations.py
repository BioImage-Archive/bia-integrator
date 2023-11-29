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
    def test_annotations_applied_when_explicit(self, study: dict, api_client: TestClient, study_initial: dict, field_annotation: dict, attribute_annotation: dict):
        rsp = api_client.get(f"studies/{study_initial['uuid']}?apply_annotations=true")
        assert rsp.status_code == 200

        study_with_annotations = rsp.json()
        assert study_with_annotations[field_annotation["key"]] == field_annotation["value"]
        assert study_with_annotations["attributes"][attribute_annotation["key"]] == attribute_annotation["value"]
    
    @pytest.mark.parametrize('update', [False, True])
    def test_annotations_not_applied_when_explicit(self, study: dict, api_client: TestClient, study_initial: dict):
        rsp = api_client.get(f"studies/{study_initial['uuid']}?apply_annotations=false")
        assert rsp.status_code == 200

        study_without_annotations = rsp.json()
        assert study_without_annotations == study
        assert study_without_annotations == study_initial
    
    def test_search_annotations_applied_when_explicit(self):
        raise Exception("TODO - same for everything else")

    def test_accession_to_objectinfo_no_apply_annotations(self):
        raise Exception("TODO - This should be deprecated anyway. Also, no need to \"annotate\" a barebones object.")

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
