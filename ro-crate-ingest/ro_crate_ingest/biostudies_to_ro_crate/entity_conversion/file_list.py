import os
import tempfile
from pathlib import Path

import pandas as pd
from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.models.linked_data.pydantic_ld.LDModel import ObjectReference
from bia_ro_crate.models.linked_data.pydantic_ld.ROCrateModel import ROCrateModel

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.filelist_api import (
    File,
    load_filelist,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    find_file_lists_under_section,
    find_sections_with_filelists_recursive,
)
from ro_crate_ingest.graph_utils import ro_crate_data_entity_id_to_path
from ro_crate_ingest.save_utils import write_filelist


class FileListMapper:

    COMBINED_FILE_LIST_ID = "combined_file_list.tsv"
    PATH_COLUMN_NAME = "path"
    DATASET_COLUMN_NAME = "dataset"
    TABLE_SCHEMA_ID = "_:ts0"
    mapped_object: list[ROCrateModel]
    columns: list[ro_crate_models.Column]
    schema: ro_crate_models.TableSchema | None
    file_list: ro_crate_models.FileList | None
    dataset_id_lookup: dict[str, str]
    partial_filelists: list[Path]
    column_bnode_int: int
    ontology_map = {
        "path": "http://bia/filePath",
        "size": "http://bia/sizeInBytes",
        "sourceImage": "http://bia/sourceImagePath",
        "dataset": "http://schema.org/isPartOf",
    }

    def __init__(
        self,
        output_ro_crate_path: Path,
    ) -> None:
        self.output_ro_crate_path = output_ro_crate_path
        self.column_bnode_int = 0
        self.partial_filelists = []
        self.mapped_object = []
        self.columns = []
        self.schema = None
        self.file_list = None
        self.combined_file_list_headers = {}

    def map(
        self,
        submission: Submission,
        dataset_id_lookup: dict[str | None, str] | None = None,
        dataset_id_by_type: dict[str, str] | None = None,
    ):
        dataset_id_lookup = dataset_id_lookup or {}
        dataset_id_by_type = dataset_id_by_type or {}

        with tempfile.TemporaryDirectory() as temporary_dir:
            tmp_dir = Path(temporary_dir)
            self._create_file_list_from_file_lists(
                submission, tmp_dir, dataset_id_lookup
            )

            self._create_file_list_from_pagetab_files(
                submission, tmp_dir, dataset_id_lookup
            )

            self._combine_file_list()

        self._resolve_duplicates(dataset_id_by_type)

        self._create_ro_crate_objects()

    def get_mapped_objects(
        self,
        submission: Submission,
        dataset_id_lookup: dict[str | None, str] | None = None,
        dataset_id_by_type: dict[str, str] | None = None,
    ) -> list[ROCrateModel]:

        if not all((self.file_list, self.schema, self.columns)):
            self.map(submission, dataset_id_lookup, dataset_id_by_type)

        ro_crate_objects = [self.file_list, self.schema]
        ro_crate_objects += self.columns

        return ro_crate_objects

    def _create_file_list_from_file_lists(
        self,
        submission: Submission,
        tmp_dir: Path,
        dataset_id_lookup: dict[str | None, str],
    ):

        dataset_sections: list[Section] = []
        find_sections_with_filelists_recursive(submission.section, dataset_sections)

        for dataset_section in dataset_sections:
            file_list_name = FileListMapper._get_filelist_name_from_dataset(
                dataset_section
            )
            file_list = load_filelist(submission.accno, file_list_name)
            self._write_list_of_files_to_file_list(
                tmp_dir,
                dataset_id_lookup[dataset_section.accno],
                file_list_name,
                file_list,
            )

    def _write_list_of_files_to_file_list(
        self, tmp_dir: Path, dataset_id: str, file_list_name, list_of_files
    ):
        dataframe_filelist = FileListMapper._convert_filelist_to_dataframe(
            list_of_files, dataset_id
        )
        FileListMapper._normalise_headers(dataframe_filelist)
        self.collect_headers(dataframe_filelist.columns.tolist())
        file_path = write_filelist(tmp_dir, file_list_name, dataframe_filelist)
        self.partial_filelists.append(file_path)

    def _create_file_list_from_pagetab_files(
        self,
        submission: Submission,
        tmp_dir: Path,
        dataset_id_lookup: dict[str | None, str],
    ):
        if generated_id := dataset_id_lookup.get(None):
            self._write_list_of_files_to_file_list(
                tmp_dir,
                generated_id,
                "filelist_from_files.tsv",
                submission.section.files,
            )

    def _combine_file_list(self):
        combined_columns = list(self.combined_file_list_headers.keys())

        self.output_path = ro_crate_data_entity_id_to_path(
            self.output_ro_crate_path, self.COMBINED_FILE_LIST_ID
        )
        if not os.path.exists(self.output_path.parent):
            os.makedirs(self.output_path.parent)

        df = pd.DataFrame(columns=combined_columns)
        df.to_csv(
            self.output_path,
            sep="\t",
            index=False,
            mode="w",
            header=True,
        )

        for file_list_path in self.partial_filelists:
            df = pd.read_csv(file_list_path, sep="\t", dtype=str)
            df = df.reindex(columns=combined_columns, fill_value="")
            if df.empty:
                continue
            df = df.fillna("")
            df.to_csv(
                self.output_path,
                sep="\t",
                index=False,
                mode="a",
                header=False,
            )

    def collect_headers(self, headers: list[str]):
        for header in headers:
            self.combined_file_list_headers[header] = None

    def _resolve_duplicates(self, dataset_id_by_type):
        file_list_df = pd.read_csv(self.output_path, sep="\t", dtype=str)

        if file_list_df["path"].is_unique:
            return

        rows = []
        for _, group in file_list_df.groupby("path", sort=False):
            rows.append(FileListMapper.resolve_duplicate_row(group, dataset_id_by_type))

        result = pd.DataFrame(rows)
        result.to_csv(self.output_path, sep="\t", index=False)

    @staticmethod
    def resolve_duplicate_row(
        group: pd.DataFrame, dataset_id_by_type: dict[str, str]
    ) -> pd.Series:
        if len(group) == 1:
            return group.iloc[0]

        selected_dataset = FileListMapper.pick_dataset(group, dataset_id_by_type)

        # Check if identical except dataset
        compare = group.drop(columns=["dataset"])
        if compare.nunique(dropna=False).max() == 1:
            row = group.iloc[0].copy()
            row["dataset"] = selected_dataset
            return row

        merged = {}
        for col in group.columns:
            if col == "dataset":
                merged[col] = selected_dataset
                continue

            vals = group[col]
            unique_vals = pd.unique(vals.dropna())

            if len(unique_vals) == 0:
                merged[col] = None
            elif len(unique_vals) == 1:
                merged[col] = unique_vals[0]
            else:
                merged[col] = unique_vals.tolist()

        return pd.Series(merged)

    @staticmethod
    def pick_dataset(group, dataset_id_by_type):
        if "sourceImage" not in group.columns:
            return group.iloc[0]["dataset"]

        valid = group[
            group["sourceImage"].notna()
            & group["sourceImage"].astype(str).str.strip().ne("")
        ]

        if valid.empty:
            return group.iloc[0]["dataset"]

        types = valid["dataset"].map(dataset_id_by_type)
        annotations = valid[types == "Annotations"]

        return (
            annotations.iloc[0]["dataset"]
            if not annotations.empty
            else valid.iloc[0]["dataset"]
        )

    @staticmethod
    def _normalise_headers(filelist_dataframe: pd.DataFrame):
        filelist_dataframe.rename(
            columns={
                "Source_Image": "sourceImage",
                "Source Image Association": "sourceImage",
                "Source Image": "sourceImage",
                "Source image association": "sourceImage",
                "Source image": "sourceImage",
                "source image": "sourceImage",
            },
            inplace=True,
        )

    @staticmethod
    def _convert_filelist_to_dataframe(
        filelist: list[File], dataset_id: str
    ) -> pd.DataFrame:
        rows = []
        for item in filelist:
            flat = {
                "path": item.path,
                "size": item.size,
                "dataset": dataset_id,
                "biostudies_type": item.type,
            }
            attributes = {attr.name: attr.value for attr in item.attributes}
            flat.update(attributes)
            rows.append(flat)

        return pd.DataFrame(rows)

    @staticmethod
    def _get_filelist_name_from_dataset(dataset_section: Section):
        file_lists = find_file_lists_under_section(dataset_section, [])
        assert len(file_lists) == 1
        return file_lists[0]

    def _create_ro_crate_objects(
        self,
    ):
        columns_for_schema = []

        for column_bnode_int, header in enumerate(
            self.combined_file_list_headers.keys()
        ):
            column = self._get_column(header, column_bnode_int)
            columns_for_schema.append(ObjectReference(**{"@id": column.id}))

        schema = self._get_schema(columns_for_schema)

        filelist_dict = {
            "@id": self.COMBINED_FILE_LIST_ID,
            "@type": ["File", "bia:FileList", "csvw:Table"],
            "tableSchema": {"@id": schema.id},
        }

        self.schema = schema
        self.file_list = ro_crate_models.FileList(**filelist_dict)

    def _get_schema(
        self,
        columns_for_schema: list[ObjectReference],
    ) -> ro_crate_models.TableSchema:
        tableSchema = {
            "@id": self.TABLE_SCHEMA_ID,
            "@type": ["csvw:Schema"],
            "column": columns_for_schema,
        }
        schema = ro_crate_models.TableSchema(**tableSchema)
        return schema

    def _get_column(
        self,
        column_name: str,
        column_bnode_int: int,
    ) -> ro_crate_models.Column:

        column_dict = {
            "@id": f"_:col{column_bnode_int}",
            "@type": ["csvw:Column"],
            "columnName": column_name,
            "propertyUrl": self.ontology_map.get(column_name),
        }

        column = ro_crate_models.Column(**column_dict)
        self.columns.append(column)
        return column
