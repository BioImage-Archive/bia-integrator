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
RUN git clone https://github.com/BioImage-Archive/bia-integrator.git && \
    cd bia-integrator/tools && \
    pip install -r requirements.txt

CMD ["sleep", "10000"]
