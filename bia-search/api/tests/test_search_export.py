import sys
from pathlib import Path
import pytest
from api.elastic import Elastic

# Add bia-export to Python path so we can import test_embed
project_root = Path(__file__).parent.parent.parent.parent
bia_export_path = project_root / "bia-export"
if str(bia_export_path) not in sys.path:
    sys.path.insert(0, str(bia_export_path))

# Now you can import from bia_export.test_embed
from bia_export.test_embed import embed_study, embed_query

@pytest.mark.asyncio
async def test_search_filtered(elastic: Elastic):
    #! because of the "replicating genome" in description
    query_embedding = embed_query("genome")

    #! applied during search, not after, so still getting k results
    query_filter = {
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
                for i in [2025]
            ],
        },
    }

    field_result = {}
    for model_name in query_embedding.keys():
        field_result[model_name] = await elastic.client.search(
            index=elastic.index_study,
            #! source={"excludes": ["embeddings_*"]},
            knn={
                "field": f"embeddings.{model_name}.embedding",
                "query_vector": query_embedding[model_name],
                "k": 10,
                "num_candidates": 100,
                "filter": query_filter
            },
        )
    
    by_accno = {
        k: [h["_source"]["accession_id"] for h in v.body["hits"]["hits"]]
        for k, v in field_result.items()
    }

    in_all = set(list(by_accno.values())[0])
    for v in by_accno.values():
        in_all = in_all.intersection(set(v))
    assert len(in_all) == 1 #! just 1 study
    assert in_all == ["S-BIAD2330"]

    assert all([
        accno[0] == "S-BIAD1012"
        for accno in by_accno.values()
    ])

@pytest.mark.asyncio
async def test_search_longer(elastic: Elastic):
    #! because of the "replicating genome" in description
    query_embedding = embed_query("genome effect on proteome")

    field_result = {}
    for model_name in query_embedding.keys():
        field_result[model_name] = await elastic.client.search(
            index=elastic.index_study,
            #! source={"excludes": ["embeddings_*"]},
            knn={
                "field": f"embeddings.{model_name}.embedding",
                "query_vector": query_embedding[model_name],
                "k": 10,
                "num_candidates": 100
            },
        )
    
    by_accno = {
        k: [h["_source"]["accession_id"] for h in v.body["hits"]["hits"]]
        for k, v in field_result.items()
    }

    in_all = set(list(by_accno.values())[0])
    for v in by_accno.values():
        in_all = in_all.intersection(set(v))
    assert len(in_all) == 1 #! half the studies match overall

    # first and second result
    assert by_accno["all-MiniLM-L6-v2"][0] == "S-BIAD1350"
    assert by_accno["msmarco-distilbert-base-tas-b"][0] == "S-BIAD1350"


@pytest.mark.asyncio
async def test_search_exclude_term(elastic: Elastic):
    #! because of the "replicating genome" in description
    query_embedding = embed_query("genome effect on proteome excluding Escherichia coli")

    field_result = {}
    for model_name in query_embedding.keys():
        field_result[model_name] = await elastic.client.search(
            index=elastic.index_study,
            #! source={"excludes": ["embeddings_*"]},
            knn={
                "field": f"embeddings.{model_name}.embedding",
                "query_vector": query_embedding[model_name],
                "k": 10,
                "num_candidates": 100
            },
        )
    
    by_accno = {
        k: [h["_source"]["accession_id"] for h in v.body["hits"]["hits"]]
        for k, v in field_result.items()
    }

    in_all = set(list(by_accno.values())[0])
    for v in by_accno.values():
        in_all = in_all.intersection(set(v))
    assert len(in_all) == 1

    # first and second result
    # !Wrong
    assert by_accno["sentence-transformers/all-MiniLM-L6-v2"][0] == "S-BIAD1350"
    assert by_accno["sentence-transformers/msmarco-distilbert-base-tas-b"][0] == "S-BIAD1350"
    assert by_accno["sentence-transformers/all-roberta-large-v1"][0] == "S-BSST564"