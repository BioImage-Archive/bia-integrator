from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from uuid import UUID
from fastapi import Request

numeric_fields_map = {
    "size_x": "representation.size_x",
    "size_y": "representation.size_y",
    "size_z": "representation.size_z",
    "size_c": "representation.size_c",
    "size_t": "representation.size_t",
    "total_size_in_bytes": "representation.total_size_in_bytes",
    "voxel_physical_size_x": "representation.voxel_physical_size_x",
    "voxel_physical_size_y": "representation.voxel_physical_size_y",
    "voxel_physical_size_z": "representation.voxel_physical_size_z",
}

image_text_fields_map = {
    "facet.organism": "creation_process.subject.sample_of.organism_classification.scientific_name",
    "facet.imaging_method": "creation_process.acquisition_process.imaging_method_name",
}

study_text_fields_map = {
    "facet.organism": "dataset.biological_entity.organism_classification.scientific_name",
    "facet.imaging_method": "dataset.acquisition_process.imaging_method_name",
}

operators_map = {
    "eq": "term",
    "gt": "gt",
    "gte": "gte",
    "lt": "lt",
    "lte": "lte",
}

study_aggregations = {
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
}

image_aggregations = {
    "image_format": {"terms": {"field": "representation.image_format"}},
    "scientific_name": {
        "terms": {
            "field": "creation_process.subject.sample_of.organism_classification.scientific_name"
        }
    },
    "imaging_method": {
        "terms": {"field": "creation_process.acquisition_process.imaging_method_name"}
    },
}


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


def build_text_query(query: Optional[str]) -> dict[str, Any]:
    if not query:
        return {}

    return {
        "should": [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["*"],
                    "type": "phrase",
                }
            },
            {
                "simple_query_string": {
                    "query": f"*{query}*",
                    "fields": ["*"],
                }
            },
        ],
        "minimum_should_match": 1,
    }


def format_elastic_results(rsp, pagination):
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


def build_params_as_list(request: Request):
    params: Dict[str, Any] = {}
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


@dataclass
class QueryBuilder:
    text_query: Optional[str] = None
    numeric_filters: List[Dict[str, Any]] = field(default_factory=list)
    study_filters: List[Dict[str, Any]] = field(default_factory=list)
    image_filters: List[Dict[str, Any]] = field(default_factory=list)

    def parse_numeric_filters(self, params: Dict[str, Any]):
        for param, value in params.items():
            if "." not in param:
                continue

            field, operator = param.split(".", 1)

            if field not in numeric_fields_map:
                continue
            if operator not in operators_map:
                continue

            elastic_field = numeric_fields_map[field]

            try:
                value = float(value)
            except Exception:
                continue

            if operator == "eq":
                self.numeric_filters.append(
                    {operators_map[operator]: {elastic_field: value}}
                )
            else:
                self.numeric_filters.append(
                    {"range": {elastic_field: {operators_map[operator]: value}}}
                )

    def parse_text_filters(self, params: Dict[str, Any], index_type: str):
        if index_type == "study":
            fields_map = study_text_fields_map
            filters = self.study_filters
        else:
            fields_map = image_text_fields_map
            filters = self.image_filters

        for key, value in params.items():
            if key not in fields_map:
                continue
            if isinstance(value, list):
                filters.append(
                    {
                        "bool": {
                            "should": [{"term": {fields_map[key]: v}} for v in value],
                            "minimum_should_match": 1,
                        }
                    }
                )
            else:
                filters.append({"term": {fields_map[key]: value}})

    def build(self) -> Dict[str, Any]:
        should_blocks = []

        # Study filters are only applied if no image rep fields are used
        if self.study_filters and not self.numeric_filters:
            should_blocks.append({"bool": {"filter": self.study_filters}})

        # Applying image filters
        img_filters = []
        img_filters.extend(self.image_filters)
        img_filters.extend(self.numeric_filters)

        if img_filters:
            should_blocks.append({"bool": {"filter": img_filters}})

        # text search
        text = build_text_query(self.text_query)
        if text:
            should_blocks.extend(text["should"])

        # Case for no query and filters used
        if not should_blocks:
            return {"match_all": {}}

        # Using OR operator here - since two indexes (study and image).
        return {"bool": {"should": should_blocks, "minimum_should_match": 1}}

    async def search(
        self, client, index: str | list[str], offset: int, size: int, aggs: dict = None
    ):
        body = {
            "query": self.build(),
            "from_": offset,
            "size": size,
        }
        if aggs:
            body["aggs"] = aggs

        return await client.search(index=index, **body)
