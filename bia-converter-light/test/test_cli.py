import pytest
from typer.testing import CliRunner

from bia_converter_light.cli import app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


def test_cli_convert_image(runner):
    # image_representation = (
    #    mock_image_representation.get_image_representation_of_interactive_display()
    # )

    result = runner.invoke(
        app,
        [
            "convert-image",
            # "S-BIADTEST",
            # str(image_representation.uuid),
            "S-BIAD1005",
            "98cd36b1-cd9f-4bd5-83a0-ad89f21808b1",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0


def test_cli_update_example_image_uri_for_dataset(runner):
    result = runner.invoke(
        app,
        [
            "update-example-image-uri-for-dataset",
            # "--help"
        ],
    )

    assert result.exit_code == 0
