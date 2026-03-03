import logging
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq

from ro_crate_ingest.empiar_to_ro_crate.empiar.file_api import get_files
from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.components import (
    assign_specimen_metadata, 
    build_dataset_blocks,
)
from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.image_tracks import (
    identify_tracks,
    validate_tracks,
)

logger = logging.getLogger(__name__)


def _dq_all(obj):
    if isinstance(obj, str):
        return dq(obj)
    elif isinstance(obj, list):
        return [_dq_all(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _dq_all(v) for k, v in obj.items()}
    return obj


def _write_proposal(
    proposal: dict, 
    output_dir_path: Path, 
    accession_id: str
) -> str:

    output_dir_path = output_dir_path or Path(__file__).parents[2] / "generated_proposals"
    output_dir_path.mkdir(parents=True, exist_ok=True)
    output_file_path = output_dir_path / f"{accession_id.lower().replace("-", "_")}.yaml"

    ryaml = YAML()
    ryaml.default_flow_style = False
    ryaml.indent(mapping=2, sequence=4, offset=2)
    ryaml.width = 4096
    # avoid alias references for repeated list objects
    ryaml.representer.ignore_aliases = lambda data: True

    with open(output_file_path, "w") as f:
        ryaml.dump(proposal, f)
    
    return str(output_file_path)


def generate_empiar_proposal(
    proposal_config_path: Path,
    proposal_output_dir_path: Path | None = None, 
    pattern_inference_delimiters: list[str] | None = None
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

    datasets_config: list[dict] = config.get("datasets", [])
    specimen_id_config = config.get("specimens", [])

    tracks = identify_tracks(files, datasets_config, specimen_id_config)

    validation = validate_tracks(tracks, files)
    logger.info(
        f"Tracks: {validation['total_tracks']} total, "
        f"{validation['complete_tracks']} complete. "
        f"Coverage: {validation['coverage']:.1%}. "
        f"Orphaned files: {validation['orphaned_file_count']}."
    )

    specimen_defaults: dict = config.get("specimen_defaults", {})
    specimens = assign_specimen_metadata(tracks, specimen_defaults, datasets_config)

    all_dataset_blocks: list[dict] = []
    for dataset_config in datasets_config:
        logger.info(f"Building dataset block: {dataset_config.get('name')}")
        all_dataset_blocks.append(build_dataset_blocks(tracks, dataset_config, pattern_inference_delimiters))

    proposal = {
        "accession_id": _dq_all(accession_id),
        "paper_doi": _dq_all(config.get("paper_doi")),
        "rembis": {
            "BioSample": _dq_all(config.get("biosamples", [])),
            "SpecimenImagingPreparationProtocol": _dq_all(config.get(
                "specimen_imaging_preparation_protocols", []
            )),
            "Specimen": _dq_all(specimens),
            "ImageAcquisitionProtocol": _dq_all(config.get("image_acquisition_protocols", [])),
            "Protocol": _dq_all(config.get("protocols", [])),
        },
        "datasets": all_dataset_blocks,
    }

    output_file_path = _write_proposal(proposal, proposal_output_dir_path, accession_id)

    logger.info(f"Proposal written to {output_file_path}.")
    return proposal
