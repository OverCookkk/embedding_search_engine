import os

import pandas as pd

from utils.milvus_handler import MilvusHandler
from utils.mysql_handler import MySQLHandler
from utils.clip_encode import CnClipEncodeModel
from fastapi import FastAPI, UploadFile, File
import uvicorn
from logs import LOGGER
from service.store import do_store
# from service.count import do_count
from service.search import do_search

from config import MILVUS_HOST, MILVUS_PORT

MYSQL_HOST = "172.31.61.41"
MYSQL_USER = "hwdata"
MYSQL_PORT = 3306
MYSQL_PWD = "Pass4dat@2018!0"
MYSQL_DB = "test"

app = FastAPI()
milvus_client = MilvusHandler(MILVUS_HOST, MILVUS_PORT)
mysql_client = MySQLHandler(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB)
encode_model = CnClipEncodeModel()


@app.post('/store')
async def store(collection_name: str = None):
    # 加载文件
    # try:
    #     text = await file.read()
    #     file_name = file.filename
    #     dirs = "data"
    #     if not os.path.exists(dirs):
    #         os.makedirs(dirs)
    #     file_path = os.path.join(os.getcwd(), os.path.join(dirs, file_name))
    #     with open(file_path, 'wb') as f:
    #         f.write(text)
    # except Exception:
    #     return {'status': -1, 'msg': 'Failed to load data.'}

    try:
        do_store(collection_name, "./data/reverse_image_search - bak.csv", milvus_client, mysql_client, encode_model)
        LOGGER.info(f"Successfully loaded data")
        return {'status': 0, 'msg': 'store data success.'}
    except Exception as e:
        LOGGER.error(e)
        return {'status': -1, 'msg': "store text data failed."}
#
# @app.post('/count')
# async def count_text(table_name: str = None):
#     try:
#         num = do_count(table_name, milvus_client)
#         LOGGER.info("Successfully count the number of titles!")
#         return num
#     except Exception as e:
#         LOGGER.error(e)
#         return {'status': -1, 'msg': e}, 400
#
@app.get('/search')
def search_text(table_name: str = None, query_sentence:str = None):
    try:
        _, image_paths, labels, distances = do_search(table_name, query_sentence, milvus_client, mysql_client, encode_model)
        res = []
        for x, y, z in zip(image_paths, labels, distances):
            res.append({'image_path:': x, 'label': y, 'distance': z})
        LOGGER.debug(f"search result:{res}")
        return res
    except Exception as e:
        LOGGER.error(e)
        return {'status': -1, 'msg': e}, 400


if __name__ == '__main__':
    # df = pd.read_csv("./data/reverse_image_search - bak.csv")  # ./data/reverse_image_search - bak.csv
    # paths = df['path'].tolist()
    # labels = df['label'].tolist()
    # # milvus_client.
    # features = []
    # for i in range(len(paths)):
    #     features.append(encode_model.extract_image_features(paths[i]))
    # LOGGER.debug(f"features len :{len(features)}")
    uvicorn.run(app=app, host='172.31.175.230', port=8010)
