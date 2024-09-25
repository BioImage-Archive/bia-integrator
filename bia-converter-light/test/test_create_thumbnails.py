from pathlib import Path
from bia_converter_light.rendering import generate_padded_thumbnail_from_ngff_uri


def test_generate_padded_thumbnail_from_ngff_uri():
    """Test function runs without errors. NOT that correct values produced"""

    local_path_to_zarr = (
        Path(__file__).parent
        / "data"
        / "test_image_representations"
        / "study_component1"
        / "im06.ome.zarr"
    )
    thumbnail = generate_padded_thumbnail_from_ngff_uri(local_path_to_zarr)
    assert thumbnail.size == (256, 256)
