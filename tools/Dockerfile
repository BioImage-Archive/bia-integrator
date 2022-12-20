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
 
# Install dependencies required to git clone.
#RUN apk update && \
#    apk add --update git && \
#    apk add --update openssh

# 1. Create the SSH directory.
# 2. Populate the private key file.
# 3. Set the required permissions.
# 4. Add github to our list of known hosts for ssh.
ARG SSH_KEY
RUN mkdir -p /root/.ssh/ && \
    echo "$SSH_KEY" > /root/.ssh/id_rsa && \
    chmod -R 600 /root/.ssh/ && \
    ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts && \
    git clone git@github.com:BioImage-Archive/bia-integrator-core.git && \
    git clone git@github.com:BioImage-Archive/bia-integrator-tools.git && \
    git clone git@github.com:BioImage-Archive/bia-integrator-data.git ~/.bia-integrator-data && \
    rm -rf /root/.ssh && \
    sed -i -e  's/-e git/#-e git/' bia-integrator-tools/requirements.txt && \
    pip install -r bia-integrator-tools/requirements.txt && \
    pip install -e ./bia-integrator-core && \
    pip install -e ./bia-integrator-tools
 
#ENTRYPOINT ["biaint", "studies", "list"]
#ENTRYPOINT ["conda", "run", "-n", "bia", "bioformats2raw"]
ENTRYPOINT ["sleep", "10000"]
