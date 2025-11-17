from pathlib import Path

import bia_integrator_api.models as api_models
import pytest
from bia_integrator_api.api import PrivateApi
from typer.testing import CliRunner

from curation.cli import curate

runner = CliRunner()


@pytest.fixture()
def attribute_yaml_file_path() -> Path:
    return Path(__file__).parent / "directives" / "test_update_attribute_directive.yaml"


def test_update_attribute(
    any_api_object: api_models.Study,
    private_client: PrivateApi,
    attribute_yaml_file_path: Path,
):
    attribute_count = len(any_api_object.additional_metadata)
    command = [
        # "apply-directive", - will need to specift the command when there are two
        str(attribute_yaml_file_path),
    ]
    result = runner.invoke(curate, command)
    assert result.exit_code == 0

    # Check that running update_attribute directives adds new attributes
    updated_study = private_client.get_study(any_api_object.uuid)
    updated_study_attribute_count = len(updated_study.additional_metadata)
    assert updated_study_attribute_count == attribute_count + 2

    # Checl that re-running update_attribute commands don't result in more attributes
    result = runner.invoke(curate, command)
    assert result.exit_code == 0
    re_updated_study = private_client.get_study(any_api_object.uuid)
    assert updated_study_attribute_count == len(re_updated_study.additional_metadata)
