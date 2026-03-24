import logging
from pathlib import Path
from typing import Optional

from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_study_uuid,
)
from bia_shared_datamodels.ro_crate_models import ROCrateCreativeWork

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    load_submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion import (
    affiliation,
    annotation_method,
    bio_sample,
    contributor,
    dataset,
    external_reference,
    file_list,
    image_acquisition_protocol,
    image_analysis_method,
    image_correlation_method,
    pagetab_file,
    protocol,
    protocol_from_growth_protocol,
    specimen_imaging_preparation_protocol,
    study,
)
from ro_crate_ingest.ro_crate_defaults import (
    create_ro_crate_folder,
    get_default_context,
    write_ro_crate_metadata,
)

logger = logging.getLogger("__main__." + __name__)


def convert_biostudies_to_ro_crate(
    accession_id: str,
    crate_path: Optional[Path],
):
    try:
        # Get information from biostudies
        submission = load_submission(accession_id)
    except AssertionError:
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

    column_list, schema_list, combined_file_list = (
        file_list.create_combined_file_list_for_study(
            ro_crate_dir, submission, roc_datasets
        )
    )
    if roc_datasets:
        roc_file_list_schema_objects = (
            column_list + schema_list + [combined_file_list]
            if combined_file_list
            else list(schema_list) + list(column_list)
        )

        graph += roc_datasets.values()
        graph += roc_file_list_schema_objects

    # TODO - Assume in this case only one filelist is present - no need to combine. However, add dataset_id column?
    if submission.section.files and len(submission.section.files) > 0:
        # create a default dataset for the files that are part of the pagetab, rather than referenced via filelist
        default_dataset = pagetab_file.create_root_dataset_for_submission(
            submission
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

    roc_external_references = external_reference.get_external_references(submission)
    graph += roc_external_references

    roc_study = study.get_study(
        submission,
        roc_contributors,
        roc_datasets.values(),
        combined_file_list,
        roc_external_references
    )
    graph.append(roc_study)

    graph.append(ROCrateCreativeWork())
    context = get_default_context()

    write_ro_crate_metadata(ro_crate_dir, context, graph)
