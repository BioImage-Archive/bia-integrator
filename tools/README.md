BIA integrator tools
====================

Tools, including a command line interface (CLI) for working with the BIA integrator.

Installation
------------

First install requirements with:

    pip install -r requirements 

This should also install the bia-integrator-core repository. Then install with:

    pip install -e .

To get an initial set of data for experimentation/testing, you can also install `bia-integrator-data` from [here](https://github.com/BioImage-Archive/bia-integrator-data), or:

    git clone git@github.com:BioImage-Archive/bia-integrator-data.git ~/.bia-integrator-data

First steps
-----------

After installation, including the data repository, you should be able to run:

    biaint studies list

to list known studies, and:

    biaint images show S-BIAD144 IM1

to show known information for a specific images. If the `biaint` command isn't found, you may need to run `rehash`.

CLI examples
------------

### Tags

List tags for a study:

    biaint annotations list-study-tags S-BIAD144

Add a tag (value `2D`) for a study:

    biaint annotations create-study-tag S-BIAD144 2D