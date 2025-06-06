from bia_assign_image.utils import get_value_from_attribute_list
from pydantic import BaseModel, Field
from typing import Optional
import logging
from bia_assign_image.api_client import store_object_in_api_idempotent
from bia_assign_image.object_creation import specimen, creation_process, image
from bia_integrator_api.api import PrivateApi
from bia_integrator_api import exceptions, models
from bia_shared_datamodels import uuid_creation

logger = logging.getLogger("__main__." + __name__)


class ImageDependencies(BaseModel):
    creation_process_uuid: Optional[str] = Field(None)
    specimen_uuid: Optional[str] = Field(None)
    dataset_uuid: Optional[str] = Field(None)
    original_file_reference_uuid: list[str] = Field(default_factory=list)

    image_acquisition_protocol_uuid: list[str] = Field(default_factory=list)
    specimen_imaging_preparation_protocol_uuid: list[str] = Field(default_factory=list)
    annotation_method_uuid: list[str] = Field(default_factory=list)
    bio_sample_uuid: list[str] = Field(default_factory=list)
    input_image_uuid: list[str] = Field(default_factory=list)
    protocol_uuid: list[str] = Field(default_factory=list)

    def has_no_downstream_dependencies(self) -> bool:
        return not any(
            [
                self.creation_process_uuid,
                self.specimen_uuid,
                len(self.image_acquisition_protocol_uuid) > 0,
                len(self.specimen_imaging_preparation_protocol_uuid) > 0,
                len(self.annotation_method_uuid) > 0,
                len(self.bio_sample_uuid) > 0,
                len(self.input_image_uuid) > 0,
            ]
        )

    def has_typical_rembi_image_leaf_objects(self) -> bool:
        "Check if the 'end' dependencies are present for a typical REMBI image. I.e. Acquisition, Specimen Preparation and BioSample."
        return all(
            [
                len(self.image_acquisition_protocol_uuid) > 0,
                len(self.specimen_imaging_preparation_protocol_uuid) > 0,
                len(self.bio_sample_uuid) > 0,
            ]
        )

    def has_typical_annotation_image_leaf_objects(self) -> bool:
        "Check if the 'end' dependencies are present for a typical annotation image. I.e. Annotation method and Image Input."
        return all(
            [
                len(self.annotation_method_uuid) > 0,
                len(self.input_image_uuid) > 0,
            ]
        )

    def has_dependencies_for_creation_process_creation(self) -> bool:
        if (
            not not self.has_typical_annotation_image_leaf_objects
            and not self.has_typical_rembi_image_leaf_objects
        ):
            return False

        if self.has_typical_rembi_image_leaf_objects():
            if self.specimen_uuid:
                return True
            else:
                False

        return True

    def has_dependencies_for_image_creation(self) -> bool:
        cases_to_test = [
            self.dataset_uuid,
            self.creation_process_uuid,
            len(self.original_file_reference_uuid) > 0,
        ]
        if self.has_typical_rembi_image_leaf_objects():
            cases_to_test.append(self.specimen_uuid)

        return all(cases_to_test)


