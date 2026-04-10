import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
    File,
)
from bia_shared_datamodels import ro_crate_models
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion.file_list import (
    convert_filelist_to_dataframe,
    normalise_headers,
    set_bia_image_type,
    create_ro_crate_filelist_and_schema_objects,
)
from urllib.parse import quote
from pathlib import Path
from ro_crate_ingest.save_utils import write_filelist


logger = logging.getLogger("__main__." + __name__)


def create_root_dataset_for_submission(submission: Submission):
    section_name = "Default template. No Study Components"
    id = f"#{quote(section_name)}"

    # Use more specific section fields, fall back to base fields
    root_attributes = attributes_to_dict(submission.attributes)
    base_section_attributes = attributes_to_dict(submission.section.attributes)

    model_dict = {
        "@id": id,
        "@type": ["Dataset", "bia:Dataset"],
        "name": base_section_attributes.get("title") or root_attributes["title"],
        "description": base_section_attributes.get("description")
        or root_attributes["description"],
        "hasPart": [],
        "associationFileMetadata": None,
    }

    return ro_crate_models.Dataset(**model_dict)


def create_file_list_from_pagetab_files(
    files: list[File], output_ro_crate_path: Path, dataset_id: str
):
    column_by_name_url: dict[str, dict[str, ro_crate_models.Column]] = {}
    schema_list: list[ro_crate_models.TableSchema] = []

    dataframe_filelist = convert_filelist_to_dataframe(files)
    normalise_headers(dataframe_filelist)
    set_bia_image_type(dataframe_filelist)

    # Add dataset ID column to file list dataframe
    column_headers = dataframe_filelist.columns.values.tolist()
    column_headers.insert(3, "dataset")
    dataframe_filelist = dataframe_filelist.reindex(columns=column_headers)
    dataframe_filelist["dataset"] = dataset_id

    filelist_id = "combined_file_list.tsv"
    write_filelist(output_ro_crate_path, filelist_id, dataframe_filelist)

    filelist = create_ro_crate_filelist_and_schema_objects(
        filelist_id=filelist_id,
        column_headers=column_headers,
        column_by_name_url=column_by_name_url,
        schema_list=schema_list,
    )

    column_list = [col for x in column_by_name_url.values() for col in x.values()]

    return column_list + schema_list + [filelist]
