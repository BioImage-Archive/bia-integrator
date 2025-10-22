from pathlib import Path

import rdflib
from collections import defaultdict
from ro_crate_ingest.crate_reader import load_ro_crate_metadata_to_graph
from ro_crate_ingest.validator.validator import (
    Severity,
    ValidationError,
    ValidationResult,
    Validator,
)
from bia_shared_datamodels.linked_data.bia_ontology_utils import load_bia_ontology


class ReferenceValidation(Validator):

    ro_crate_metadata_graph: rdflib.Graph
    bia_ontology: rdflib.Graph

    def __init__(
        self,
        ro_crate_metadata_path: Path,
    ):
        self.ro_crate_metadata_graph = load_ro_crate_metadata_to_graph(
            ro_crate_metadata_path
        )
        self.bia_ontology = load_bia_ontology()

        super().__init__()

    def _get_properties_to_validate(self) -> dict[rdflib.Node, set[rdflib.Node]]:
        object_properties = set(
            self.bia_ontology.subjects(
                rdflib.RDF.type, rdflib.OWL.ObjectProperty, unique=True
            )
        )

        object_properties_and_ranges = {}
        for property in object_properties:
            range_class = set(self.bia_ontology.objects(property, rdflib.RDFS.range))
            object_properties_and_ranges[property] = range_class

        return object_properties_and_ranges

    def validate(self) -> ValidationResult:
        subjects_and_types = self.ro_crate_metadata_graph.subject_objects(
            rdflib.RDF.type, unique=True
        )
        typed_subjects = defaultdict(set)
        for subject, subject_type in subjects_and_types:
            typed_subjects[subject].add(subject_type)

        properties_to_validate = self._get_properties_to_validate()

        for subject, predicate, obj in self.ro_crate_metadata_graph:
            if predicate in properties_to_validate:
                if obj not in typed_subjects:
                    self.issues.append(
                        ValidationError(
                            message=f"Ro-crate object contains references to {obj} which is not defined in the ro-crate.",
                            location_description=f"At ro-crate object with @id: {subject}",
                            severity=Severity.ERROR,
                        )
                    )
                else:
                    object_types = typed_subjects[obj]
                    range_types = properties_to_validate[predicate]
                    type_intersection = object_types & range_types
                    if len(type_intersection) == 0:
                        self.issues.append(
                            ValidationError(
                                message=f"Ro-crate object contains references to {obj} which is not of the expected type.",
                                location_description=f"At ro-crate object with @id: {subject}",
                                severity=Severity.ERROR,
                            )
                        )

        return ValidationResult(
            sorted(self.issues, key=lambda issue: str(issue.location_description))
        )
