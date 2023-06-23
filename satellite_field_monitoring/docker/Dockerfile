# Start with a base image containing Miniconda3
FROM continuumio/miniconda3

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Set the environment variables for the conda environment
ENV PATH /opt/conda/envs/env/bin:$PATH

# Install mamba
RUN conda install -c conda-forge mamba

# Create a conda environment using the environment.yml file and make sure that all necessary python packages are installed
RUN mamba env create -f environment.yml

# Activate the environment
RUN echo "source activate env" > ~/.bashrc

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "env", "/bin/bash", "-c"]

# Ensure that the python and conda packages are available to the metadata
RUN conda init bash && exec bash

# Run the command to start your application
CMD ["python", "/app/src/scripts.py"]
