import urllib.request
import tempfile
import logging
import starfile
import pandas as pd

logger = logging.getLogger("__main__." + __name__)

from pathlib import Path


def read_point_data_to_dataframe(url: str, file_type: str) -> pd.DataFrame:

    match file_type:
        case "star":
            return read_star_file_from_url(url)
        case _:
            NotImplementedError(f"Cannot handle {file_type}")


def read_star_file_from_url(url: str) -> pd.DataFrame:
    """
    The starfile library requires a path to read a file from disk.
    Therefore, creating a temporary directory, downloading the file to that location, and reading it.
    The temporary directory (and all its contents) will be deleted on exit of the 'with' block.
    """
    with urllib.request.urlopen(url) as response:
        file_data = response.read()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "temp.star"
        temp_path.write_bytes(file_data)
        starfile_data = starfile.read(temp_path)

    if not isinstance(starfile_data, pd.DataFrame):
        raise NotImplementedError(
            "Need to convert Dict[str, Union[str, int, float]] from a star file that doesn't have a loop block into a pandas Dataframe"
        )

    return starfile_data
