# Start with a base image containing Python runtime
FROM continuumio/miniconda3

# Set the working directory in the Docker image
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Create the environment:
COPY environment.yml .

# Install mamba
RUN conda install mamba -c conda-forge

# Use mamba to create the environment
RUN mamba env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Confirm gdal installation
RUN gdalinfo --version

# Make sure the environment is activated:
RUN gdal-config --version

# Set PYTHONPATH
ENV PYTHONPATH="/app/miniconda3/envs/myenv/lib/python3.11/site-packages:${PYTHONPATH}"


# The command that will run when the container is started:
# CMD ["python", "main.py"]
