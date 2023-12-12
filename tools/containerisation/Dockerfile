# Based on https://kevalnagda.github.io/conda-docker-tutorial

# Define base image
FROM continuumio/miniconda3
 
# Set working directory for the project
WORKDIR /bia

# Create Conda environment for bia tools
RUN conda create -n bia python=3.10
 
# Override default shell and use bash and bia env
SHELL ["conda", "run", "-n", "bia", "/bin/bash", "-c"]
 
# Get bioformats2raw
RUN conda install -y -c ome -c conda-forge -c bioconda bioformats2raw

# Install poetry
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | python3 -
#ENV PATH="$PATH:/root/.poetry/bin"
ENV PATH="$PATH:/root/.local/bin"

# Install bia-integrator code 
RUN git clone https://github.com/BioImage-Archive/bia-integrator.git && \
    #cd bia-integrator/tools/dev
    cd bia-integrator/tools/dev && \
    poetry env use python3 && \
    poetry install

CMD ["sleep", "10000"]
