import pandas as pd
from bia_shared_datamodels.ro_crate_models import Column


class FileList:
    """
    A file list is a columnar metadata container describing other files in an ro-crate.
    It is made up of the data about the other files (data), and a schema (a dictionary of Column objects, keyed by id).
    Its schema is usually described in the ro-crate-metadata.json, using a csvw:TableSchema object to hold a set of csvw:Column objects.
    """

    ro_crate_id: str | None
    schema: dict[str, Column]
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

        self._validate_schema_dict(schema)
        schema_name_map = {
            column.columnName: column.id for column in self.schema.values()
        }
        self._validate_column_defitions(schema_name_map, data.columns, strict)
        column_id_map = {
            col_name: schema_name_map[col_name] for col_name in data.columns
        }
        self.data = data.rename(columns=column_id_map)

        super().__init__()

    def _validate_schema_dict(self, schema: dict[str, Column]):
        if all(key == column.id for key, column in schema.items()):
            self.schema = schema
        else:
            raise KeyError(
                "Schema dictionary must have keys that are the IDs of the column objects"
            )

    def _validate_column_defitions(
        self, schema_name_map: dict[str, str], data_columns: pd.Index, strict: bool
    ):
        if strict:
            if list(schema_name_map.keys()) != list(data_columns):
                raise ValueError("Schema does not match data columns")

        for column in data_columns:
            if column not in schema_name_map:
                raise ValueError(
                    "Schema does not contain columns with names that match data columns."
                )

    def get_column_properties(self) -> dict[str, None | str]:
        return {column.id: column.propertyUrl for column in self.schema.values()}

    def get_column_names(self) -> dict[str, str]:
        return {column.id: column.columnName for column in self.schema.values()}

    def add_filelist_id_column(self) -> None:
        if self.ro_crate_id:
            filelist_id_name = self.FILE_LIST_ID_COL
            self.data[filelist_id_name] = self.ro_crate_id
            self.schema[filelist_id_name] = Column.model_validate(
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

        self.schema[self.DATASET_COLUMN_ID] = Column.model_validate(
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
            sorted_schema_columns[column_id] = self.schema[column_id]
        self.schema = sorted_schema_columns

    def align_data_columns_to_schema(self):
        self.data = self.data[list(self.schema.keys())]

    def to_processable_data(self) -> pd.DataFrame:
        semantic_column_map = {}
        non_semantic_column_map = {}
        for column in self.schema.values():
            if column.propertyUrl:
                semantic_column_map[column.id] = column.propertyUrl
            else:
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
                        existing_data = self._ensure_list(row.get(propertyUrl, []))
                        value = self._ensure_list(value or [])
                        output_row[propertyUrl] = existing_data + value
                    else:
                        output_row[propertyUrl] = value
                else:
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

    @staticmethod
    def _ensure_list(possible_list):
        return possible_list if isinstance(possible_list, list) else [possible_list]
