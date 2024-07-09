import logging
from pathlib import Path
from typing import List, Dict
from .utils import (
    find_sections_recursive,
    get_generic_section_as_list,
    dict_to_uuid,
    get_generic_section_as_dict
)
import bia_ingest_sm.conversion.biosample as biosample_conversion
import bia_ingest_sm.conversion.study as study_conversion
from ..biostudies import (
    Submission,
    attributes_to_dict,
    find_file_lists_in_submission,
    flist_from_flist_fname,
    file_uri,
)
from ..config import settings
from src.bia_models import bia_data_model, semantic_models

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_experimental_imaging_dataset(
    submission: Submission, persist_artefacts=False
) -> List[bia_data_model.ExperimentalImagingDataset]:
    """
    Map biostudies.Submission study components to bia_data_model.ExperimentalImagingDataset
    """
    study_components = find_sections_recursive(
        submission.section, ["Study Component",], []
    )
    analysis_method_dict = get_image_analysis_method(submission)

    file_reference_uuids = get_file_reference_by_study_component(
        submission, persist_artefacts=persist_artefacts
    )

    # TODO: Need to persist this (API finally, but initially to disk)
    biosamples_in_submission = biosample_conversion.get_biosample(submission)

    # Index biosamples by title_id. Makes linking with associations more
    # straight forward.
    # Use for loop instead of dict comprehension to allow biosamples with
    # same title to form list
    biosamples_in_submission_uuid = {}
    for biosample in biosample_conversion.get_biosample(submission, persist_artefacts=persist_artefacts):
        if biosample.title_id in biosamples_in_submission_uuid:
            biosamples_in_submission_uuid[biosample.title_id].append(biosample.uuid)
        else:
            biosamples_in_submission_uuid[biosample.title_id] = [
                biosample.uuid,
            ]

    experimental_imaging_dataset = []
    for section in study_components:
        attr_dict = attributes_to_dict(section.attributes)
        key_mapping = [
            ("biosample", "Biosample", None,),
            ("specimen", "Specimen", None,),
            ("image_acquisition", "Image acquisition", None,),
            ("image_analysis", "Image analysis", None,),
            ("image_correlation", "Image correlation", None,),
        ]
        associations = get_generic_section_as_list(
            section, ["Associations",], key_mapping
        )

        analysis_method_list = []
        biosample_list = []
        image_acquisition_method_list = []
        correlation_method_list = []
        specimen_preparation_method_list = []

        if len(associations) > 0:
            # Image Analysis Method
            analysis_methods_from_associations = [
                a.get("image_analysis") for a in associations
            ]
            for analysis_method in analysis_method_dict.values():
                if (
                    analysis_method.method_description
                    in analysis_methods_from_associations
                ):
                    analysis_method_list.append(analysis_method)

            # Biosample
            biosamples_from_associations = [a.get("biosample") for a in associations]
            for biosample in biosamples_from_associations:
                if biosample in biosamples_in_submission_uuid:
                    biosample_list.extend(biosamples_in_submission_uuid[biosample])

        section_name = attr_dict["Name"]
        study_component_file_references = file_reference_uuids.get(section_name, [])
        model_dict = {
            "title_id": section_name,
            # "description": attr_dict["Description"],
            "submitted_in_study": study_conversion.get_study_uuid(submission),
            "file": study_component_file_references,
            "image": [],
            "specimen_preparation_method": specimen_preparation_method_list,
            "acquisition_method": image_acquisition_method_list,
            "biological_entity": biosample_list,
            "analysis_method": analysis_method_list,
            "correlation_method": correlation_method_list,
            "file_reference_count": len(study_component_file_references),
            "image_count": 0,
            "example_image_uri": [],
        }
        # TODO: Add 'description' to computation of uuid (Maybe accno?)
        model_dict["uuid"] = dict_to_uuid(
            model_dict, ["title_id", "submitted_in_study",]
        )
        experimental_imaging_dataset.append(
            bia_data_model.ExperimentalImagingDataset.model_validate(model_dict)
        )

    if persist_artefacts and experimental_imaging_dataset:
        output_dir = (
            Path(settings.bia_data_dir)
            / "experimental_imaging_datasets"
            / submission.accno
        )
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
            logger.info(f"Created {output_dir}")
        for dataset in experimental_imaging_dataset:
            output_path = output_dir / f"{dataset.uuid}.json"
            output_path.write_text(dataset.model_dump_json(indent=2))
            logger.info(f"Written {output_path}")

    return experimental_imaging_dataset


def get_image_analysis_method(
    submission: Submission,
) -> Dict[str, semantic_models.ImageAnalysisMethod]:

    key_mapping = [
        ("method_description", "Title", None,),
        ("features_analysed", "Image analysis overview", None,),
    ]

    return get_generic_section_as_dict(
        submission,
        ["Image analysis",],
        key_mapping,
        semantic_models.ImageAnalysisMethod,
    )


def get_file_reference_by_study_component(
    submission: Submission, persist_artefacts: bool = False
) -> Dict[str, List[bia_data_model.FileReference]]:
    """
    Return Dict of list of file references in study components.
    """
    file_list_dicts = find_file_lists_in_submission(submission)
    fileref_to_study_components = {}

    if persist_artefacts:
        output_dir = Path(settings.bia_data_dir) / "file_references" / submission.accno
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
            logger.info(f"Created {output_dir}")

    for file_list_dict in file_list_dicts:
        study_component_name = file_list_dict["Name"]
        if study_component_name not in fileref_to_study_components:
            fileref_to_study_components[study_component_name] = []

        fname = file_list_dict["File List"]
        files_in_fl = flist_from_flist_fname(submission.accno, fname)
        for f in files_in_fl:
            file_dict = {
                "accession_id": submission.accno,
                "file_name": str(f.path),
                "size_in_bytes": str(f.size),
            }
            fileref_uuid = dict_to_uuid(
                file_dict, ["accession_id", "file_name", "size_in_bytes"]
            )
            fileref_to_study_components[study_component_name].append(fileref_uuid)
            # TODO - Not storing submission_dataset uuid yet!!!
            if persist_artefacts:
                file_dict["uuid"] = fileref_uuid
                file_dict["uri"] = file_uri(submission.accno, f)
                file_dict["submission_dataset"] = fileref_uuid
                file_dict["format"] = f.type
                file_dict["attribute"] = attributes_to_dict(f.attributes)
                file_reference = bia_data_model.FileReference.model_validate(file_dict)
                output_path = output_dir / f"{fileref_uuid}.json"
                output_path.write_text(file_reference.model_dump_json(indent=2))
                logger.info(f"Written {output_path}")

    return fileref_to_study_components
