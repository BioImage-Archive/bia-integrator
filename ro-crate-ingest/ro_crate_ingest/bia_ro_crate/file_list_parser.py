import pathlib
import re

import pandas as pd
from bia_shared_datamodels.ro_crate_models import (
    Column,
)
from bia_shared_datamodels.ro_crate_models import FileList as FileListMetadata
from bia_shared_datamodels.ro_crate_models import (
    TableSchema,
)

from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.bia_ro_crate.file_list import FileList

DEFAULT_LIST_PROPERTIES = [
    "http://bia/associatedBiologicalEntity",
    "http://bia/associatedImagingPreparationProtocol",
    "http://bia/associatedImageAcquisitionProtocol",
    "http://bia/associatedAnnotationMethod",
    "http://bia/associatedProtocol",
    "http://bia/associatedSourceImage",
    "http://bia/sourceImagePath",
    "http://bia/sourceImageName",
]


class FileListParser:

    ro_crate_root: pathlib.Path
    bia_rocrate_metadata: BIAROCrateMetadata
    list_properties: list[str]

    def __init__(
        self,
        ro_crate_root: pathlib.Path,
        bia_rocrate_metadata: BIAROCrateMetadata,
        list_properties: list[str] | None = None,
    ) -> None:
        self.ro_crate_root = ro_crate_root
        self.bia_rocrate_metadata = bia_rocrate_metadata
        self.list_properties = list_properties or DEFAULT_LIST_PROPERTIES

    def parse(self, file_list_id: pathlib.Path) -> FileList:

        file_list: FileListMetadata = self.bia_rocrate_metadata.get_object(file_list_id)

        if not file_list:
            raise KeyError(f"{file_list_id} not found in ro-crate")

        schema_object: TableSchema = self.bia_rocrate_metadata.get_object(
            file_list.tableSchema.id
        )

        columns: list[Column] = [
            self.bia_rocrate_metadata.get_object(column_ref.id)
            for column_ref in schema_object.column
        ]

        data = pd.read_csv(self.ro_crate_root / file_list_id, delimiter="\t")

        split_re = re.compile(r"\s*,\s*")

        def _expand_array_cells(value):
            if not isinstance(value, str) or not value.strip():
                return []
            value = value.strip().strip("[] ")
            parts = split_re.split(value)
            clean_list_value = [
                reference.strip().strip("\"'")
                for reference in parts
                if reference.strip()
            ]
            return clean_list_value

        for column in columns:
            if column.propertyUrl in self.list_properties:
                data[column.columnName] = data[column.columnName].apply(
                    _expand_array_cells,
                )

        return FileList(ro_crate_id=str(file_list_id), schema=columns, data=data)
