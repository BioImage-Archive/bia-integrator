from bia_export.website_export.utils import read_api_json_file
from bia_export.website_export.utils import (
    read_all_json,
)
from bia_export.website_export.website_models import (
    BioSample,
    ExperimentallyCapturedImage,
    ImageAcquisition,
    Specimen,
    SpecimenGrowthProtocol,
    SpecimenImagingPreparationProtocol,
)


from bia_shared_datamodels import bia_data_model
from pydantic import BaseModel


from pathlib import Path
from typing import List, Type
import logging

logger = logging.getLogger("__main__." + __name__)


def create_ec_images(
    accession_id: str, root_directory: Path
) -> ExperimentallyCapturedImage:
    eci_map = {}

    if root_directory:

        image_directory = root_directory.joinpath(
            f"experimentally_captured_images/{accession_id}/*.json"
        )
        api_ecis: List[bia_data_model.ExperimentallyCapturedImage] = read_all_json(
            image_directory, bia_data_model.ExperimentallyCapturedImage
        )

        def process_list(
            uuid_list: List[str],
            accession_id: str,
            website_type: Type[BaseModel],
            bia_type: Type[BaseModel],
            path_name: str,
        ):
            obj_list = []
            for uuid in uuid_list:
                path = root_directory.joinpath(
                    f"{path_name}/{accession_id}/{uuid}.json"
                )
                api_object = read_api_json_file(path, bia_type)
                obj_dict = api_object.model_dump() | {"default_open": True}
                obj_list.append(website_type(**obj_dict))
            return obj_list

        for image in api_ecis:

            image_acquisition_list = process_list(
                image.acquisition_process_uuid,
                accession_id,
                ImageAcquisition,
                bia_data_model.ImageAcquisition,
                "image_acquisitions",
            )

            specimen_path = root_directory.joinpath(
                f"specimens/{accession_id}/{image.subject_uuid}.json"
            )
            api_specimen: bia_data_model.Specimen = read_api_json_file(
                specimen_path, bia_data_model.Specimen
            )

            biosample_list = process_list(
                api_specimen.sample_of_uuid,
                accession_id,
                BioSample,
                bia_data_model.BioSample,
                "biosamples",
            )
            sipp_list = process_list(
                api_specimen.imaging_preparation_protocol_uuid,
                accession_id,
                SpecimenImagingPreparationProtocol,
                bia_data_model.SpecimenImagingPreparationProtocol,
                "specimen_imaging_preparation_protocols",
            )
            sgp_list = process_list(
                api_specimen.growth_protocol_uuid,
                accession_id,
                SpecimenGrowthProtocol,
                bia_data_model.SpecimenGrowthProtocol,
                "specimen_growth_protocols",
            )

            specimen_dict = api_specimen.model_dump() | {
                "imaging_preparation_protocol": sipp_list,
                "sample_of": biosample_list,
                "growth_protocol": sgp_list,
            }
            eic_dict = image.model_dump() | {
                "acquisition_process": image_acquisition_list,
                "subject": Specimen(**specimen_dict),
            }

            eci_map[str(image.uuid)] = (
                ExperimentallyCapturedImage(**eic_dict)
            ).model_dump(mode="json")

    return eci_map
