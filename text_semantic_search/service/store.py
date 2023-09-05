import sys

import pandas as pd
import hashlib

sys.path.append('../')
from config import DEFAULT_TABLE
from logs import LOGGER


def extract_features(file_dir, encode_model):
    try:
        data = pd.read_csv(file_dir)
        title_data = data['title'].tolist()
        text_data = data['text'].tolist()
        sentence_embeddings = encode_model.sentence_encode(title_data)
        return str_to_int64(title_data), title_data, text_data, sentence_embeddings
    except Exception as e:
        LOGGER.error(f" Error with extracting feature from question {e}")


def str_to_int64(data):
    int64_data = []
    for i in range(len(data)):
        md5_hash = hashlib.md5(data[i].encode()).hexdigest()
        int64_data.append(int(md5_hash, 16) & 0xFFFFFFFF)
    return int64_data


def format_data(ids, title_data, text_data):
    data = []
    for i in range(len(ids)):
        value = (str(ids[i])), title_data[i], text_data[i]
        data.append(value)
    return data


def do_store(collection_name, file_dir, milvus_client, mysql_client, encode_model):
    try:
        if not collection_name:
            collection_name = DEFAULT_TABLE

        # embedding
        mIds, title_data, text_data, sentence_embeddings = extract_features(file_dir, encode_model)
        LOGGER.debug(f"mids len :{len(mIds)}")
        # 插入milvus
        milvus_client.create_collection(collection_name)
        milvus_client.insert(collection_name, mIds, sentence_embeddings)
        # 插入数据库
        mysql_client.create_mysql_table(collection_name)
        mysql_client.insert_data_to_mysql(collection_name, format_data(mIds, title_data, text_data))
    except Exception as e:
        LOGGER.error(e)
    return len(mIds)

