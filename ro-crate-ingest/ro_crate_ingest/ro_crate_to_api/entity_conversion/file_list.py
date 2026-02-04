import logging
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from urllib.parse import unquote

import bia_integrator_api.models as APIModels
import numpy as np
import pandas as pd
from bia_shared_datamodels import ro_crate_models
from bia_shared_datamodels.linked_data.ontology_terms import BIA, DUBLINCORE, SCHEMA
from bia_shared_datamodels.linked_data.pydantic_ld import FieldContext, ROCrateModel
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_dataset_uuid,
)
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_file_reference_uuid,
)
from rdflib import RDF, URIRef

from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.bia_ro_crate.file_list import FileList
from ro_crate_ingest.bia_ro_crate.parser.tsv_metadata_parser import TSVMetadataParser
from ro_crate_ingest.save_utils import PersistenceMode, persist

logger = logging.getLogger("__main__." + __name__)


def parse_file_list(
    bia_rocrate_metadata: BIAROCrateMetadata,
) -> FileList:

    # For now, assuming this is TSV
    parser = TSVMetadataParser(bia_rocrate_metadata)
    parser.parse()

    file_list = parser.result

    size_in_bytes = file_list.get_column_id_by_property(str(BIA.sizeInBytes))
    if not size_in_bytes:
        # TODO: add logic to fetch sizes from files
        pass

    # TODO: move this into the per-row logic to not add non-user data to the file reference attributes
    name_column = file_list.get_column_id_by_property(str(SCHEMA.name))
    if not name_column:
        file_path_col_id = file_list.get_column_id_by_property(str(BIA.filePath))
        file_list.add_column(
            ro_crate_models.Column.model_validate(
                {
                    "columnName": str(SCHEMA.name),
                    "propertyUrl": str(SCHEMA.name),
                    "@id": str(SCHEMA.name),
                    "@type": "csvw:Column",
                }
            ),
            file_list.data[file_path_col_id],
        )

    return file_list


def process_and_persist_file_references(
    file_list: FileList,
    roc_metadata: BIAROCrateMetadata,
    study_uuid: str,
    accession_id: str,
    url_prefix: str | None,
    persistence_mode: PersistenceMode,
    max_workers: int,
):
    datasets: dict[str, ro_crate_models.Dataset] = roc_metadata.get_objects_by_type()[
        ro_crate_models.Dataset
    ]
    dataframe_rows = file_list.data.to_dict("records")
    semantic_schema = file_list.schema
    property_lookup = {
        propertyURL: columnId
        for columnId, propertyURL in file_list.get_column_properties().items()
        if propertyURL
    }
    dataset_field_map = get_dataset_field_map()

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        func = partial(
            create_file_reference_and_result_data_row,
            study_uuid=study_uuid,
            accession_id=accession_id,
            file_ref_url_prefix=url_prefix,
            persistence_mode=persistence_mode,
            schema=semantic_schema,
            property_lookup=property_lookup,
            datasets=datasets,
            dataset_field_map=dataset_field_map,
        )
        results = list(executor.map(func, dataframe_rows))

    result_dataframe = pd.DataFrame(results).dropna(subset=[RDF.type])

    # fill_missing_association_columns(result_dataframe)

    return result_dataframe


