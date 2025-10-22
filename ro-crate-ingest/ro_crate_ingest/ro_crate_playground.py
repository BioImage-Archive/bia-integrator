from pathlib import Path
from rocrate import rocrate
from bia_shared_datamodels import ro_crate_models

def read_rocrate() ->  rocrate.ROCrate:
    path = Path(__file__).parents[1] / "test"/ "empiar_to_ro_crate" / "output_data" / "EMPIAR-STARFILETEST"
    return rocrate.ROCrate(path)


roc = read_rocrate()

# for x in roc.get_by_type("bia:Dataset"):
#     print(x)

class BIADataset(ro_crate_models.Dataset, rocrate.Dataset):
    pass