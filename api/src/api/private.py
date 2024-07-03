from ..models import persistence as db_models
from ..models.repository import Repository, OverwriteMode
from ..models import api as api_models
from ..api import exceptions
from .auth import get_current_user
from . import constants
from uuid import UUID
from ..logging import log_info

from typing import List
from fastapi import APIRouter, status, Depends, UploadFile, Response

from ome_types import from_xml

router = APIRouter(
    prefix="/private",
    dependencies=[Depends(get_current_user)],
    tags=[constants.OPENAPI_TAG_PRIVATE],
)


@router.post("/studies", status_code=status.HTTP_201_CREATED)
async def create_study(
    study: db_models.BIAStudy,
    db: Repository = Depends(),
    overwrite_mode: OverwriteMode = OverwriteMode.FAIL,
) -> None:
    log_info(f"Creating study {study.accession_id}")
    db.overwrite_mode = overwrite_mode
    if study.version != 0:
        raise exceptions.InvalidRequestException(
            f"Expecting all newly created objects to have version 0. Got {study.version}"
        )
    await db.persist_doc(study)

    return None


@router.patch("/studies", status_code=status.HTTP_200_OK)
async def update_study(study: db_models.BIAStudy, db: Repository = Depends()) -> None:
    log_info(f"Updating study {study.accession_id}. New version: {study.version}")
    await db.update_doc(study)

    return None


@router.post(
    "/studies/{study_uuid}/refresh_counts", status_code=status.HTTP_201_CREATED
)
async def study_refresh_counts(study_uuid: str, db: Repository = Depends()) -> None:
    """Recalculate and persist counts for other objects pointing to this study."""

    log_info(f"Recalculating reference counts for study {study_uuid}")
    await db.study_refresh_counts(study_uuid)

    return None


@router.post("/images", status_code=status.HTTP_201_CREATED)
async def create_images(
    study_images: List[db_models.BIAImage],
    response: Response,
    db: Repository = Depends(),
    overwrite_mode: OverwriteMode = OverwriteMode.FAIL,
) -> api_models.BulkOperationResponse:
    log_info(
        f"Creating {len(study_images)} images. First image attached to study: {study_images[0].study_uuid if len(study_images) else 'EMPTY LIST'}"
    )
    db.overwrite_mode = overwrite_mode
    # always report errors based on idx not uuid, for cases where we have multiple documents with the same uuid (they will always have different indices)
    create_bulk_response = api_models.BulkOperationResponse(
        items=[
            api_models.BulkOperationItem(status=0, idx_in_request=idx, message="")
            for idx in range(len(study_images))
        ]
    )
    await db.bulk_validate_object_dependency(
        study_images,
        {
            "study_uuid": db_models.BIAStudy,
            "image_acquisitions_uuid": db_models.ImageAcquisition,
        },
        create_bulk_response,
    )

    await db.persist_docs(
        study_images, ref_bulk_operation_response=create_bulk_response
    )

    create_bulk_response.build_item_idx_by_status()

    if create_bulk_response.item_idx_by_status.keys() != {201}:
        response.status_code = 400

    return create_bulk_response


@router.patch("/images/single", status_code=status.HTTP_200_OK)
async def update_image(
    study_image: db_models.BIAImage, db: Repository = Depends()
) -> None:
    """Bulk update not available - update_many only has one filter for the entire update
    @TODO: Find common bulk update usecases and map them to mongo operations"""

    log_info(f"Updating image {study_image.uuid}. New version: {study_image.version}")

    await db.validate_object_dependency(
        study_image,
        {
            "study_uuid": db_models.BIAStudy,
            "image_acquisitions_uuid": db_models.ImageAcquisition,
        },
    )
    await db.update_doc(study_image)

    return None


@router.post("/images/bulk")
async def create_images_bulk() -> None:
    """TODO: Maybe file-based async?"""
    raise Exception("Not implemented")


@router.post(
    "/images/{image_uuid}/representations/single", status_code=status.HTTP_201_CREATED
)
async def create_image_representation(
    image_uuid: str,
    representation: db_models.BIAImageRepresentation,
    db: Repository = Depends(),
) -> None:
    log_info(f"Adding an image representation to image {image_uuid}")
    await db.list_item_push(image_uuid, "representations", representation)

    return None


@router.post("/file_references", status_code=status.HTTP_201_CREATED)
async def create_file_references(
    file_references: List[db_models.FileReference],
    response: Response,
    db: Repository = Depends(),
    overwrite_mode: OverwriteMode = OverwriteMode.FAIL,
) -> api_models.BulkOperationResponse:
    log_info(
        f"Creating {len(file_references)} file references. First file reference attached to study: {file_references[0].study_uuid if len(file_references) else 'EMPTY LIST'}"
    )
    db.overwrite_mode = overwrite_mode
    # always report errors based on idx not uuid, for cases where we have multiple documents with the same uuid (they will always have different indices)
    create_bulk_response = api_models.BulkOperationResponse(
        items=[
            api_models.BulkOperationItem(status=0, idx_in_request=idx, message="")
            for idx in range(len(file_references))
        ]
    )

    await db.bulk_validate_object_dependency(
        docs_to_verify=file_references,
        field_type_map={
            "study_uuid": db_models.BIAStudy,
        },
        ref_bulk_operation_response=create_bulk_response,
    )
    await db.persist_docs(
        file_references, ref_bulk_operation_response=create_bulk_response
    )

    create_bulk_response.build_item_idx_by_status()

    if create_bulk_response.item_idx_by_status.keys() != {201}:
        response.status_code = 400

    return create_bulk_response


