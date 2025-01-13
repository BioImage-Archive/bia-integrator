from fastapi import APIRouter, Depends
from pydantic.alias_generators import to_snake

# ?
import bia_shared_datamodels.bia_data_model as shared_data_models
from api.app import get_db
from api.models.repository import Repository
from api.models.api import Pagination, DatasetStats
from api import constants
from typing import List, Type, Annotated

router = APIRouter(
    prefix="",
    tags=[constants.OPENAPI_TAG_PUBLIC, constants.OPENAPI_TAG_PRIVATE],
)
models_public: List[shared_data_models.DocumentMixin] = [
    shared_data_models.Study,
    shared_data_models.FileReference,
    shared_data_models.ImageRepresentation,
    shared_data_models.Dataset,
    shared_data_models.Specimen,
    shared_data_models.Image,
    shared_data_models.ImageAcquisitionProtocol,
    shared_data_models.SpecimenImagingPreparationProtocol,
    shared_data_models.Protocol,
    shared_data_models.BioSample,
    shared_data_models.CreationProcess,
    shared_data_models.AnnotationData,
    shared_data_models.AnnotationMethod,
]


@router.get("/dataset/{uuid}/stats")
async def getDatasetStats(
    uuid: shared_data_models.UUID, db: Annotated[Repository, Depends(get_db)]
) -> DatasetStats:
    # check it exists and is a dataset
    dataset = await db.get_doc(uuid, shared_data_models.Dataset)

    n_images = await db.aggregate(
        [
            {
                "$match": {
                    "submission_dataset_uuid": uuid,
                    "model": shared_data_models.Image.get_model_metadata().model_dump(),
                }
            },
            {"$count": "n_images"},
        ]
    )
    n_filerefs = await db.aggregate(
        [
            {
                "$match": {
                    "submission_dataset_uuid": uuid,
                    "model": shared_data_models.FileReference.get_model_metadata().model_dump(),
                }
            },
            {"$count": "n_filerefs"},
        ]
    )
    fileref_size_bytes = await db.aggregate(
        [
            {
                "$match": {
                    "submission_dataset_uuid": uuid,
                    "model": shared_data_models.FileReference.get_model_metadata().model_dump(),
                }
            },
            {"$group": {"_id": None, "size_bytes": {"$sum": "$size_in_bytes"}}},
        ]
    )
    file_type_counts = await db.aggregate(
        [
            {
                "$match": {
                    "submission_dataset_uuid": uuid,
                    "model": shared_data_models.FileReference.get_model_metadata().model_dump(),
                }
            },
            {"$group": {"_id": "$format", "count": {"$sum": 1}}},
        ]
    )

    return DatasetStats(
        image_count=n_images[0]["n_images"],
        file_reference_count=n_filerefs[0]["n_filerefs"],
        file_reference_size_bytes=fileref_size_bytes[0]["size_bytes"],
        file_type_counts={agg["_id"]: agg["count"] for agg in file_type_counts},
    )


def make_get_item(t: Type[shared_data_models.DocumentMixin]):
    # variables are function-scoped => add wrapper to bind each value of t
    # https://eev.ee/blog/2011/04/24/gotcha-python-scoping-closures/

    # @TODO: nicer wrapper?
    async def get_item(
        uuid: shared_data_models.UUID, db: Annotated[Repository, Depends(get_db)]
    ) -> t:
        return await db.get_doc(uuid, t)

    return get_item


def make_reverse_link_handler(
    source_attribute: str,
    source_type: Type[shared_data_models.DocumentMixin],
    target_type: Type[shared_data_models.DocumentMixin],
):
    async def get_descendents(
        uuid: shared_data_models.UUID,
        db: Annotated[Repository, Depends(get_db)],
        pagination: Annotated[Pagination, Depends()],
    ) -> List[source_type]:
        # Check target document actually exists (and is typed correctly - esp. important for union-typed links)
        #   see workaround_union_reference_types
        await db.get_doc(uuid, target_type)

        return await db.find_docs_by_link_value(
            link_attribute_in_source=source_attribute,
            link_attribute_value=uuid,
            source_type=source_type,
            pagination=pagination,
        )

    return get_descendents


def router_add_reverse_link(
    router: APIRouter, link_target_type, link_source_type, link_attribute_name
):
    router.add_api_route(
        f"/{to_snake(link_target_type.__name__)}/{{uuid}}/{to_snake(link_source_type.__name__)}",
        response_model=List[link_source_type],
        operation_id=f"get{link_source_type.__name__}Linking{link_target_type.__name__}",
        summary=f"Get {link_source_type.__name__} Linking {link_target_type.__name__}",
        methods=["GET"],
        endpoint=make_reverse_link_handler(
            link_attribute_name, link_source_type, link_target_type
        ),
        description="Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram",
    )


def make_reverse_links(router: APIRouter) -> APIRouter:
    for model in models_public:
        for (
            link_attribute_name,
            link_object_reference,
        ) in model.get_object_reference_fields().items():
            # Just in case we accidentally link to a private model somehow (technically possible)
            #   just raise and defer definining behaviour until we use it
            link_target_options = (
                [link_object_reference.link_dest_type]
                if link_object_reference.link_dest_type
                else link_object_reference.workaround_union_reference_types
            )
            for link_dest_option in link_target_options:
                if link_dest_option in models_public:
                    router_add_reverse_link(
                        router,
                        link_dest_option,
                        model,
                        link_attribute_name,
                    )
                else:
                    raise Exception("TODO: Link from a public model to a nonpublic one")


def make_router() -> APIRouter:
    for t in models_public:
        router.add_api_route(
            f"/{to_snake(t.__name__)}/{{uuid}}",
            response_model=t,
            operation_id=f"get{t.__name__}",
            summary=f"Get {t.__name__}",
            methods=["GET"],
            endpoint=make_get_item(t),
        )

    make_reverse_links(router)

    return router
