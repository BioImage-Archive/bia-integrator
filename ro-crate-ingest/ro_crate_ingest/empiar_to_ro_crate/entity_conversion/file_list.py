import pandas as pd
import logging
import parse

from dataclasses import dataclass
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


@dataclass
class PatternMatch:
    file_pattern: str
    dataset_id: str
    object_type: str | None
    yaml_object: dict | None


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

    path_pattern_objects = get_file_patterns_matches_and_objects(
        yaml_file, empiar_api_entry, datasets_map
    )

    file_list_df = expand_dataframe_metadata(path_pattern_objects, file_df)

    dataframes_by_dataset_map = split_dataframe_by_dataset(file_list_df)

    ro_crate_objects: list = [schema]
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
    path_pattern_objects: list[PatternMatch],
    file_df: pd.DataFrame,
):

    file_list_df = file_df.apply(
        expand_row_metadata,
        args=(path_pattern_objects,),
        axis=1,
    )

    return file_list_df


def get_file_patterns_matches_and_objects(
    yaml_file, empiar_api_entry: Entry, datasets_map: dict[str, ro_crate_models.Dataset]
) -> list[PatternMatch]:
    """
    yaml containts the assigned image, annotation & file assocaiation file patterns
    empiar api entry has folder paths

    returns a list of PatternMatch objects, containing:
        file pattern which can be used to match file paths
        dataset id
        (optional) object type,
        (optional) object from yaml
    """

    image_to_dataset_map = []
    annotation_data_to_dataset_map = []
    file_pattern_to_dataset_map = []
    images_set_path_to_dataset_map = []

    imageset_to_path = {
        imageset.name: imageset.directory for imageset in empiar_api_entry.imagesets
    }

    title_to_dataset_id = {
        imageset_title: dataset.id for imageset_title, dataset in datasets_map.items()
    }

    for dataset in yaml_file["datasets"]:
        dataset_id = title_to_dataset_id[dataset["title"]]
        for image in dataset.get("assigned_images", ()):
            image_to_dataset_map.append(
                PatternMatch(
                    f"data/{image["file_pattern"]}",
                    dataset_id,
                    "http://bia/Image",
                    image,
                )
            )
        for annotation in dataset.get("assigned_annotations", ()):
            annotation_data_to_dataset_map.append(
                PatternMatch(
                    f"data/{annotation["file_pattern"]}",
                    dataset_id,
                    "http://bia/AnnotationData",
                    annotation,
                )
            )
        for additional_file in dataset.get("additional_files", ()):
            file_pattern_to_dataset_map.append(
                PatternMatch(
                    f"data/{additional_file["file_pattern"]}",
                    dataset_id,
                    None,
                    additional_file,
                )
            )
        images_set_path_to_dataset_map.append(
            PatternMatch(
                f"{imageset_to_path[dataset["title"]]}{{rest}}",
                dataset_id,
                None,
                None,
            )
        )

    # Order matters for preferential matching: image_sets should be last, and file_patterns should be after images & annotation.
    path_maps = (
        image_to_dataset_map
        + annotation_data_to_dataset_map
        + file_pattern_to_dataset_map
        + images_set_path_to_dataset_map
    )

    return path_maps


def expand_row_metadata(
    row: pd.Series,
    path_maps: list[PatternMatch],
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

    for pattern_match in path_maps:
        if parse.parse(pattern_match.file_pattern, path):
            update_row(
                output_row,
                pattern_match.yaml_object,
                pattern_match.object_type,
                pattern_match.dataset_id,
            )
            break

    return pd.Series(output_row)


def update_row(
    output_row: dict,
    yaml_object: Optional[dict],
    row_type: Optional[str],
    dataset_id: str,
):
    output_row["type"] = row_type
    output_row["dataset_ref"] = dataset_id

    if yaml_object:
        output_row["label"] = yaml_object.get("label", None)
        output_row["associated_annotation_method"] = (
            f"_:{yaml_object["annotation_method_title"]}"
            if yaml_object.get("annotation_method_title", None)
            else None
        )
        output_row["associated_protocol"] = (
            f"_:{yaml_object["protocol_title"]}"
            if yaml_object.get("protocol_title", None)
            else None
        )
        input_images = yaml_object.get("input_image_label", None)
        if isinstance(input_images, list):
            output_row["source_image_label"] = [
                input_image.get("label") for input_image in input_images
            ]
        else:
            output_row["source_image_label"] = input_images


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
    columns_for_schema: list[ro_crate_models.Column],
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
