import os
import pytest
from bia_embed.cli import api_client
from bia_integrator_api.models.study import Study
from bia_integrator_api.models.contributor import Contributor
from bia_integrator_api.models.affiliation import Affiliation
from uuid import uuid4
from datetime import datetime

def pytest_configure(config: pytest.Config):
    os.environ.setdefault("API_BASE_URL", "http://localhost:8080")
    os.environ.setdefault("API_USERNAME", "test@example.com")
    os.environ.setdefault("API_PASSWORD", "test")

@pytest.fixture(scope="session")
def existing_study():
    study_uuid = str(uuid4())
    study = Study(
        uuid = study_uuid,
        title = study_uuid,
        description = study_uuid,
        object_creator="submitter",
        version=0,
        accession_id=study_uuid,
        licence="https://creativecommons.org/publicdomain/zero/1.0/",
        author=[Contributor(display_name="Test Author", affiliation=[Affiliation(display_name="Test Affiliation")])],
        release_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
    )
    return study