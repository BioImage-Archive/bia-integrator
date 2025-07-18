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
)
import json
from pydantic import BaseModel, Field
from pathlib import Path
import logging
import os
from typing import Optional

logger = logging.getLogger("__main__." + __name__)


class ROCrateCreativeWork(BaseModel):
    id: str = Field(alias="@id", default="ro-crate-metadata.json")
    type: str = Field(alias="@type", default="CreativeWork")
    conformsTo: dict = Field(default={"@id": "https://w3id.org/ro/crate/1.1"})
    about: dict = Field(default={"@id": "./"})


def convert_biostudies_to_ro_crate(accession_id: str, crate_path: Optional[Path]):
    try:
        # Get information from biostudies
        submission = load_submission(accession_id)
    except AssertionError as error:
        logger.error("Failed to retrieve information from BioStudies")
        logging.exception("message")
        return

    graph = []

    roc_iam = image_analysis_method.get_image_analysis_method_by_title(submission)
    graph += roc_iam.values()

    roc_icm = image_correlation_method.get_image_correlation_method_by_title(submission)
    graph += roc_icm.values()

    roc_gp = protocol_from_growth_protocol.get_growth_protocol_by_title(submission)
    graph += roc_gp.values()

    roc_taxon, roc_bio_sample, bs_association_map = (
        bio_sample.get_taxons_bio_samples_and_association_map(submission, roc_gp)
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

    roc_datasets = dataset.get_datasets_by_accno(
        submission,
        image_aquisition_protocols=roc_iap,
        specimen_imaging_preparation_protocols=roc_sipp,
        annotation_methods=roc_annotation_method,
        image_analysis_methods=roc_iam,
        image_correlation_method=roc_icm,
        bio_samples_association=bs_association_map,
    )
    graph += roc_datasets.values()

    roc_file_list_schema_objects = file_list.create_file_list(
        crate_path, submission, roc_datasets
    )
    graph += roc_file_list_schema_objects

    roc_affiliation_by_accno = affiliation.get_affiliations_by_accno(submission)
    graph += roc_affiliation_by_accno.values()

    roc_contributors = contributor.get_contributors(
        submission, roc_affiliation_by_accno
    )
    graph += roc_contributors

    roc_study = study.get_study(submission, roc_contributors, roc_datasets.values())
    graph.append(roc_study)

    graph.append(ROCrateCreativeWork())

    with open(
        Path(__file__).parents[3]
        / "bia-shared-datamodels"
        / "src"
        / "bia_shared_datamodels"
        / "linked_data"
        / "bia_ro_crate_context.json"
    ) as f:
        bia_specific_context = json.loads(f.read())

    bia_ro_crate_context = [
        "https://w3id.org/ro/crate/1.1/context",
        bia_specific_context,
    ]

    logging.info(f"writing to {crate_path}")

    with open(crate_path / "ro-crate-metadata.json", "w") as f:
        f.write(
            json.dumps(
                {
                    "@context": bia_ro_crate_context,
                    "@graph": [
                        json.loads(x.model_dump_json(by_alias=True))
                        for x in reversed(graph)
                    ],
                },
                indent=4,
            )
        )
