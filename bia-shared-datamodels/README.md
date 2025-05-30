### First time setup
poetry install

### Description

Below shows the class diagram for the Shared BIA Models.

<img src=".src/bia_shared_datamodels/Data model - document based - 2024_09.svg">

To edit the diagram, see: https://docs.google.com/drawings/d/1y_0GjhIxhB1hVvjIBoTyEv8_SE1jXuJ_9-QK6ScouBg/edit



### RO Crate context

Run the generate_context.py script to re-generate a json-ld context for use in RO crate documents, e.g:

poetry run python3 src/scripts/generate_context.py