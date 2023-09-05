import os
import sys

sys.path.append('../')
from config import DEFAULT_TABLE
from logs import LOGGER


def get_images(path):
    pics = []
    for f in os.listdir(path):
        if ((f.endswith(extension) for extension in
             ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']) and not f.startswith('.DS_Store')):
            pics.append(os.path.join(path, f))
    return pics


def extract_features(image_dir, model):
    try:
        names = []
        embeddings = []
        img_list = get_images(image_dir)  # 图像列表
        total = len(img_list)
        for i, image_path in enumerate(img_list):  # 对每张图像逐个提取特征
            try:
                names.append(image_path)
                embeddings.append(model.extract_feat(image_path))
                LOGGER.info(f"Extracting feature from image No. {i + 1} , {total} images in total")
            except Exception as e:
                LOGGER.error(f"Error with extracting feature from image {e}")
                continue
        return names, embeddings
    except Exception as e:
        LOGGER.error(f" Error with extracting feature from question {e}")


def format_data(ids, names):
    data = [(str(i), n) for i, n in zip(ids, names)]
    return data


def do_store(collection_name, image_dir, milvus_client, mysql_client, model):
    try:
        if not collection_name:
            collection_name = DEFAULT_TABLE

        # 提取embedding
        names, embeddings = extract_features(image_dir, model)
        # 插入milvus
        milvus_client.create_collection(collection_name)
        ids = milvus_client.insert(collection_name, embeddings)
        # 插入数据库
        mysql_client.create_mysql_table(collection_name)
        mysql_client.insert_data_to_mysql(collection_name, format_data(ids, names))
    except Exception as e:
        LOGGER.error(e)
    return len(ids)
