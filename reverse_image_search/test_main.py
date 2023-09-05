from fastapi.testclient import TestClient
# import gdown
import zipfile
from run import app

client = TestClient(app)


def test_drop():
    response = client.post("/drop")
    assert response.status_code == 200


def test_store():
    response = client.post(
        '/store',
        json={"File": "./data"}
    )
    assert response.status_code == 200


def test_count():
    response = client.post("/count")
    assert response.status_code == 200


def test_search():
    _test_upload_file = './data/test.jpg'
    _files = {'image': open(_test_upload_file, 'rb')}
    response = client.post('/search', files=_files)
    assert response.status_code == 200
