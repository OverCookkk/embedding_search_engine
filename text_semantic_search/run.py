import os

from utils.milvus_handler import MilvusHandler
from utils.mysql_handler import MySQLHandler
from utils.encode import SentenceModel
from fastapi import FastAPI, UploadFile, File
import uvicorn
from logs import LOGGER
from service.store import do_store
from service.count import do_count
from service.search import do_search

from config import MILVUS_HOST, MILVUS_PORT

MYSQL_HOST = "127.0.0.1"
MYSQL_USER = ""
MYSQL_PORT = 3306
MYSQL_PWD = ""
MYSQL_DB = "test"

app = FastAPI()
milvus_client = MilvusHandler(MILVUS_HOST, MILVUS_PORT)
mysql_client = MySQLHandler(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB)
encode_model = SentenceModel()


@app.post('/store_text')
async def store_test(file: UploadFile = File(...), collection_name: str = None):
    # 加载文件
    try:
        text = await file.read()
        file_name = file.filename
        dirs = "data"
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        file_path = os.path.join(os.getcwd(), os.path.join(dirs, file_name))
        with open(file_path, 'wb') as f:
            f.write(text)
    except Exception:
        return {'status': -1, 'msg': 'Failed to load data.'}

    try:
        count = do_store(collection_name, file_path, milvus_client, mysql_client, encode_model)
        LOGGER.info(f"Successfully loaded data, total count: {count}")
        return {'status': 0, 'msg': 'store data success.'}
    except Exception as e:
        LOGGER.error(e)
        return {'status': -1, 'msg': "store text data failed."}

@app.post('/count')
async def count_text(table_name: str = None):
    try:
        num = do_count(table_name, milvus_client)
        LOGGER.info("Successfully count the number of titles!")
        return num
    except Exception as e:
        LOGGER.error(e)
        return {'status': -1, 'msg': e}, 400

@app.get('/search')
def search_text(table_name: str = None, query_sentence:str = None):
    try:
        _, title, text, distance = do_search(table_name, query_sentence, milvus_client, mysql_client, encode_model)
        res = []
        for x, y, z in zip(title, text, distance):
            res.append({'title:': x, 'content': y, 'distance': z})
        LOGGER.debug(f"search result:{res}")
        return res
    except Exception as e:
        LOGGER.error(e)
        return {'status': -1, 'msg': e}, 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='127.0.0.1', port=8010)
