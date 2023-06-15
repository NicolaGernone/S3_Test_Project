import logging
import os
from contextlib import nullcontext
from dataclasses import dataclass, field
from io import BytesIO
from multiprocessing import Pool

import boto3
import pandas as pd
import requests
from decouple import config
from moto import mock_s3

media_root = config('MEDIA_ROOT')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Code Analysis

Main functionalities:
The S3Services class provides functionalities to monitor fields and fetch and upload images to an S3 bucket. It uses a FieldMonitor data class to store necessary parameters and an AWS S3 client for operations. The class can also be used with a mock S3 client for testing purposes.

Methods:
- get_image(): Fetches and uploads an image to the specified S3 bucket.
- create_params(): Creates a dictionary of parameters for the GET request.
- create_image_path(): Creates the image path for the uploaded image.
- upload_image(): Uploads the image to the specified S3 bucket or saves it to a local file.
- monitor_fields(): Monitors the fields based on the CSV file.
- get_context(): Gets the context for S3 operations.
- load_fields_from_csv(): Loads field data from CSV.
- process_fields_async(): Processes fields asynchronously.

Fields:
- FieldMonitor: A data class for monitoring fields. Contains all necessary parameters and AWS S3 client for the operations.
- fields_csv: A list of fields to be monitored.
- api_key: An API key for making GET requests.
- nasa_url: The URL for the NASA API.
- bucket_name: The name of the S3 bucket to upload images to.
- s3_client: An AWS S3 client for operations.
- csv_file: The path to the CSV file containing field data.
- use_mock_s3: A boolean flag to indicate whether to use a mock S3 client or not.
"""

class S3Services:
    
    @dataclass
    class FieldMonitor:
        """Data class for monitoring fields. 

        Contains all necessary parameters and AWS S3 client for the operations.
        """
        fields_csv: list = field(default_factory=lambda: config('FIELDS_CSV').split(','))
        api_key: str = field(default_factory=lambda: config('API_KEY'))
        nasa_url: str = field(default_factory=lambda: config('NASA_URL'))
        bucket_name: str = field(default_factory=lambda: config('BUCKET_NAME'))
        s3_client: boto3.client = field(default_factory=lambda: boto3.client(config('AWS_SERVICE_NAME')) if not bool(config('USE_MOCK_S3')) else mock_s3())
        csv_file: str = field(default_factory=lambda: config('CSV_URL'))
        use_mock_s3: bool = field(default_factory=lambda: bool(config('USE_MOCK_S3')))
        
        
        def __post_init__(self):
            mandatory_fields = ['fields_csv', 'api_key', 'nasa_url', 'bucket_name', 's3_client', 'csv_file', 'use_mock_s3']
            for field_name in mandatory_fields:
                if getattr(self, field_name) is None:
                    raise ValueError(f"{field_name} is mandatory.")
                

    @staticmethod
    def get_image(field_monitor: FieldMonitor, fields: dict):
        """Fetch and upload an image to the specified S3 bucket.

        Args:
            field_monitor (FieldMonitor): An instance of FieldMonitor data class.
            fields (dict): A dictionary containing field_id, date, lat, lon, dim.

        Raises:
            requests.exceptions.RequestException: If there's an error in making the GET request.
        """
        field_id = fields['field_id']
        params = S3Services.create_params(field_monitor, fields)
        try:
            with requests.get(url=field_monitor.nasa_url, params=params, stream=True) as response:
                response.raise_for_status()
                image_path = S3Services.create_image_path(field_id, fields['date'])
                S3Services.upload_image(field_monitor, response, image_path)
            logger.info(f"Image for field {field_id} uploaded successfully.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in getting image for field {field_id} with error {str(e)}")
            raise

    @staticmethod
    def create_params(field_monitor: FieldMonitor, fields: dict) -> dict:
        """Create a dictionary of parameters for the GET request."""
        return {
            'api_key': field_monitor.api_key,
            'date': fields['date'],
            'lat': fields['lat'],
            'lon': fields['lon'],
            'dim': fields['dim'],
        }

    @staticmethod
    def create_image_path(field_id: str, date: str) -> str:
        """Create the image path for the uploaded image."""
        return f'{field_id}/{date}_imagery.png'

    @staticmethod
    def upload_image(field_monitor: FieldMonitor, response, image_path: str) -> None:
        """Upload the image to the specified S3 bucket or save it to a local file."""
        with BytesIO() as file_obj:
            for chunk in response.iter_content(chunk_size=8192):
                file_obj.write(chunk)
            file_obj.seek(0)
            if not field_monitor.use_mock_s3:
                field_monitor.s3_client.upload_fileobj(file_obj, field_monitor.bucket_name, image_path)
            else:
                # Save the image to a local file
                os.makedirs(os.path.dirname(media_root + image_path), exist_ok=True)
                with open(media_root + image_path, 'wb') as img_file:
                    file_obj.seek(0)  # Make sure we're at the start of the file_obj
                    img_file.write(file_obj.read())  # Write the contents of file_obj, not response.content

    @staticmethod
    def monitor_fields(field_monitor: FieldMonitor) -> None:
        """Monitors the fields based on the CSV file.

        Args:
            field_monitor (FieldMonitor): An instance of FieldMonitor data class.

        Raises:
            ValueError: If there's any error in monitoring the fields.
        """
        try:
            with S3Services.get_context(field_monitor):
                fields = S3Services.load_fields_from_csv(field_monitor)
                S3Services.process_fields_async(field_monitor, fields)

            logger.info('Monitoring fields completed successfully.')
        except ValueError as e:
            logger.error(f"An error occurred while monitoring fields: {e}")
            raise

    @staticmethod
    def get_context(field_monitor: FieldMonitor):
        """Get the context for S3 operations."""
        if not field_monitor.use_mock_s3:
            field_monitor.s3_client.create_bucket(Bucket=field_monitor.bucket_name)
            return nullcontext()
        else:
            return mock_s3()

    @staticmethod
    def load_fields_from_csv(field_monitor: FieldMonitor) -> dict:
        """Load field data from CSV."""
        return pd.read_csv(filepath_or_buffer=field_monitor.csv_file, header=0, names=field_monitor.fields_csv).to_dict(orient='records')

    @staticmethod
    def process_fields_async(field_monitor: FieldMonitor, fields: dict) -> None:
        """Process fields asynchronously."""
        with Pool() as pool:
            pool.starmap(S3Services.get_image, [(field_monitor, field) for field in fields])