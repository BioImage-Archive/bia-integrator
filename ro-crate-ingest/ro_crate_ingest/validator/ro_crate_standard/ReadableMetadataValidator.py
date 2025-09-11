from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from pathlib import Path
from rocrate.rocrate import read_metadata


class ReadableMetadataValidator(Validator):

    path_to_ro_crate_metadata: Path

    def __init__(self, path_to_ro_crate_metadata):
        self.path_to_ro_crate_metadata = path_to_ro_crate_metadata
        super().__init__()

    def validate(self) -> ValidationResult:
        try:
            read_metadata(self.path_to_ro_crate_metadata)
        except Exception as e:
            self.issues.append(
                ValidationError(
                    severity=Severity.ERROR,
                    message=e,
                )
            )

        return ValidationResult(issues=self.issues)
