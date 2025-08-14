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
            file_reference_from_row_dict,
            study_uuid=study_uuid,
            accession_id=accession_id,
            file_ref_url_prefix=url_prefix,
            persistence_mode=persistence_mode,
            image_extensions=image_extensions,
        )
        results = list(executor.map(func, rows))
    return pd.DataFrame(results)


def file_reference_from_row_dict(
    row: dict,
    study_uuid: str,
    accession_id: str,
    file_ref_url_prefix: str,
    persistence_mode: PersistenceMode,
    image_extensions: list[str],
) -> APIModels.FileReference:
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

    image_id = select_image_id(row, image_extensions)
    image_label = None
    if image_id:
        image_label = select_image_label(row)
    file_list_source_image_id = select_file_list_source_image_id(row)

    return {
        "path": row["path"],
        "file_ref_uuid": str(uuid),
        "dataset_roc_id": dataset_roc_id,
        "dataset_uuid": dataset_uuid,
        "image_id": image_id,
        "image_label_from_filelist": image_label,
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


def select_image_id(row: dict, image_extensions: list[str]) -> Optional[str]:
    if not pd.isna(row.get("image_id", nan)):
        return row["image_id"]

    if not pd.isna(row.get("info_from_file_list", nan)):
        file_list_info = row["info_from_file_list"]
        if file_list_info.get("http://schema.org/name", None):
            return file_list_info["http://schema.org/name"]
        elif file_list_info.get("https://schema.org/name", None):
            return file_list_info["https://schema.org/name"]

    standardised_file_extension = get_standardised_extension(row["path"])
    if standardised_file_extension in image_extensions:
        return row["path"]


def select_image_label(row: dict) -> Optional[str]:
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


def select_file_list_source_image_id(row: dict) -> Optional[str]:
    info_from_file_list = row.get("info_from_file_list", nan)
    source_image_id = nan
    if not pd.isna(info_from_file_list):
        if "http://bia/sourceImagePath" in info_from_file_list:
            sid = info_from_file_list["http://bia/sourceImagePath"]
            if sid != "":
                source_image_id = sid
        elif "http://bia/sourceImageName" in info_from_file_list:
            sid = info_from_file_list["http://bia/sourceImageName"]
            if sid != "":
                source_image_id = sid

    return source_image_id
