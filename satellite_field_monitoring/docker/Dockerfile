# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the GDAL dependencies
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Define environment variable you need for CPLUS_INCLUDE_PATH
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install poetry
RUN pip install poetry

# Project initialization (copy only necessary files):
COPY poetry.lock pyproject.toml ./

# Disabling virtual env creation by poetry (poetry will use the system python3)
RUN poetry config virtualenvs.create false

# Project initialization (install dependencies):
RUN poetry install --no-interaction --no-ansi


# The application is bind-mounted from the host, no need to COPY
# However, if you'd like to build a standalone image, uncomment the next line:
# COPY . /app

# The command to run the application is provided by docker-compose, no need for CMD
# However, if you'd like to build a standalone image, uncomment the next line:
# CMD ["python", "main.py"]