@router.patch("/file_references/single", status_code=status.HTTP_200_OK)
async def update_file_reference(
    file_reference: db_models.FileReference, db: Repository = Depends()
) -> None:
    log_info(
        f"Updating file reference {file_reference.uuid}. New version: {file_reference.version}"
    )
    # await db.validate_uuid_type(file_reference.study_uuid, db_models.BIAStudy)
    await db.validate_object_dependency(
        file_reference,
        {
            "study_uuid": db_models.BIAStudy,
        },
    )
    await db.update_doc(file_reference)

    return None


@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection: db_models.BIACollection,
    db: Repository = Depends(),
    overwrite_mode: OverwriteMode = OverwriteMode.FAIL,
) -> None:
    log_info(f"Creating collection {collection.uuid}")
    db.overwrite_mode = overwrite_mode
    for study_uuid in collection.study_uuids:
        await db.find_study_by_uuid(study_uuid)

    if collection.version == 0:
        await db.persist_doc(collection)
    else:
        await db.update_doc(collection)

    return None


@router.post("/image_acquisitions", status_code=status.HTTP_201_CREATED)
async def create_image_acquisition(
    image_acquisition: db_models.ImageAcquisition,
    db: Repository = Depends(),
    overwrite_mode: OverwriteMode = OverwriteMode.FAIL,
) -> None:
    log_info(f"Creating Image Acquisition {image_acquisition.uuid}")
    db.overwrite_mode = overwrite_mode
    # await db.validate_uuid_type(image_acquisition.specimen_uuid, db_models.Specimen)
    await db.validate_object_dependency(
        image_acquisition,
        {
            "specimen_uuid": db_models.Specimen,
        },
    )
    await db.persist_doc(image_acquisition)

    return None


@router.patch("/image_acquisitions", status_code=status.HTTP_200_OK)
async def update_image_acquisition(
    image_acquisition: db_models.ImageAcquisition, db: Repository = Depends()
) -> None:
    log_info(
        f"Updating Image acquisition {image_acquisition.uuid}. New version: {image_acquisition.version}"
    )
    # await db.validate_uuid_type(image_acquisition.specimen_uuid, db_models.Specimen)
    await db.validate_object_dependency(
        image_acquisition,
        {
            "specimen_uuid": db_models.Specimen,
        },
    )
    await db.update_doc(image_acquisition)

    return None


@router.post("/specimens", status_code=status.HTTP_201_CREATED)
async def create_specimen(
    specimen: db_models.Specimen,
    db: Repository = Depends(),
    overwrite_mode: OverwriteMode = OverwriteMode.FAIL,
) -> None:
    log_info(f"Creating specimen {specimen.uuid}")
    db.overwrite_mode = overwrite_mode
    # await db.validate_uuid_type(specimen.biosample_uuid, db_models.Biosample)
    await db.validate_object_dependency(
        specimen,
        {
            "biosample_uuid": db_models.Biosample,
        },
    )
    await db.persist_doc(specimen)

    return None


@router.patch("/specimens", status_code=status.HTTP_200_OK)
async def update_specimen(
    specimen: db_models.Specimen, db: Repository = Depends()
) -> None:
    log_info(f"Updating Specimen {specimen.uuid}. New version: {specimen.version}")
    # await db.validate_uuid_type(specimen.biosample_uuid, db_models.Biosample)
    await db.validate_object_dependency(
        specimen,
        {
            "biosample_uuid": db_models.Biosample,
        },
    )
    await db.update_doc(specimen)

    return None


@router.post("/biosamples", status_code=status.HTTP_201_CREATED)
async def create_biosample(
    biosample: db_models.Biosample,
    db: Repository = Depends(),
    overwrite_mode: OverwriteMode = OverwriteMode.FAIL,
) -> None:
    log_info(f"Creating Biosample {biosample.uuid}")
    db.overwrite_mode = overwrite_mode
    await db.persist_doc(biosample)

    return None


@router.patch("/biosamples", status_code=status.HTTP_200_OK)
async def update_biosample(
    biosample: db_models.Biosample, db: Repository = Depends()
) -> None:
    log_info(f"Updating Biosample {biosample.uuid}. New version: {biosample.version}")
    await db.update_doc(biosample)

    return None


@router.post("/images/{image_uuid}/ome_metadata", status_code=status.HTTP_201_CREATED)
async def set_image_ome_metadata(
    image_uuid: UUID, ome_metadata_file: UploadFile, db: Repository = Depends()
) -> db_models.BIAImageOmeMetadata:
    if not ome_metadata_file.size:
        raise exceptions.InvalidRequestException("File has size 0")

    try:
        ome_metadata = from_xml(ome_metadata_file.file._file, validate=True)
    except Exception as e:
        raise exceptions.InvalidRequestException(str(e))

    bia_image_ome_metadata = await db.upsert_ome_metadata_for_image(
        image_uuid, ome_metadata.model_dump(mode="json", exclude_defaults=True)
    )

    return bia_image_ome_metadata
