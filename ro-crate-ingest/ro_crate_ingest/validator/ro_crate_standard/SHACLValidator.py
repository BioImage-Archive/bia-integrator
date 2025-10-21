from pathlib import Path

from rocrate_validator import models, services

from ro_crate_ingest.validator.validator import (
    Severity,
    ValidationError,
    ValidationResult,
    Validator,
)


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
                        severity=Severity(
                            severity_map.get(issue.severity.name, "INFO")
                        ),
                        location_description=error_location,
                        message=(
                            issue.message
                            if issue.message
                            else f"ro-crate shacl validation failed without message."
                        ),
                    )
                )

        return ValidationResult(issues=self.issues)
