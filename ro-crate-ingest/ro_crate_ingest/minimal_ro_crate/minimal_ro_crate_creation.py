import logging
from pathlib import Path

from bia_ro_crate.models.ro_crate_models import ROCrateCreativeWork
from ro_crate_ingest.biostudies_to_ro_crate.biostudies_conversion import (
    convert_biostudies_to_ro_crate,
)
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api import load_empiar_entry
from ro_crate_ingest.empiar_to_ro_crate.entity_conversion import (
    dataset,
    contributor,
    study,
    file_list,
)
from ro_crate_ingest.ro_crate_defaults import (
    create_ro_crate_folder,
    get_default_context,
    write_ro_crate_metadata,
)

logger = logging.getLogger(__name__)


def make_minimal_ro_crate(accession_id: str, crate_path: Path | None = None):
    if accession_id.startswith(("S-BIAD", "S-BSST")):
        convert_biostudies_to_ro_crate(accession_id, crate_path)
        return
    elif accession_id.startswith("EMPIAR"):
        empiar_api_entry = load_empiar_entry(accession_id)
    else:
        logger.error("Accession id must start with S-BIAD, S-BSST, or EMPIAR")
        return

    ro_crate_dir = create_ro_crate_folder(accession_id, crate_path)

    graph = []

    roc_dataset_title_map = dataset.get_datasets_by_imageset_title(
        empiar_api_entry=empiar_api_entry,
    )
    graph += roc_dataset_title_map.values()

    roc_file_lists_objects = file_list.create_file_list(
        ro_crate_dir, empiar_api_entry, roc_dataset_title_map, accession_id=accession_id
    )
    graph += roc_file_lists_objects

    roc_contributors = contributor.get_contributors(empiar_api_entry)
    graph += roc_contributors

    roc_study = study.get_study(
        accession_id=accession_id,
        empiar_api_entry=empiar_api_entry,
        contributors=roc_contributors,
        datasets=roc_dataset_title_map.values(),
        publications=[],
    )
    graph.append(roc_study)

    graph.append(ROCrateCreativeWork())
    context = get_default_context()

    write_ro_crate_metadata(ro_crate_dir, context, graph)