def find_exisiting_image_dependencies(
    file_references: models.FileReference, api_client: PrivateApi
):
    file_ref_uuids = [f.uuid for f in file_references]
    dataset_uuids = [f.submission_dataset_uuid for f in file_references]
    assert len(set(dataset_uuids)) == 1
    submission_dataset_uuid = dataset_uuids[0]
    dataset: models.Dataset = api_client.get_dataset(submission_dataset_uuid)

    image_acquisition_protocol_uuid = get_value_from_attribute_list(
        dataset.additional_metadata, "image_acquisition_protocol_uuid"
    )
    specimen_imaging_preparation_protocol_uuid = get_value_from_attribute_list(
        dataset.additional_metadata, "specimen_imaging_preparation_protocol_uuid"
    )
    bio_sample_uuid = get_value_from_attribute_list(
        dataset.additional_metadata, "bio_sample_uuid"
    )
    annotation_method_uuid = get_value_from_attribute_list(
        dataset.additional_metadata, "annotation_method_uuid"
    )

    # TODO: check what ingest stores for protocol uuid as we do not want to use growth protocols here.
    protocol_uuid = []

    input_image_uuid = find_input_image_dependencies(
        file_references, api_client, study_uuid=dataset.submitted_in_study_uuid
    )

    return ImageDependencies(
        dataset_uuid=submission_dataset_uuid,
        original_file_reference_uuid=file_ref_uuids,
        image_acquisition_protocol_uuid=image_acquisition_protocol_uuid,
        specimen_imaging_preparation_protocol_uuid=specimen_imaging_preparation_protocol_uuid,
        bio_sample_uuid=bio_sample_uuid,
        annotation_method_uuid=annotation_method_uuid,
        input_image_uuid=input_image_uuid,
        protocol_uuid=protocol_uuid,
    )


def find_input_image_dependencies(
    file_references: models.FileReference, api_client: PrivateApi, study_uuid: str
):
    input_image_uuid_list = []

    input_file_ref_uuid_list = []
    for file_ref in file_references:
        # TODO: logic to find something about the source image path & then work out the input image uuid from there?
        # Or add it to ingest logic
        input_file_ref_uuid_list.extend(
            get_value_from_attribute_list(
                file_ref.additional_metadata, "source_image_uuid"
            )
        )

    if len(input_file_ref_uuid_list) > 0:
        input_file_ref_uuid_list = list(set(input_file_ref_uuid_list))
        input_image_unique_str = image.create_image_uuid_unique_string(
            input_file_ref_uuid_list
        )
        input_image_uuid = uuid_creation.create_image_uuid(
            study_uuid, input_image_unique_str
        )
        try:
            input_image = api_client.get_image(str(input_image_uuid))
        except exceptions.NotFoundException:
            raise RuntimeError(
                f"Could not find expected dependency Image {input_image_uuid} that is expected to have been created from file references: {input_file_ref_uuid_list}"
            )
        input_image_uuid_list.append(input_image.uuid)

    return input_image_uuid_list


def create_missing_dependencies(
    study_uuid: str,
    image_uuid: str,
    existing_dependencies: ImageDependencies,
    api_client,
    dryrun: bool,
) -> ImageDependencies:

    missing_dependencies = {
        "specimen": None,
        "creation_process": None,
    }

    if existing_dependencies.has_typical_rembi_image_leaf_objects():
        bia_specimen = specimen.get_specimen(
            study_uuid,
            image_uuid,
            existing_dependencies.specimen_imaging_preparation_protocol_uuid,
            existing_dependencies.bio_sample_uuid,
        )
        missing_dependencies["specimen"] = bia_specimen

        if dryrun:
            logger.info(
                f"Dryrun: Created specimen(s) {bia_specimen}, but not persisting."
            )
        else:
            store_object_in_api_idempotent(api_client, bia_specimen)

        existing_dependencies.specimen_uuid = bia_specimen.uuid

    if not existing_dependencies.has_dependencies_for_creation_process_creation():
        raise ValueError(
            f"Missing dependencies for CreationProcess creation. Found: {existing_dependencies}"
        )

    bia_creation_process = creation_process.get_creation_process(
        study_uuid,
        image_uuid,
        existing_dependencies.specimen_uuid,
        existing_dependencies.image_acquisition_protocol_uuid,
        existing_dependencies.input_image_uuid,
        existing_dependencies.annotation_method_uuid,
        existing_dependencies.protocol_uuid,
    )
    missing_dependencies

    if dryrun:
        logger.info(
            f"Dryrun: Created creation process(es) {bia_creation_process}, but not persisting."
        )
    else:
        store_object_in_api_idempotent(api_client, bia_creation_process)

    existing_dependencies.creation_process_uuid = bia_creation_process.uuid

    return existing_dependencies
