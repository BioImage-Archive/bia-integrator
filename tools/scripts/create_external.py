import logging

import click
from ruamel.yaml import YAML

from bia_integrator_core.models import BIAStudy
from bia_integrator_core.interface import persist_study


logger = logging.getLogger(__file__)


@click.command()
@click.argument("yaml_fpath")
def main(yaml_fpath):

    logging.basicConfig(level=logging.INFO)

    yaml = YAML()
    with open(yaml_fpath) as fh:
        raw_data = yaml.load(fh)

    bia_study = BIAStudy.parse_obj(raw_data)

    persist_study(bia_study)


if __name__ == "__main__":
    main()