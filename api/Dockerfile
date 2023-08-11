# Define base image
FROM python:3.10.0

EXPOSE 8080


# Override default shell and use bash and bia env
#RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
#    /bin/bash ~/miniconda.sh -b -p /opt/conda
#ENV PATH=/opt/conda/bin:$PATH
#RUN conda env create -f conda_env.yml

# add files that poetry needs first so layers up to (including) pulling dependencies get cached
ADD ./poetry.lock /integrator-api/poetry.lock
ADD ./pyproject.toml /integrator-api/pyproject.toml
WORKDIR /integrator-api

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
RUN poetry install

# Everything up to here should be cached most times

# add the actual project, which is what is often changed in between two different container builds
ADD ./ /integrator-api

ENTRYPOINT ["/root/.local/bin/poetry"]
CMD ["run", "python", "-m", "src.app"]
