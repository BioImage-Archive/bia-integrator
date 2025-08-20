from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    load_submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion import (
    contributor,
    study,
    affiliation,
    dataset,
    image_acquisition_protocol,
    specimen_imaging_preparation_protocol,
    bio_sample,
    annotation_method,
    image_analysis_method,
    image_correlation_method,
    protocol_from_growth_protocol,
    file_list,
    protocol,
    pagetab_file,
)
from bia_shared_datamodels.uuid_creation import create_study_uuid
import json
from pydantic import BaseModel, Field
from pathlib import Path
import logging
from typing import Optional
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_study_uuid,
)
from ro_crate_ingest.ro_crate_defaults import (
    ROCrateCreativeWork,
    get_default_context,
    write_ro_crate_metadata,
    create_ro_crate_folder,
)

logger = logging.getLogger("__main__." + __name__)


def convert_biostudies_to_ro_crate(accession_id: str, crate_path: Optional[Path]):
    try:
        # Get information from biostudies
        submission = load_submission(accession_id)
    except AssertionError as error:
        logger.error("Failed to retrieve information from BioStudies")
        logging.exception("message")
        return

    ro_crate_dir = create_ro_crate_folder(accession_id, crate_path)

    graph = []

    # Used for the creation of other uuids, not the actual study.
    study_uuid = create_study_uuid(submission.accno)

    roc_iam = image_analysis_method.get_image_analysis_method_by_title(submission)
    graph += roc_iam.values()

    roc_icm = image_correlation_method.get_image_correlation_method_by_title(submission)
    graph += roc_icm.values()

    roc_gp = protocol_from_growth_protocol.get_growth_protocol_by_title(
        submission, study_uuid
    )
    graph += roc_gp.values()

    roc_taxon, roc_bio_sample, bs_association_map = (
        bio_sample.get_taxons_bio_samples_and_association_map(
            submission, roc_gp, accession_id
        )
    )
    graph += roc_bio_sample
    graph += roc_taxon

    roc_sipp = specimen_imaging_preparation_protocol.get_specimen_imaging_prepratation_protocol_by_title(
        submission
    )
    graph += roc_sipp.values()

    roc_annotation_method = annotation_method.get_annotation_method_by_title(submission)
    graph += roc_annotation_method.values()

    roc_iap = image_acquisition_protocol.get_image_acquisition_protocol_by_title(
        submission
    )
    graph += roc_iap.values()

    roc_generic_protocols = protocol.get_protocol_by_title(submission)
    graph += roc_generic_protocols.values()

    roc_datasets = dataset.get_datasets_by_accno(
        submission,
        image_aquisition_protocols=roc_iap,
        specimen_imaging_preparation_protocols=roc_sipp,
        annotation_methods=roc_annotation_method,
        image_analysis_methods=roc_iam,
        image_correlation_method=roc_icm,
        bio_samples_association=bs_association_map,
        protocols=roc_generic_protocols,
    )
    graph += roc_datasets.values()

    roc_file_list_schema_objects = file_list.create_file_list(
        ro_crate_dir, submission, roc_datasets
    )
    graph += roc_file_list_schema_objects

    roc_dataset_and_filelist_objs = (
        pagetab_file.get_dataset_and_filelist_for_pagetab_files(
            ro_crate_dir, submission
        )
    )
    graph += roc_dataset_and_filelist_objs

    roc_affiliation_by_accno = affiliation.get_affiliations_by_accno(submission)
    graph += roc_affiliation_by_accno.values()

    roc_contributors = contributor.get_contributors(
        submission,
        roc_affiliation_by_accno,
    )
    graph += roc_contributors

    roc_study = study.get_study(submission, roc_contributors, roc_datasets.values())
    graph.append(roc_study)

    graph.append(ROCrateCreativeWork())
    context = get_default_context()

    write_ro_crate_metadata(ro_crate_dir, context, graph)
