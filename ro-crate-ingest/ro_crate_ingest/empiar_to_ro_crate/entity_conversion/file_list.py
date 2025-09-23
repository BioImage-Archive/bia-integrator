import pandas as pd
import logging
import parse

from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import Entry
from ro_crate_ingest.empiar_to_ro_crate.empiar.file_api import get_files, EMPIARFile
from pathlib import Path
from bia_shared_datamodels import ro_crate_models
from bia_shared_datamodels.linked_data.pydantic_ld.LDModel import ObjectReference
from ro_crate_ingest.save_utils import write_filelist
from typing import Optional
from itertools import chain

logger = logging.getLogger("__main__." + __name__)

# Avoid debug logging for every attempted parse.
requests_logger = logging.getLogger("parse")
requests_logger.setLevel(logging.INFO)

COLUMN_BNODE_INT = 0
SCHEMA_BNODE_INT = 0


def generate_relative_filelist_path(dataset_path: str) -> str:
    return str(Path(dataset_path) / f"file_list.tsv")


def create_file_list(
    output_ro_crate_path: Path,
    yaml_file: dict,
    empiar_api_entry: Entry,
    datasets_map: dict[str, ro_crate_models.Dataset],
) -> list[
    ro_crate_models.FileList | ro_crate_models.TableSchema | ro_crate_models.Column
]:
    """
    Unlike biostudies, all EMPIAR file lists have the same schema.

    Note will created a filelist for 'unnasigned' files that do not match any dataset if there are any. This is not expected to be ingested to the api.
    """

    columns = get_column_list()
    schema = get_schema(columns)

    file_df = create_base_dataframe_from_file_paths(yaml_file)

    file_list_df = expand_dataframe_metadata(
        yaml_file, empiar_api_entry, datasets_map, file_df
    )

    dataframes_by_dataset_map = split_dataframe_by_dataset(file_list_df)

    ro_crate_objects = [schema]
    ro_crate_objects.extend(columns)

    for dataset_id, dataframe in dataframes_by_dataset_map.items():
        file_list_id = generate_relative_filelist_path(dataset_id)
        ro_crate_objects.append(get_ro_crate_filelist(file_list_id, schema))
        write_filelist(output_ro_crate_path, file_list_id, dataframe)

    return ro_crate_objects


def create_base_dataframe_from_file_paths(yaml_file):
    files: list[EMPIARFile] = get_files(yaml_file["accession_id"])
    file_df: pd.DataFrame = pd.DataFrame(
        files,
    ).map(lambda x: x[1])
    file_df.columns = ["file_path", "size_in_bytes"]
    return file_df


def expand_dataframe_metadata(
    yaml_file: dict,
    empiar_api_entry: Entry,
    datasets_map: dict[str, ro_crate_models.Dataset],
    file_df: pd.DataFrame,
):
    dir_to_imageset_map = {
        Path(imageset.directory): imageset.name
        for imageset in empiar_api_entry.imagesets
    }

    imageset_to_dataset_id = {
        imageset_title: dataset.id for imageset_title, dataset in datasets_map.items()
    }

    yaml_datasets_by_title = {
        dataset["title"]: dataset for dataset in yaml_file["datasets"]
    }

    additional_files_pattern_to_dataset_map = {}
    for dataset in yaml_file["datasets"]:
        for additional_file in dataset.get("additional_files", []):
            additional_files_pattern_to_dataset_map[additional_file["file_pattern"]] = (
                dataset["title"]
            )

    file_list_df = file_df.apply(
        expand_row_metdata,
        args=(
            dir_to_imageset_map,
            additional_files_pattern_to_dataset_map,
            imageset_to_dataset_id,
            yaml_datasets_by_title,
        ),
        axis=1,
    )

    return file_list_df


def expand_row_metdata(
    row: pd.Series,
    dir_to_imageset_map: dict[Path, str],
    additional_files_pattern_to_dataset_map: dict[str, str],
    imageset_to_dataset_id: dict[str, StopIteration],
    yaml_dataset_by_title: dict,
) -> pd.Series:
    file_path: Path = row["file_path"]

    path = file_path.as_posix()

    output_row = {
        "file_path": str(file_path),
        "size_in_bytes": int(row["size_in_bytes"]),
        "dataset_ref": None,
        "type": None,
        "label": None,
        "source_image_label": None,
        "associated_annotation_method": None,
        "associated_protocol": None,
    }

    imageset_title = find_matching_imageset_path(dir_to_imageset_map, path)

    output_row["dataset_ref"] = get_dataset_id(
        additional_files_pattern_to_dataset_map,
        imageset_to_dataset_id,
        path,
        imageset_title,
    )

    if imageset_title and (imageset_title in yaml_dataset_by_title):
        dataset = yaml_dataset_by_title[imageset_title]

        # Build a flattened sequence of (object, type) pairs
        objects_with_types = chain(
            ((obj, "http://bia/Image") for obj in dataset.get("assigned_images", ())),
            (
                (obj, "http://bia/AnnotationData")
                for obj in dataset.get("assigned_annotations", ())
            ),
        )

        for obj, obj_type in objects_with_types:
            if is_matching_file_pattern_from_yaml_object(obj, path):
                update_row(output_row, obj, obj_type)
                break

    return pd.Series(output_row)


