from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
)
from pathlib import Path
from rocrate_validator import services, models


class SHACLValidator(Validator):

    path_to_ro_crate: Path

    def __init__(self, path_to_ro_crate: Path):
        self.path_to_ro_crate = path_to_ro_crate
        super().__init__()

    def validate(self) -> ValidationResult:
        settings = services.ValidationSettings(
            rocrate_uri=self.path_to_ro_crate,
            profile_identifier="ro-crate-1.1",
            requirement_severity=models.Severity.REQUIRED,
        )

        result = services.validate(settings)

        severity_map = {
            "REQUIRED": "ERROR",
            "RECOMMENDED": "WARNING",
            "OPTIONAL": "INFO",
        }

        if result.has_issues():
            for issue in result.issues:
                error_location = (
                    f"At ro-crate object with @id: {issue.violatingEntity}"
                    if issue.violatingEntity
                    else None
                )
                self.issues.append(
                    ValidationError(
                        severity=severity_map.get(issue.severity.name),
                        location_description=error_location,
                        message=issue.message,
                    )
                )

        return ValidationResult(issues=self.issues)
