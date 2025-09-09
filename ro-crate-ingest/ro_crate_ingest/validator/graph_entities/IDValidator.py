from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from rdflib import URIRef


class IDValidator(Validator):

    def __init__(self):
        super().__init__()

    def validate(self, graph: list[dict]) -> ValidationResult:

        roc_object_location_template = "At ro-crate object with @id: {roc_id}"

        ro_crate_object_ids = []

        for ro_crate_object in graph:

            roc_object_id = ro_crate_object.get("@id")

            if roc_object_id == "ro-crate-metadata.json":
                # We don't need to validate the self-reffering entity for the ro-crate-metadata.json.
                continue

            if roc_object_id in ro_crate_object_ids:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            roc_id=roc_object_id
                        ),
                        message=f"Two objects with the same @id: @id should be unique.",
                    )
                )

            if not URIRef(roc_object_id):
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            roc_id=roc_object_id
                        ),
                        message=f"ID does not create a valid URI or blank node identifier",
                    )
                )

        return ValidationResult(
            issues=self.issues,
        )
