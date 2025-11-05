from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

import rdflib
from bia_shared_datamodels import ro_crate_models
from bia_shared_datamodels.linked_data.bia_ontology_utils import load_bia_ontology
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel

from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.bia_ro_crate.parser.jsonld_metadata_parser import (
    JSONLDMetadataParser,
)
from ro_crate_ingest.bia_ro_crate.parser.tsv_metadata_parser import (
    TSVMetadataParser,
)
from ro_crate_ingest.validator.validator import (
    Severity,
    ValidationError,
    ValidationResult,
    Validator,
)


class FileListReferenceValidator(Validator):
    """
    Validate that when the contents of a ro-crate references another object in the ro-crate-metadata.json, that reference exists and is of expected type.

    Whether a column in a file list is expected to contain references (and their expected type) is based on the definitions in the bia ontology.

    NB: this does not validate source image references, as those have more complex dependencies;
    e.g. whether the files are present in the ro-crate or referenced, or whether references are by path, id, or label.
    """

    ro_crate_objects: BIAROCrateMetadata
    ro_crate_root: Path
    ERROR_MESSAGE_LOCATION = "In filelist: {filelist_id}, at row: {row_index}."
    ROC_LOOKUP_TYPES = {
        "http://bia/associatedBiologicalEntity": ro_crate_models.BioSample,
        "http://bia/associatedImagingPreparationProtocol": ro_crate_models.SpecimenImagingPreparationProtocol,
        "http://bia/associatedImageAcquisitionProtocol": ro_crate_models.ImageAcquisitionProtocol,
        "http://bia/associatedAnnotationMethod": ro_crate_models.AnnotationMethod,
        "http://bia/associatedProtocol": ro_crate_models.Protocol,
        "http://bia/associatedSubject": ro_crate_models.Specimen,
    }

    def __init__(
        self,
        ro_crate_path: Path,
    ):
        ro_crate_metatadata_parser = JSONLDMetadataParser()
        ro_crate_metatadata_parser.parse(ro_crate_path)
        self.ro_crate_objects = ro_crate_metatadata_parser.result
        self.ro_crate_root = ro_crate_path
        super().__init__()

    def _get_properties_to_validate(self) -> dict[rdflib.Node, set[rdflib.Node]]:
        bia_ontology = load_bia_ontology()

        object_properties = set(
            bia_ontology.subjects(
                rdflib.RDF.type, rdflib.OWL.ObjectProperty, unique=True
            )
        )

        object_properties_and_ranges = {}
        for property in object_properties:
            range_class = set(bia_ontology.objects(property, rdflib.RDFS.range))
            object_properties_and_ranges[property] = range_class

        return object_properties_and_ranges

    def validate(self) -> ValidationResult:

        roc_metadata_lookup = self.ro_crate_objects.get_object_lookup()
        file_lists_roc_objects = self.ro_crate_objects.get_objects_by_type()[
            ro_crate_models.FileList
        ]

        if len(file_lists_roc_objects) == 0:
            return ValidationResult(
                issues=self.issues,
            )

        tsv_file_list_parser = TSVMetadataParser(
            ro_crate_root=self.ro_crate_root, ro_crate_metadata=self.ro_crate_objects
        )

        for file_list_id in file_lists_roc_objects:
            tsv_file_list_parser.parse(Path(unquote(str(file_list_id))))
            file_list = tsv_file_list_parser.result
            processeable_dataframe = file_list.to_processable_data()

            columns_to_check = self._get_columns_to_check(
                processeable_dataframe.columns
            )

            if not columns_to_check:
                continue

            processeable_dataframe.apply(
                self._check_row_reference_and_type,
                args=(roc_metadata_lookup, columns_to_check, self, file_list_id),
                axis=1,
            )

        return ValidationResult(
            issues=self.issues,
        )

    def _get_columns_to_check(self, columns: Iterable[str]):

        column_types_to_check = {}

        for column in columns:
            if column in self.ROC_LOOKUP_TYPES:
                column_types_to_check[column] = self.ROC_LOOKUP_TYPES[column]

        return column_types_to_check

    @staticmethod
    def _check_row_reference_and_type(
        row,
        roc_metadata_lookup: dict[str, ROCrateModel],
        columns_to_check: dict[str, type[ROCrateModel]],
        file_list_validator: "FileListReferenceValidator",
        file_list_id: str,
    ):
        for column in columns_to_check:
            references = row[column]
            if isinstance(references, str):
                references = [references]

            for reference in references:
                message = None
                if reference not in roc_metadata_lookup:
                    message = f"{reference} does not exist in ro-crate-metadata.json"
                elif not isinstance(
                    roc_metadata_lookup[reference], columns_to_check[column]
                ):
                    message = f"{reference} references an object of unexpected type."

                if message:
                    file_list_validator.issues.append(
                        ValidationError(
                            severity=Severity.ERROR,
                            message=message,
                            location_description=file_list_validator.ERROR_MESSAGE_LOCATION.format(
                                filelist_id=file_list_id,
                                row_index=row["http://bia/filePath"],
                            ),
                        )
                    )
