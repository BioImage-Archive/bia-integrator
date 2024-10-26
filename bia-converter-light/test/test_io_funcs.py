from pathlib import Path
import filecmp

from bia_converter_light.io import unzip_fileref_and_get_fpath
from bia_converter_light import utils
from bia_shared_datamodels.mock_objects import get_image_representation_dict
from bia_shared_datamodels.bia_data_model import ImageRepresentation


def compare_directories_recursively(d1: str, d2: str) -> bool:
    comparison = filecmp.dircmp(d1, d2)
    if (
        comparison.left_only
        or comparison.right_only
        or comparison.diff_files
        or comparison.funny_files
    ):
        return False

    for subdir in comparison.common_dirs:
        new_dir1 = str(Path(d1, subdir))
        new_dir2 = str(Path(d2, subdir))
        if not compare_directories_recursively(new_dir1, new_dir2):
            return False

    return True


# Set environment variable for cache directory
def test_unzip_fileref_and_get_fpath(tmp_path, monkeypatch):
    temp_dir = tmp_path
    monkeypatch.setattr(utils.settings, "cache_root_dirpath", temp_dir)
    im_rep_dict = get_image_representation_dict()
    im_rep = ImageRepresentation.model_validate(im_rep_dict)
    im_rep.image_format = ".zarr"

    zarr_path = str(
        Path(__file__).parent
        / "data"
        / "test_image_representations"
        / "study_component1"
        / "im06.ome.zarr"
    )
    input_fpath = Path(f"{zarr_path}.zip")
    unzipped_zarr_path = unzip_fileref_and_get_fpath(im_rep, input_fpath)

    assert compare_directories_recursively(zarr_path, str(unzipped_zarr_path))
