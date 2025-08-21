import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import bia_integrator_api.models as APIModels
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_file_reference_uuid,
)
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_dataset_uuid,
)
import pathlib
from ro_crate_ingest.save_utils import persist, PersistenceMode
from numpy import nan
from ro_crate_ingest.settings import get_settings
from typing import Optional
import logging

logger = logging.getLogger("__main__." + __name__)


def process_and_persist_file_references(
    df: pd.DataFrame,
    study_uuid: str,
    accession_id: str,
    url_prefix: str,
    persistence_mode: PersistenceMode,
    max_workers=None,
):

    image_extensions = accepted_image_extensions(
        get_settings().accepted_bioformats_file
    )

    rows = df.to_dict("records")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        func = partial(
            create_file_reference_and_result_data_row,
            study_uuid=study_uuid,
            accession_id=accession_id,
            file_ref_url_prefix=url_prefix,
            persistence_mode=persistence_mode,
            image_extensions=image_extensions,
        )
        results = list(executor.map(func, rows))

    # Only return the result data that has had an id identified for it (and should therefore be created)
    return pd.DataFrame(results).dropna(subset=["result_data_id"])


def create_file_reference_and_result_data_row(
    row: dict,
    study_uuid: str,
    accession_id: str,
    file_ref_url_prefix: str,
    persistence_mode: PersistenceMode,
    image_extensions: list[str],
) -> APIModels.FileReference:
    """
    Creates & persists file references.
    Return the required information needed to create result data (images, annotationd data).
    """
    import pandas as pd
    from numpy import nan

    size_in_bytes = select_size_in_bytes(row)

    uuid, uuid_attr = create_file_reference_uuid(study_uuid, row["path"], size_in_bytes)

    additional_metadata = [uuid_attr.model_dump()]

    if not pd.isna(row.get("info_from_file_list", nan)):
        additional_metadata.append(
            {
                "provenance": APIModels.Provenance.BIA_INGEST,
                "name": "attributes_from_file_list",
                "value": row["info_from_file_list"],
            }
        )

    dataset_roc_id = select_dataset(row)
    dataset_uuid = str(create_dataset_uuid(study_uuid, dataset_roc_id)[0])

    model_dict = {
        "uuid": str(uuid),
        "submission_dataset_uuid": dataset_uuid,
        "file_path": row["path"],
        "version": 0,
        "size_in_bytes": size_in_bytes,
        "format": get_suffix(row["path"]),
        "uri": get_file_ref_uri(file_ref_url_prefix, accession_id, row["path"]),
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": additional_metadata,
    }

    persist(
        accession_id,
        APIModels.FileReference,
        [APIModels.FileReference(**model_dict)],
        persistence_mode,
    )

    return information_for_result_data_creation(
        row, image_extensions, uuid, dataset_roc_id, dataset_uuid
    )


def information_for_result_data_creation(
    row, image_extensions, uuid, dataset_roc_id, dataset_uuid
) -> Optional[dict]:

    result_data_id, obj_type = select_result_data_id_and_type(row, image_extensions)
    result_data_label_from_filelist = None
    file_list_source_image_id = None
    if result_data_id:
        result_data_label_from_filelist = get_result_data_label_in_filelist(row)
        file_list_source_image_id = get_file_list_source_image_id(row)
    return {
        "path": row["path"],
        "file_ref_uuid": str(uuid),
        "dataset_roc_id": dataset_roc_id,
        "dataset_uuid": dataset_uuid,
        "result_type": obj_type,
        "result_data_id": result_data_id,
        "result_data_label_from_filelist": result_data_label_from_filelist,
        "source_image_id_from_filelist": file_list_source_image_id,
    }


def get_suffix(file_path: str) -> str:
    # TODO: Deal with different forms of 'the same' file types consistently across all ingest modules.
    return pathlib.Path(file_path).suffix


def get_file_ref_uri(file_ref_url_prefix, accession_id, file_path) -> str:
    if file_ref_url_prefix == "empiar":
        accession_no = accession_id.split("-")[1]
        return f"https://ftp.ebi.ac.uk/empiar/world_availability/{accession_no}/data/{file_path}"
    elif file_ref_url_prefix == "biostudies":
        return f"https://www.ebi.ac.uk/biostudies/files/{accession_id}/{file_path}"
    else:
        return "None?"


