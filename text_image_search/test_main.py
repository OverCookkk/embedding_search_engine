# from fastapi.testclient import TestClient
# import gdown
# import zipfile
# from run import app
# from fastapi import FastAPI, UploadFile, File
import time

import requests

# client = TestClient(app)


# def test_drop():
#     response = client.post("/drop")
#     assert response.status_code == 200
#
#
def test_store():
    response = requests.get('http://127.0.0.1:8010/store')

    # 检查响应状态码
    if response.status_code == 200:
        # 获取响应数据
        data = response.json()
        print(data)
    else:
        print(f"请求失败，状态码：{response.status_code}")

#
#
# def test_count():
#     response = client.post("/count")
#     assert response.status_code == 200


def test_search():
    # 发送GET请求
    start = time.time()
    response = requests.get('http://127.0.0.1:8010/search?query_sentence=鸟')

    # 检查响应状态码
    if response.status_code == 200:
        # 获取响应数据
        data = response.json()
        print(data)
    else:
        print(f"请求失败，状态码：{response.status_code}")

    print(time.time() - start)

test_search()