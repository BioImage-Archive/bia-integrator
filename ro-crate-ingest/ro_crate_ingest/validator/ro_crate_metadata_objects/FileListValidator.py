from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from pathlib import Path
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels.ro_crate_models import Column, TableSchema, FileList


class FileListValidator(Validator):
    ro_crate_root: Path
    ro_crate_object_lookup: dict[str, ROCrateModel]
    file_lists: dict[str, FileList]
    table_schemas: dict[str, TableSchema]
    columns: dict[str, Column]

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

        super().__init__()

    def validate(self) -> ValidationResult:
        file_path_column_ids = self._check_ro_crate_contains_file_path_colum()

        if len(file_path_column_ids) > 0:
            self._check_schemas_contain_required_columns(file_path_column_ids)

        for file_list_id, file_list in self.file_lists.items():
            pass

        return ValidationResult(
            issues=self.issues,
        )

    def _validate_referenced_paths_exist(self):
        pass

    def _validate_file_lists_exist(self):
        pass

    def _validate_columns_match_schema(self):
        pass

    def _validate_referenced_ro_crate_objects_exist(self):
        pass

    def _check_schemas_contain_required_columns(self, file_path_column_ids: list[str]):
        roc_object_location_template = (
            "At ro-crate TableSchema object with @id: {roc_id}"
        )

        for schema_id, schema in self.table_schemas.items():
            file_path_column = []
            for column_ref in schema.column:
                column_id = column_ref.id
                if column_id in file_path_column_ids:
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
        return file_path_column_ids
