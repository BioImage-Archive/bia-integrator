from typing import Any, Optional
from pydantic import create_model, Field
from uuid import UUID
from fastapi import Request, Query
from inspect import Signature, Parameter
from api.elastic import Elastic
from api.queryBuilder import QueryBuilder
from api.resources import (numeric_aggs, aggregations, operators_map, fields_map)

def handle_numeric_fields_aggs_results(data: dict) -> dict:
    selected = data.get("selected")
    global_ = data.get("all_stats")
    if not isinstance(selected, dict) or not isinstance(global_, dict):
        return data

    sel_doc_count = selected.get("doc_count")
    glob_doc_count = global_.get("doc_count")

    glob_map = {"min": "globalMin", "max": "globalMax", "avg": "globalAvg", "sum": "globalSum"}

    for k in numeric_aggs:
        sel_stats = selected.get(k)
        glob_stats = global_.get(k)
        if not isinstance(sel_stats, dict) and not isinstance(glob_stats, dict):
            continue

        merged = dict(sel_stats or {})
        if sel_doc_count is not None:
            merged["count"] = sel_doc_count
        if isinstance(glob_stats, dict):
            merged.update({out_k: glob_stats[in_k] for in_k, out_k in glob_map.items() if in_k in glob_stats})
        if glob_doc_count is not None:
            merged["globalCount"] = glob_doc_count

        data[k] = merged

    data.pop("selected", None)
    data.pop("all_stats", None)
    return data

async def get_query_results(request: Request, 
    elastic: Elastic, 
    pagination: dict[str, int], 
    query: str | None, 
    index_type: str, 
    view_fields: list[str] | None = None
) -> dict:
    include_nested_author = True if index_type == "study" else False
    elastic_index = elastic.index_study if index_type == "study" else elastic.index_image
    params = build_params_as_list(request)
    qb = QueryBuilder(text_query=query)
    qb.parse_params(
        query=query, params=params, index_type=index_type, include_nested_author=include_nested_author
    )
    rsp = await qb.search(
        client=elastic.client,
        index=elastic_index,
        offset=pagination["offset"],
        size=pagination["page_size"],
        aggs=aggregations[index_type],
        view_fields=view_fields
    )
    return format_elastic_results(rsp, pagination, aggregations[index_type])



def is_valid_uuid(uuid: str):
    try:
        uuid_obj = UUID(uuid)
    except ValueError:
        return False
    return True


def build_pagination(page: int, page_size: int) -> dict[str, int]:
    return {
        "offset": (page - 1) * page_size,
        "page": page,
        "page_size": page_size,
    }


def calculate_total_pages(total: int, page_size: int) -> int:
    return (total + page_size - 1) // page_size if page_size > 0 else 0


def format_elastic_results(rsp, pagination, aggs):
    if "aggregations" in rsp.body and aggs:
        rsp.body["aggregations"] = reorder_dict_by_spec(
            aggs, rsp.body["aggregations"]
        )
        rsp.body["aggregations"] = handle_numeric_fields_aggs_results(
            rsp.body["aggregations"]
        )
        
    total = rsp.body["hits"]["total"]["value"]
    total_pages = calculate_total_pages(total, pagination["page_size"])

    return {
        "hits": rsp.body["hits"],
        "facets": rsp.body["aggregations"] if "aggregations" in rsp.body.keys() else {},
        "pagination": {
            "page": pagination["page"],
            "page_size": pagination["page_size"],
            "total_pages": total_pages,
        },
    }

def reorder_dict_by_spec(spec: dict, data: dict) -> dict:
    """
    Reorders keys in `data` to match `spec` (only for keys present in spec),
    and appends any extra keys at the end.
    """
    out = {}
    for k in spec.keys():
        if k in data:
            out[k] = data[k]
    # keep anything unexpected (if any)
    for k, v in data.items():
        if k not in out:
            out[k] = v
    return out


def build_params_as_list(request: Request):
    params: dict[str, Any] = {}
    for key, value in request.query_params.multi_items():
        if key in params:
            existing = params[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                params[key] = [existing, value]
        else:
            params[key] = value
    return params


def force_query_params(facet_dict: dict[str, dict]):
    """
    Forces FastAPI to treat every field in a dependency model as a query parameter
    rather than a request body.
    """
    params = []
    
    fields = {}

    for facet_alias in facet_dict.keys():
        if facet_alias == "numeric":
            for field in facet_dict["numeric"].keys():
                description = (
                    f"Filter by `{field}`.\n\n"
                    f"Works with operators: `{"`, `".join(operators_map.keys())}`.\n\n"
                    f"Examples: `?{field}.gt=1`, `?{field}.lt=3`"
                )
                fields[f"{field}"] = (Optional[float], Field(None, title=field, description=description, alias=field))
        elif facet_alias == "has":
            for field in facet_dict["has"].keys():
                description = (
                    f"Filter by `{field.replace('facet.', '')}`.\n\n"
                    f"Examples: `?has.{field}=True`, `?has.{field}=False`"
                )
                fields[field.replace(".", "_")] = (
                    Optional[list[str]],
                    Field(
                        None,
                        alias=field,
                        alias_priority=1,
                        description=description,
                    )
                )
        else:
            description = (
                f"Filter by `{facet_alias.replace('facet.', '')}`.\n\n"
                f"Works with operators: `{"`, `".join(["eq", "or", "not"])}`. Default operator is `or`.\n\n"
                f"Examples: `?{facet_alias}.eq=value`, `?{facet_alias}.or=value1&{facet_alias}.or=value2`, `?{facet_alias}.not=value1`"
            )
            fields[facet_alias.replace(".", "_")] = (
                Optional[list[str]],
                Field(
                    None,
                    alias=facet_alias,
                    alias_priority=1,
                    description=description,
                )
            )

    param_model = create_model("Query", **fields)

    for name, field in param_model.model_fields.items():
        default = Query(
            default=field.default,
            alias=field.alias,
            description=field.description,
        )

        params.append(
            Parameter(
                name=name,
                kind=Parameter.KEYWORD_ONLY,
                default=default,
                annotation=field.annotation,
            )
        )

    param_model.__signature__ = Signature(params)
    return param_model


AdvancedSearchFilters = force_query_params(fields_map["study"] | fields_map["image"])
ImageSearchFilters = force_query_params(fields_map["image"])
StudySearchFilters = force_query_params(fields_map["study"])
