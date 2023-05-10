import typer
import logging
from ruamel.yaml import YAML

from bia_integrator_core.models import BIAStudy, FileReference
from bia_integrator_core.interface import persist_study

from bia_integrator_tools.identifiers import uri_to_id


app = typer.Typer()


logger = logging.getLogger(__file__)


@app.command()
def ingest_from_yaml(yaml_fpath: str):

    logging.basicConfig(level=logging.INFO)

    yaml = YAML()

    with open(yaml_fpath) as fh:
        raw = yaml.load(fh)

    study = BIAStudy.parse_obj(raw['study'])

    filerefs = {}
    for item in raw['file_references']:
        uri = item['uri']
        id = uri_to_id(study.accession_id, uri)

        fileref = FileReference(
            id=id,
            accession_id=study.accession_id,
            name=item['name'],
            size_in_bytes=0,
            uri=uri,
            type=item['type'],
            attributes=item['attributes']
        )

        filerefs[id] = fileref

    study.file_references = filerefs

    persist_study(study)


if __name__ == "__main__":
    app()