import pytest
import boto3
from moto import mock_s3

from satellite_field_monitoring.services.satellite import S3Services


@pytest.fixture
def mock_env_variables(monkeypatch):
    # Mocking environment variables
    monkeypatch.setenv('AWS_SERVICE_NAME', 's3')
    monkeypatch.setenv('API_KEY', 'your_api_key')
    monkeypatch.setenv('NASA_URL', 'http://example.com')
    monkeypatch.setenv('BUCKET_NAME', 'test_bucket')
    monkeypatch.setenv('CSV_URL', 'path_to_your_test_csv')
    monkeypatch.setenv('FIELDS_CSV', 'field_id,date,lat,lon,dim')

@pytest.fixture
def field_monitor(mock_env_variables):
    return S3Services.FieldMonitor()

@pytest.fixture
def mock_s3_service():
    with mock_s3():
        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket="test_bucket")
        yield conn
