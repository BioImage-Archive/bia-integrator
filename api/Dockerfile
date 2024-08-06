# Define base image
FROM python:3.10.0

EXPOSE 8080

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH

WORKDIR /bia-integrator

COPY . .

WORKDIR /bia-integrator/api

# Poetry lock command likely unnecessary as we are copying the whole project
# For local development we only need to solve the lock once
RUN poetry install

CMD ["poetry", "run", "uvicorn", "--workers", "4", "--port", "8080", "--log-config", ".api/src/log_config.yml", "--host", "0.0.0.0", "api.app:app"]
