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

@pytest.mark.asyncio
async def test_search_approx_clusters(elastic: Elastic):
    """
    Approximate clusters around 2025 submissions
    """
    rsp = await elastic.client.search(
        index=elastic.index_study,
        query={
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
        },
        size=1000
    )

    assert rsp.body['hits']['total']['value'] == 355

    centroid_treshold = 0.95
    cluster_treshold = 0.8
    clusters_by_model_by_centroid = {}
    for idx, h in enumerate(rsp.body['hits']['hits']):
        doc = h['_source']

        for model_name, val in doc['embeddings'].items():
            clusters_by_model_by_centroid[model_name] = clusters_by_model_by_centroid.get(model_name, {})
            in_cluster = any([
                doc['accession_id'] in v
                for v in clusters_by_model_by_centroid[model_name].values()
            ])
            if in_cluster: continue

            similar = await elastic.client.search(
                index=elastic.index_study,
                #! source={"excludes": ["embeddings_*"]},
                knn={
                    "field": f"embeddings.{model_name}.embedding",
                    "query_vector": val['embedding'],
                    "k": 1000,
                    "num_candidates": 1000
                },
                min_score=cluster_treshold,
                size=1000
            )
            
            is_center = len([
                s['_source']
                for s in similar.body['hits']['hits']
                if s['_score'] < 1 and s['_score'] >= centroid_treshold
            ]) > 0
            if is_center:
                clusters_by_model_by_centroid[model_name][doc['accession_id']] = [
                    doc['_source']['accession_id'] for doc in similar.body['hits']['hits']
                ]
    
    #! Found a duplicate
    assert clusters_by_model_by_centroid['sentence-transformers/all-MiniLM-L6-v2']['S-BIAD2438'] == ['S-BIAD2438', 'S-BIAD2432']

    #! Found studies relating viruses and macrophages
    assert clusters_by_model_by_centroid['sentence-transformers/all-MiniLM-L6-v2']['S-BIAD2327'] == [
        'S-BIAD2327',
        'S-BIAD931'
    ]

    # Clusters together studies where description refers to some figure in the manuscript

@pytest.mark.asyncio
async def test_single_knn_timing(elastic: Elastic):
    """
    timing for db of all submissions on website, on local
    """
    study = (await elastic.client.search(
        index=elastic.index_study,
        query={
            "term": {
                "accession_id": "S-BIAD2437"
            }
        }
    )).body['hits']['hits'][0]['_source']

    model_name = "sentence-transformers/all-roberta-large-v1"
    similar_1k = await elastic.client.search(
        index=elastic.index_study,
        knn={
            "field": f"embeddings.{model_name}.embedding",
            "query_vector": study['embeddings'][model_name]['embedding'],
            "k": 1000,
            "num_candidates": 1000
        },
        size=1000
    )
    assert similar_1k['took'] > 200 and similar_1k['took'] < 300

    similar_10 = await elastic.client.search(
        index=elastic.index_study,
        knn={
            "field": f"embeddings.{model_name}.embedding",
            "query_vector": study['embeddings'][model_name]['embedding'],
            "k": 10,
            "num_candidates": 100
        }
    )
    assert similar_10['took'] < 10