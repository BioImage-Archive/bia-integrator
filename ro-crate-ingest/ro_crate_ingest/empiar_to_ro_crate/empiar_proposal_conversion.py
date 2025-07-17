from pathlib import Path
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api import load_empiar_entry
import yaml
from ro_crate_ingest.ro_crate_defaults import (
    ROCrateCreativeWork,
    get_default_context,
    write_ro_crate_metadata,
    create_ro_crate_folder,
)
from ro_crate_ingest.empiar_to_ro_crate.entity_conversion import (
    bio_sample,
    annotation_method,
    image_acquisition_protocol,
    specimen_imaging_preparation_protocol,
    image_analysis_method,
    image_correlation_method,
    dataset,
    contributor,
    study,
)
import logging

logger = logging.getLogger("__main__." + __name__)


def convert_empiar_proposal_to_ro_crate(proposal_path: Path, crate_path: Path):

    with open(proposal_path) as f:
        yaml_file = yaml.safe_load(f)
    accession_id = yaml_file["accession_id"]
    empiar_api_entry = load_empiar_entry(accession_id)

    graph = []

    roc_bio_samples, roc_taxon_dict = bio_sample.get_bio_samples_and_taxons(yaml_file)
    graph += roc_bio_samples
    graph += roc_taxon_dict.values()

    roc_image_acquisition_protocol = (
        image_acquisition_protocol.get_image_acquisition_protocols(yaml_file)
    )
    graph += roc_image_acquisition_protocol

    roc_specimen_imaging_preparation_protocol = specimen_imaging_preparation_protocol.get_specimen_imaging_preparation_protocols(
        yaml_file
    )
    graph += roc_specimen_imaging_preparation_protocol

    roc_annotation_method = annotation_method.get_annotation_methods(yaml_file)
    graph += roc_annotation_method

    roc_image_correlation_method = (
        image_correlation_method.get_image_correlation_methods(yaml_file)
    )
    graph += roc_image_correlation_method

    roc_image_correlation_method = image_analysis_method.get_image_analysis_methods(
        yaml_file
    )
    graph += roc_image_correlation_method

    roc_dataset = dataset.get_datasets(yaml_file, empiar_api_entry)
    graph += roc_dataset

    roc_contributors = contributor.get_contributors(empiar_api_entry)
    graph += roc_contributors

    roc_study = study.get_study(
        accession_id=accession_id,
        empiar_api_entry=empiar_api_entry,
        contributors=roc_contributors,
        datasets=roc_dataset,
    )
    graph.append(roc_study)

    graph.append(ROCrateCreativeWork())
    context = get_default_context()

    ro_crate_dir = create_ro_crate_folder(accession_id, crate_path)
    write_ro_crate_metadata(ro_crate_dir, context, graph)
