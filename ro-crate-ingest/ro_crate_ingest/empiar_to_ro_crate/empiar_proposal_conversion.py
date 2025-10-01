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
    file_list,
    protocol,
)
import logging

logger = logging.getLogger("__main__." + __name__)


def convert_empiar_proposal_to_ro_crate(proposal_path: Path, crate_path: Path | None):

    with open(proposal_path) as f:
        yaml_file = yaml.safe_load(f)
    accession_id = yaml_file["accession_id"]
    empiar_api_entry = load_empiar_entry(accession_id)

    ro_crate_dir = create_ro_crate_folder(accession_id, crate_path)

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

    roc_image_correlation_method_map = (
        image_correlation_method.get_image_correlation_methods_by_title(yaml_file)
    )
    graph += roc_image_correlation_method_map.values()

    roc_image_analysis_methods_map = (
        image_analysis_method.get_image_analysis_methods_by_title(yaml_file)
    )
    graph += roc_image_analysis_methods_map.values()

    roc_protocol = protocol.get_protocols(yaml_file)
    graph += roc_protocol

    roc_dataset_title_map = dataset.get_datasets_by_imageset_title(
        yaml_file=yaml_file,
        empiar_api_entry=empiar_api_entry,
        image_analysis_methods_map=roc_image_analysis_methods_map,
        image_correlation_method_map=roc_image_correlation_method_map,
    )
    graph += roc_dataset_title_map.values()

    roc_file_lists_objects = file_list.create_file_list(
        ro_crate_dir, yaml_file, empiar_api_entry, roc_dataset_title_map
    )
    graph += roc_file_lists_objects

    roc_contributors = contributor.get_contributors(empiar_api_entry)
    graph += roc_contributors

    roc_study = study.get_study(
        accession_id=accession_id,
        empiar_api_entry=empiar_api_entry,
        contributors=roc_contributors,
        datasets=roc_dataset_title_map.values(),
    )
    graph.append(roc_study)

    graph.append(ROCrateCreativeWork())
    context = get_default_context()

    write_ro_crate_metadata(ro_crate_dir, context, graph)
