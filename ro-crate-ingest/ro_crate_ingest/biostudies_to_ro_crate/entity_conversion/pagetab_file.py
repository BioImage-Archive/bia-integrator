import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
    File,
)
from bia_shared_datamodels import ro_crate_models
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion.file_list import (
    convert_filelist_to_dataframe,
    normalise_headers,
    generate_relative_filelist_path,
    create_ro_crate_filelist_and_schema_objects,
)
from urllib.parse import quote
from pathlib import Path
from ro_crate_ingest.save_utils import write_filelist


logger = logging.getLogger("__main__." + __name__)


def create_root_dataset_for_submission(root_section: Section):
    section_name = "Default template. No Study Components"
    id = f"{quote(section_name)}/"

    filelist_id_ref = {"@id": generate_relative_filelist_path(id, "filelist.tsv")}
    root_attributes = attributes_to_dict(root_section.attributes)

    model_dict = {
        "@id": id,
        "@type": ["Dataset", "bia:Dataset"],
        "name": root_attributes["title"],
        "description": root_attributes["description"],
        "hasPart": [filelist_id_ref],
        "associationFileMetadata": filelist_id_ref,
    }

    return ro_crate_models.Dataset(**model_dict)


def create_file_list_from_pagetab_files(
    files: list[File], output_ro_crate_path: Path, dataset_id: str
):

    column_by_name_url: dict[str, dict[str, ro_crate_models.Column]] = {}
    schema_list: list[ro_crate_models.TableSchema] = []

    dataframe_filelist = convert_filelist_to_dataframe(files)
    normalise_headers(dataframe_filelist)

    filelist_id = generate_relative_filelist_path(dataset_id, "filelist.tsv")
    write_filelist(output_ro_crate_path, filelist_id, dataframe_filelist)

    filelist = create_ro_crate_filelist_and_schema_objects(
        filelist_id=filelist_id,
        column_headers=dataframe_filelist.columns.values.tolist(),
        column_by_name_url=column_by_name_url,
        schema_list=schema_list,
    )

    column_list = [col for x in column_by_name_url.values() for col in x.values()]

    return column_list + schema_list + [filelist]
