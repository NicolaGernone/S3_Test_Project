# Satellite Field Monitoring

This project is a Python application that monitors a list of fields using public NASA imagery from the Landsat 8 constellation. The imagery is provided by NASA through the Earth API.

## Environment Variables

The application requires the following environment variables:

* `DATE`: The date to monitor the fields.
* `API_KEY`: Your NASA API key.
* `BUCKET_NAME`: The name of your S3 bucket.
* `FIELDS_CSV`: The path to your CSV file with the field data.
* `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
* `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.
* `AWS_REGION`: Your AWS region.

These environment variables should be set in a `.env` file in the project root.

## Setup

1. Clone the repository.
2. Navigate into the project directory.
3. Use make to build the Docker container: `make build`
4. Use make to run the Docker container: `make run`

## Docker

You can run the application in a Docker container. Use the included `docker-compose.yml` file to build and run the Docker container. 

## Makefile

You can use the included Makefile to build and run the Docker container. The following commands are available:

* `make build`: Build the Docker container.
* `make run`: Run the Docker container.
* `make test`: Run the tests in the Docker container.
* `make down`: Remove the Docker container.