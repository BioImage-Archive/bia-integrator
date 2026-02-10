import tempfile
from urllib.parse import unquote
import pandas as pd
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.filelist_api import (
    File,
    load_filelist,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    find_file_lists_under_section,
    find_sections_with_filelists_recursive,
)
from pathlib import Path
from bia_shared_datamodels import ro_crate_models
from bia_shared_datamodels.linked_data.pydantic_ld.LDModel import ObjectReference
from ro_crate_ingest.save_utils import write_filelist
from urllib.parse import quote


COMBINED_FILE_LIST_ID = "combined_file_list.tsv"


def generate_relative_filelist_path(dataset_path: str, file_list_name: str) -> str:
    return str(Path(dataset_path) / f"{quote(Path(file_list_name).stem)}.tsv")


def get_filelist_name_from_dataset(dataset_section: Section):
    file_lists = find_file_lists_under_section(dataset_section, [])
    assert len(file_lists) == 1
    return file_lists[0]


def create_file_list(
    output_ro_crate_path: Path,
    submission: Submission,
    dataset_by_accno: dict[str, ro_crate_models.Dataset],
) -> list[
    ro_crate_models.FileList | ro_crate_models.TableSchema | ro_crate_models.Column
]:
    dataset_sections: list[Section] = []
    find_sections_with_filelists_recursive(submission.section, dataset_sections)

    column_by_name_url: dict[str, dict[str, ro_crate_models.Column]] = {}
    schema_list: list[ro_crate_models.TableSchema] = []
    filelist: list[ro_crate_models.FileList] = []

    for dataset_section in dataset_sections:
        roc_dataset = dataset_by_accno[dataset_section.accno]
        file_list_name = get_filelist_name_from_dataset(dataset_section)

        file_list = load_filelist(submission.accno, file_list_name)
        dataframe_filelist = convert_filelist_to_dataframe(file_list)
        normalise_headers(dataframe_filelist)

        filelist_id = generate_relative_filelist_path(roc_dataset.id, file_list_name)
        write_filelist(output_ro_crate_path, filelist_id, dataframe_filelist)

        filelist.append(
            create_ro_crate_filelist_and_schema_objects(
                filelist_id=filelist_id,
                column_headers=dataframe_filelist.columns.values.tolist(),
                column_by_name_url=column_by_name_url,
                schema_list=schema_list,
            )
        )

    column_list = []
    for x in column_by_name_url.values():
        [column_list.append(col) for col in x.values()]

    return column_list + schema_list + filelist


def convert_filelist_to_dataframe(filelist: list[File]) -> pd.DataFrame:
    rows = []
    for item in filelist:
        flat = {"path": item.path, "size": item.size, "type": item.type}
        attributes = {attr.name: attr.value for attr in item.attributes}
        flat.update(attributes)
        rows.append(flat)

    return pd.DataFrame(rows)


def normalise_headers(filelist_dataframe: pd.DataFrame):
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


def create_ro_crate_filelist_and_schema_objects(
    filelist_id: str,
    column_headers: list[str],
    column_by_name_url: dict[str, dict[str, ro_crate_models.Column]],
    schema_list: list[ro_crate_models.TableSchema],
) -> ro_crate_models.FileList:
    columns_for_schema = []

    for column_bnode_int, header in enumerate(column_headers):
        column = get_column(header, column_by_name_url, column_bnode_int)
        columns_for_schema.append(ObjectReference(**{"@id": column.id}))

    schema = get_schema(columns_for_schema, schema_list)

    filelist_dict = {
        "@id": filelist_id,
        "@type": ["File", "bia:FileList", "csvw:Table"],
        "tableSchema": {"@id": schema.id},
    }

    return ro_crate_models.FileList(**filelist_dict)


def get_schema(
    columns_for_schema: list[ObjectReference],
    schema_list: list[ro_crate_models.TableSchema],
    schema_bnode_int: int = 0,
) -> ro_crate_models.TableSchema:
    for existing_schema in schema_list:
        pairs = zip(existing_schema.column, columns_for_schema)
        if all(x == y for x, y in pairs):
            return existing_schema

    ts_id = f"_:ts{schema_bnode_int}"
    tableSchema = {
        "@id": ts_id,
        "@type": ["csvw:Schema"],
        "column": columns_for_schema,
    }
    schema = ro_crate_models.TableSchema(**tableSchema)
    schema_list.append(schema)
    return schema


