from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import logging

logger = logging.getLogger("__main__." + __name__)


def create_api_protocol(
    crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
) -> list[APIModels.Protocol]:
    ro_crate_protocol = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.Protocol)
    )

    protocol_list = []
    for protocol in ro_crate_protocol:
        protocol_list.append(convert_protocol(protocol, study_uuid))

    return protocol_list


def convert_protocol(
    ro_crate_protocol: ROCrateModels.Protocol,
    study_uuid: str,
) -> APIModels.Protocol:

    title = None
    if ro_crate_protocol.title:
        title = ro_crate_protocol.title
    elif ro_crate_protocol.id:
        title = ro_crate_protocol.id

    protocol = {
        "uuid": str(
            uuid_creation.create_protocol_uuid(ro_crate_protocol.id, study_uuid)
        ),
        "title": title,
        "protocol_description": ro_crate_protocol.protocolDescription,
        "version": 0,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": [],
    }

    return APIModels.Protocol(**protocol)
