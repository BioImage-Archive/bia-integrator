import json
import logging
import yaml

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.core.parser.ro_crate_parser import ROCrateParser
from pathlib import Path
from ro_crate_ingest.save_utils import write_modified_file_list

from ro_crate_ingest.ro_crate_modification.enrichment.enricher import apply_enrichment
from ro_crate_ingest.ro_crate_modification.enrichment.utils import (
    ASSOCIATED_SOURCE_IMAGE_PROPERTY,
)
from ro_crate_ingest.ro_crate_modification.modification_config import ModificationConfig

logger = logging.getLogger(__name__)


_TYPE_ORDER = {
    ro_crate_models.ROCrateCreativeWork: 0,
    ro_crate_models.Study: 1,
    ro_crate_models.Contributor: 2,
    ro_crate_models.Affiliaton: 3,
    ro_crate_models.Publication: 4,
    ro_crate_models.FileList: 5,
    ro_crate_models.Column: 6,
    ro_crate_models.TableSchema: 7,
    ro_crate_models.Dataset: 8,
    ro_crate_models.Protocol: 9,
    ro_crate_models.ImageAnalysisMethod: 10,
    ro_crate_models.ImageCorrelationMethod: 11,
    ro_crate_models.AnnotationMethod: 12,
    ro_crate_models.Specimen: 13,
    ro_crate_models.CreationProcess: 14,
    ro_crate_models.SpecimenImagingPreparationProtocol: 15,
    ro_crate_models.ImageAcquisitionProtocol: 16,
    ro_crate_models.Taxon: 17,
    ro_crate_models.BioSample: 18,
}


def _sort_graph(entities):
    def sort_key(entity):
        type_order = _TYPE_ORDER.get(type(entity), 99)
        return (type_order, entity.id)
    return sorted(entities, key=sort_key)


def _normalize_legacy_source_image_column(ro_crate_metadata, file_list) -> None:
    """
    If the parsed minimal RO-Crate still carries the old file-list column
    name/property ('source_image_label' / http://bia/sourceImageLabel), retarget
    that existing column to the newer associated_source_image shape instead of
    creating a duplicate column.
    """
    try:
        id_to_name = file_list.get_column_names()
    except Exception:
        return

    legacy_col_ids = [
        col_id for col_id, name in id_to_name.items() if name == "source_image_label"
    ]
    for col_id in legacy_col_ids:
        column = ro_crate_metadata.get_object(col_id)
        if column is None:
            continue
        column.columnName = "associated_source_image"
        column.propertyUrl = ASSOCIATED_SOURCE_IMAGE_PROPERTY


def apply_modifications(
    ro_crate_path: Path, 
    modification_config_path: Path
):
    """
    Modify the ro-crate — metadata and/or file list — at the given path, 
    with the given modifications.
    """
    with open(ro_crate_path / "ro-crate-metadata.json") as f:
        original_crate = json.load(f)
    original_context = original_crate["@context"]

    ro_crate_parser = ROCrateParser(ro_crate_path)
    ro_crate_parser.parse()
    parsed_submission_metadata = ro_crate_parser.result

    ro_crate_metadata = parsed_submission_metadata.metadata
    file_list = parsed_submission_metadata.file_list

    mod_config = ModificationConfig.model_validate(
        yaml.safe_load(modification_config_path.read_text())
    )

    ro_crate_metadata, file_list = apply_enrichment(ro_crate_metadata, file_list, mod_config)
    _normalize_legacy_source_image_column(ro_crate_metadata, file_list)

    graph_objects = [
        json.loads(entity.model_dump_json(by_alias=True))
        for entity in _sort_graph(ro_crate_metadata.get_objects())
    ]

    crate_path = ro_crate_metadata.get_base_path()
    output_path = crate_path / "modified"
    output_path.mkdir(exist_ok=True)
    with open(output_path / "ro-crate-metadata.json", "w") as f:
        json.dump({"@context": original_context, "@graph": graph_objects}, f, indent=4)

    write_modified_file_list(output_path, file_list)