def select_dataset(row: dict) -> str:
    preference_order = ["image_dataset_id", "flist_list_dataset_id", "disk_dataset_id"]

    for key in preference_order:
        value = row.get(key, nan)
        if not pd.isna(value):
            return value

    raise ValueError(f"No dataset found for file: {row["path"]}")


def select_size_in_bytes(row: dict) -> int:

    disk_size_in_bytes = row.get("disk_size_in_bytes", nan)
    if not pd.isna(disk_size_in_bytes):
        return int(disk_size_in_bytes)

    file_list_info = row.get("info_from_file_list", nan)
    if not pd.isna(file_list_info) and "http://bia/sizeInBytes" in file_list_info:
        return int(file_list_info["http://bia/sizeInBytes"])

    raise ValueError(f"No dataset found for file: {row["path"]}")


def select_result_data_id_and_type(
    row: dict, image_extensions: list[str]
) -> tuple[Optional[str], Optional[str]]:
    """
    Finds the most appropriate string to use as an ID for result data (images or annotation data).
    If not found, this file reference shouldn't be processed
    """
    id = None
    bia_type = None

    if not pd.isna(row.get("image_id", nan)):
        id = row["image_id"]
        bia_type = "http://bia/Image"

    if not pd.isna(row.get("info_from_file_list", nan)):
        file_list_info = row["info_from_file_list"]
        if file_list_info.get("http://schema.org/name", None):
            id = file_list_info["http://schema.org/name"]
        elif file_list_info.get("https://schema.org/name", None):
            id = file_list_info["https://schema.org/name"]

        if file_list_info.get("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", None):
            bia_type = file_list_info["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]
        elif id:
            # Assume something that has been named in a filelist is an image if not specified that it's annotation data
            bia_type = "http://bia/Image"

    if not id:
        standardised_file_extension = get_standardised_extension(row["path"])
        if standardised_file_extension in image_extensions:
            id = row["path"]
            bia_type = "http://bia/Image"
    elif not bia_type:
        standardised_file_extension = get_standardised_extension(row["path"])
        if standardised_file_extension in image_extensions:
            bia_type = "http://bia/Image"

    return id, bia_type


def get_result_data_label_in_filelist(row: dict) -> Optional[str]:
    if not pd.isna(row.get("info_from_file_list", nan)):
        file_list_info = row["info_from_file_list"]
        if file_list_info.get("http://schema.org/name", None):
            return file_list_info["http://schema.org/name"]
        elif file_list_info.get("https://schema.org/name", None):
            return file_list_info["https://schema.org/name"]


def get_standardised_extension(file_path: str) -> str:
    """Return standardized extension for a given file path."""

    ext_map = {
        ".ome.zarr.zip": ".ome.zarr.zip",
        ".zarr.zip": ".zarr.zip",
        ".ome.zarr": ".ome.zarr",
        ".ome.tiff": ".ome.tiff",
        ".ome.tif": ".ome.tiff",
        ".tar.gz": ".tar.gz",
        ".jpeg": ".jpg",
        ".tif": ".tiff",
    }

    ext = pathlib.Path(file_path).suffix.lower()
    if len(ext) > 1 and not ext[0] == ".":
        ext = "." + ext

    if ext in ext_map:
        return ext_map[ext]
    else:
        return ext


def accepted_image_extensions(path: str) -> list[str]:
    file_formats = [s for s in pathlib.Path(path).read_text().split("\n") if len(s) > 0]
    return file_formats


def get_file_list_source_image_id(row: dict) -> Optional[str]:
    info_from_file_list = row.get("info_from_file_list", nan)
    source_image_id = nan
    if not pd.isna(info_from_file_list):
        if "http://bia/sourceImagePath" in info_from_file_list:
            sid: str = info_from_file_list["http://bia/sourceImagePath"]
            if sid.startswith("["):
                source_image_id = [
                    x.strip("'\"\\ ") for x in sid.strip("[]").split(",")
                ]
            elif sid != "":
                source_image_id = [sid]
        elif "http://bia/sourceImageLabel" in info_from_file_list:
            sid = info_from_file_list["http://bia/sourceImageLabel"]
            if sid.startswith("["):
                source_image_id = [
                    x.strip("'\"\\ ") for x in sid.strip("[]").split(",")
                ]
            elif sid != "":
                source_image_id = [sid]

    return source_image_id
