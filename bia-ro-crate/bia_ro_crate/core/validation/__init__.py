from typing import TYPE_CHECKING

from bia_ro_crate.core.validation.severity import Severity
from bia_ro_crate.core.validation.validation_error import ValidationError

if TYPE_CHECKING:
    from bia_ro_crate.core.validation.crate_validator import ROCrateValidator

__all__ = [
    "ROCrateValidator",
    "Severity",
    "ValidationError",
]


def __getattr__(name: str):
    if name == "ROCrateValidator":
        from bia_ro_crate.core.validation.crate_validator import ROCrateValidator

        return ROCrateValidator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
