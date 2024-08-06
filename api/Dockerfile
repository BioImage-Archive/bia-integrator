# Define base image
FROM python:3.10.0

EXPOSE 8080

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH

WORKDIR /bia-integrator

ADD api/poetry.lock* api/poetry.lock
ADD api/pyproject.toml api/pyproject.toml
ADD bia-shared-datamodels bia-shared-datamodels

WORKDIR /bia-integrator/api
RUN poetry install

ADD . ..

CMD ["poetry", "run", "uvicorn", "--workers", "4", "--port", "8080", "--log-config", "src/log_config.yml", "--host", "0.0.0.0", "api.app:app"]
