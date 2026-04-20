import pandas as pd

from collections.abc import Iterable
from rdflib import URIRef

from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata
from bia_ro_crate.core.file_list import FileList
from bia_ro_crate.core.parser.file_list_parser import FileListParser
from bia_ro_crate.core.validation.severity import Severity
from bia_ro_crate.core.validation.validation_error import ValidationError


class ROCrateValidator:
    _metadata: BIAROCrateMetadata
    _file_list: FileList
    _parse_issues: list[ValidationError]

    def __init__(self, metadata: BIAROCrateMetadata, file_list: FileList) -> None:
        self._metadata = metadata
        self._file_list = file_list
        self._parse_issues = []

    @property
    def issues(self) -> list[ValidationError]:
        return list(self._parse_issues)

    def validate(self) -> None:
        self._validate_crate_connectivity()

    def _validate_crate_connectivity(self) -> None:
        metadata_ids = set(self._metadata.get_object_lookup())
        referenced_ids = self._metadata_reference_ids()
        referenced_ids.update(self._file_list_reference_ids())

        unconnected_ids = sorted(
            metadata_ids
            - referenced_ids
            - {self._metadata.DEFAULT_RO_CRATE_FILENAME}
        )

        if unconnected_ids:
            self._parse_issues.append(
                ValidationError(
                    severity=Severity.WARNING,
                    message=(
                        "Found RO-Crate objects with no inbound references across "
                        "ro-crate-metadata.json and file list references: "
                        f"{', '.join(unconnected_ids)}"
                    ),
                )
            )

    def _metadata_reference_ids(self) -> set[str]:
        references: set[str] = set()
        for entity in self._metadata.get_objects():
            entity_dict = entity.model_dump(by_alias=True, mode="json")
            for key, value in entity_dict.items():
                if key in {"@id", "@type"}:
                    continue
                references.update(self._collect_object_reference_ids(value))
        return references

    def _file_list_reference_ids(self) -> set[str]:
        reference_column_ids = {
            column_id
            for column_id, property_url in self._file_list.get_column_properties().items()
            if property_url
            and URIRef(str(property_url)) in FileListParser.ROC_METADATA_LOOKUP_TYPES
        }

        references: set[str] = set()
        for column_id in reference_column_ids:
            for value in self._file_list.data[column_id]:
                references.update(self._normalise_file_list_value(value))
        return references

    @classmethod
    def _collect_object_reference_ids(cls, value: object) -> set[str]:
        if isinstance(value, dict):
            if set(value.keys()) == {"@id"} and isinstance(value["@id"], str):
                return {value["@id"]}

            nested_references: set[str] = set()
            for nested_value in value.values():
                nested_references.update(cls._collect_object_reference_ids(nested_value))
            return nested_references

        if isinstance(value, list):
            nested_references: set[str] = set()
            for nested_value in value:
                nested_references.update(cls._collect_object_reference_ids(nested_value))
            return nested_references

        return set()

    @staticmethod
    def _normalise_file_list_value(value: object) -> Iterable[str]:
        if isinstance(value, list):
            return [str(item) for item in value if str(item)]

        if isinstance(value, str):
            return [value] if value else []

        if pd.isna(value):
            return []

        return [str(value)]
