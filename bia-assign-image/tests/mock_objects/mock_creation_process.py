from uuid import uuid4
from copy import deepcopy
from bia_shared_datamodels import bia_data_model

basic_creation_process_dict = {
    "version": 0,
}

def get_creation_process_with_one_file_reference() -> bia_data_model.CreationProcess:
    creation_process_dict = deepcopy(basic_creation_process_dict)

    creation_process_dict["uuid"] = uuid4()

    return bia_data_model.CreationProcess.model_validate(creation_process_dict)