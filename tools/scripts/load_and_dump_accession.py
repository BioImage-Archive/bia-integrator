import click
from bia_integrator_core.integrator import load_and_annotate_study


@click.command()
@click.argument("accession_id")
def main(accession_id):

    study = load_and_annotate_study(accession_id)
    print(study.json(indent=2))
    

if __name__ == "__main__":
    main()