def create_file_reference_and_result_data_row(
    row: dict,
    study_uuid: str,
    accession_id: str,
    file_ref_url_prefix: str | None,
    persistence_mode: PersistenceMode,
    schema: dict[str, ro_crate_models.Column],
    property_lookup: dict[str, str],
    datasets: dict[str, ro_crate_models.Dataset],
    dataset_field_map: dict[URIRef, str],
):
    import pandas as pd
    from numpy import nan

    semantic_row = {
        URIRef(propertyURL): row[columnID]
        for propertyURL, columnID in property_lookup.items()
    }

    size_in_bytes = semantic_row[BIA.sizeInBytes]
    file_path = semantic_row[BIA.filePath]

    uuid, uuid_attr = create_file_reference_uuid(study_uuid, file_path, size_in_bytes)

    additional_metadata = [uuid_attr.model_dump()]

    additional_metadata.append(
        {
            "provenance": APIModels.Provenance.BIA_INGEST,
            "name": "attributes_from_file_list",
            "value": {
                schema[colID].columnName: colValue for colID, colValue in row.items()
            },
        }
    )

    dataset_roc_id = semantic_row[SCHEMA.isPartOf]
    dataset_uuid = str(create_dataset_uuid(study_uuid, dataset_roc_id)[0])
    file_format = get_suffix(file_path)
    uri = get_file_ref_uri(file_ref_url_prefix, accession_id, file_path)

    model_dict = {
        "uuid": str(uuid),
        "submission_dataset_uuid": dataset_uuid,
        "file_path": file_path,
        "version": 0,
        "size_in_bytes": size_in_bytes,
        "format": file_format,
        "uri": uri,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": additional_metadata,
    }

    persist(
        accession_id,
        APIModels.FileReference,
        [APIModels.FileReference(**model_dict)],
        persistence_mode,
    )

    if pd.isna(semantic_row[SCHEMA.name]) or not semantic_row[SCHEMA.name]:
        semantic_row[SCHEMA.name] = file_path

    fill_missing_association_from_dataset(semantic_row, datasets, dataset_field_map)

    semantic_row[SCHEMA.isPartOf] = dataset_uuid

    semantic_row[DUBLINCORE.identifier] = str(uuid)

    semantic_row[DUBLINCORE.hasFormat] = file_format

    semantic_row[BIA.uri] = uri

    return semantic_row


def get_suffix(file_path: str) -> str:
    # TODO: Deal with different forms of 'the same' file types consistently across all ingest modules.
    return Path(file_path).suffix


def get_file_ref_uri(
    file_ref_url_prefix: str | None, accession_id: str, file_path: str
) -> str:
    if file_ref_url_prefix == "empiar":
        accession_no = accession_id.split("-")[1]
        return f"https://ftp.ebi.ac.uk/empiar/world_availability/{accession_no}/{file_path}"
    elif file_ref_url_prefix == "biostudies":
        return f"https://www.ebi.ac.uk/biostudies/files/{accession_id}/{file_path}"
    else:
        logger.warning("No known url for file reference")
        return "None?"


def fill_missing_association_from_dataset(
    semantic_row: dict,
    datasets: dict[str, ro_crate_models.Dataset],
    dataset_field_map: dict[URIRef, str],
) -> None:
    dataset = datasets[semantic_row[SCHEMA.isPartOf]]

    list_fields = [
        BIA.associatedBiologicalEntity,
        BIA.associatedImagingPreparationProtocol,
        BIA.associatedImageAcquisitionProtocol,
        BIA.associatedAnnotationMethod,
        BIA.associatedProtocol,
        BIA.associatedSourceImage,
    ]

    for field_uri in list_fields:
        if field_uri not in semantic_row:
            semantic_row[field_uri] = [
                reference.id
                for reference in getattr(dataset, dataset_field_map[field_uri], ())
            ]

    unique_fields = [
        BIA.associatedCreationProcess,
        BIA.associatedSubject,
    ]

    for field_uri in unique_fields:
        if field_uri not in semantic_row:
            reference = getattr(dataset, dataset_field_map[field_uri], None)
            semantic_row[field_uri] = reference.id if reference else None


def get_dataset_field_map() -> dict[URIRef, str]:
    field_map = {}
    dataset_context = ro_crate_models.Dataset.generate_field_context()
    for context_term in dataset_context:
        if not context_term.is_reverse:
            field_map[URIRef(context_term.full_uri)] = context_term.field_name
    return field_map


# def fill_missing_association_columns(dataframe: pd.DataFrame) -> None:
#     list_fields = [
#         str(BIA.associatedBiologicalEntity),
#         str(BIA.associatedImagingPreparationProtocol),
#         str(BIA.associatedImageAcquisitionProtocol),
#         str(BIA.associatedAnnotationMethod),
#         str(BIA.associatedProtocol),
#         str(BIA.associatedSourceImage),
#     ]

#     for field in list_fields:
#         if field not in dataframe.columns:
#             dataframe[field] = [[] for _ in range(dataframe.shape[0])]

#     unique_fields = [
#         str(BIA.associatedCreationProcess),
#         str(BIA.associatedSubject),
#     ]

#     for field in unique_fields:
#         if field not in dataframe:
#             dataframe[field] = np.nan
