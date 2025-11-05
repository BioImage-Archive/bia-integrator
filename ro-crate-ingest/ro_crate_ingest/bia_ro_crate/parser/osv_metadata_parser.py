import os
import re
from pathlib import Path

import pandas as pd
from bia_shared_datamodels.ro_crate_models import (
    Column,
)
from bia_shared_datamodels.ro_crate_models import FileList as FileListMetadata
from bia_shared_datamodels.ro_crate_models import (
    TableSchema,
)

from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.bia_ro_crate.parser.metadata_parser import MetadataParser


class OSVMetadataParser(MetadataParser):
    """
    Generic parser for operator separated value (e.g. csv, tsv) file lists:
    i.e. structured files who's schema is described in the ro-crate metadata.json
    """

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

    bia_rocrate_metadata: BIAROCrateMetadata
    ro_crate_root: Path

    def __init__(
        self,
        ro_crate_metadata: BIAROCrateMetadata,
        ro_crate_root: Path,
        *,
        context: dict | None = None,
    ) -> None:

        self.ro_crate_root = ro_crate_root
        self.bia_rocrate_metadata = ro_crate_metadata

        multivalued_properties_key = "multivalued_properties"
        if context and multivalued_properties_key in context:
            if not isinstance(context[multivalued_properties_key], list):
                raise TypeError(
                    f"{multivalued_properties_key} in context should be a list (of string or URIRefs of the properties)"
                )
            self.multivalued_properties = [
                str(list_property)
                for list_property in context[multivalued_properties_key]
            ]
        else:
            self.multivalued_properties = self.DEFAULT_LIST_PROPERTIES

        super().__init__(context=context)

    def _get_full_path(self, path) -> Path:
        full_file_path = self.ro_crate_root / path

        if not os.path.exists(full_file_path) or not os.path.isfile(full_file_path):
            raise ValueError(f"{full_file_path} does not exist or is not a file.")

        return full_file_path

    def _get_schema(self, file_list_id) -> dict[str, Column]:

        file_list: FileListMetadata = self.bia_rocrate_metadata.get_object(file_list_id)

        if not file_list:
            raise KeyError(f"{file_list_id} not found in ro-crate")

        schema_object: TableSchema = self.bia_rocrate_metadata.get_object(
            file_list.tableSchema.id
        )

        columns: dict[str, Column] = {
            column_ref.id: self.bia_rocrate_metadata.get_object(column_ref.id)
            for column_ref in schema_object.column
        }

        return columns

    def _expand_list_columns(
        self, data: pd.DataFrame, columns: dict[str, Column]
    ) -> None:
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

        for column in columns.values():
            if column.propertyUrl in self.multivalued_properties:
                data[column.columnName] = data[column.columnName].apply(
                    _expand_array_cells,
                )
