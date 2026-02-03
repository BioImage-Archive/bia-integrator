from typing import Annotated, List, Optional
import typer
import logging
from rich.logging import RichHandler

from bia_embed.util import embed_text
from bia_embed.settings import Settings
from bia_integrator_api.util import get_client_private
from bia_integrator_api.models.embedding import Embedding
from uuid import UUID
import hashlib

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()

app = typer.Typer()

settings = Settings()
api_client = get_client_private(
    username=settings.api_username,
    password=settings.api_password,
    api_base_url=settings.api_base_url
)

@app.command()
def study(
    accno: Annotated[
        Optional[List[str]], typer.Argument(help="Accession IDs of the study to embed")
    ] = None,
):
    logger.info(f"API: {settings.api_username}@{settings.api_base_url}")
    
    studies = []
    logger.info(accno)
    if accno:
        studies = [
            api_client.search_study_by_accession(accession_id)
            for accession_id in accno
        ]
        studies = [
            s for s in studies if s
        ]
    else:
        studies = api_client.search_study(page_size=10000)
    assert len(studies) < 10000, "More studies than one max page"
    if not studies: return

    logger.info(f"Embedding {len(studies)} studies")
    studies_embed_data = [
        f"""
{s.title.strip()}
{s.description.strip()}
        """
        for s in studies
    ]
    logger.debug(f"Example embed data: {studies_embed_data[0]}")

    study_embeddings = [
        embed_text(embed_data)
        for embed_data in studies_embed_data
    ]
    
    for (study, data, embedding) in zip(studies, studies_embed_data, study_embeddings):
        model = "sentence-transformers/all-roberta-large-v1"
        embedding = embedding[model]

        hexdigest = hashlib.md5(f"{study.uuid}_{model}".encode("utf-8")).hexdigest()
        embedding_uuid = UUID(version=4, hex=hexdigest)
        api_embedding = Embedding(
            uuid=str(embedding_uuid),
            vector=embedding['embedding'],
            version=0,
            embedding_model=model,
            for_document_uuid=study.uuid,
            additional_metadata={
                'input_text': data
            }
        )
        api_client.post_embedding(api_embedding)

@app.command()
def delete_for_model(model: str = "sentence-transformers/all-roberta-large-v1"):
    api_client.delete_embedding_by_model(model)

if __name__ == "__main__":
    app()

