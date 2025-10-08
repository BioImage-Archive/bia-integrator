import os
from pathlib import Path

import pandas as pd
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels.ro_crate_models import Column, FileList, TableSchema

from ro_crate_ingest.validator.validator import (
    Severity,
    ValidationError,
    ValidationResult,
    Validator,
)


class FileListSchemaValidator(Validator):
    ro_crate_root: Path
    ro_crate_object_lookup: dict[str, ROCrateModel]
    file_lists: dict[str, FileList]
    table_schemas: dict[str, TableSchema]
    columns: dict[str, Column]
    file_path_column_ids: list[str]

    def __init__(self, ro_crate_objects: dict[str, ROCrateModel], ro_crate_root: Path):
        self.ro_crate_root = ro_crate_root
        self.ro_crate_object_lookup = ro_crate_objects

        for object_id, ro_crate_object in ro_crate_objects.items():
            if isinstance(ro_crate_object, FileList):
                self.file_lists[object_id] = ro_crate_object
            elif isinstance(ro_crate_object, TableSchema):
                self.table_schemas[object_id] = ro_crate_object
            elif isinstance(ro_crate_object, Column):
                self.columns[object_id] = ro_crate_object

        self.file_path_column_ids = []

        super().__init__()

    def validate(self) -> ValidationResult:

        validation_order = [
            self._check_ro_crate_contains_file_path_colum,
            self._check_schemas_contain_required_columns,
            self._validate_file_list_tsvs_exist,
            self._validate_tsv_columns_match_schema,
        ]

        for validation_function in validation_order:
            validation_function()
            if len(self.issues) > 0:
                return ValidationResult(
                    issues=self.issues,
                )

        return ValidationResult(
            issues=self.issues,
        )

    def _validate_referenced_paths_exist(self, file_path_row):
        if not os.path.exists(self.ro_crate_root / file_path_row):
            self.issues.append(
                ValidationError(
                    severity=Severity.ERROR,
                    message=f"{file_path_row}",
                )
            )

    def _validate_file_list_tsvs_exist(self):
        for file_list_id in self.file_lists:
            if not os.path.exists(self.ro_crate_root / file_list_id):
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        message=f"No file list exists at {file_list_id}",
                    )
                )
                continue
            if not file_list_id.endswith(".tsv"):
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        message=f"{file_list_id} is not a .tsv file.",
                    )
                )
                continue

    def _validate_tsv_columns_match_schema(self):

        for file_list_id, file_list in self.file_lists.items():
            schema = self.table_schemas[file_list.tableSchema.id]
            column_order = [
                self.columns[column.id].columnName for column in schema.column
            ]

            filelist_dataframe = pd.read_csv(
                self.ro_crate_root / file_list_id, sep="\t"
            )

            for column_name in filelist_dataframe.columns:
                if column_name not in column_order:
                    self.issues.append(
                        ValidationError(
                            severity=Severity.ERROR,
                            message=f"Column {column_name} expected in {file_list_id} but not found.",
                        )
                    )

            if filelist_dataframe.columns.to_list() != column_order:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        message=f"Expected order of columns is {column_order} but found {filelist_dataframe.columns}.",
                    )
                )

    def _check_schemas_contain_required_columns(self):
        roc_object_location_template = (
            "At ro-crate TableSchema object with @id: {roc_id}"
        )

        for schema_id, schema in self.table_schemas.items():
            file_path_column = []
            for column_ref in schema.column:
                column_id = column_ref.id
                if column_id in self.file_path_column_ids:
                    file_path_column.append(column_id)

            if match_count := len(file_path_column) != 1:
                error_message = (
                    f"Missing column with property http://bia/filePath."
                    if match_count == 0
                    else f"Multiple columns with property http://bia/filePath present. There should only be 1"
                )
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            schema_id
                        ),
                        message=error_message,
                    )
                )

    def _check_ro_crate_contains_file_path_colum(self):
        file_path_column_ids = []
        for column_id, column in self.columns.items():
            if column.propertyUrl == "http://bia/filePath":
                file_path_column_ids.append(column_id)

        if len(file_path_column_ids) == 0:
            self.issues.append(
                ValidationError(
                    severity=Severity.ERROR,
                    message=f"No file list column has been assigned csvw:propertyUrl http://bia/filePath in the ro-crate-metadata.json.",
                )
            )
        self.file_path_column_ids = file_path_column_ids
