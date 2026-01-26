import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download

MODEL_NAMES = [
    # smaller models - not used except for testing
    # 'sentence-transformers/all-MiniLM-L6-v2',
    # 'sentence-transformers/msmarco-distilbert-base-tas-b',
    'sentence-transformers/all-roberta-large-v1'
]
LOCAL_MODELS_DIR = Path.home() / ".cache" / "sentence_transformers_local"

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

def download_models():
    """Download models explicitly offline inference."""
    if LOCAL_MODELS_DIR.exists():
        return {name: LOCAL_MODELS_DIR / name for name in MODEL_NAMES}
    
    LOCAL_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_paths = {}
    
    for model_name in MODEL_NAMES:
        model_id = f"{model_name}"
        local_path = LOCAL_MODELS_DIR / model_name
        
        if not local_path.exists():
            snapshot_download(repo_id=model_id, local_dir=str(local_path))
        
        model_paths[model_name] = local_path
    
    return model_paths

MODEL_PATHS = download_models()

def embed_text(embed_text: str, model_paths=MODEL_PATHS):
    """Generate embeddings using locally downloaded models."""    
    embeddings = {}
    
    for model_name in MODEL_NAMES:
        model = SentenceTransformer(str(model_paths[model_name]))
        # model = SentenceTransformer(str(model_paths[model_name]))
        # embed_text = str(json.dumps(study))
        embeddings[model_name] = {
            "val": embed_text,
            "embedding": model.encode(embed_text).tolist()
        }
    return embeddings

def embed_query(query: str, model_paths=MODEL_PATHS):
    """Generate embeddings using locally downloaded models."""
    query_embeddings = {}
    for model_name in MODEL_NAMES:
        model = SentenceTransformer(str(model_paths[model_name]))
        query_embeddings[model_name] = model.encode(query).tolist()
    return query_embeddings
