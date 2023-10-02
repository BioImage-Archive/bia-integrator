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

DEFAULT_TEMPLATE = "ai-glossary.html.j2"

def generate_help_page_html(template_fname):

    template = env.get_template(template_fname)
    rendered = template.render()
    return rendered

@click.command()
@click.option("--template-fname", default=DEFAULT_TEMPLATE)
def main(template_fname: str):

    logging.basicConfig(level=logging.INFO)

    rendered = generate_help_page_html(template_fname)
    
    print(rendered)    

if __name__ == "__main__":
    main()