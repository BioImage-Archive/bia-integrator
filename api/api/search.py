from fastapi import APIRouter, Depends, Query
from api import constants
from api.models.elastic import Elastic
from api.public import models_public
from pydantic.alias_generators import to_snake
from typing import List, Annotated, Optional, Type
from api.models.repository import Repository
from api.app import get_db, get_elastic
from api.models.api import Pagination
import bia_shared_datamodels.bia_data_model as shared_data_models
import re

router = APIRouter(
    prefix="/search", tags=[constants.OPENAPI_TAG_PUBLIC, constants.OPENAPI_TAG_PRIVATE]
)


@router.get("/study/accession")
async def searchStudyByAccession(
    accession_id: str, db: Annotated[Repository, Depends(get_db)]
) -> Optional[shared_data_models.Study]:
    studies = await db.get_docs(
        {"accession_id": accession_id},
        shared_data_models.Study,
        pagination=Pagination(start_from_uuid=None, page_size=1),
    )

    if not studies:
        return None
    else:
        return studies[0]


@router.get("/image_representation/file_uri_fragment")
async def searchImageRepresentationByFileUri(
    file_uri: Annotated[str, Query(min_length=5, max_length=1000)],
    db: Annotated[Repository, Depends(get_db)],
    pagination: Annotated[Pagination, Depends()],
) -> List[shared_data_models.ImageRepresentation]:
    return await db.get_docs(
        {"file_uri": {"$regex": f"^.*{re.escape(file_uri)}.*$"}},
        shared_data_models.ImageRepresentation,
        pagination=pagination,
    )


def make_search_items(t: Type[shared_data_models.DocumentMixin]):
    async def get_items(
        db: Annotated[Repository, Depends(get_db)],
        pagination: Annotated[Pagination, Depends()],
        filter_uuid: Annotated[List[shared_data_models.UUID], Query()] = None,
    ) -> List[t]:
        """
        Get all objects with a certain type
        """

        doc_filter = {}
        if filter_uuid:
            doc_filter["uuid"] = {"$in": filter_uuid}

        return await db.get_docs(
            doc_filter,
            t,
            pagination=pagination,
        )

    return get_items


@router.get("/fts")
async def fts(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    query: Annotated[str, Query(min_length=1, max_length=500)],
) -> dict:
    rsp = await elastic.client.search(
        index=elastic.index,
        query={
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["*"],
                            "type": "phrase",
                        }
                    },
                    {"query_string": {"query": f"*{query}*", "fields": ["*"]}},
                ]
            }
        },
        size=5,
    )

    return rsp.body["hits"]


def make_router() -> APIRouter:
    for t in models_public:
        router.add_api_route(
            f"/{to_snake(t.__name__)}",
            response_model=List[t],
            operation_id=f"search{t.__name__}",
            summary=f"Search all objects of type {t.__name__}",
            methods=["GET"],
            endpoint=make_search_items(t),
        )

    return router
