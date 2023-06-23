import os
import logging
import urllib.parse

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape # type: ignore


logger = logging.getLogger(os.path.basename(__file__))

env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
#template = env.get_template("dataset-landing.html.j2")

DEFAULT_TEMPLATE = "access-help-landing.html.j2"

def generate_help_page_html(template_fname):

    template = env.get_template(template_fname)

    view_button_uri = "https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/pages/assets/view_download_buttons.png"
    copy_button_uri = "https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/pages/assets/copy_s3_button.png"

    rendered = template.render(view_button_uri=view_button_uri,copy_button_uri=copy_button_uri)

    return rendered

@click.command()
@click.option("--template-fname", default=DEFAULT_TEMPLATE)
def main(template_fname: str):

    logging.basicConfig(level=logging.INFO)

    rendered = generate_help_page_html(template_fname)
    
    print(rendered)    

if __name__ == "__main__":
    main()