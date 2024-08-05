import logging
from pathlib import Path
from typing import List, Dict
from .utils import (
    dict_to_uuid,
    filter_model_dictionary,
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
    find_file_lists_in_submission,
    flist_from_flist_fname,
    file_uri,
)
from .. import biostudies # To make reference to biostudies.File explicit
from ..config import settings
from bia_shared_datamodels import bia_data_model

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_file_reference_by_study_component(
    submission: Submission,
    datasets_in_submission: List[bia_data_model.ExperimentalImagingDataset | bia_data_model.ImageAnnotationDataset], persist_artefacts: bool = False
) -> Dict[str, List[bia_data_model.FileReference]]:
    """
    Return Dict of list of file references in study components.
    """

    # Get list of study component titles to process
    sc_titles_from_datasets_in_submission = { dataset.title_id for dataset in datasets_in_submission }
    file_list_dicts = find_file_lists_in_submission(submission)
    sc_titles_from_file_lists = set([file_list_dict["Name"] for file_list_dict in file_list_dicts])
    study_components_to_process = list(sc_titles_from_datasets_in_submission.intersection(sc_titles_from_file_lists))

    if not study_components_to_process:
        message = f"""
            Intersection of Study component titles from datasets in submission ({sc_titles_from_datasets_in_submission}) and file lists in submission ( {sc_titles_from_file_lists} ) was null - exiting
        """
        logger.warning(message)
        return

    if persist_artefacts:
        output_dir = Path(settings.bia_data_dir) / "file_references" / submission.accno
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
            logger.info(f"Created {output_dir}")

    fileref_to_study_components = {}
    datasets_to_process = { ds.title_id: ds for ds in datasets_in_submission if ds.title_id in study_components_to_process }
    file_lists_to_process = { file_list_dict["Name"]: file_list_dict for file_list_dict in file_list_dicts if file_list_dict["Name"] in study_components_to_process }
    for study_component_name in study_components_to_process:
        dataset = datasets_to_process[study_component_name]
        file_list_dict = file_lists_to_process[study_component_name]
        if study_component_name not in fileref_to_study_components:
            fileref_to_study_components[study_component_name] = []

        fname = file_list_dict["File List"]
        files_in_fl = flist_from_flist_fname(submission.accno, fname)

        #for f in files_in_fl:
        #    file_dict = {
        #        "accession_id": submission.accno,
        #        "file_path": str(f.path),
        #        "size_in_bytes": str(f.size),
        #    }
        #    fileref_uuid = dict_to_uuid(
        #        file_dict, ["accession_id", "file_path", "size_in_bytes"]
        #    )
        #    file_dict["uuid"] = fileref_uuid
        #    file_dict["uri"] = file_uri(submission.accno, f)
        #    file_dict["submission_dataset_uuid"] = dataset_uuid
        #    file_dict["format"] = f.type
        #    file_dict["attribute"] = attributes_to_dict(f.attributes)
        #    file_dict = filter_model_dictionary(file_dict, bia_data_model.FileReference)
        #    file_reference = bia_data_model.FileReference.model_validate(file_dict)
        #    fileref_to_study_components[study_component_name].append(file_reference)
        #    # TODO - Not storing submission_dataset uuid yet!!!
        #    if persist_artefacts:
        #        output_path = output_dir / f"{fileref_uuid}.json"
        #        output_path.write_text(file_reference.model_dump_json(indent=2))
        #        logger.info(f"Written {output_path}")
        file_references = get_file_reference_for_submission_dataset(
            submission.accno, dataset, files_in_fl
        )

        if persist_artefacts:
            for file_reference in file_references:
                output_path = output_dir / f"{file_reference.uuid}.json"
                output_path.write_text(file_reference.model_dump_json(indent=2))
                logger.info(f"Written {output_path}")
        
        fileref_to_study_components[study_component_name].extend(
            file_references
        )

    return fileref_to_study_components


def get_file_reference_for_submission_dataset(
    accession_id: str,
    submission_dataset: [bia_data_model.ExperimentalImagingDataset|bia_data_model.ImageAnnotationDataset],
    files_in_file_list: List[biostudies.File]) -> List[bia_data_model.FileReference]:
    """
    Return list of file references for particular submission dataset
    """

    file_references = []
    for f in files_in_file_list:
        file_dict = {
            "accession_id": accession_id,
            "file_path": str(f.path),
            "size_in_bytes": str(f.size),
        }
        fileref_uuid = dict_to_uuid(
            file_dict, ["accession_id", "file_path", "size_in_bytes"]
        )
        file_dict["uuid"] = fileref_uuid
        file_dict["uri"] = file_uri(accession_id, f)
        file_dict["submission_dataset_uuid"] = submission_dataset.uuid
        file_dict["format"] = f.type
        file_dict["attribute"] = attributes_to_dict(f.attributes)
        file_dict = filter_model_dictionary(file_dict, bia_data_model.FileReference)
        file_reference = bia_data_model.FileReference.model_validate(file_dict)
        file_references.append(file_reference)

    return file_references
