import os
import logging
import urllib.parse

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import get_aliases


logger = logging.getLogger(os.path.basename(__file__))


env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

template = env.get_template("image-landing.html.j2")

def sig_format(n):
    inte = int(n)
    n -= inte
    return str(inte + float("{0:.2g}".format(n)))

def generate_image_page_html(accession_id, image_id):

    bia_study = load_and_annotate_study(accession_id)
    bia_image = bia_study.images[image_id]
    author_names = ', '.join([ 
        author.name
        for author in bia_study.authors
    ])

    reps_by_type = {
        representation.type: representation
        for representation in bia_image.representations
    }

    aliases = get_aliases(accession_id)
    aliases_by_id = {
        alias.image_id: alias.name
        for alias in aliases
    }
    image_alias = aliases_by_id.get(image_id, image_id)


    # Format physical dimensions to X unit x Y unit x Z unit format before passing on to the template
    psize = None
    px = py = px = None
    if bia_image.attributes.get('PhysicalSizeX'):
        px = sig_format(float(bia_image.attributes['PhysicalSizeX']))
        py = sig_format(float(bia_image.attributes['PhysicalSizeY']))  
        psize = '{} {} x {} {}'.format(px,bia_image.attributes[u'PhysicalSizeXUnit'],py,bia_image.attributes[u'PhysicalSizeYUnit'])
        if bia_image.attributes.get('PhysicalSizeZ'):
            pz = sig_format(float(bia_image.attributes['PhysicalSizeZ']))
            psize += ' x {} {}'.format(pz,str(bia_image.attributes['PhysicalSizeZUnit']))
    
    # Convert image dimensions to X x Y x Z format before passing on to the template
    dims = None
    dx = dy = dz = None
    if bia_image.dimensions :
        dl = bia_image.dimensions.split(',')
        if dl[0].startswith('('):
            dl[0] = dl[0].split('(')[1]
            dx = dl[-1].split(')')[0]
            dy = dl[-2]
            dims = dx + ' x ' + dy 
            if dl[-3].strip() != '1':
                dz = dl[-3]
                dims += ' x ' + dz
        else:
            dims = bia_image.dimensions
    elif bia_image.attributes.get('SizeX'):
        dx = bia_image.attributes['SizeX']
        dy = bia_image.attributes['SizeY']
        dims = str(dx) + ' x ' + str(dy)
        if bia_image.attributes['SizeZ'].strip() != '1':
            dz = bia_image.attributes['SizeZ']
            dims += ' x ' + str(dz)

    pdims = None        
    if dx and px:
        pdims = "{0:.1f}".format(float(dx)*float(px)) + bia_image.attributes[u'PhysicalSizeXUnit'] + ' x ' \
            + "{0:.1f}".format(float(dy)*float(py)) + bia_image.attributes[u'PhysicalSizeYUnit']
        if dz and pz:
            pdims += ' x ' + "{0:.1f}".format(float(dz)*float(pz)) + bia_image.attributes[u'PhysicalSizeZUnit']


    try:
        download_uri = urllib.parse.quote(reps_by_type["fire_object"].uri, safe=":/")
    except KeyError:
        download_uri = None
        
    rendered = template.render(
        study=bia_study,
        image=bia_image,
        image_alias=image_alias,
        zarr_uri=reps_by_type["ome_ngff"].uri,
        psize=psize,
        pdims=pdims,
        dimensions=dims,
        authors=author_names,
        download_uri=download_uri
    )

    return rendered


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    rendered = generate_image_page_html(accession_id, image_id)

    print(rendered)




if __name__ == "__main__":
    main()