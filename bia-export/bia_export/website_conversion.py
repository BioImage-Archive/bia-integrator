
from pathlib import Path
import json
import logging
from .website_models import (
    Study,
    ExperimentalImagingDataset
)
from glob import glob
from typing import List

logger = logging.getLogger(__name__)

def create_study(
        accession_id: str,
        root_directory: Path
) -> Study:
    if root_directory:
        study_path = root_directory.joinpath(f'studies/{accession_id}.json')

        logger.info(f'Loading study from {study_path}')
        
        with open(study_path, "r") as study_file:
            study_dict = json.load(study_file)
        
        study_dict["experimental_imaging_component"] = convert_experimental_imaging_datasets(accession_id, root_directory)

        study = Study(**study_dict)

        return study


def convert_experimental_imaging_datasets(accession_id: str, root_directory: Path = None) -> List[ExperimentalImagingDataset]:
    datasets = []
    if root_directory:

        eid_directory = root_directory.joinpath(f'experimental_imaging_datasets/{accession_id}/*.json')
        eid_paths = glob(str(eid_directory))

        for eid_path in eid_paths:

            logger.info(f'Loading study from {eid_path}')

            with open(eid_path, "r") as eid_file:
                eid_dict = json.load(eid_file)
            eid = ExperimentalImagingDataset(**eid_dict)
            datasets.append(eid)
    
    return datasets
            
