from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from ro_crate_ingest.graph_utils import get_hasPart_parent_id_from_child
from pathlib import Path
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import csv
import rdflib
import logging

logger = logging.getLogger("__main__." + __name__)


def find_file_lists(
    crate_objects_by_id: dict[str, ROCrateModel],
    ro_crate_path: Path,
    crate_graph: rdflib.Graph,
):
    file_lists = {
        id: obj
        for id, obj in crate_objects_by_id.items()
        if isinstance(obj, ROCrateModels.FileList)
    }

    for id, fl_obj in file_lists.items():
        file_list_dataset_id = get_hasPart_parent_id_from_child(
            id, crate_graph, ro_crate_path
        )
        print(file_list_dataset_id)

        file_list_path = ro_crate_path / id
        fl = []
        with open(file_list_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fl.append(row)
        print(fl)


def validate_file_list_schema(csv_dict: dict, crate_objects_by_id):
    # TODO add actual validation logic
    return True
