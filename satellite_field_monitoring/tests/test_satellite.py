# test_your_module.py
import pytest
import requests
from io import BytesIO
from satellite_field_monitoring.services.satellite import S3Services


def test_field_monitor(mock_env_variables):
    field_monitor = S3Services.FieldMonitor()
    assert field_monitor.api_key == 'your_api_key'
    assert field_monitor.nasa_url == 'http://example.com'
    assert field_monitor.bucket_name == 'test_bucket'
    assert field_monitor.csv_file == 'path_to_your_test_csv'
    assert field_monitor.field_names == ['field_id','date','lat','lon','dim']

def test_get_image_success(mock_s3_service, requests_mock, mock_env_variables):
    # Mock the image request
    requests_mock.get('http://example.com', content=b'image_data')

    fields = {'field_id': '1', 'date': '2023-06-14', 'lat': '10', 'lon': '20', 'dim': '0.1'}

    field_monitor = S3Services.FieldMonitor()

    # This should not raise an exception
    S3Services.get_image(field_monitor, fields)

def test_get_image_failure(mock_s3_service, requests_mock, mock_env_variables):
    # Mock the image request to return a 404 status code
    requests_mock.get('http://example.com', status_code=404)

    fields = {'field_id': '1', 'date': '2023-06-14', 'lat': '10', 'lon': '20', 'dim': '0.1'}

    field_monitor = S3Services.FieldMonitor()

    # This should raise a requests.exceptions.RequestException
    with pytest.raises(requests.exceptions.RequestException):
        S3Services.get_image(field_monitor, fields)

def test_monitor_fields_success(mock_s3_service, mock_env_variables):
    field_monitor = S3Services.FieldMonitor()

    # This should not raise an exception
    S3Services.monitor_fields(field_monitor)
