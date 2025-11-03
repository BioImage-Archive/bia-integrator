from typing import Iterable

import pandas as pd
from bia_shared_datamodels.ro_crate_models import Column
from rdflib import Graph


class FileList:
    ro_crate_id: str | None
    ro_crate_schema: dict[str, Column]
    data: pd.DataFrame
    FILE_LIST_ID_COL: str = "_filelist_id"
    PROPERTYLESS_COLUMNS: str = "_propertyless_columns"
    DATASET_COLUMN_ID: str = "_part_of_dataset"

    def __init__(
        self,
        schema: dict[str, Column],
        data: pd.DataFrame,
        ro_crate_id: str | None = None,
        strict: bool = False,
    ) -> None:
        self.ro_crate_id = ro_crate_id

        if all(key == column.id for key, column in schema.items()):
            self.ro_crate_schema = schema
        else:
            raise KeyError(
                "Schema dictionary must have keys that are the IDs of the column objects"
            )

        dataframe_column_names = data.columns
        name_map = {
            column.columnName: column.id for column in self.ro_crate_schema.values()
        }

        if strict:
            if list(name_map.keys()) != list(dataframe_column_names):
                raise ValueError("Schema does not match data columns")

        try:
            column_ids = {
                col_name: name_map[col_name] for col_name in dataframe_column_names
            }
        except KeyError:
            raise ValueError(
                "Schema does not contain columns with names that match data columns."
            )

        self.data = data.rename(columns=column_ids)

        super().__init__()

    def get_column_properties(self) -> dict[str, None | str]:
        return {
            column.id: column.propertyUrl for column in self.ro_crate_schema.values()
        }

    def get_column_names(self) -> dict[str, str]:

        return {
            column.id: column.columnName for column in self.ro_crate_schema.values()
        }

    def add_filelist_id_column(self) -> None:
        if self.ro_crate_id:
            filelist_id_name = self.FILE_LIST_ID_COL
            self.data[filelist_id_name] = self.ro_crate_id
            self.ro_crate_schema[filelist_id_name] = Column.model_validate(
                {
                    "columnName": filelist_id_name,
                    "@id": filelist_id_name,
                    "@type": "http://www.w3.org/ns/csvw#Column",
                }
            )
            self.ro_crate_id = None

    def add_dataset_column(self, file_list_dataset_map: dict[str, str]) -> None:
        if self.FILE_LIST_ID_COL not in self.data.columns:
            self.add_filelist_id_column()

        self.data[self.DATASET_COLUMN_ID] = self.data[self.FILE_LIST_ID_COL].map(
            file_list_dataset_map
        )

        self.ro_crate_schema[self.DATASET_COLUMN_ID] = Column.model_validate(
            {
                "columnName": self.DATASET_COLUMN_ID,
                "@id": self.DATASET_COLUMN_ID,
                "@type": "http://www.w3.org/ns/csvw#Column",
                "propertyUrl": "http://schema.org/isPartOf",
            }
        )

    def align_schema_to_data_columns(self):
        sorted_schema_columns = {}
        for column_id in self.data.columns:
            sorted_schema_columns[column_id] = self.ro_crate_schema[column_id]
        self.ro_crate_schema = sorted_schema_columns

    def align_data_columns_to_schema(self):
        self.data = self.data[list(self.ro_crate_schema.keys())]

    def merge(self, other: "FileList", align_schema_with_data: bool = True):
        self.add_filelist_id_column()
        other.add_filelist_id_column()
        combined = pd.concat([self.data, other.data], ignore_index=True)
        self.data = combined

        self.ro_crate_schema = other.ro_crate_schema | self.ro_crate_schema

        if align_schema_with_data:
            self.align_schema_to_data_columns()
        else:
            self.align_data_columns_to_schema()

    def to_processable_data(self) -> pd.DataFrame:
        semantic_column_map = {}
        non_semantic_column_map = {}
        for column in self.ro_crate_schema.values():
            if column.propertyUrl:
                semantic_column_map[column.id] = column.propertyUrl
            elif column.columnName:
                non_semantic_column_map[column.id] = column.columnName

        def _to_property_cols(
            row: pd.Series,
            semantic_column_map: dict[str, str | None],
            non_semantic_column_map: dict[str, str],
            propertyless_column_name: str,
        ) -> pd.Series:
            non_prop_rows = {}
            output_row = {}
            for col_id, value in row.items():
                if col_id in semantic_column_map:
                    propertyUrl = semantic_column_map[col_id]
                    if propertyUrl in row:
                        existing_data = row.get(propertyUrl) or []
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                        value = value or []
                        if not isinstance(value, list):
                            value = [value]
                        output_row[propertyUrl] = existing_data + value
                    else:
                        output_row[propertyUrl] = value
                elif col_id in non_semantic_column_map:
                    non_prop_rows[non_semantic_column_map[col_id]] = value

            output_row[propertyless_column_name] = non_prop_rows
            return pd.Series(output_row)

        result_data = self.data.apply(
            _to_property_cols,
            args=(
                semantic_column_map,
                non_semantic_column_map,
                self.PROPERTYLESS_COLUMNS,
            ),
            axis=1,
        )

        return result_data
