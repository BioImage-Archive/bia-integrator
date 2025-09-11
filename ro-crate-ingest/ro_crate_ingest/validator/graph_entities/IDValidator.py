from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)

class IDValidator(Validator):

    graph = list[dict]

    def __init__(self, graph):
        self.graph = graph
        super().__init__()

    def validate(self) -> ValidationResult:

        roc_object_location_template = "At ro-crate object with @id: {roc_id}"

        ro_crate_object_ids = []

        for ro_crate_object in self.graph:

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
            else:
                ro_crate_object_ids.append(roc_object_id)

            #TODO: add URI/blank node validation as per: https://www.researchobject.org/ro-crate/specification/1.2/appendix/jsonld#describing-entities-in-json-ld

        return ValidationResult(
            issues=self.issues,
        )
