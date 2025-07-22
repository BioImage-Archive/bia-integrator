from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from ro_crate_ingest.graph_utils import get_hasPart_parent_id_from_child
from ro_crate_ingest.ro_crate_to_api.entity_conversion.file_reference import (
    create_api_file_reference,
)
import bia_integrator_api.models as APIModels
from pathlib import Path
from bia_shared_datamodels import semantic_models, ro_crate_models
import csv
import rdflib
import logging
from typing import Optional
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_dataset_uuid,
)


logger = logging.getLogger("__main__." + __name__)


def process_file_lists(
    crate_objects_by_id: dict[str, ROCrateModel],
    ro_crate_path: Path,
    crate_graph: rdflib.Graph,
    study_uuid: str,
) -> tuple[list[APIModels.FileReference], list[str]]:
    file_lists = {
        id: obj
        for id, obj in crate_objects_by_id.items()
        if isinstance(obj, ro_crate_models.FileList)
    }

    file_refs = []
    file_paths = []

    for id, fl_obj in file_lists.items():
        file_list_dataset_ro_crate_id = get_hasPart_parent_id_from_child(
            id, crate_graph, ro_crate_path
        )
        dataset_uuid = str(
            create_dataset_uuid(study_uuid, file_list_dataset_ro_crate_id)[0]
        )

        property_map = get_file_list_column_property_map(fl_obj, crate_objects_by_id)
        filtered_property_map = {k: v for k, v in property_map.items() if v}

        file_list_path = ro_crate_path / id
        with open(file_list_path, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                file_ref, path = create_file_reference_from_row(
                    row,
                    filtered_property_map,
                    dataset_uuid,
                    study_uuid,
                    ro_crate_path,
                )
                file_refs.append(file_ref)
                file_paths.append(path)

    return file_refs, file_paths


def validate_file_list_schema(csv_dict: dict, crate_objects_by_id):
    # TODO add actual validation logic
    return True


def get_file_list_column_property_map(
    file_list: ro_crate_models.FileList, crate_objects_by_id: dict[str, ROCrateModel]
):
    schema_id = file_list.tableSchema.id
    schema: ro_crate_models.TableSchema = crate_objects_by_id[schema_id]

    property_mappings = {}
    for column_ref in schema.column:
        column: ro_crate_models.Column = crate_objects_by_id[column_ref.id]

        property_mappings[column.columnName] = column.propertyUrl

    return property_mappings


def create_file_reference_from_row(
    row: dict[str, str],
    property_map: dict[str, Optional[str]],
    file_list_dataset_id: str,
    study_uuid: str,
    ro_crate_path: Path,
) -> APIModels.FileReference:


    mapped_row = {}

    for key, value in row.items():
        if key in property_map:
            mapped_row[property_map[key]] = value
        else:
            mapped_row[key] = value

    attributes = [
        {
            "provenance": semantic_models.Provenance.bia_ingest,
            "name": "attributes_from_biostudies.File",
            "value": {
                "attributes": row,
            },
        }
    ]

    return (
        create_api_file_reference(
            mapped_row, study_uuid, file_list_dataset_id, ro_crate_path, attributes
        ),
        ro_crate_path / mapped_row["http://bia/filePath"],
    )
