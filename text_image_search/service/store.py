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


def format_data(paths, labels):
    data = []
    for i in range(len(paths)):
        value = paths[i], labels[i]
        data.append(value)
    return data


def do_store(collection_name, file_dir, milvus_client, mysql_client, encode_model):
    try:
        if not collection_name:
            collection_name = DEFAULT_TABLE

        # embedding
        df = pd.read_csv(file_dir)    # ./data/reverse_image_search - bak.csv
        paths = df['path'].tolist()
        labels = df['label'].tolist()
        # milvus_client.
        features = []
        for i in range(len(paths)):
            features.append(encode_model.extract_image_features(paths[i]))
            LOGGER.debug(f"extract_image_features num：{i}, total:{len(paths)}")
        LOGGER.debug(f"features len :{len(features)}")

        mysql_client.create_mysql_table(collection_name)
        milvus_client.create_collection(collection_name)
        # TODO:后续可以改成 批量插入和更新
        for i in range(len(features)):
            # 查询mysql
            mysql_id = mysql_client.query_data_to_mysql(collection_name, paths[i])
            if mysql_id != 0:    # 存在数据
                # 更新mysql
                mysql_client.update_data_to_mysql(collection_name, mysql_id, paths[i], labels[i])
                # 更新milvus
                milvus_client.upsert(collection_name, [mysql_id], [features[i]], [labels[i]])
            else:   # 不存在数据
                # 插入mysql
                new_mysql_id = mysql_client.insert_data_to_mysql(collection_name, paths[i], labels[i])
                # 插入milvus
                ids = milvus_client.insert(collection_name, [new_mysql_id], [features[i]], [labels[i]])
            # LOGGER.debug(f"mysql_ids :{mysql_ids}")

    except Exception as e:
        LOGGER.error(e)
    return

