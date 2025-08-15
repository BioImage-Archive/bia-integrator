import pandas as pd
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import Entry
from ro_crate_ingest.empiar_to_ro_crate.empiar.file_api import get_files, EMPIARFile
from pathlib import Path
from bia_shared_datamodels import ro_crate_models
from bia_shared_datamodels.linked_data.pydantic_ld.LDModel import ObjectReference
from ro_crate_ingest.save_utils import write_filelist
import parse
from typing import Optional
import logging

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
    Unlike biostudies, all EMPIAR file lists have the same schema
    """

    columns = get_column_list()
    schema = get_schema(columns)

    file_df = create_base_file_dataframe(yaml_file)

    file_list_df = expand_dataframe_metadata(
        yaml_file, empiar_api_entry, datasets_map, file_df
    )

    split_dfs = split_dataframes_by_dataset(file_list_df)

    ro_crate_objects = [schema]
    ro_crate_objects.extend(columns)

    for dataset_id, dataframe in split_dfs.items():
        file_list_id = generate_relative_filelist_path(dataset_id)
        ro_crate_objects.append(get_ro_crate_filelist(file_list_id, schema))
        write_filelist(output_ro_crate_path, file_list_id, dataframe)

    return ro_crate_objects


def create_base_file_dataframe(yaml_file):
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
        find_matching_imageset_and_images,
        args=(
            dir_to_imageset_map,
            additional_files_pattern_to_dataset_map,
            imageset_to_dataset_id,
            yaml_datasets_by_title,
        ),
        axis=1,
    )

    return file_list_df


def find_matching_imageset_and_images(
    row: pd.Series,
    dir_to_imageset_map: dict[Path, str],
    additional_files_pattern_to_dataset_map: dict[str, str],
    imageset_to_dataset_id: dict[str, StopIteration],
    yaml_dataset_by_title: dict,
) -> pd.Series:
    file_path: Path = row["file_path"]

    path = file_path.as_posix()

    dataset_id = None
    imageset_title = None
    source_image_label = None
    associated_annotation_method = None
    associated_protocol = None
    bia_type = None
    label = None

    for dir_path in dir_to_imageset_map:
        if path.startswith(dir_path.as_posix()):
            dataset_id = imageset_to_dataset_id.get(dir_to_imageset_map[dir_path], None)
            imageset_title = dir_to_imageset_map[dir_path]
    if dataset_id is None:
        for pattern in additional_files_pattern_to_dataset_map:
            result = parse.parse(pattern, path)
            if result is not None:
                dataset_id = imageset_to_dataset_id.get(
                    additional_files_pattern_to_dataset_map[pattern], None
                )

    if imageset_title and (imageset_title in yaml_dataset_by_title):
        for image in yaml_dataset_by_title[imageset_title].get("assigned_images", []):
            pattern = image.get("file_pattern", None)
            if pattern:
                result = parse.parse(f"data/{pattern}", path)
                if result is not None:
                    label = image["label"]
                    bia_type = "http://bia/Image"
                    source_image_label = image.get("input_image_label", None)
                    associated_annotation_method = image.get(
                        "associated_annotation_title", None
                    )
                    associated_protocol = image.get("associated_protocol_title", None)
                    break
        if not label:
            for annotation_data in yaml_dataset_by_title[imageset_title].get(
                "assigned_annotations", []
            ):
                pattern = annotation_data.get("file_pattern", None)
                if pattern:
                    result = parse.parse(f"data/{pattern}", path)
                    if result is not None:
                        label = annotation_data["label"]
                        bia_type = "http://bia/AnnotationData"
                        source_image_label = annotation_data.get(
                            "input_image_label", None
                        )
                        if is_list_of_dicts(source_image_label):
                            source_image_label = [
                                source_img_dict["label"]
                                for source_img_dict in source_image_label
                            ]
                        associated_annotation_method = annotation_data.get(
                            "associated_annotation_title", None
                        )
                        associated_protocol = annotation_data.get(
                            "associated_protocol_title", None
                        )
                        break

    return pd.Series(
        {
            "file_path": str(file_path),
            "size_in_bytes": int(row["size_in_bytes"]),
            "dataset_ref": dataset_id,
            "type": bia_type,
            "label": label,
            "source_image_label": source_image_label,
            "associated_annotation_method": associated_annotation_method,
            "associated_protocol": associated_protocol,
        }
    )


def split_dataframes_by_dataset(file_df: pd.DataFrame):
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


def is_list_of_dicts(object_from_yaml):
    return (
        isinstance(object_from_yaml, list)
        and len(object_from_yaml) > 0
        and isinstance(object_from_yaml[0], dict)
    )
