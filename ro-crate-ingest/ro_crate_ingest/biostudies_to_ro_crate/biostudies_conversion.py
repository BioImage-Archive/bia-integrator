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
from pathlib import Path
import logging
from typing import Optional
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_study_uuid,
)
from ro_crate_ingest.ro_crate_defaults import (
    get_default_context,
    write_ro_crate_metadata,
    create_ro_crate_folder,
)
from bia_shared_datamodels.ro_crate_models import ROCrateCreativeWork

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
    if not submission.accno:
        raise ValueError("Missing accession id for study: cannot proccess.")
    study_uuid = str(create_study_uuid(submission.accno)[0])

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

    if submission.section.files and len(submission.section.files) > 0:
        # create a default dataset for the files that are part of the pagetab, rather than referenced via filelist
        default_dataset = pagetab_file.create_root_dataset_for_submission(
            submission.section
        )
        graph.append(default_dataset)

        file_list_and_dependencies = pagetab_file.create_file_list_from_pagetab_files(
            submission.section.files, ro_crate_dir, default_dataset.id
        )
        graph += file_list_and_dependencies

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
