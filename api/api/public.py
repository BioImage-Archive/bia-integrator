from fastapi import APIRouter, Depends
from pydantic.alias_generators import to_snake

# ?
import bia_shared_datamodels.bia_data_model as shared_data_models
from .models.repository import Repository
from . import constants
from typing import List, Type

router = APIRouter(
    prefix="",
    tags=[constants.OPENAPI_TAG_PUBLIC],
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
    async def get_item(uuid: shared_data_models.UUID, db: Repository = Depends()) -> t:
        return await db.get_doc(uuid, t)

    return get_item


def make_reverse_links(router: APIRouter) -> APIRouter:
    def make_reverse_link_handler(
        source_attribute: str, source_type: Type[shared_data_models.DocumentMixin]
    ):
        async def get_descendents(
            uuid: shared_data_models.UUID, db: Repository = Depends()
        ) -> List[source_type]:
            return await db.get_docs(
                # !!!!
                # source_attribute has list values sometimes (for models that reference a list of other objects)
                #   mongo queries just so happen have the semantics we want
                # a.i. list_attribute: some_val means "any value in list_attribute is equal to some_val"
                doc_filter={source_attribute: uuid},
                doc_type=source_type,
            )

        return get_descendents

    for model in models_public:
        for (
            link_attribute_name,
            link_attribute_type,
        ) in model.get_object_reference_fields().items():
            # Just in case we accidentally link to a private model somehow (technically possible)
            #   just raise and defer definining behaviour until we use it
            if link_attribute_type in models_public:
                router.add_api_route(
                    f"/{to_snake(link_attribute_type.__name__)}/{{uuid}}/{to_snake(model.__name__)}",
                    response_model=List[model],
                    operation_id=f"get{model.__name__}In{link_attribute_type.__name__}",
                    summary=f"Get {model.__name__} In {link_attribute_type.__name__}",
                    methods=["GET"],
                    endpoint=make_reverse_link_handler(link_attribute_name, model),
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


@router.get("/placeholder")
def example_custom_handler():
    pass
