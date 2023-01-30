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
RUN conda install -y -c ome bioformats2raw

# Install bia-integrator code 
RUN git clone https://github.com/BioImage-Archive/bia-integrator-core.git && \
    git clone https://github.com/BioImage-Archive/bia-integrator-tools.git && \
    # Comment out lines for bia-integrator* so not installed vi requirements
    sed -i -e  's/-e git/#-e git/' bia-integrator-tools/requirements.txt && \
    pip install -r bia-integrator-tools/requirements.txt && \
    pip install -e ./bia-integrator-core && \
    pip install -e ./bia-integrator-tools

CMD ["sleep", "10000"]