def update_row(output_row: dict, yaml_object: dict, row_type: str):
    output_row["label"] = yaml_object["label"]
    output_row["type"] = row_type
    output_row["associated_annotation_method"] = yaml_object.get(
        "annotation_method_title", None
    )
    output_row["associated_protocol"] = yaml_object.get("protocol_title", None)

    input_images = yaml_object.get("input_image_label", None)
    if isinstance(input_images, list):
        output_row["source_image_label"] = [
            input_image.get("label") for input_image in input_images
        ]
    else:
        output_row["source_image_label"] = input_images


def get_dataset_id(
    additional_files_pattern_to_dataset_map: dict[str, str],
    imageset_to_dataset_id: dict[str, str],
    path: Path,
    imageset_title: str,
) -> Optional[str]:
    dataset_id = imageset_to_dataset_id.get(imageset_title, None)
    if dataset_id is None:
        for pattern in additional_files_pattern_to_dataset_map:
            result = parse.parse(pattern, path)
            if result is not None:
                dataset_id = imageset_to_dataset_id.get(
                    additional_files_pattern_to_dataset_map[pattern], None
                )

    return dataset_id


def find_matching_imageset_path(
    dir_to_imageset_map: dict[Path, str], path: Path
) -> Optional[str]:
    for dir_path in dir_to_imageset_map:
        if path.startswith(dir_path.as_posix()):
            imageset_title = dir_to_imageset_map[dir_path]
            return imageset_title


def is_matching_file_pattern_from_yaml_object(
    image_or_annotation_data: dict, path: Path
) -> bool:
    pattern = image_or_annotation_data.get("file_pattern", None)
    if pattern:
        result = parse.parse(f"data/{pattern}", path)
        return result is not None
    else:
        return False


def split_dataframe_by_dataset(file_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    split_dfs = {}
    for name in file_df["dataset_ref"].dropna().unique():
        x = file_df[file_df["dataset_ref"] == name]
        y = x.drop("dataset_ref", axis=1)
        split_dfs[name] = y

    unassigned_files = file_df[file_df["dataset_ref"].isna()]
    if len(unassigned_files) > 0:
        x = unassigned_files
        y = x.drop("dataset_ref", axis=1)
        split_dfs["unassigned"] = y
    return split_dfs


def get_ro_crate_filelist(
    filelist_id: str, schema: ro_crate_models.TableSchema
) -> ro_crate_models.FileList:

    filelist_dict = {
        "@id": filelist_id,
        "@type": ["File", "bia:FileList", "csvw:Table"],
        "tableSchema": {"@id": schema.id},
    }

    return ro_crate_models.FileList(**filelist_dict)


def get_schema(
    columns_for_schema: list[ObjectReference],
) -> ro_crate_models.TableSchema:

    tableSchema = {
        "@id": "_:ts0",
        "@type": ["csvw:Schema"],
        "column": [{"@id": column.id} for column in columns_for_schema],
    }
    schema = ro_crate_models.TableSchema(**tableSchema)
    return schema


def get_column_list() -> list[ro_crate_models.Column]:
    columns_properties = {
        "file_path": "http://bia/filePath",
        "size_in_bytes": "http://bia/sizeInBytes",
        "type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        "label": "http://schema.org/name",
        "source_image_label": "http://bia/sourceImageLabel",
        "associated_annotation_method": "http://bia/associatedAnnotationMethod",
        "associated_protocol": "http://bia/associatedProtocol",
    }

    id_no = 0
    columns = []

    for column_header, property in columns_properties.items():
        model_dict = {
            "@id": f"_:col{id_no}",
            "@type": ["csvw:Column"],
            "columnName": column_header,
        }
        if property:
            model_dict["propertyUrl"] = property
        columns.append(ro_crate_models.Column(**model_dict))
        id_no += 1

    return columns
