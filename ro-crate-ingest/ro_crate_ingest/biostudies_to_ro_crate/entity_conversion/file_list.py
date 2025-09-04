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
    global COLUMN_BNODE_INT
    COLUMN_BNODE_INT = 0
    global SCHEMA_BNODE_INT
    SCHEMA_BNODE_INT = 0

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

    for header in column_headers:
        column = get_column(header, column_by_name_url)
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
) -> ro_crate_models.TableSchema:
    for existing_schema in schema_list:
        pairs = zip(existing_schema.column, columns_for_schema)
        if all(x == y for x, y in pairs):
            return existing_schema

    global SCHEMA_BNODE_INT
    ts_id = f"_:ts{SCHEMA_BNODE_INT}"
    SCHEMA_BNODE_INT += 1
    tableSchema = {
        "@id": ts_id,
        "@type": ["csvw:Schema"],
        "column": columns_for_schema,
    }
    schema = ro_crate_models.TableSchema(**tableSchema)
    schema_list.append(schema)
    return schema


def get_column(
    column_name: str, column_by_name_url: dict[str, dict[str, ro_crate_models.Column]]
) -> ro_crate_models.Column:
    ontology_map = {
        "path": "http://bia/filePath",
        "size": "http://bia/sizeInBytes",
        "sourceImage": "http://bia/sourceImagePath",
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
        global COLUMN_BNODE_INT
        column_id = f"_:col{COLUMN_BNODE_INT}"
        COLUMN_BNODE_INT += 1
        column_dict = column_data | {"@id": column_id, "@type": ["csvw:Column"]}
        column = ro_crate_models.Column(**column_dict)

        if column.columnName not in column_by_name_url:
            column_by_name_url[column.columnName] = {}

        column_by_name_url[column.columnName][column.propertyUrl] = column

    return column
