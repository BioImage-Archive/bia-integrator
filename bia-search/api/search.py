from fastapi import APIRouter, Depends, Query, Request
from typing import Annotated, Any
from api.elastic import Elastic
from api.app import get_elastic
from api.queryBuilder import QueryBuilder
from api.utils import (
    ImageSearchFilters,
    StudySearchFilters,
    AdvancedSearchFilters,
    build_pagination,
    format_elastic_results,
    is_valid_uuid,
    build_params_as_list,
    aggregations,
)

router = APIRouter(prefix="/search")


@router.get("/fts")
async def fts(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    request: Request,
    filters: StudySearchFilters = Depends(),
    query: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=100)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
) -> dict:
    params = build_params_as_list(request)
    qb = QueryBuilder(text_query=query)
    qb.parse_text_query(query)
    qb.parse_boolean_filters(params, "study")
    pagination = build_pagination(page, page_size)
    rsp = await qb.search(
        client=elastic.client,
        index=elastic.index_study,
        offset=pagination["offset"],
        size=pagination["page_size"],
        aggs=aggregations["study"],
    )

    return format_elastic_results(rsp, pagination, aggregations["study"])


@router.get("/fts/image")
async def fts_image(
    request: Request,
    elastic: Annotated[Elastic, Depends(get_elastic)],
    filters: ImageSearchFilters = Depends(),
    query: Annotated[str | None, Query()] = None,
    includeDerivedImages: Annotated[bool, Query()] = False,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=100)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
) -> dict:
    pagination = build_pagination(page, page_size)

    # Fast-path for UUID lookup + deriveImagesLookup
    if query and is_valid_uuid(query):
        return await uuid_search(
            elastic,
            query=query,
            aggregations=aggregations["image"],
            pagination=pagination,
            includeDerivedImages=includeDerivedImages,
        )

    # Normal text search
    params = build_params_as_list(request)
    qb = QueryBuilder(text_query=query)
    qb.parse_text_query(query)
    qb.parse_numeric_filters(params)
    qb.parse_boolean_filters(params, "image")
    pagination = build_pagination(page, page_size)

    rsp = await qb.search(
        client=elastic.client,
        index=elastic.index_image,
        offset=pagination["offset"],
        size=pagination["page_size"],
        aggs=aggregations["image"],
    )

    return format_elastic_results(rsp, pagination, aggregations["image"])


async def uuid_search(
    elastic: Elastic,
    query: str,
    aggregations: dict[str, Any],
    pagination: dict[str, int],
    includeDerivedImages: bool = False,
) -> dict:
    """
    Fast path for UUID lookup + optional derived images.
    Function score makes sure the source image is the first result
    """

    should = [{"term": {"uuid": query}}]

    if includeDerivedImages:
        should.append({"term": {"creation_process.input_image_uuid": query}})

    query_body = {
        "function_score": {
            "query": {
                "bool": {
                    "should": should,
                    "minimum_should_match": 1,
                }
            },
            "functions": [
                {"filter": {"term": {"uuid": query}}, "weight": 100},
                {
                    "filter": {"term": {"creation_process.input_image_uuid": query}},
                    "weight": 10,
                },
            ],
            "score_mode": "max",
            "boost_mode": "sum",
        }
    }

    rsp = await elastic.client.search(
        index=elastic.index_image,
        query=query_body,
        from_=pagination["offset"],
        size=pagination["page_size"],
        aggs=aggregations,
    )
    return format_elastic_results(rsp, pagination, aggregations)


@router.get("/advanced")
async def advanced_search(
    request: Request,
    elastic: Annotated[Elastic, Depends(get_elastic)],
    filters: AdvancedSearchFilters = Depends(),
    query: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=100)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
):
    params = build_params_as_list(request)

    qb = QueryBuilder(text_query=query)
    qb.parse_text_query(query)
    qb.parse_boolean_filters(params, "image", True)
    qb.parse_numeric_filters(params)

    elastic_indexes = [elastic.index_image]
    if not qb.numeric_filters:
        qb.parse_boolean_filters(params, "study", True)
        elastic_indexes.append(elastic.index_study)

    pagination = build_pagination(page, page_size)

    rsp = await qb.search(
        client=elastic.client,
        index=elastic_indexes,
        offset=pagination["offset"],
        size=pagination["page_size"],
    )

    return format_elastic_results(rsp, pagination, aggregations["image"])
