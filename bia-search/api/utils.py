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
    "eq": "",
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

boolean_operators = {"and", "or", "not"}


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
    numeric_filters: bool = False

    must: List[Dict[str, Any]] = field(default_factory=list)
    should: List[Dict[str, Any]] = field(default_factory=list)
    filter: List[Dict[str, Any]] = field(default_factory=list)
    must_not: List[Dict[str, Any]] = field(default_factory=list)

    def parse_text_query(self, query: Optional[str]):
        if not query:
            return

        self.must.append(
            {
                "multi_match": {
                    "query": query,
                    "fields": ["*"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            },
        )

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
                self.filter.append(
                    {"range": {elastic_field: {"gte": value, "lte": value}}}
                )
            else:
                self.filter.append(
                    {"range": {elastic_field: {operators_map[operator]: value}}}
                )
            self.numeric_filters = True

    def parse_boolean_filters(self, params: Dict[str, Any], index_type: str):
        """
        Parse filters of form:
            field.eq=value
            field.or=value1,value2
            field.not=value
        Into proper ES must/filter/should/must_not blocks.
        """

        for param, value in params.items():
            parts = param.split(".")

            if len(parts) < 2 or parts[0] in numeric_fields_map:
                continue

            if len(parts) == 2:
                operator = "or"
            else:
                operator = parts[-1]
            field_key = f"{parts[0]}.{parts[1]}"

            es_field = (
                study_text_fields_map.get(field_key)
                if index_type == "study"
                else image_text_fields_map.get(field_key)
            )

            if not es_field:
                continue

            values = (
                value.split(",") if isinstance(value, str) and "," in value else value
            )

            if operator == "eq":
                if isinstance(values, list):
                    self.filter.append({"terms": {es_field: values}})
                else:
                    self.filter.append({"term": {es_field: values}})
                continue

            if operator == "or":
                if isinstance(values, list):
                    should_clause = [{"term": {es_field: v}} for v in values]
                else:
                    should_clause = [{"term": {es_field: values}}]

                self.should.append(
                    {"bool": {"should": should_clause, "minimum_should_match": 1}}
                )
                continue

            if operator == "not":
                if isinstance(values, list):
                    self.must_not.append({"terms": {es_field: values}})
                else:
                    self.must_not.append({"term": {es_field: values}})
                continue

    def build(self) -> Dict[str, Any]:
        if not (self.must or self.filter or self.should or self.must_not):
            return {"match_all": {}}

        return {
            "bool": {
                "must": self.must,
                "filter": self.filter,
                "should": self.should,
                "must_not": self.must_not,
            }
        }

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
