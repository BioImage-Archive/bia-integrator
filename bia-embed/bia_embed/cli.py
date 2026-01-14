from typing import List, Optional
import typer
import logging
from rich.logging import RichHandler
from .settings import Settings
from bia_integrator_api import PrivateApi



logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()

app = typer.Typer()


@app.command()
def study(
    accNo: Optional[List[str]] = typer.Argument(
        default_factory=lambda _: [],
        help="Accession numbers of the studies to embed (optional)",
    ),
):
    settings = Settings()
    
    api_client = PrivateApi()
    studies = api_client.searchStudy(filter_uuid=accNo, pageSize=10000)
    assert len(studies < 10000), "More studies than one max page"

    studies_embed_data = [
        f"""
        {s['title']}
        {s['description']}
        """
        for s in studies
    ]
    print(studies_embed_data)


if __name__ == "__main__":
    app()

