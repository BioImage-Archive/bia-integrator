from bia_ro_crate.models.linked_data.pydantic_ld import ROCrateModel
from bia_ro_crate.models.ro_crate_generator_utils import get_all_ro_crate_classes


def initialise_association_map() -> dict[type[ROCrateModel], dict[str, str]]:
    """
    Sets up a dictionary of the form:
    {
        <Ro-crate class>: {}
    }

    for all ro-crate classes. The value dictionaries are expected to be of the form:
    {
        <pagetab reference> : <ro-crate id>
    }

    in order to be re-combined into associations at a later stage.
    """
    ro_crate_classes = get_all_ro_crate_classes()

    association_map = {roc_type: dict() for roc_type in ro_crate_classes.values()}

    return association_map
