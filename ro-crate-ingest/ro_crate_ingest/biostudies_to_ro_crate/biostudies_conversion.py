import logging
from pathlib import Path
from collections import Counter

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    find_section_types_recursive,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    load_submission,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion.rembi_mifa_mapping import (
    utils,
    AnnotationMethodMapper,
    ImageAcquisitionProtocolMapper,
    BioSampleTaxonMapper,
    ImageAnalysisMethodMapper,
    ImageCorrelationMethodMapper,
    ProtocolMapper,
    GrowthProtocolMapper,
    SpecimenImagingPreprationProtocolMapper,
)
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion import (
    affiliation,
    contributor,
    dataset,
    external_reference,
    file_list,
    pagetab_file,
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
    crate_path: Path | None,
    fail_on_unprocessed_sections: bool = False,
):
    try:
        # Get information from biostudies
        submission = load_submission(accession_id)
    except AssertionError:
        logger.error("Failed to retrieve information from BioStudies")
        logging.exception("message")
        return

    # Raise error if there are sections that will not be processed
    section_types_not_processed = [
        f"{section}: {n}" for section, n in get_unprocessed_section_types(submission)
    ]
    if section_types_not_processed:
        unprocessed_str = "\n".join(section_types_not_processed)
        message = f"The following section types cannot be processed:\nsection type: n_occurences\n{unprocessed_str}"
        if fail_on_unprocessed_sections:
            raise ValueError(message)
        else:
            logger.warning(message)

    ro_crate_dir = create_ro_crate_folder(accession_id, crate_path)

    graph = []

    association_map = utils.initialise_association_map()

    graph += ImageAnalysisMethodMapper().get_mapped_objects(submission, association_map)
    graph += ImageCorrelationMethodMapper().get_mapped_objects(
        submission, association_map
    )
    graph += GrowthProtocolMapper().get_mapped_objects(submission, association_map)
    graph += BioSampleTaxonMapper().get_mapped_objects(submission, association_map)
    graph += SpecimenImagingPreprationProtocolMapper().get_mapped_objects(
        submission, association_map
    )
    graph += AnnotationMethodMapper().get_mapped_objects(submission, association_map)

    graph += ImageAcquisitionProtocolMapper().get_mapped_objects(
        submission, association_map
    )
    graph += ProtocolMapper().get_mapped_objects(submission, association_map)

    roc_datasets = dataset.get_datasets_by_accno(submission, association_map)

    (
        column_list,
        schema_list,
        combined_file_list,
    ) = file_list.create_combined_file_list_for_study(
        ro_crate_dir, submission, roc_datasets
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
        default_dataset = pagetab_file.create_root_dataset_for_submission(submission)
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
        roc_external_references,
    )
    graph.append(roc_study)

    graph.append(ROCrateCreativeWork())
    context = get_default_context()

    write_ro_crate_metadata(ro_crate_dir, context, graph)


def get_unprocessed_section_types(submission: Submission) -> list[tuple]:
    """Return count of types of unprocessed sections"""

    convertible_section_types = [
        c.lower()
        for c in [
            "organisation",
            "organization",
            "Annotations",
            "Biosample",
            "author",
            "Study Component",
            "Associations",
            "Imaging Method",
            "Image acquisition",
            "Image analysis",
            "Image correlation",
            "Specimen",
            "Protocol",
            "Study",
            "Organism",
        ]
    ]
    section_types_in_submission = set(find_section_types_recursive(submission.section))
    unprocessed_section_types = [
        section_type
        for section_type in section_types_in_submission
        if section_type not in convertible_section_types
    ]

    non_empty_unprocessed_sections = Counter()
    for section_type in unprocessed_section_types:
        sections = find_sections_recursive(
            submission.section,
            [
                section_type,
            ],
            [],
        )
        for section in sections:
            if not section.is_empty():
                non_empty_unprocessed_sections.update(
                    [
                        section.type,
                    ]
                )

    return non_empty_unprocessed_sections.most_common()
