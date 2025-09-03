from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import ro_crate_models
import pandas as pd
from pathlib import Path
from ro_crate_ingest.graph_utils import (
    get_dataset_for_filelist,
    get_hasPart_parent_id_from_child,
)
import csv
import logging
from urllib.parse import unquote
from rdflib import Graph

logger = logging.getLogger("__main__." + __name__)


def create_combined_file_dataframe(
    crate_objects_by_id: dict[str, ROCrateModel],
    ro_crate_path: Path,
    crate_graph: Graph,
) -> pd.DataFrame:
    dataset_ro_crate_objects: list[ro_crate_models.Dataset] = []
    file_lists_ro_crate_objects: list[ro_crate_models.FileList] = []
    image_ro_crate_objects: list[ro_crate_models.Image] = []
    annotation_data_ro_crate_objects: list[ro_crate_models.AnnotationData] = []

    for crate_obj in crate_objects_by_id.values():
        if isinstance(crate_obj, ro_crate_models.Dataset):
            dataset_ro_crate_objects.append(crate_obj)
        elif isinstance(crate_obj, ro_crate_models.Image):
            image_ro_crate_objects.append(crate_obj)
        elif isinstance(crate_obj, ro_crate_models.FileList):
            file_lists_ro_crate_objects.append(crate_obj)
        elif isinstance(crate_obj, ro_crate_models.AnnotationData):
            annotation_data_ro_crate_objects.append(crate_obj)

    result_data = image_ro_crate_objects + annotation_data_ro_crate_objects

    size_order = {
        "disk_files": 0,
        "file_list": 0,
        "result_data": 0,
    }

    file_df = ro_crate_files_df(
        ro_crate_path, dataset_ro_crate_objects, size_order, file_lists_ro_crate_objects
    )

    ro_crate_result_data_df = ro_crate_object_df(
        result_data, size_order, crate_graph, ro_crate_path
    )

    file_list_dataframe = file_list_df(
        crate_objects_by_id,
        ro_crate_path,
        file_lists_ro_crate_objects,
        size_order,
        crate_graph,
    )

    dataframes = {
        "disk_files": file_df,
        "file_list": file_list_dataframe,
        "result_data": ro_crate_result_data_df,
    }

    combined_datafame = combine_dataframes(dataframes, size_order)

    return combined_datafame


def combine_dataframes(
    dataframes: dict[str, pd.DataFrame], size_order: dict[str, int]
) -> pd.DataFrame:
    """
    Outer join is performed on largest dataframe to smallest as this is (apparantly) the most efficient memory wise.
    """
    sorted_keys = sorted(size_order, key=size_order.get)
    if size_order[sorted_keys[2]] > 0 and size_order[sorted_keys[1]] > 0:
        df_join_1 = pd.merge(
            dataframes[sorted_keys[2]],
            dataframes[sorted_keys[1]],
            on="path",
            how="outer",
        )
    else:
        return dataframes[sorted_keys[2]]

    if size_order[sorted_keys[0]] > 0:
        df_join_2 = pd.merge(
            df_join_1, dataframes[sorted_keys[0]], on="path", how="outer"
        )
        return df_join_2
    else:
        return df_join_1


def file_list_df(
    crate_objects_by_id: dict[str, ROCrateModel],
    ro_crate_path: Path,
    file_lists_ro_crate_objects: list[ro_crate_models.FileList],
    size_order: dict[str, int],
    crate_graph: Graph,
):
    file_list_file = []
    file_list_df_size = 0
    for file_list in file_lists_ro_crate_objects:
        file_list_columns_map = get_file_list_column_property_map(
            file_list, crate_objects_by_id
        )
        file_list_path = ro_crate_path / unquote(file_list.id)
        dataset_id = get_dataset_for_filelist(
            file_list.id,
            crate_graph,
            ro_crate_path,
        )
        with open(file_list_path, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                normalised_row = {
                    file_list_columns_map.get(key, key): value
                    for key, value in row.items()
                }
                file_list_file.append(
                    (
                        normalised_row["http://bia/filePath"],
                        normalised_row,
                        file_list.id,  # Might be able to remove this column!
                        dataset_id,
                    )
                )
                file_list_df_size += 1

    file_list_dataframe = pd.DataFrame.from_records(
        file_list_file,
        columns=[
            "path",
            "info_from_file_list",
            "file_list_id",
            "flist_list_dataset_id",
        ],
    )
    size_order["file_list"] = file_list_df_size
    return file_list_dataframe


def ro_crate_object_df(
    rd_ro_crate_objects: list[ro_crate_models.Image],
    size_order: dict[str, int],
    crate_graph: Graph,
    ro_crate_path: Path,
):
    rd_file = []

    for result_data in rd_ro_crate_objects:
        rd_dataset = get_hasPart_parent_id_from_child(
            result_data.id, crate_graph, ro_crate_path
        )
        rd_type = (
            ro_crate_models.AnnotationData.model_config["model_type"]
            if isinstance(result_data, ro_crate_models.AnnotationData)
            else ro_crate_models.Image.model_config["model_type"]
        )
        if "Dataset" in result_data.type:
            files = [
                (
                    f.as_posix(),
                    result_data.id,
                    rd_dataset,
                    rd_type,
                )
                for f in Path(result_data.id).rglob("*")
                if f.is_file()
            ]
            rd_file.extend(files)
        else:
            rd_file.append(
                (
                    Path(result_data.id).as_posix(),
                    result_data.id,
                    rd_dataset,
                    rd_type,
                )
            )

    ro_crate_image_df = pd.DataFrame(
        rd_file, columns=["path", "result_data_id", "image_dataset_id", "object_type"]
    )
    size_order["result_data"] = len(ro_crate_image_df)
    return ro_crate_image_df


def ro_crate_files_df(
    ro_crate_path: Path,
    dataset_ro_crate_objects: list[ro_crate_models.Dataset],
    size_order: dict[str, int],
    file_lists_ro_crate_objects: list[ro_crate_models.FileList],
):
    file_list_rel_paths = [unquote(fl.id) for fl in file_lists_ro_crate_objects]
    ro_crate_files = []
    for dataset in dataset_ro_crate_objects:
        path = ro_crate_path / unquote(dataset.id)
        files = [
            (
                f.relative_to(ro_crate_path).as_posix(),
                dataset.id,
                f.stat().st_size,
            )
            for f in path.rglob("*")
            if (
                f.is_file()
                and f.relative_to(ro_crate_path).as_posix() not in file_list_rel_paths
            )
        ]
        ro_crate_files.extend(files)

    file_df = pd.DataFrame(
        ro_crate_files, columns=["path", "disk_dataset_id", "disk_size_in_bytes"]
    )
    size_order["disk_files"] = len(file_df)
    return file_df


def get_file_list_column_property_map(
    file_list: ro_crate_models.FileList, crate_objects_by_id: dict[str, ROCrateModel]
):
    schema_id = file_list.tableSchema.id
    schema: ro_crate_models.TableSchema = crate_objects_by_id[schema_id]

    property_mappings = {}
    for column_ref in schema.column:
        column: ro_crate_models.Column = crate_objects_by_id[column_ref.id]
        if column.propertyUrl:
            property_mappings[column.columnName] = column.propertyUrl

    return property_mappings
