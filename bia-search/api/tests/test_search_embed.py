import pathlib
import json
from sentence_transformers import SentenceTransformer
from api.elastic import Elastic
import pytest_asyncio

# 384 dims
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 768 dims
# model = SentenceTransformer("sentence-transformers/msmarco-distilbert-base-tas-b")


def test_make_test_data():
    study_metadata_path = (
        pathlib.Path(__file__).parent / "test_data" / "bia-test-embeddings.json"
    )

    with open(study_metadata_path, "r") as f:
        study_metadata = json.load(f)

        new_study_metadata = []
        for v in study_metadata:
            v = {"author": v["author"], "embeddings": []}

            for a in v["author"]:
                embedding = model.encode("author" + " : " + json.dumps(a))
                v["embeddings"].append(embedding.tolist())

            for i, emb in enumerate(v["embeddings"]):
                v[f"embeddings_{i}"] = emb

            del v["embeddings"]
            new_study_metadata.append(v)
    with open(study_metadata_path, "w") as f:
        json.dump(new_study_metadata, f, indent=2)


import pytest


@pytest.mark.asyncio
async def test_search_embed(elastic: Elastic):
    result = await elastic.client.search(
        index=elastic.index_embed, query={"match_all": {}}
    )

    assert result["hits"]["total"]["value"] == 3

    results = []
    for query in [
        "cloud",
        "brain",
        "hospital",
        "childrens hospital",
        "american university",
        "address",
        "institution",
        "stadium",
        "drosophila",
        "computer",
        "scientist person human Earth inhabitant",
        "scientist",
        "this is a long test sentence to see what happens when I refer to a university and a park where children play in the same text",
    ]:
        query_embedding = model.encode(query).tolist()

        all_results = []
        for field in ["embeddings_0", "embeddings_1", "embeddings_2"]:
            field_result = await elastic.client.search(
                index=elastic.index_embed,
                source={"excludes": ["embeddings_*"]},
                knn={
                    "field": field,
                    "query_vector": query_embedding,
                    "k": 10,
                    "num_candidates": 10,
                },
            )
            all_results.extend(field_result["hits"]["hits"])

        # Sort by score and take top results
        all_results.sort(key=lambda x: x["_score"], reverse=True)

        # Create result structure with best matches
        result = {
            "hits": {
                "hits": all_results[:10],  # Top 10 across all fields
                "total": {"value": len(all_results)},
            }
        }
        results.append(result)

    scores = [r["hits"]["hits"][0]["_score"] for r in results]
    assert scores[0] > scores[1] > scores[2]
