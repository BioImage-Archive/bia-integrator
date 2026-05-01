from fastapi import APIRouter, Depends, Query, Request
from typing import Annotated
from api.elastic import Elastic
from api.app import get_elastic
from api.utils import (
    get_query_results,
    StudySearchFilters,
    ImageSearchFilters,
    build_pagination,
    build_params_as_list,
    aggregations,
)
from api.resources import study_browse_card_field_l, image_browse_card_field_l

router = APIRouter(prefix="/website")


@router.get("/doc")
async def get_doc(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    uuid: Annotated[str, Query(min_length=1, max_length=500)],
) -> dict:
    rsp = await elastic.client.search(
        index=[elastic.index_study, elastic.index_image],
        query={"match": {"uuid": uuid}},
        size=1,
    )

    return rsp.body["hits"]


@router.get("/browse/study")
async def get_study_cards(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    request: Request,
    filters: StudySearchFilters = Depends(),
    query: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=1000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
) -> dict:
    pagination = build_pagination(page, page_size)
    return await get_query_results(
        request=request,
        elastic=elastic,
        query=query,
        index_type="study",
        pagination=pagination,
        view_fields=study_browse_card_field_l,
    )


@router.get("/browse/image")
async def get_image_cards(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    request: Request,
    filters: ImageSearchFilters = Depends(),
    query: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=1000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
) -> dict:
    pagination = build_pagination(page, page_size)
    return await get_query_results(
        request=request,
        elastic=elastic,
        query=query,
        index_type="image",
        pagination=pagination,
        view_fields=image_browse_card_field_l,
    )
