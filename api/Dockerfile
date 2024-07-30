# Define base image
FROM python:3.10.0

EXPOSE 8080

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH

# add files that poetry needs first so layers up to (including) pulling dependencies get reused
WORKDIR /bia-integrator

#   only add poetry.lock if it exists (building on local)
ADD ./api/poetry.lock* api/poetry.lock
ADD ./api/pyproject.toml api/pyproject.toml
ADD ./bia-shared-datamodels bia-shared-datamodels

WORKDIR /bia-integrator/api
RUN poetry install

# Everything up to here should be reused most times

# add the actual project, which is what is often changed in between two different container builds
ADD ./api ./

CMD ["poetry", "run", "uvicorn", "--workers", "4", "--port", "8080", "--log-config", "./api/log_config.yml", "--host", "0.0.0.0", "api.app:app"]
