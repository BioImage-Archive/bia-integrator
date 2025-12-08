from fastapi import APIRouter, Depends, Query, Request
from typing import Annotated, Any
from api.elastic import Elastic
from api.app import get_elastic
from api.utils import (
    QueryBuilder,
    build_pagination,
    build_text_query,
    format_elastic_results,
    is_valid_uuid,
    build_params_as_list,
    study_aggregations,
    image_aggregations,
)

router = APIRouter(prefix="/search")


@router.get("/fts")
async def fts(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    query: Annotated[str | None, Query()] = None,
    organism: Annotated[
        list[str] | None, Query(max_length=4, alias="facet.organism")
    ] = None,
    imaging_method: Annotated[
        list[str] | None, Query(max_length=4, alias="facet.imaging_method")
    ] = None,
    year: Annotated[list[str] | None, Query(max_length=4, alias="facet.year")] = None,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=100)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
) -> dict:
    filters = []
    if organism:
        filters.append(
            {
                "terms": {
                    "dataset.biological_entity.organism_classification.scientific_name": organism,
                }
            }
        )
    if imaging_method:
        filters.append(
            {
                "terms": {
                    "dataset.acquisition_process.imaging_method_name": imaging_method,
                }
            }
        )
    if year:
        filters.append(
            {
                "bool": {
                    "should": [
                        {
                            "range": {
                                "release_date": {
                                    "gte": f"{i}-01-01",
                                    "lte": f"{i}-12-31",
                                }
                            }
                        }
                        for i in year
                    ],
                },
            }
        )

    query_body = {
        "bool": {
            "filter": filters,
        }
    }
    query_body["bool"].update(build_text_query(query))

    pagination = build_pagination(page, page_size)

    rsp = await elastic.client.search(
        index=elastic.index_study,
        query=query_body,
        from_=pagination["offset"],
        size=pagination["page_size"],
        aggs=study_aggregations,
    )

    return format_elastic_results(rsp, pagination)


@router.get("/fts/image")
async def fts_image(
    request: Request,
    elastic: Annotated[Elastic, Depends(get_elastic)],
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
            aggregations=image_aggregations,
            pagination=pagination,
            includeDerivedImages=includeDerivedImages,
        )

    # Normal text search
    params = build_params_as_list(request)
    qb = QueryBuilder(text_query=query)
    qb.parse_numeric_filters(params)
    qb.parse_text_filters(params, "image")
    pagination = build_pagination(page, page_size)

    rsp = await qb.search(
        client=elastic.client,
        index=elastic.index_image,
        offset=pagination["offset"],
        size=pagination["page_size"],
        aggs=image_aggregations,
    )

    return format_elastic_results(rsp, pagination)


async def uuid_search(
    elastic: Elastic,
    query: str,
    aggregations: dict[str, Any],
    pagination: dict[str, int],
    includeDerivedImages: bool = False,
) -> dict:
    """
    Fast path for UUID lookup + optional derived images.
    """
    should = [{"term": {"uuid": query}}]

    if includeDerivedImages:
        should.append({"term": {"creation_process.input_image_uuid": query}})

    query_body = {
        "bool": {
            "should": should,
            "minimum_should_match": 1,
        }
    }
    rsp = await elastic.client.search(
        index=elastic.index_image,
        query=query_body,
        from_=pagination["offset"],
        size=pagination["page_size"],
        aggs=aggregations,
    )
    return format_elastic_results(rsp, pagination)


@router.get("/advanced")
async def advanced_search(
    request: Request,
    elastic: Annotated[Elastic, Depends(get_elastic)],
    query: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=100)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
):
    params = build_params_as_list(request)

    qb = QueryBuilder(text_query=query)
    qb.parse_text_filters(params, "image")
    qb.parse_numeric_filters(params)

    elastic_indexes = [elastic.index_image]
    if not qb.numeric_filters:
        qb.parse_text_filters(params, "study")
        elastic_indexes.append(elastic.index_study)

    pagination = build_pagination(page, page_size)

    rsp = await qb.search(
        client=elastic.client,
        index=elastic_indexes,
        offset=pagination["offset"],
        size=pagination["page_size"],
    )

    return format_elastic_results(rsp, pagination)
