from collections import defaultdict
from pathlib import Path
from typing import Iterable

import rdflib

from ro_crate_ingest.bia_ro_crate.parser.jsonld_metadata_parser import (
    JSONLDMetadataParser,
)
from ro_crate_ingest.validator.validator import (
    Severity,
    ValidationError,
    ValidationResult,
    Validator,
)


class FileListDefinitionValidator(Validator):
    """
    Use to validate that if an ro-crate-metadata.json document contains filelist defintions,
    the schema of the filelists (also defined in the ro-crate-metadata.json) contains columns
    which are annotatied with the required properties.

    Note this does NOT validate anything to do with the contents of a file list itself,
    only the graph of information described in the ro-crate-metadata.json.
    """

    ro_crate_metadata_graph: rdflib.Graph
    required_properties: set[str]
    file_path_property: rdflib.URIRef = rdflib.URIRef("http://bia/filePath")

    # return schemas in use by filelists, and all propertyUrls of their columns (if any)
    SCHEMA_COLUMN_PROPERTY_QUERY: str = """
        prefix bia: <http://bia/>
        prefix csvw: <http://www.w3.org/ns/csvw#>
        SELECT ?schema ?column ?propertyUrl
        {
            ?schema rdf:type csvw:Schema .
            FILTER EXISTS { 
                ?fileList csvw:tableSchema ?schema .
                ?fileList rdf:type bia:FileList . 
            }
            OPTIONAL {
                ?schema csvw:column ?column .
                ?column csvw:propertyUrl ?propertyUrl .
            }
        }
    """

    # return all columns and their propertyUrls
    COLUMN_PROPERTY_URLS_QUERY: str = """
        prefix bia: <http://bia/>
        prefix csvw: <http://www.w3.org/ns/csvw#>
        SELECT ?column ?propertyUrl
        {
            ?column rdf:type csvw:Column .
            ?column csvw:propertyUrl ?propertyUrl .
        }
    """

    # return all filelists and their schemas (if any)
    FILE_LIST_OBJECTS_QUERY: str = """
        prefix bia: <http://bia/>
        prefix csvw: <http://www.w3.org/ns/csvw#>
        SELECT ?fileList ?schema
        {
            ?fileList rdf:type bia:FileList .
            OPTIONAL { 
                ?fileList csvw:tableSchema ?schema .
            }
        }
    """

    def __init__(
        self,
        ro_crate_metadata_path: Path,
        additional_required_column_properties: (
            Iterable[str | rdflib.URIRef] | None
        ) = None,
    ):
        ro_crate_metadata_parser = JSONLDMetadataParser()
        ro_crate_metadata_parser.parse(ro_crate_metadata_path)
        ro_crate_metadata = ro_crate_metadata_parser.result
        self.ro_crate_metadata_graph = ro_crate_metadata.to_graph()

        self.required_properties = set()
        self.required_properties.add(str(self.file_path_property))
        if additional_required_column_properties:
            (
                self.required_properties.add(str(required_property))
                for required_property in additional_required_column_properties
            )

        super().__init__()

    def validate(self) -> ValidationResult:

        file_list_objects_results = self.ro_crate_metadata_graph.query(
            self.FILE_LIST_OBJECTS_QUERY
        )

        if len(file_list_objects_results) > 0:
            for result_row in file_list_objects_results:
                if not result_row.schema:
                    self.issues.append(
                        ValidationError(
                            severity=Severity.ERROR,
                            location_description=f"At ro-crate FileList with @id: {result_row.fileList}",
                            message=f"No schema object found in ro-crate-metadata.",
                        )
                    )
            self._check_required_columns_are_present()
            self._check_schemas_use_required_columns()

        return ValidationResult(
            issues=self.issues,
        )

    def _check_schemas_use_required_columns(self):
        roc_object_location_template = (
            "At ro-crate {object_type} object with @id: {schema_id}"
        )

        schema_to_column_property_result = self.ro_crate_metadata_graph.query(
            self.SCHEMA_COLUMN_PROPERTY_QUERY
        )

        schema_map = defaultdict(set)
        for result in schema_to_column_property_result:
            schema_map[result.schema].add(str(result.propertyUrl))

        for schema, property_urls in schema_map.items():
            for required_property in self.required_properties:
                if str(required_property) not in property_urls:
                    self.issues.append(
                        ValidationError(
                            severity=Severity.ERROR,
                            location_description=roc_object_location_template.format(
                                object_type="TableSchema", schema_id=schema
                            ),
                            message=f"Missing column with required property: {required_property}",
                        )
                    )

    def _check_required_columns_are_present(self):
        error_message_template = "No column has been assigned csvw:propertyUrl {property_url} in the ro-crate-metadata.json."

        resolved_query = self.ro_crate_metadata_graph.query(
            self.COLUMN_PROPERTY_URLS_QUERY
        )

        column_properties = [
            str(result_row.propertyUrl) for result_row in resolved_query
        ]

        for required_property in self.required_properties:
            if required_property not in column_properties:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        message=error_message_template.format(
                            property_url=str(required_property)
                        ),
                    )
                )
