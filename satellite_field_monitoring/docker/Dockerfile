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

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add poetry to PATH
ENV PATH="${PATH}:/root/.poetry/bin"

# Copy poetry lock files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --no-dev

# Confirm gdal installation
RUN gdalinfo --version

# Make sure the environment is activated:
RUN echo "Make sure gdal is installed:"
RUN gdal-config --version

# The command that will run when the container is started:
CMD ["python", "main.py"]
