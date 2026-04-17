from pathlib import Path

from bia_ro_crate.core.parsed_ro_crate import ParsedROCrate
from bia_ro_crate.core.parser.base_parser import Parser
from bia_ro_crate.core.parser.jsonld_metadata_parser import JSONLDMetadataParser
from bia_ro_crate.core.parser.tsv_metadata_parser import TSVMetadataParser
from bia_ro_crate.core.validation.crate_validator import ROCrateValidator


class ROCrateParser(Parser[ParsedROCrate]):
    def parse(self, target: Path | str | None = None):
        metadata_parser = JSONLDMetadataParser(self._ro_crate_root)
        try:
            metadata_parser.parse(target=target)
        finally:
            self._parse_issues.extend(metadata_parser.issues)

        metadata = metadata_parser.result

        file_list_parser = TSVMetadataParser(metadata)
        try:
            file_list_parser.parse()
        finally:
            self._parse_issues.extend(file_list_parser.issues)

        file_list = file_list_parser.result

        crate_validator = ROCrateValidator(metadata, file_list)
        crate_validator.validate()
        self._parse_issues.extend(crate_validator.issues)

        self._result = ParsedROCrate(metadata=metadata, file_list=file_list)
