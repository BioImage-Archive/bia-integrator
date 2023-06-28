# Define base image
FROM python:3.10.0

EXPOSE 8000

# Set working directory for the project
ADD ./ /integrator-api
WORKDIR /integrator-api

# Override default shell and use bash and bia env
#RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
#    /bin/bash ~/miniconda.sh -b -p /opt/conda
#ENV PATH=/opt/conda/bin:$PATH
#RUN conda env create -f conda_env.yml

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
RUN poetry install

ENTRYPOINT ["/root/.local/bin/poetry"]
CMD ["run", "python", "-m", "src.app"]
