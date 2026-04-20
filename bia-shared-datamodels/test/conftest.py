from pathlib import Path

import pytest

@pytest.fixture()
def path_to_example_ro_crate(request: pytest.FixtureRequest) -> Path:
    return (
        Path(__file__).parents[1]
        / "src"
        / "bia_shared_datamodels"
        / "mock_ro_crate"
        / request.param
    )
