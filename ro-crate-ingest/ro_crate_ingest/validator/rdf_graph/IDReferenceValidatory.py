from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from rdflib import Graph


class IDReferenceValidator(Validator):
    ro_crate_object_lookup: dict[str, ROCrateModel]
    bia_ontology: Graph | None

    def __init__(self, ro_crate_objects: dict[str, ROCrateModel], ro_crate):
        self.ro_crate_object_lookup = ro_crate_objects
        self.bia_ontology = None
        super().__init__()

    def validate(self) -> ValidationResult:
        for object_id, ro_crate_object in self.ro_crate_object_lookup.items():
            object_class = ro_crate_object.__class__
            for field_name, field_info in object_class.model_fields:
                pass

        return ValidationResult(self.issues)
