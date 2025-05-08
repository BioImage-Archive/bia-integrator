# Define base image
FROM python:3.10.0

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH

# add files that poetry needs first so layers up to (including) pulling dependencies get reused
WORKDIR /bia-integrator

#   only add poetry.lock if it exists (building on local)
ADD bia-export/poetry.lock* bia-export/poetry.lock
ADD bia-export/pyproject.toml bia-export/pyproject.toml

# This needed to be added because it's a poetry dep 
ADD bia-shared-datamodels bia-shared-datamodels
ADD bia-test-data bia-test-data
ADD clients clients

WORKDIR /bia-integrator/bia-export

# This will now cache unless theres changes to the lock file, or the pyproject.toml, or bia-shared-datamodels
RUN poetry install --no-root

# jq needed for the elastic refresh script
RUN apt-get update && apt-get install -y jq

# Add the rest of the files
# The previous layers will cache fully and only this layer will be rebuilt if there are changes to the files.

ADD . ..

RUN poetry --directory ../bia-export install
