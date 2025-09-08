from ro_crate_ingest.ro_crate_defaults import get_all_ro_crate_classes
from ro_crate_ingest.crate_reader import expand_entity
from ro_crate_ingest.validator.validator import (
    ValidationError,
    ValidationResult,
    Validator,
    Severity,
)
from bia_shared_datamodels.linked_data.pydantic_ld import ROCrateModel
import pydantic
from pathlib import Path
from typing import Optional
import logging
from rocrate.rocrate import read_metadata
from rocrate_validator import services, models


class BaseROCrateValidator(Validator):

    def validate(self, path_to_ro_crate: Path) -> ValidationResult:
        settings = services.ValidationSettings(
            rocrate_uri=path_to_ro_crate,
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
                if issue.violatingEntity:
                    self.issues.append(
                        ValidationError(
                            severity=severity_map.get(issue.severity.name),
                            location_description=f"At ro-crate object with @id: {issue.violatingEntity}",
                            message=issue.message,
                        )
                    )
                else:
                    self.issues.append(
                        ValidationError(
                            severity=severity_map.get(issue.severity.name),
                            message=issue.message,
                        )
                    )

        try:
            read_metadata(path_to_ro_crate / "ro-crate-metadata.json")
        except Exception as e:
            self.issues.append(
                ValidationError(
                    severity=Severity.ERROR,
                    message=e,
                )
            )

        return ValidationResult(issues=self.issues)
