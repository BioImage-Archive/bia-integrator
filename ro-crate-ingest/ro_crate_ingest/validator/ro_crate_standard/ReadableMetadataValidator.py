from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from pathlib import Path
from rocrate.rocrate import read_metadata


class ReadableMetadataValidator(Validator):

    def validate(self, path_to_ro_crate_metadata: Path) -> ValidationResult:
        try:
            read_metadata(path_to_ro_crate_metadata)
        except Exception as e:
            self.issues.append(
                ValidationError(
                    severity=Severity.ERROR,
                    message=e,
                )
            )

        return ValidationResult(issues=self.issues)
