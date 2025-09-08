from ro_crate_ingest.ro_crate_defaults import get_all_ro_crate_classes
from ro_crate_ingest.crate_reader import expand_entity
from ro_crate_ingest.validator.generic_validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from bia_shared_datamodels.linked_data.pydantic_ld import ROCrateModel
import pydantic
from typing import Optional
import logging


class GraphValidator(Validator):

    class_map: dict

    def __init__(self):
        self.class_map = get_all_ro_crate_classes()
        super().__init__()

    def validate(self, graph: list[dict], context) -> ValidationResult:

        roc_object_location_template = "At ro-crate object with @id: {roc_id}"

        ro_crate_object_by_id = {}

        for ro_crate_object in graph:

            if ro_crate_object.get("@id") == "ro-crate-metadata.json":
                # We don't need to validate the self-reffering entity for the ro-crate-metadata.json.
                continue

            try:
                object_types = expand_entity(ro_crate_object, context)["@type"]
            except KeyError:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            roc_id=ro_crate_object.get("@id")
                        ),
                        message=f"Missing @type field. Found: {ro_crate_object.keys()}",
                    )
                )

            class_intersection = self._get_class_intersection(object_types)

            if (class_intersection_count := len(class_intersection)) != 1:
                if class_intersection_count == 0:
                    self.issues.append(
                        ValidationError(
                            severity=Severity.ERROR,
                            location_description=roc_object_location_template.format(
                                roc_id=ro_crate_object.get("@id")
                            ),
                            message=f"@type of object does not contain any BIA classes. @type contains: {", ".join(ro_crate_object.get("@type"))}",
                        )
                    )
                else:
                    self.issues.append(
                        ValidationError(
                            severity=Severity.ERROR,
                            location_description=roc_object_location_template.format(
                                roc_id=ro_crate_object.get("@id")
                            ),
                            message=f"@type of object contains multiple BIA classes. @type contains: {", ".join(sorted(class_intersection))}",
                        )
                    )
                continue

            model = self.class_map[class_intersection[0]]

            try:
                ro_crate_object: ROCrateModel = model(**ro_crate_object)
            except pydantic.ValidationError as e:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            roc_id=ro_crate_object.get("@id")
                        ),
                        message=str(e),
                    )
                )
                continue

            if ro_crate_object.id in ro_crate_object_by_id:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            roc_id=ro_crate_object.id
                        ),
                        message=f"Two objects with the same @id: @id should be unique.",
                    )
                )

            ro_crate_object_by_id[ro_crate_object.id] = ro_crate_object

        return ValidationResult(
            issues=self.issues, validated_object=ro_crate_object_by_id
        )

    def _get_class_intersection(self, object_types: list[str]):
        return list(set(self.class_map.keys()) & set(object_types))
