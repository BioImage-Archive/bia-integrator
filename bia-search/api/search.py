from fastapi import APIRouter, Depends, Query
from typing import Annotated
from api.elastic import Elastic
from api.app import get_elastic

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
    if query:
        query_body["bool"]["should"] = [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["*"],
                    "type": "phrase",
                }
            },
            {"simple_query_string": {"query": f"*{query}*", "fields": ["*"]}},
        ]
        query_body["bool"]["minimum_should_match"] = 1

    # Calculate offset from page and page_size
    offset = (page - 1) * page_size

    rsp = await elastic.client.search(
        index=elastic.index_study,
        query=query_body,
        from_=offset,
        size=page_size,
        aggs={
            "scientific_name": {
                "terms": {
                    "field": "dataset.biological_entity.organism_classification.scientific_name"
                }
            },
            "release_date": {
                "date_histogram": {
                    "field": "release_date",
                    "calendar_interval": "1y",
                    "format": "yyyy",
                }
            },
            "imaging_method": {
                "terms": {
                    "field": "dataset.acquisition_process.imaging_method_name",
                }
            },
        },
    )

    total = rsp.body["hits"]["total"]["value"]
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "hits": rsp.body["hits"],
        "facets": rsp.body["aggregations"],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }


@router.get("/fts/image")
async def fts_image(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    query: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=100)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
) -> dict:
    filters = []
    query_body = {
        "bool": {
            "filter": filters,
        }
    }

    if query:
        query_body["bool"]["should"] = [{"match": {"uuid": query}}]
        query_body["bool"]["minimum_should_match"] = 1

    # Calculate offset from page and page_size
    offset = (page - 1) * page_size

    rsp = await elastic.client.search(
        index=elastic.index_image,
        query=query_body,
        from_=offset,
        size=page_size,
        aggs={"image_format": {"terms": {"field": "representation.image_format"}}},
    )

    total = rsp.body["hits"]["total"]["value"]
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "hits": rsp.body["hits"],
        "facets": rsp.body["aggregations"],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }


@router.get("/fts/image")
async def fts_image(
    elastic: Annotated[Elastic, Depends(get_elastic)],
    query: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1, alias="pagination.page", le=100)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pagination.page_size")] = 50,
) -> dict:
    filters = []
    query_body = {
        "bool": {
            "filter": filters,
        }
    }

    if query:
        query_body["bool"]["should"] = [{"match": {"uuid": query}}]
        query_body["bool"]["minimum_should_match"] = 1

    rsp = await elastic.client.search(
        index=elastic.index_image,
        query={
            "bool": {
                "should": [{"match": {"uuid": query}}],
                "minimum_should_match": 1,
            }
        },
        aggs={"image_format": {"terms": {"field": "representation.image_format"}}},
        size=50,
    )

    total = rsp.body["hits"]["total"]["value"]
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "hits": rsp.body["hits"],
        "facets": rsp.body["aggregations"],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }
