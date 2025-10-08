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


class FileListValidator(Validator):
    ro_crate_root: Path
    file_list: FileList
    table_schemas: TableSchema
    columns: dict[str, Column]
    ontology: rdflib.Graph

    def __init__(
        self,
        ro_crate_root: Path,
        file_list: FileList,
        schema: TableSchema,
        columns: dict[str, Column],
        ontology: rdflib.Graph,
    ):
        self.ro_crate_root = ro_crate_root
        self.file_list = file_list
        self.schema = schema
        self.columns = columns
        self.bia_ontology = ontology
        super().__init__()

    def validate(self) -> ValidationResult:
        file_list_path = self.ro_crate_root / self.file_list.id
        file_list_contents = pd.read_csv(file_list_path, delimiter="\t")

        file_path_column, object_columns = self._get_columns_to_check()

        file_list_contents.apply(
            self._validate_files_exist,
            args=(file_path_column, self),
            axis=1,
        )

        file_list_contents.apply(
            self._validate_object_reference,
            args=(object_columns, self),
            axis=1,
        )

        return ValidationResult(
            issues=self.issues,
        )

    @staticmethod
    def _validate_files_exist(
        row: pd.Series,
        file_path_column,
        file_list_validator: "FileListValidator",
    ):

        relative_file_path = str(row[file_path_column])

        file_path = file_list_validator.ro_crate_root / relative_file_path

        if not os.path.exists(file_path):
            file_list_validator.issues.append(
                ValidationError(
                    severity=Severity.ERROR,
                    location_description=f"In file list: {file_list_validator.file_list.id}.",
                    message=f"File reference: {relative_file_path} does not exist.",
                )
            )
        
    
    @staticmethod
    def _validate_object_reference(
        row: pd.Series,
        object_columns,
        file_list_validator: "FileListValidator",
    ):

        for object_column, expected_type in object_columns:
            reference = row[object_column]

    def _get_columns_to_check(self) -> tuple[str, dict]:
        properties_and_ranges = self._get_properties_and_types_to_check()

        object_columns = {}
        file_path_column = None

        for column_name, column in self.columns.items():
            if column.propertyUrl in properties_and_ranges:
                object_columns[column_name] = properties_and_ranges[column.propertyUrl]
            elif column.propertyUrl == "http://bia/filePath":
                file_path_column = column_name

        return file_path_column, object_columns

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
