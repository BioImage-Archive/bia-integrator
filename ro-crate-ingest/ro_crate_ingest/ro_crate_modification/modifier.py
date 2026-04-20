import json
import logging
import yaml

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.core.parser import JSONLDMetadataParser, TSVMetadataParser
from pathlib import Path
from ro_crate_ingest.save_utils import write_modified_file_list

from ro_crate_ingest.ro_crate_modification.enrichment.enricher import apply_enrichment
from ro_crate_ingest.ro_crate_modification.modification_config import ModificationConfig

logger = logging.getLogger(__name__)


_TYPE_ORDER = {
    ro_crate_models.ROCrateCreativeWork: 0,
    ro_crate_models.Study: 1,
    ro_crate_models.Contributor: 2,
    ro_crate_models.Affiliaton: 3,
    ro_crate_models.FileList: 4,
    ro_crate_models.Column: 5,
    ro_crate_models.TableSchema: 6,
    ro_crate_models.Dataset: 7,
    ro_crate_models.Protocol: 8,
    ro_crate_models.ImageAnalysisMethod: 9,
    ro_crate_models.ImageCorrelationMethod: 10,
    ro_crate_models.AnnotationMethod: 11,
    ro_crate_models.Specimen: 12,
    ro_crate_models.CreationProcess: 13,
    ro_crate_models.SpecimenImagingPreparationProtocol: 14,
    ro_crate_models.ImageAcquisitionProtocol: 15,
    ro_crate_models.Taxon: 16,
    ro_crate_models.BioSample: 17,
}


def _sort_graph(entities):
    def sort_key(entity):
        type_order = _TYPE_ORDER.get(type(entity), 99)
        return (type_order, entity.id)
    return sorted(entities, key=sort_key)


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

    ro_crate_metadata_parser = JSONLDMetadataParser(ro_crate_path)
    ro_crate_metadata_parser.parse()
    ro_crate_metadata = ro_crate_metadata_parser.result

    file_list_parser = TSVMetadataParser(ro_crate_metadata)
    file_list_parser.parse()
    file_list = file_list_parser.result

    mod_config = ModificationConfig.model_validate(
        yaml.safe_load(modification_config_path.read_text())
    )

    ro_crate_metadata, file_list = apply_enrichment(ro_crate_metadata, file_list, mod_config)

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
