import os
import unittest
from contextlib import nullcontext
from io import BytesIO

import boto3
import pytest
import requests
from moto import mock_s3

from src.services.satellite import S3Services

media_root = 'media/'

class TestS3Services:
    
    @pytest.mark.skip(reason="Error in duplicated values in bucket_name")
    # Tests that the image is fetched and uploaded successfully.
    def test_fields_monitoring_success(self, mocker, field_monitor):
        
        with mock_s3():
            s3 = boto3.client('s3')
            s3.create_bucket(Bucket=field_monitor.bucket_name)
            
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = b'fake-image-data'

        mocker.patch('requests.get', return_value=mock_response)
                    
        # Test
        S3Services.monitor_fields(field_monitor)
            
        # Assert
        s3_objects = s3.list_objects(Bucket=field_monitor.bucket_name)
        assert len(s3_objects['Contents']) == len(field_monitor.fields_csv)


    # Tests that missing mandatory fields raise ValueError.
    def test_missing_mandatory_field(self, field_monitor):
        # Set up
        field_monitor.api_key=None

        # Test and assert
        with pytest.raises(ValueError):
            S3Services.monitor_fields(field_monitor)

    # Tests that invalid mandatory fields raise ValueError.
    def test_invalid_mandatory_field(self, field_monitor):
        # Set up
        field_monitor.fields_csv=''

        # Test and assert
        with pytest.raises(ValueError):
            S3Services.monitor_fields(field_monitor)

    # Tests that GET request error raises requests.exceptions.RequestException.
    def test_get_request_error(self, requests_mock, field_monitor):
        
        # Set up
        fields = {'field_id': 'test', 'date': '2022-01-01', 'lat': '0', 'lon': '0', 'dim': '0'}

        requests_mock.get(field_monitor.nasa_url, exc=requests.exceptions.RequestException)

        # Test and assert
        with pytest.raises(requests.exceptions.RequestException):
            S3Services.get_image(field_monitor, fields)

    # Tests that images are saved to local file if use_mock_s3 is True.
    def test_save_image_to_local_file(self, field_monitor):
        # Set up
        field_monitor.use_mock_s3=True
        fields = {'field_id': 'test', 'date': '2022-01-01', 'lat': '0', 'lon': '0', 'dim': '0'}
        response = requests.Response()
        response.raw = BytesIO(b'test image')

        # Test
        S3Services.upload_image(field_monitor, response, S3Services.create_image_path(fields['field_id'], fields['date']))

        # Assert
        assert os.path.exists(media_root + S3Services.create_image_path(fields['field_id'], fields['date']))

    @pytest.mark.skip(reason="Error in duplicated values in bucket_name")
    # Tests that S3 bucket is created if it does not exist.
    def test_create_s3_bucket(self, mocker, field_monitor):
        # Set up
        field_monitor.use_mock_s3=True
        # Generate a unique bucket name for this test
        with mock_s3():
            s3 = boto3.client('s3')
            
            # Mock S3Services.get_context(field_monitor)
            with unittest.mock.patch.object(S3Services, 'get_context') as mock_get_context:
                mock_get_context.return_value = nullcontext()

                # Test
                S3Services.monitor_fields(field_monitor)

                # Assert
                assert field_monitor.bucket_name in [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]

    # Tests the handling of unexpected responses from external APIs.
    def test_unexpected_responses_handling(self, requests_mock):
        # Set up
        field_monitor = S3Services.FieldMonitor()
        fields = {'field_id': 'test', 'date': '2022-01-01', 'lat': '0', 'lon': '0', 'dim': '0'}

        requests_mock.get(field_monitor.nasa_url, status_code=400)

        # Test and assert
        with pytest.raises(requests.exceptions.RequestException):
            S3Services.get_image(field_monitor, fields)

    # Tests that GET request error raises requests.exceptions.RequestException.
    def test_get_request_error(self, requests_mock, field_monitor):
        # Set up
        fields = {'field_id': 'test', 'date': '2022-01-01', 'lat': '0', 'lon': '0', 'dim': '0'}

        requests_mock.get(field_monitor.nasa_url, exc=requests.exceptions.RequestException)

        # Test and assert
        with pytest.raises(requests.exceptions.RequestException):
            S3Services.get_image(field_monitor, fields)

    @pytest.mark.skip(reason="Error in duplicated values in bucket_name")
    # Tests the handling of large files.
    def test_large_files_handling(self, mocker, field_monitor):
        # Set up
        fields = {'field_id': 'test', 'date': '2022-01-01', 'lat': '0', 'lon': '0', 'dim': '0'}
        response = requests.Response()
        response.raw = BytesIO(b'test image' * 100000000)
        with mock_s3():
            s3 = boto3.client('s3')
            s3.create_bucket(Bucket=field_monitor.bucket_name)
                
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            mock_response.iter_content.return_value = b'fake-image-data'

            mocker.patch('requests.get', return_value=mock_response)
                        
            # Test
            S3Services.monitor_fields(field_monitor)
                
            # Assert
            s3_objects = s3.list_objects(Bucket=field_monitor.bucket_name)
            assert len(s3_objects['Contents']) == len(field_monitor.fields_csv)


    # Tests the handling of unexpected responses from external APIs.
    def test_unexpected_responses_handling(self, requests_mock, field_monitor):
        # Set up
        fields = {'field_id': 'test', 'date': '2022-01-01', 'lat': '0', 'lon': '0', 'dim': '0'}

        requests_mock.get(field_monitor.nasa_url, status_code=400)

        # Test and assert
        with pytest.raises(requests.exceptions.RequestException):
            S3Services.get_image(field_monitor, fields)