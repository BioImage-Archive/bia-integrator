import json

import click
from bia_integrator_core.interface import get_collection
from bia_integrator_core.integrator import load_and_annotate_study


@click.command()
@click.argument("collection_name")
def main(collection_name):
    collection = get_collection(collection_name)

    aggregated = {}
    for accession_id in collection.accession_ids:
        study = load_and_annotate_study(accession_id)
    
        aggregated[accession_id] = json.loads(study.json())

    print(json.dumps(aggregated))


if __name__ == "__main__":
    main()