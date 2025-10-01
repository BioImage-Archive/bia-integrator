import pandas as pd
from annotation_data_converter.point_annotations.converters.PointAnnotationConverter import (
    PointAnnotationConverter,
)
from pathlib import Path
from urllib.request import urlopen


class CSVConverter(PointAnnotationConverter):

    def load(self):
        if file_path := self.proposal.local_file_path:
            self.point_annotation_data = CSVConverter._read_csv_from_path(
                file_path
            )
        else:
            file_uri_list = self.image_representation.file_uri
            if len(file_uri_list) != 1:
                raise NotImplementedError(
                    "Cannot handle cases where starfile annotation data is made up of more than one image representation."
                )
            self.point_annotation_data = CSVConverter._read_csv_from_url(
                file_uri_list[0]
            )

    @staticmethod
    def _read_csv_from_path(file_path: Path):
        return pd.read_csv(file_path)

    @staticmethod
    def _read_csv_from_url(url):
        with urlopen(url) as response:
            return pd.read_csv(response)
