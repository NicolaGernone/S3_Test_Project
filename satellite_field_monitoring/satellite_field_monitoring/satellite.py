import os
from contextlib import nullcontext
from dataclasses import dataclass, field
from multiprocessing import Pool
from typing import Optional
from io import BytesIO

import boto3
import pandas as pd
import requests
from moto import mock_s3

class S3Services:
    
    @dataclass
    class FieldMonitor:
        """Data class for monitoring fields. 

        Contains all necessary parameters and AWS S3 client for the operations.
        """
        fields_csv: Optional[list] = field(default_factory=lambda: os.getenv('FIELDS_CSV').split(','))
        date: Optional[str] = field(default_factory=lambda: os.getenv('DATE') or pd.Timestamp.today().strftime('%Y-%m-%d'))
        api_key: str = field(default_factory=lambda: os.getenv('API_KEY'))
        nasa_url: str = field(default_factory=lambda: os.getenv('NASA_URL'))
        bucket_name: str = field(default_factory=lambda: os.getenv('BUCKET_NAME'))
        s3_client: boto3.client = field(default_factory=lambda: boto3.client(os.getenv('AWS_SERVICE_NAME')) if not bool(os.getenv('USE_MOCK_S3')) else mock_s3())
        csv_file: str = field(default_factory=lambda: os.getenv('CSV_URL'))
        
        
        def __post_init__(self):
            mandatory_fields = ['api_key', 'nasa_url', 'bucket_name', 'csv_file', 's3_client']
            for field_name in mandatory_fields:
                if getattr(self, field_name) is None:
                    raise ValueError(f"{field_name} is mandatory.")
                

    @staticmethod
    def get_image(field_monitor: FieldMonitor, fields: list):
        """Fetch and upload an image to the specified S3 bucket.

        Args:
            field_monitor (FieldMonitor): An instance of FieldMonitor data class.
            fields (list): A list containing field_id, lat, lon, dim.

        Raises:
            requests.exceptions.RequestException: If there's an error in making the GET request.
        """
        field_id, lat, lon, dim = fields
        params = {
            'api_key': field_monitor.api_key,
            'date': field_monitor.date,
            'lat': lat,
            'lon': lon,
            'dim': dim,
        }
        try:
            with requests.get(url=field_monitor.nasa_url, params=params, stream=True) as response:
                response.raise_for_status()
                image_path = f'{field_id}/{field_monitor.date}_imagery.png'
                with BytesIO() as file_obj:
                    for chunk in response.iter_content(chunk_size=8192):
                        file_obj.write(chunk)
                    file_obj.seek(0)
                    if not bool(os.getenv('USE_MOCK_S3')):
                        field_monitor.s3_client.upload_fileobj(file_obj, field_monitor.bucket_name, image_path)
                    else:
                        # Save the image to a local file
                        os.makedirs(os.path.dirname('images/' + image_path), exist_ok=True)
                        with open(image_path, 'wb') as img_file:
                            img_file.write(response.content)                        
                    print(f"Image for field {field_id} uploaded successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error in getting image for field {field_id} with error {str(e)}")
            raise

    @staticmethod
    def monitor_fields(field_monitor: FieldMonitor):
        """Monitors the fields based on the CSV file.

        Args:
            field_monitor (FieldMonitor): An instance of FieldMonitor data class.

        Raises:
            Exception: If there's any error in monitoring the fields.
        """
        try:
            with nullcontext() if not bool(os.getenv('USE_MOCK_S3')) else mock_s3():
                if not bool(os.getenv('USE_MOCK_S3')):
                    field_monitor.s3_client.create_bucket(Bucket=field_monitor.bucket_name)
                    
                fields = pd.read_csv(filepath_or_buffer=field_monitor.csv_file, header=0, names=field_monitor.fields_csv).values.tolist()
                
                #Async method call
                with Pool() as pool:
                    pool.starmap(S3Services.get_image, [(field_monitor, field) for field in fields])

            print('Monitoring fields completed successfully.')
        except Exception as e:
            print(f"An error occurred while monitoring fields: {e}")
            raise

