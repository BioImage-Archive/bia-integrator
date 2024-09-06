from fastapi import APIRouter, Depends
from pydantic.alias_generators import to_snake

# ?
import bia_shared_datamodels.bia_data_model as shared_data_models
from api.models.repository import Repository, get_db
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
    shared_data_models.ExperimentalImagingDataset,
    shared_data_models.Specimen,
    shared_data_models.ExperimentallyCapturedImage,
    shared_data_models.ImageAcquisition,
    shared_data_models.SpecimenImagingPreparationProtocol,
    shared_data_models.SpecimenGrowthProtocol,
    shared_data_models.BioSample,
    shared_data_models.ImageAnnotationDataset,
    shared_data_models.AnnotationFileReference,
    shared_data_models.DerivedImage,
    shared_data_models.AnnotationMethod,
]


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
        uuid: shared_data_models.UUID, db: Annotated[Repository, Depends(get_db)]
    ) -> List[source_type]:
        # Check target document actually exists (and is typed correctly - esp. important for union-typed links)
        #   see workaround_union_reference_types
        await db.get_doc(uuid, target_type)

        return await db.get_docs(
            # !!!!
            # source_attribute has list values sometimes (for models that reference a list of other objects)
            #   mongo queries just so happen have the semantics we want
            # a.i. list_attribute: some_val means "any value in list_attribute is equal to some_val"
            doc_filter={source_attribute: uuid},
            doc_type=source_type,
        )

    return get_descendents


def router_add_reverse_link(
    router: APIRouter, link_target_type, link_source_type, link_attribute_name
):
    router.add_api_route(
        f"/{to_snake(link_target_type.__name__)}/{{uuid}}/{to_snake(link_source_type.__name__)}",
        response_model=List[link_source_type],
        operation_id=f"get{link_source_type.__name__}In{link_target_type.__name__}",
        summary=f"Get {link_source_type.__name__} In {link_target_type.__name__}",
        methods=["GET"],
        endpoint=make_reverse_link_handler(
            link_attribute_name, link_source_type, link_target_type
        ),
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

    from bia_shared_datamodels.bia_data_model import Study

    @router.get("/study")
    async def getStudies(db: Annotated[Repository, Depends(get_db)]) -> List[Study]:
        """
        @TODO: Filters?
        """
        return await db.get_docs(
            doc_filter={"model": {"type_name": "Study"}}, doc_type=Study
        )

    return router


@router.get("/placeholder")
def example_custom_handler():
    pass
