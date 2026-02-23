import logging
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq

from ro_crate_ingest.empiar_to_ro_crate.empiar.file_api import get_files
from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.components import (
    build_dataset_blocks,
)
from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.image_tracks import (
    assign_specimen_metadata,
    identify_tracks,
    validate_tracks,
)

logger = logging.getLogger(__name__)


def dq_all(obj):
    if isinstance(obj, str):
        return dq(obj)
    elif isinstance(obj, list):
        return [dq_all(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: dq_all(v) for k, v in obj.items()}
    return obj


def _write_proposal(proposal: dict, output_path: Path) -> None:
    ryaml = YAML()
    ryaml.default_flow_style = False
    ryaml.indent(mapping=2, sequence=4, offset=2)
    ryaml.width = 4096
    # avoid alias references for repeated list objects
    ryaml.representer.ignore_aliases = lambda data: True

    with open(output_path, "w") as f:
        ryaml.dump(proposal, f)


def generate_empiar_proposal(
    proposal_config_path: Path,
    proposal_output_path: Path | None = None,
) -> dict:
    """
    Generate a full EMPIAR proposal YAML from a minimal pre-proposal config,
    located at proposal_config_path.

    Writes proposal to file at proposal_output_path.
    """
    with open(proposal_config_path) as f:
        config = YAML().load(f)

    accession_id: str = config["accession_id"]
    files = get_files(accession_id)
    logger.info(f"Loaded {len(files)} files for {accession_id}.")

    global_defaults: dict = config.get("defaults", {})
    datasets_config: list[dict] = config.get("datasets", [])

    tracks = identify_tracks(files, datasets_config)

    validation = validate_tracks(tracks, files)
    logger.info(
        f"Tracks: {validation['total_tracks']} total, "
        f"{validation['complete_tracks']} complete. "
        f"Coverage: {validation['coverage']:.1%}. "
        f"Orphaned files: {validation['orphaned_file_count']}."
    )

    specimens = assign_specimen_metadata(tracks, global_defaults, datasets_config)

    all_dataset_blocks: list[dict] = []
    for dataset_config in datasets_config:
        logger.info(f"Building dataset block: {dataset_config.get('name')}")
        all_dataset_blocks.extend(build_dataset_blocks(tracks, dataset_config))

    proposal = {
        "accession_id": dq_all(accession_id),
        "paper_doi": dq_all(config.get("paper_doi")),
        "rembis": {
            "BioSample": dq_all(config.get("biosamples", [])),
            "SpecimenImagingPreparationProtocol": dq_all(config.get(
                "specimen_imaging_preparation_protocols", []
            )),
            "Specimen": dq_all(specimens),
            "ImageAcquisitionProtocol": dq_all(config.get("image_acquisition_protocols", [])),
            "Protocol": dq_all(config.get("protocols", [])),
        },
        "datasets": all_dataset_blocks,
    }

    output_path = proposal_output_path or Path(
        f"local-data/{accession_id}_proposal.yaml"
    )
    _write_proposal(proposal, output_path)

    logger.info(f"Proposal written to {output_path}.")
    return proposal
