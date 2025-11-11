import logging

from bia_shared_datamodels import ro_crate_models
from typing import Any, Dict, List
from urllib.parse import quote

from ro_crate_ingest.cets_to_ro_crate.entity_conversion.file_list import generate_relative_filelist_path


logger = logging.getLogger("__main__." + __name__)


def get_datasets_from_cets(
    cets_data: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """
    Convert CETS data to RO-Crate Dataset entities.
    Note: convention is to prepend CETS objects with cets_, thus a cets_dataset is a dataset in the CETS sense; 
    otherwise correspondence with BIA RO-Crate entities is assumed. 
    """
    
    datasets = {}

    cets_dataset_name = cets_data.get("name", None)
    if not cets_dataset_name:
        raise ValueError("CETS dataset must have a 'name' field; none found.")

    for region in cets_data.get("regions", []):

        cets_region_name = region.get("name", None)
        if not cets_region_name:
            raise ValueError("CETS region must have a 'name' field; none found.")
        
        id = quote(f"{cets_dataset_name} {cets_region_name}/")

        filelist_id = generate_relative_filelist_path(id)

        model_dict = {
            "@id": id,
            "@type": ["Dataset", "bia:Dataset"],
            "title": cets_region_name,
            "description": "",
            "associatedBiologicalEntity": [],
            "associatedSpecimenImagingPreparationProtocol": [],
            "associatedSpecimen": None,
            "associatedImageAcquisitionProtocol": [],
            "associatedAnnotationMethod": [],
            "associatedImageAnalysisMethod": [],
            "associatedImageCorrelationMethod": [],
            "associatedProtocol": [],
            "hasPart": [{"@id": filelist_id}],
            "associationFileMetadata": {"@id": filelist_id}
        }

        datasets[id] = ro_crate_models.Dataset(**model_dict)
    
    return datasets


def _create_dataset_id(tomograms: List[Dict]) -> str:
    """Create a dataset ID from tomogram paths."""
    first_tomo_path = tomograms[0].get("path", "")
    path_parts = first_tomo_path.split("/")
    
    if "data" in path_parts:
        data_idx = path_parts.index("data")
        if data_idx + 2 < len(path_parts):
            dataset_part = f"{path_parts[data_idx + 1]}/{path_parts[data_idx + 2]}"
            return quote(f"{dataset_part}/")
    
    return quote(f"dataset_{id(tomograms)}/")
