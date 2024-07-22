import logging
from pathlib import Path
from typing import List, Dict
from .utils import (
    dict_to_uuid,
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
    find_file_lists_in_submission,
    flist_from_flist_fname,
    file_uri,
)
from ..config import settings
from bia_shared_datamodels import bia_data_model

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
                "file_path": str(f.path),
                "size_in_bytes": str(f.size),
            }
            fileref_uuid = dict_to_uuid(
                file_dict, ["accession_id", "file_path", "size_in_bytes"]
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
