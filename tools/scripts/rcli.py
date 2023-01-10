import json

import typer
import requests
from bia_integrator_core.models import BIAStudy

URI = "http://127.0.0.1:8000/studies/list"
SHOW_URI = "http://127.0.0.1:8000/studies/show/{accession_id}"

app = typer.Typer()


studies_app = typer.Typer()
app.add_typer(studies_app, name="studies")


@studies_app.command("list")
def list():
    r = requests.get(URI)
    assert r.status_code == 200

    accession_ids = json.loads(r.content.decode())
    print('\n'.join(accession_ids))


@studies_app.command("show")
def show_study(accession_id: str):
    r = requests.get(SHOW_URI.format(accession_id=accession_id))
    assert r.status_code == 200

    print(BIAStudy.parse_raw(r.content))


if __name__ == "__main__":
    app()