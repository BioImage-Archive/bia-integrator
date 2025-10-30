from pathlib import Path
from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata_parser import (
    BIAROCrateMetadataParser,
)
from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.bia_ro_crate.file_list_parser import TSVFileListParser
from ro_crate_ingest.bia_ro_crate.file_list import FileList
import os
from bia_shared_datamodels import ro_crate_models


class BIAROCrateParser:
    """
    Basic processor of BioImage Archive ro-crates.
    Will read the info from the ro-crate-metadata.json (using the BIAROCrateMetadataParser) and from file lists (using the FileListParser).
    """

    def __init__(self) -> None:
        pass

    def parse(self, ro_crate_root: Path) -> tuple[BIAROCrateMetadata, FileList | None]:
        if not os.path.isdir(ro_crate_root):
            raise ValueError("Input path should be the root directory of the ro-crate.")

        metadata_parser = BIAROCrateMetadataParser()
        metadata = metadata_parser.parse_to_objects(ro_crate_root)

        roc_file_lists = metadata.get_objects_by_type()[ro_crate_models.FileList]

        if len(roc_file_lists) == 0:
            return metadata, None
        else:
            file_list_ids = list(roc_file_lists.keys())

            file_list_parser = TSVFileListParser(ro_crate_root, metadata)

            combined_file_list = file_list_parser.parse(file_list_ids[0])

            for file_list_id in file_list_ids[1:]:
                file_list = file_list_parser.parse(file_list_id)
                combined_file_list.merge(file_list)

            return metadata, combined_file_list
