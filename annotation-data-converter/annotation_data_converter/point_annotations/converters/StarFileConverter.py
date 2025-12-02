import urllib.request
import tempfile
import starfile
import pandas as pd
from pathlib import Path
from annotation_data_converter.point_annotations.converters.PointAnnotationConverter import (
    PointAnnotationConverter,
)


class StarFileConverter(PointAnnotationConverter):
    
    def load(self):
        if file_path := self.proposal.local_file_path:
            unfiltered_dataframe = StarFileConverter._read_star_file_from_path(
                file_path
            )
        else:
            file_uri_list = self.annotation_data_file_reference.file_path
            if len(file_uri_list) != 1:
                raise NotImplementedError(
                    "Cannot handle cases where starfile annotation data is made up of more than one file."
                )
            unfiltered_dataframe = StarFileConverter._read_star_file_from_url(
                file_uri_list[0]
            )

        if self.proposal.filter_column and self.proposal.filter_value:
            filtered_data = unfiltered_dataframe.loc[
                unfiltered_dataframe[self.proposal.filter_column]
                == self.proposal.filter_value
            ]
            self.point_annotation_data = filtered_data
        else:
            self.point_annotation_data = unfiltered_dataframe

    @staticmethod
    def _read_star_file_from_url(url: str) -> pd.DataFrame:
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
            starfile_data = StarFileConverter._read_star_file_from_path(temp_path)

        return starfile_data

    @staticmethod
    def _read_star_file_from_path(path: Path) -> pd.DataFrame:
        starfile_data = starfile.read(path)
        if not isinstance(starfile_data, pd.DataFrame):
            raise NotImplementedError(
                "Need to convert Dict[str, Union[str, int, float]] from a star file that doesn't have a loop block into a pandas Dataframe"
            )

        return starfile_data