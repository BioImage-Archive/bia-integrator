from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bia_ro_crate.core.parser.jsonld_metadata_parser import JSONLDMetadataParser
    from bia_ro_crate.core.parser.ro_crate_parser import ROCrateParser
    from bia_ro_crate.core.parser.tsv_metadata_parser import TSVMetadataParser

__all__ = ["TSVMetadataParser", "JSONLDMetadataParser", "ROCrateParser"]


def __getattr__(name: str):
    if name == "JSONLDMetadataParser":
        from bia_ro_crate.core.parser.jsonld_metadata_parser import JSONLDMetadataParser

        return JSONLDMetadataParser
    if name == "ROCrateParser":
        from bia_ro_crate.core.parser.ro_crate_parser import ROCrateParser

        return ROCrateParser
    if name == "TSVMetadataParser":
        from bia_ro_crate.core.parser.tsv_metadata_parser import TSVMetadataParser

        return TSVMetadataParser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