def get_column(
    column_name: str,
    column_by_name_url: dict[str, dict[str, ro_crate_models.Column]],
    column_bnode_int,
) -> ro_crate_models.Column:
    ontology_map = {
        "path": "http://bia/filePath",
        "size": "http://bia/sizeInBytes",
        "sourceImage": "http://bia/sourceImagePath",
        "dataset": "http://schema.org/isPartOf",
    }

    column_data = {"columnName": column_name}
    if column_name in ontology_map:
        column_data["propertyUrl"] = ontology_map[column_name]
    else:
        column_data["propertyUrl"] = None

    try:
        column = column_by_name_url[column_data["columnName"]][
            column_data["propertyUrl"]
        ]
    except KeyError:
        column_id = f"_:col{column_bnode_int}"
        column_dict = column_data | {"@id": column_id, "@type": ["csvw:Column"]}
        column = ro_crate_models.Column(**column_dict)

        if column.columnName not in column_by_name_url:
            column_by_name_url[column.columnName] = {}

        column_by_name_url[column.columnName][column.propertyUrl] = column

    return column


def combine_file_lists(
    file_list_path_by_dataset: dict[str, Path],
    output_ro_crate_path: Path,
    file_list_id: str,
):
    # Run in two passes: first to gather all columns, then to write combined filelist
    # Some file lists may be quite large, so avoid loading them all into memory at once
    # Also preserve order of columns as they first appear therefore, not using set
    all_columns = []
    for file_list_path in file_list_path_by_dataset.values():
        df = pd.read_csv(file_list_path, sep="\t", dtype=str, nrows=0)
        for column in df.columns.tolist():
            if column not in all_columns:
                all_columns.append(column)

    # Add dataset ID column (after 'type' column) if not already present
    if "dataset" not in all_columns:
        all_columns.insert(3, "dataset")

    # Write headers for combined file list
    output_path = output_ro_crate_path / file_list_id
    df = pd.DataFrame(columns=all_columns)
    df.to_csv(
        output_path,
        sep="\t",
        index=False,
        mode="w",
        header=True,
    )

    for dataset, file_list_path in file_list_path_by_dataset.items():
        df = pd.read_csv(file_list_path, sep="\t", dtype=str)
        df = df.reindex(columns=all_columns, fill_value="")

        if df.empty:
            continue

        df = df.fillna("")
        df["dataset"] = dataset

        df.to_csv(
            output_path,
            sep="\t",
            index=False,
            mode="a",
            header=False,
        )


def create_combined_file_list_for_study(
    output_ro_crate_path: Path,
    submission: Submission,
    dataset_by_accno: dict[str, ro_crate_models.Dataset],
) -> tuple[
    list[ro_crate_models.Column],
    list[ro_crate_models.TableSchema],
    ro_crate_models.FileList,
]:
    file_list_paths_by_dataset: dict[str, Path] = {}
    with tempfile.TemporaryDirectory() as temporary_dir:
        temporary_output_directory = Path(temporary_dir)

        # Create individual file lists in temp directory then combine them.
        create_file_list(temporary_output_directory, submission, dataset_by_accno)

        file_list_paths = [f for f in temporary_output_directory.rglob("*.tsv")]

        for dataset in dataset_by_accno.values():
            file_list_dir = temporary_output_directory / unquote(dataset.id)
            file_list_path = [p for p in file_list_dir.glob("*.tsv")]
            n_file_lists = len(file_list_path)
            if n_file_lists != 1:
                raise ValueError(
                    f"Exactly one file list for dataset with ID {dataset.id}. Got {n_file_lists}. Values {file_list_path}."
                )
            elif file_list_path[0] not in file_list_paths:
                raise ValueError(
                    f"Expected file list path for dataset with id {dataset.id} not found while combining file lists. Got {file_list_path[0]}, expected one of {file_list_path[0]}. Expected on of {file_list_paths}"
                )
            file_list_paths_by_dataset[dataset.id] = file_list_path[0]
        combine_file_lists(
            file_list_paths_by_dataset,
            output_ro_crate_path,
            COMBINED_FILE_LIST_ID,
        )

    global COLUMN_BNODE_INT
    COLUMN_BNODE_INT = 0

    column_by_name_url: dict[str, dict[str, ro_crate_models.Column]] = {}
    schema_list: list[ro_crate_models.TableSchema] = []

    column_headers = pd.read_csv(
        output_ro_crate_path / COMBINED_FILE_LIST_ID, sep="\t", dtype=str, nrows=0
    ).columns.values.tolist()

    combined_file_list = create_ro_crate_filelist_and_schema_objects(
        filelist_id=COMBINED_FILE_LIST_ID,
        column_headers=column_headers,
        column_by_name_url=column_by_name_url,
        schema_list=schema_list,
    )

    column_list: list[ro_crate_models.Column] = []
    for x in column_by_name_url.values():
        [column_list.append(col) for col in x.values()]

    return column_list, schema_list, combined_file_list
