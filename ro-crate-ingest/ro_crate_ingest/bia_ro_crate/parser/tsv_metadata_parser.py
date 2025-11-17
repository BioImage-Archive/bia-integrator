from pathlib import Path
from urllib.parse import quote

import pandas as pd
from ro_crate_ingest.bia_ro_crate.parser.osv_metadata_parser import OSVMetadataParser

from ro_crate_ingest.bia_ro_crate.file_list import FileList


class TSVMetadataParser(OSVMetadataParser):

    def parse(self, path: Path):

        file_list_id = quote(str(path))
        columns = self._get_schema(file_list_id)

        full_file_path = self._get_full_path(path)

        data = pd.read_csv(full_file_path, delimiter="\t")

        self._expand_list_columns(data, columns)
        self._handle_empty_single_value_columns(data, columns)

        self._result = FileList(ro_crate_id=file_list_id, schema=columns, data=data)
