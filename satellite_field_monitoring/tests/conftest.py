from unittest.mock import MagicMock
import uuid

import pytest

from src.services.satellite import S3Services


class FakeResponse:
    def __init__(self, *args, **kwargs):
        self.iter_content = iter([b'test_image_data'])
        
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

@pytest.fixture
def field_monitor():
    fields_csv = 'field_id,date,lat,lon,dim'
    api_key = 'test_api_key'
    nasa_url = 'https://api.nasa.gov/planetary/earth/imagery'
    bucket_name = 'test_bucket'
    s3_client = MagicMock()
    csv_file = 'fields.csv'
    use_mock_s3 = True

    return S3Services.FieldMonitor(fields_csv, api_key, nasa_url, bucket_name, s3_client, csv_file, use_mock_s3)

@pytest.fixture
def mock_response():
    return FakeResponse()

@pytest.fixture
def mock_os(mocker):
    mocker.patch('os.remove')
    
@pytest.fixture
def generate_unique_bucket_name():
    return f"test-bucket-{uuid.uuid4()}"