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
import rdflib
from enum import Enum


class RemoteFileMode(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class FileListValidator(Validator):
    ro_crate_root: Path
    ro_crate_object_lookup: dict[str, ROCrateModel]
    file_list_objects: dict[str, FileList]
    file_lists_map: dict[str, pd.DataFrame]
    table_schemas: dict[str, TableSchema]
    columns: dict[str, Column]
    file_path_column_ids: list[str]
    ontology: rdflib.Graph
    object_reference_columns: dict[str, str]
    remote_file_mode: RemoteFileMode

    def __init__(
        self,
        ro_crate_objects: dict[str, ROCrateModel],
        ro_crate_root: Path,
        ontology: rdflib.Graph,
        remote_file_mode: RemoteFileMode = RemoteFileMode.LOCAL,
    ):
        self.ro_crate_root = ro_crate_root
        self.ro_crate_object_lookup = ro_crate_objects

        self.columns = {}
        self.table_schemas = {}
        self.file_list_objects = {}

        for object_id, ro_crate_object in ro_crate_objects.items():
            if isinstance(ro_crate_object, FileList):
                self.file_list_objects[object_id] = ro_crate_object
            elif isinstance(ro_crate_object, TableSchema):
                self.table_schemas[object_id] = ro_crate_object
            elif isinstance(ro_crate_object, Column):
                self.columns[object_id] = ro_crate_object

        self.file_path_column_ids = []
        self.file_lists_map = {}
        self.object_reference_columns = {}
        self.ontology = ontology
        self.remote_file_mode = remote_file_mode

        super().__init__()

    def validate(self) -> ValidationResult:

        if self.file_list_objects == {}:
            return ValidationResult(issues=self.issues)

        validation_order = [
            self._check_ro_crate_contains_required_columns,
            self._check_schemas_use_required_columns,
            self._validate_file_list_tsvs_exist,
            self._validate_tsv_columns_match_schema,
        ]

        for validation_function in validation_order:
            validation_function()
            if len(self.issues) > 0:
                return ValidationResult(
                    issues=self.issues,
                )

        self._get_reference_column_to_check()

        for file_list_id, file_list in self.file_lists_map.items():
            self._validate_file_list_contents(file_list_id, file_list)

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
        for file_list_id in self.file_list_objects:
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

        for file_list_id, file_list in self.file_list_objects.items():
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
                        message=f"Expected order of columns is {column_order} but found {filelist_dataframe.columns.to_list()}.",
                    )
                )

            self.file_lists_map[file_list_id] = filelist_dataframe

    def _check_schemas_use_required_columns(self):
        roc_object_location_template = (
            "At ro-crate TableSchema object with @id: {schema_id}"
        )

        for schema_id, schema in self.table_schemas.items():
            file_path_column = []
            for column_ref in schema.column:
                column_id = column_ref.id
                if column_id in self.file_path_column_ids:
                    file_path_column.append(column_id)

            if (match_count := len(file_path_column)) != 1:
                error_message = (
                    f"Missing column with property http://bia/filePath."
                    if match_count == 0
                    else f"Multiple columns with property http://bia/filePath present. There should only be 1"
                )
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            schema_id=schema_id
                        ),
                        message=error_message,
                    )
                )

    def _check_ro_crate_contains_required_columns(self):
        error_message_template = "No column has been assigned csvw:propertyUrl {property_url} in the ro-crate-metadata.json."

        file_path_property = "http://bia/filePath"
        file_path_column_ids = self._get_column_ids_by_property_url(file_path_property)
        if len(file_path_column_ids) == 0:
            self.issues.append(
                ValidationError(
                    severity=Severity.ERROR,
                    message=error_message_template.format(
                        property_url=file_path_property
                    ),
                )
            )
        else:
            self.file_path_column_ids = file_path_column_ids

        if self.remote_file_mode == RemoteFileMode.REMOTE:
            size_in_bytes_property = "https://bia/sizeInBytes"
            size_in_bytes = self._get_column_ids_by_property_url(size_in_bytes_property)
            if len(size_in_bytes) == 0:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        message=error_message_template.format(
                            property_url=size_in_bytes_property
                        ),
                    )
                )

    def _get_column_ids_by_property_url(self, property_url: str) -> list[str]:
        column_ids = []
        for column_id, column in self.columns.items():
            if column.propertyUrl == property_url:
                column_ids.append(column_id)
        return column_ids

    def _get_reference_column_to_check(self):
        properties_and_ranges = self._get_properties_and_types_to_check()

        object_columns = {}
        for column_name, column in self.columns.items():
            if column.propertyUrl:
                property_uri = rdflib.URIRef(column.propertyUrl)
                if property_uri in properties_and_ranges:
                    object_columns[column_name] = properties_and_ranges[property_uri]

        self.object_reference_columns = object_columns

    def _get_properties_and_types_to_check(self) -> dict:
        resolved_query = self.ontology.query(
            """
                prefix obo: <http://purl.obolibrary.org/obo/>
                prefix bia: <http://bia/>
                SELECT ?objprop ?range
                {
                    ?objprop rdf:type owl:ObjectProperty .
                    ?objprop rdfs:domain ?domain
                    FILTER (?domain IN ( obo:IAO_0000030, bia:FileReference))
                    ?objprop rdfs:range ?range
                }
            """
        )
        return {x.objprop: x.range for x in resolved_query}

    def _validate_file_list_contents(self, file_list_id: str, file_list: pd.DataFrame):
        for index, row in file_list.iterrows():
            self._validate_object_references(row, file_list_id, str(index))
            if self.remote_file_mode == RemoteFileMode.LOCAL:
                self._validate_file_reference_exists(row, file_list_id, str(index))

    def _validate_object_references(
        self, row: pd.Series, file_list_id: str, index: str
    ):
        tsv_error_location = "In file list: {file_list_id}, at row index: {index}"

        for object_column_id, expected_type in self.object_reference_columns.items():
            object_column_name = self.columns[object_column_id].columnName
            if object_column_name in row:
                reference = str(row[object_column_name])

                if reference not in self.ro_crate_object_lookup:
                    self.issues.append(
                        ValidationError(
                            severity=Severity.ERROR,
                            location_description=tsv_error_location.format(
                                file_list_id=file_list_id, index=index
                            ),
                            message=f"RO-Crate object: {reference} does not exist in ro-crate-metadata.json.",
                        )
                    )
                else:
                    ro_crate_object_type: type[ROCrateModel] = (
                        self.ro_crate_object_lookup[reference].__class__
                    )

                    type_uri = ro_crate_object_type.model_config["model_type"]

                    if expected_type != rdflib.URIRef(type_uri):
                        self.issues.append(
                            ValidationError(
                                severity=Severity.ERROR,
                                location_description=tsv_error_location.format(
                                    file_list_id=file_list_id, index=index
                                ),
                                message=f"RO-Crate object: {reference} is of type {type_uri}, and not expected type: {expected_type}.",
                            )
                        )

    def _validate_file_reference_exists(
        self, row: pd.Series, file_list_id: str, index: str
    ):
        tsv_error_location = "In file list: {file_list_id}, at row index: {index}"

        file_path_column_names = [
            self.columns[column_id].columnName
            for column_id in self.file_path_column_ids
        ]
        file_path_column = (set(file_path_column_names) & set(row.keys())).pop()

        relative_file_path = str(row[file_path_column])

        file_path = self.ro_crate_root / relative_file_path

        if not os.path.exists(file_path):
            self.issues.append(
                ValidationError(
                    severity=Severity.ERROR,
                    location_description=tsv_error_location.format(
                        file_list_id=file_list_id, index=index
                    ),
                    message=f"File reference: {relative_file_path} does not exist.",
                )
            )
