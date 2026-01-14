from typing import Annotated, List, Optional
import typer
import logging
from rich.logging import RichHandler

from bia_embed.util import embed_text
from bia_embed.settings import Settings
from bia_integrator_api import PrivateApi
from bia_integrator_api.util import get_client
from uuid import UUID

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()

app = typer.Typer()


@app.command()
def study(
    accno: Annotated[
        Optional[List[str]], typer.Argument(help="Accession IDs of the study to embed")
    ] = None,
):
    settings = Settings()
    
    api_client = get_client(
        api_base_url=settings.api_base_url
    )

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
        for model, embedding in embedding.items():
            embedding_uuid = UUID(f"{study.uuid}_{model}")
            api_client.post_document_embedding(
                study.uuid,
                {
                    'uuid': embedding_uuid,
                    'embedding': embedding,
                    'for_document_uuid': study.uuid,
                    'additional_metadata': {
                        'model': model,
                        'input_text': data
                    }
                }
            )

@app.command()
def embed_placeholder():
    pass

if __name__ == "__main__":
    app()

