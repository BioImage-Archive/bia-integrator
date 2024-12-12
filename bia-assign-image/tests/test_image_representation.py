"""Test ImageRepresentation creation"""

import pytest
from bia_test_data.mock_objects import (
    mock_file_reference,
    mock_image_representation,
    mock_image,
)
from bia_test_data.mock_objects.mock_object_constants import accession_id
from bia_assign_image import image_representation


@pytest.mark.parametrize(
    ("image_representation_use_type", "mock_creation_function"),
    (
        (
            "uploaded_by_submitter",
            mock_image_representation.get_image_representation_of_uploaded_by_submitter,
        ),
        (
            "thumbnail",
            mock_image_representation.get_image_representation_of_thumbnail,
        ),
        (
            "static_display",
            mock_image_representation.get_image_representation_of_static_display,
        ),
        (
            "interactive_display",
            mock_image_representation.get_image_representation_of_interactive_display,
        ),
    ),
)
def test_create_representation_of_single_image(
    image_representation_use_type,
    mock_creation_function,
):
    expected = mock_creation_function()

    file_references = mock_file_reference.get_file_reference()
    created = image_representation.get_image_representation(
        accession_id=accession_id,
        file_references=file_references[:1],
        image=mock_image.get_image_with_one_file_reference(),
        use_type=image_representation_use_type,
    )

    assert created == expected
