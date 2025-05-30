from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import logging

logger = logging.getLogger("__main__." + __name__)


def create_api_specimen_imaging_preparation_protocol(
    crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
) -> list[APIModels.SpecimenImagingPreparationProtocol]:
    ro_crate_sipp = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.SpecimenImagingPreparationProtocol)
    )

    sipp_list = []
    for sipp in ro_crate_sipp:
        sipp_list.append(
            convert_specimen_imaging_preparation_protocol(
                sipp, crate_objects_by_id, study_uuid
            )
        )

    return sipp_list


def convert_specimen_imaging_preparation_protocol(
    ro_crate_sipp: ROCrateModels.SpecimenImagingPreparationProtocol,
    crate_objects_by_id: dict[str, ROCrateModel],
    study_uuid: str,
) -> APIModels.SpecimenImagingPreparationProtocol:

    title = None
    if ro_crate_sipp.title:
        title = ro_crate_sipp.title
    elif ro_crate_sipp.id:
        title = ro_crate_sipp.id

    signal_channel_info_list = []
    for signal_channel_info_reference in ro_crate_sipp.signalChannelInformation:
        signal_channel_info_list.append(
            convert_signal_channel_info(
                crate_objects_by_id[signal_channel_info_reference.id]
            )
        )

    sipp = {
        "uuid": str(
            uuid_creation.create_specimen_imaging_preparation_protocol_uuid(
                ro_crate_sipp.id, study_uuid
            )
        ),
        "title": title,
        "protocol_description": ro_crate_sipp.protocolDescription,
        "version": 0,
        "signal_channel_information": signal_channel_info_list,
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": [],
    }

    return APIModels.SpecimenImagingPreparationProtocol(**sipp)


def convert_signal_channel_info(
    ro_crate_sci: ROCrateModels.SignalChannelInformation,
) -> APIModels.SignalChannelInformation:
    sci = {
        "signal_contrast_mechanism_description": ro_crate_sci.signalContrastMechanismDescription,
        "channel_biological_entity": ro_crate_sci.channelBiologicalEntity,
        "channel_content_description": ro_crate_sci.channelContentDescription,
        "additional_metadata": [],
    }
    return APIModels.SignalChannelInformation(**sci)
