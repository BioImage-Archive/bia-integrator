from .mock_objects import mock_image

def test_bia_image_with_one_file_reference():
    assert mock_image.get_image_with_one_file_reference()