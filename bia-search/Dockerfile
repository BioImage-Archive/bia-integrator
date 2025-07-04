# Define base image
FROM python:3.13.0

EXPOSE 8080

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH

# add files that poetry needs first so layers up to (including) pulling dependencies get reused
WORKDIR /bia-integrator

#   only add poetry.lock if it exists (building on local)
ADD bia-search/poetry.lock* bia-search/poetry.lock
ADD bia-search/pyproject.toml bia-search/pyproject.toml

WORKDIR /bia-integrator/bia-search

# This will now cache unless theres changes to the lock file, or the pyproject.toml, or bia-shared-datamodels
RUN poetry install --no-root

# Add the rest of the files
# The previous layers will cache fully and only this layer will be rebuilt if there are changes to the files.

ADD . ..

CMD ["poetry", "run", "uvicorn", "--workers", "1", "--port", "8080", "--log-config", "api/log_config.yml", "--host", "0.0.0.0", "--no-access-log", "api.app:app"]
