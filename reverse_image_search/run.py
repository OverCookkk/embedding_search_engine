import os

from utils.milvus_handler import MilvusHandler
from utils.mysql_handler import MySQLHandler
from fastapi import FastAPI, File, UploadFile
import uvicorn
from logs import LOGGER
from service.store import do_store
from service.count import do_count
from service.search import do_search
from pydantic import BaseModel
from typing import Optional
from utils.encode import ImageModel
from fastapi.param_functions import Form

from config import MILVUS_HOST, MILVUS_PORT, TOP_K

MYSQL_HOST = ""
MYSQL_USER = ""
MYSQL_PORT = 3306
MYSQL_PWD = ""
MYSQL_DB = ""

app = FastAPI()
milvus_client = MilvusHandler(MILVUS_HOST, MILVUS_PORT)
mysql_client = MySQLHandler(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB)
encode_model = ImageModel()


class Item(BaseModel):
    Table: Optional[str] = None
    File: str

@app.post('/store')
async def store(item: Item):
    try:
        count = do_store(item.Table, item.File, milvus_client, mysql_client, encode_model)
        LOGGER.info(f"Successfully store data, total count: {count}")
        return {'status': 0, 'msg': 'store image data success.'}
    except Exception as e:
        LOGGER.error(e)
        return {'status': -1, 'msg': "store image data failed."}

@app.post('/count')
async def count(table_name: str = None):
    try:
        num = do_count(table_name, milvus_client)
        LOGGER.info("Successfully count the number of titles!")
        return num
    except Exception as e:
        LOGGER.error(e)
        return {'status': -1, 'msg': e}, 400

@app.post('/search')
async def search(image: UploadFile = File(...), topk: int = Form(TOP_K), table_name: str = None):
    try:
        content = await image.read()
        img_path = image.filename
        with open(img_path, "wb+") as f:
            f.write(content)
        paths, distances = do_search(table_name, img_path, milvus_client, mysql_client, encode_model)
        res = []
        for x, y in zip(paths, distances):
            res.append({'image_path:': x, 'distance': y})
        LOGGER.debug(f"search result:{res}")
        return res
    except Exception as e:
        LOGGER.error(e)
        return {'status': -1, 'msg': e}, 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='127.0.0.1', port=8010)
