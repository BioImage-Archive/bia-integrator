from typing import Any, Optional
from pydantic import create_model, Field
from uuid import UUID
from fastapi import Request, Query
from inspect import Signature, Parameter

fields_map = {
    "study": {
        "facet.organism": "dataset.biological_entity.organism_classification.scientific_name",
        "facet.imaging_method": "dataset.acquisition_process.imaging_method_name",
        "facet.year": "release_date",
        "facet.licence": "licence",
        "facet.annotation_type": "dataset.annotation_process.method_type"
    },
    "image": {
        "facet.organism": "creation_process.subject.sample_of.organism_classification.scientific_name",
        "facet.imaging_method": "creation_process.acquisition_process.imaging_method_name",
        "facet.image_format": "representation.image_format",
    },
    "numeric": {
        "size_x": "representation.size_x",
        "size_y": "representation.size_y",
        "size_z": "representation.size_z",
        "size_c": "representation.size_c",
        "size_t": "representation.size_t",
        "total_size_in_bytes": "representation.total_size_in_bytes",
        "voxel_physical_size_x": "representation.voxel_physical_size_x",
        "voxel_physical_size_y": "representation.voxel_physical_size_y",
        "voxel_physical_size_z": "representation.voxel_physical_size_z",
        "total_physical_size_x": "total_physical_size_x",
        "total_physical_size_y": "total_physical_size_y",
        "total_physical_size_z": "total_physical_size_z",
    }
}

operators_map = {
    "numeric": {
        "eq": "",
        "gt": "gt",
        "gte": "gte",
        "lt": "lt",
        "lte": "lte",
        "or": "or",
        "not": "not"
    },
    "boolean_operators": {"and", "or", "not"}}

aggregations = {
    "study": {
        "scientific_name": { "terms": {"field": fields_map["study"]["facet.organism"] }},
        "release_date": {
            "date_histogram": {
                "field": fields_map["study"]["facet.year"],
                "calendar_interval": "1y",
                "format": "yyyy",
            }
        },
        "imaging_method": { "terms": {"field": fields_map["study"]["facet.imaging_method"] }},
        "annotation_type": { "terms": {"field": fields_map["study"]["facet.annotation_type"] }},
        "licence": { "terms": {"field": fields_map["study"]["facet.licence"] }},
    }, 
    "image" : {
        "scientific_name": { "terms": {"field": fields_map["image"]["facet.organism"] }},
        "image_format": { "terms": {"field": fields_map["image"]["facet.image_format"] }},
        "imaging_method": { "terms": {"field": fields_map["image"]["facet.imaging_method"]}},
        "number_of_channels": {
            "filters": {
                "keyed": False,
                "filters": {
                    "1":  { "term":  { fields_map["numeric"]["size_c"]: 1 } }, "2":  { "term":  { fields_map["numeric"]["size_c"]: 2 } }, 
                    "3":  { "term":  { fields_map["numeric"]["size_c"]: 3 } }, "4":  { "term":  { fields_map["numeric"]["size_c"]: 4 } }, 
                    "5":  { "term":  { fields_map["numeric"]["size_c"]: 5 } }, "More than 5": { "range": { fields_map["numeric"]["size_c"]: { "gt": 5 } } }
                }
            }
        }
    }
}

numeric_aggs = {
    "image_pixel_x": fields_map["numeric"]["size_x"],
    "image_pixel_y": fields_map["numeric"]["size_y"],
    "z_planes": fields_map["numeric"]["size_z"],
    "time_steps": fields_map["numeric"]["size_t"],
    "total_size_in_bytes": fields_map["numeric"]["total_size_in_bytes"],
    "total_physical_size_x": fields_map["numeric"]["total_physical_size_x"],
    "total_physical_size_y": fields_map["numeric"]["total_physical_size_y"],
    "total_physical_size_z": fields_map["numeric"]["total_physical_size_z"],
    "voxel_physical_size_x": fields_map["numeric"]["voxel_physical_size_x"],
    "voxel_physical_size_y": fields_map["numeric"]["voxel_physical_size_y"],
    "voxel_physical_size_z": fields_map["numeric"]["voxel_physical_size_z"],
}

aggregations["image"]["selected"] = {
    "filter": {"match_all": {}},
    "aggs": {k: {"stats": {"field": f}} for k, f in numeric_aggs.items()},
}

aggregations["image"]["all_stats"] = {
    "global": {},
    "aggs": {k: {"stats": {"field": f}} for k, f in numeric_aggs.items()},
}

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


def force_query_params(facet_dict: dict[str, str], generate_numeric_params: bool = False):
    """
    Forces FastAPI to treat every field in a dependency model as a query parameter
    rather than a request body.
    """
    params = []
    
    fields = {}

    for facet_alias in facet_dict.keys():
        description = (
            f"Filter by `{facet_alias.replace('facet.', '')}`.\n\n"
            f"Works with operators: `{"`, `".join(["eq", "or", "not"])}`. Default operator is `or`.\n\n"
            f"Examples: `?{facet_alias}.eq=value`, `?{facet_alias}.or=value1,value2`, `?{facet_alias}=value1,value2`"
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

    if generate_numeric_params:
        for field in fields_map["numeric"].keys():
            description = (
                f"Filter by `{field}`.\n\n"
                f"Works with operators: `{"`, `".join(operators_map.keys())}`.\n\n"
                f"Examples: `?{field}.gt=1`, `?{field}.lt=3`"
            )
            fields[f"{field}"] = (Optional[float], Field(None, title=field, description=description, alias=field))

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


AdvancedSearchFilters = force_query_params(fields_map["study"] | fields_map["image"], True)
ImageSearchFilters = force_query_params(fields_map["image"], True)
StudySearchFilters = force_query_params(fields_map["study"])
