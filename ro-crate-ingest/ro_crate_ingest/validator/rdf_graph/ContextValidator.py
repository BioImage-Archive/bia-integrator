from ro_crate_ingest.ro_crate_defaults import get_all_ro_crate_classes
from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels.linked_data.ld_context.SimpleJSONLDContext import (
    SimpleJSONLDContext,
)
from bia_shared_datamodels.ro_crate_generator_utils import generate_standard_bia_context
from pyld.jsonld import JsonLdProcessor


class ContextValidator(Validator):
    expected_bia_context_terms: SimpleJSONLDContext
    context_to_check: dict

    def __init__(self, context_to_check: dict | list | str):

        # Using pyld's JsonLdProcessor to handle the possible variablitiy in context definition structure
        jsonld_processor = JsonLdProcessor()
        self.context_to_check = jsonld_processor.process_context(
            active_ctx={"mappings": {}}, local_ctx=context_to_check, options=None
        )["mappings"]

        self._get_expected_context()

        super().__init__()

    def _get_expected_context(self) -> None:
        self.expected_bia_context_terms = generate_standard_bia_context()

    def validate(self) -> ValidationResult:

        for term in self.expected_bia_context_terms.terms:
            term_key = term.field_name
            if term_key in self.context_to_check:
                id_mapping = self.context_to_check[term_key]
                expected_uri = str(term.full_uri)
                if id_mapping["@id"] != expected_uri:
                    self.issues.append(
                        ValidationError(
                            message=f"Term has been remapped in context: {term_key} must be mapped to {expected_uri}",
                            location_description=f"At {term_key}",
                            severity=Severity.ERROR,
                        )
                    )

        return ValidationResult(self.issues)
