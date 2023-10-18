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
        '/store')
    assert response.status_code == 200


def test_count():
    response = client.post("/count")
    assert response.status_code == 200


def test_search():
    response = client.get(
        "/search?query_sentence=magpie"
    )
    assert response.status_code == 200
    # assert len(response.json()) == 9
    print(response.json())

test_search()