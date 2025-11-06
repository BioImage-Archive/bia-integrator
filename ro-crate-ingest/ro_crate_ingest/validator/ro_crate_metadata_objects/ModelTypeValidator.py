from ro_crate_ingest.ro_crate_defaults import get_all_ro_crate_classes
from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
import pydantic
import pyld


class ModelTypeValidator(Validator):

    class_map: dict
    graph_objects: list[dict]
    context: dict | list | str

    def __init__(self, graph_objects: list[dict], context: dict | list | str):
        self.class_map = get_all_ro_crate_classes()
        self.context = context
        self.graph_objects = graph_objects
        super().__init__()

    def validate(self) -> ValidationResult:

        roc_object_location_template = "At ro-crate object with @id: {roc_id}"

        ro_crate_object_by_id: dict[str, ROCrateModel] = {}

        for ro_crate_object_dict in self.graph_objects:

            if ro_crate_object_dict.get("@id") == "ro-crate-metadata.json":
                # We don't need to validate the self-reffering entity for the ro-crate-metadata.json.
                continue

            try:
                object_types = self._expand_entity(ro_crate_object_dict, self.context)[
                    "@type"
                ]
            except KeyError:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            roc_id=ro_crate_object_dict.get("@id")
                        ),
                        message=f"Missing @type field. Found: {ro_crate_object_dict.keys()}",
                    )
                )
                continue

            class_intersection = self._get_class_intersection(object_types)

            if (class_intersection_count := len(class_intersection)) != 1:

                error_msg = (
                    f"@type of object does not contain any BIA classes. @type contains: {", ".join(ro_crate_object_dict.get("@type"))}"
                    if class_intersection_count == 0
                    else f"@type of object contains multiple BIA classes. @type contains: {", ".join(sorted(class_intersection))}"
                )

                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            roc_id=ro_crate_object_dict.get("@id")
                        ),
                        message=error_msg,
                    )
                )
                continue

            model = self.class_map[class_intersection.pop()]

            try:
                ro_crate_object: ROCrateModel = model(**ro_crate_object_dict)
            except pydantic.ValidationError as e:
                self.issues.append(
                    ValidationError(
                        severity=Severity.ERROR,
                        location_description=roc_object_location_template.format(
                            roc_id=ro_crate_object_dict.get("@id")
                        ),
                        message=str(e),
                    )
                )
                continue

            ro_crate_object_by_id[ro_crate_object.id] = ro_crate_object

        return ValidationResult(
            issues=self.issues, validated_object=ro_crate_object_by_id
        )

    def _get_class_intersection(self, object_types: list[str]) -> set[str]:
        return set(self.class_map.keys()) & set(object_types)

    @staticmethod
    def _expand_entity(
        entity: dict, context: dict | list | str
    ) -> dict[str, str | list[dict] | list[str]]:
        document = {"@context": context, "@graph": [entity]}
        expanded = pyld.jsonld.expand(document)
        return expanded[0]
