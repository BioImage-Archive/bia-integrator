from dataclasses import dataclass, field
from typing import Any
from api.utils import operators_map, fields_map, reorder_dict_by_spec


@dataclass
class QueryBuilder:
    """
    QueryBuilder transforms incoming URL query parameters into a valid Elasticsearch
    bool query. It supports:

    - Text search, Numeric filters, Boolean facet filters
    - Allows eq (AND), or (OR), not (NOT)
    - Handles the facet.year by converting into a range filter

    The builder accumulates clauses in must, filter, should, and must_not lists,
    then produces a complete Elasticsearch bool query using `build()`."""

    text_query: str | None
    numeric_filters: bool = False

    must: list[dict[str, Any]] = field(default_factory=list)
    should: list[dict[str, Any]] = field(default_factory=list)
    filter: list[dict[str, Any]] = field(default_factory=list)
    must_not: list[dict[str, Any]] = field(default_factory=list)

    def parse_text_query(self, query: str | None):
        if query:
            self.must.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"],
                        "type": "phrase",
                    }
                }
            )

    def parse_numeric_filters(self, params: dict[str, Any]):
        for param, value in params.items():
            if "." not in param:
                continue

            field, operator = param.split(".", 1)

            if field not in fields_map["numeric"] and operator not in operators_map:
                continue

            elastic_field = fields_map["numeric"][field]

            try:
                value = float(value)
            except Exception:
                continue

            if operator == "eq":
                range_filter = {"range": {elastic_field: {"gte": value, "lte": value}}}

            else:
                range_filter = {
                    "range": {
                        elastic_field: {operators_map["numeric"][operator]: value}
                    }
                }
            self.filter.append(range_filter)
            self.numeric_filters = True

    def parse_boolean_filters(
        self, params: dict[str, Any], index_type: str, allow_root_should: bool = False
    ):
        """
        Parse filters of form: field.eq=value, field.or=value1,value2, field.not=value
        Into proper ES must/filter/should/must_not blocks.
        """
        field_map = fields_map[index_type]

        operator_handlers = {
            "eq": self._handle_eq,
            "or": lambda field, values: self._handle_or(
                field, values, allow_root_should
            ),
            "not": self._handle_not,
        }

        for param, value in params.items():
            parts = param.split(".")

            if len(parts) < 2 or parts[0] in fields_map["numeric"]:
                continue

            operator = parts[2] if len(parts) == 3 else "or"

            field_key = f"{parts[0]}.{parts[1]}"

            elastic_field = field_map.get(field_key)

            if not elastic_field:
                continue

            values = (
                value.split(",") if isinstance(value, str) and "," in value else value
            )
            if values is None:
                return
            if field_key == "facet.year" and index_type == "study":
                self.parse_year_filter(values)
                continue

            handler = operator_handlers.get(operator)
            if handler:
                handler(elastic_field, values)

    def _handle_eq(self, elastic_field: str, values: Any):
        if isinstance(values, list):
            for v in values:
                self.filter.append({"term": {elastic_field: v}})
        else:
            self.filter.append({"term": {elastic_field: values}})

    def _handle_or(self, elastic_field: str, values: Any, allow_root_should: bool):
        should_clause = (
            [{"term": {elastic_field: v}} for v in values]
            if isinstance(values, list)
            else [{"term": {elastic_field: values}}]
        )

        if allow_root_should:
            # Advanced search: treat as scoring OR across documents
            self.should.extend(should_clause)
        else:
            self.filter.append(
                {
                    "bool": {
                        "should": should_clause,
                        "minimum_should_match": 1,
                    }
                }
            )

    def _handle_not(self, elastic_field: str, values: Any):
        if isinstance(values, list):
            self.must_not.append({"terms": {elastic_field: values}})
        else:
            self.must_not.append({"term": {elastic_field: values}})

    def parse_year_filter(self, values):
        def _year_to_range(year: str) -> dict[str, Any]:
            return {
                "range": {
                    "release_date": {
                        "gte": f"{year}-01-01",
                        "lte": f"{year}-12-31",
                    }
                }
            }

        if not isinstance(values, list):
            values = [values]

        values = [str(v) for v in values if v is not None]

        self.filter.append(
            {
                "bool": {
                    "should": [_year_to_range(v) for v in values],
                },
            }
        )

    def build(self) -> dict[str, Any]:
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

        rsp = await client.search(index=index, **body)
        if "aggregations" in rsp and aggs:
            rsp.body["aggregations"] = reorder_dict_by_spec(
                aggs, rsp.body["aggregations"]
            )
        return rsp
