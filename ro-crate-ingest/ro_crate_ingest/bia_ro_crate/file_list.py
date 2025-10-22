from typing import Iterable

import pandas as pd
from bia_shared_datamodels.ro_crate_models import Column
from rdflib import Graph


class FileList:
    ro_crate_id: str | None
    ro_crate_schema: dict[str, Column]
    data: pd.DataFrame

    def __init__(
        self,
        schema: Iterable[Column] | dict[str, Column],
        data: pd.DataFrame,
        ro_crate_id: str | None = None,
        strict: bool = False,
    ) -> None:
        self.ro_crate_id = ro_crate_id

        if isinstance(schema, dict):
            if all(key == column.id for key, column in schema.items()):
                self.ro_crate_schema = schema
            else:
                raise KeyError(
                    "If schema is a dictionary, keys must be the IDs of the column objects"
                )
        else:
            self.ro_crate_schema = {column.id: column for column in schema}

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
        return {column.id: column.propertyUrl for column in self.ro_crate_schema}

    def get_column_names(self) -> dict[str, str]:

        return {column.id: column.columnName for column in self.ro_crate_schema}

    def to_graph(self) -> Graph:
        filelist_column = None
        column_properties = {}

        for column_id, property_id in self.get_column_properties().items():
            if property_id:
                if property_id == "http://bia/fileList":
                    filelist_column = column_id
                else:
                    column_properties[column_id] = property_id

        filelist_graph = Graph()

        for row in self.data:
            fileid = row.get(filelist_column)
            for column_id, property_id in column_properties:
                if value := row.get(column_id):
                    filelist_graph.add((fileid, property_id, value))

        return filelist_graph

    def move_filelist_id_to_data(self) -> None:
        if self.ro_crate_id:
            filelist_id_name = "_filelist_id"
            column_type = "http://www.w3.org/ns/csvw#Column"
            self.data[filelist_id_name] = self.ro_crate_id
            self.ro_crate_schema.append(
                Column.model_validate(
                    {
                        "columnName": filelist_id_name,
                        "@id": filelist_id_name,
                        "@type": column_type,
                    }
                )
            )

    def align_schema_to_data_columns(self):
        sorted_schema_columns = {}
        for column_id in self.data.columns:
            sorted_schema_columns[column_id] = self.ro_crate_schema[column_id]
        self.ro_crate_schema = sorted_schema_columns

    def align_data_columns_to_schema(self):
        self.data = self.data[list(self.ro_crate_schema.keys())]

    def merge(self, other: "FileList", align_schema_with_data: bool = True):
        self.move_filelist_id_to_data()
        other.move_filelist_id_to_data()
        combined = pd.concat([self.data, other.data], ignore_index=True)
        self.data = combined

        self.ro_crate_schema = other.ro_crate_schema | self.ro_crate_schema

        if align_schema_with_data:
            self.align_schema_to_data_columns()
        else:
            self.align_data_columns_to_schema()
