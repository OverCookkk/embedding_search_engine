import sys

from pymilvus import FieldSchema, DataType, CollectionSchema, Collection, connections
from pymilvus.orm import utility

sys.path.append('../')
from config import VECTOR_DIMENSION, METRIC_TYPE
from logs import LOGGER


class MilvusHandler:
    def __init__(self, host, port):
        try:
            # 连接
            connections.connect(host=host, port=port)
            self.collection = None
            LOGGER.debug(f"Successfully connect to Milvus with IP:{host} and PORT:{port}")
        except Exception as e:
            LOGGER.error(f"Failed to connect Milvus: {e}")
            sys.exit(1)

    def set_collection(self, collection_name):
        if utility.has_collection(collection_name):
            self.collection = Collection(name=collection_name)
        else:
            LOGGER.error(f"Failed to set collection in Milvus")
            sys.exit(1)

    def create_collection(self, collection_name):
        try:
            # 如果存在就使用，不存在则创建collection，并创建索引
            if not utility.has_collection(collection_name):
                field1 = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True,
                                     auto_id=True)  # 如果主键设置自增auto_id=True，则会不需要插入
                field2 = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, description="float vector",
                                     dim=VECTOR_DIMENSION, is_primary=False)
                schema = CollectionSchema(fields=[field1, field2], description="collection description")
                self.collection = Collection(name=collection_name, schema=schema)
                self.create_index(collection_name)
            else:
                self.collection = Collection(name=collection_name)
        except Exception as e:
            LOGGER.error(f"Failed to create collection: {e}")

    def create_index(self, collection_name):
        self.set_collection(collection_name)
        default_index = {"index_type": "IVF_SQ8", "metric_type": METRIC_TYPE, "params": {"nlist": 16384}}
        status = self.collection.create_index(field_name="embedding", index_params=default_index)
        if not status.code:
            LOGGER.debug(
                f"Successfully create index in collection:{collection_name} with param:{default_index}")
            return status
        else:
            raise Exception(status.message)

    def insert(self, collection_name, vectors):
        try:
            self.set_collection(collection_name)
            data = [vectors]
            milvus_result = self.collection.insert(data)
            LOGGER.debug(f"Insert rows: {milvus_result.insert_count} ")
            # self.collection.flush()  # The flush call will seal any remaining segments and send them for indexing
            self.collection.load()  # 当创建一个集合后，它默认处于未加载状态。通过调用collection.load()方法，你可以将集合加载到内存中，以便进行查询和其他操作

            ids = milvus_result.primary_keys
            LOGGER.debug(f"Insert vectors to Milvus in collection: {collection_name} with {len(vectors)} rows")
            return ids
        except Exception as e:
            LOGGER.error(f"Failed to insert data into Milvus: {e}")

    def count(self, collection_name):
        # Get the number of milvus collection
        try:
            self.set_collection(collection_name)
            self.collection.flush()  # 必须调用flush刷盘，否则无法查询到数量
            num = self.collection.num_entities
            LOGGER.debug(f"Successfully get the num:{num} of the collection:{collection_name}")
            return num
        except Exception as e:
            LOGGER.error(f"Failed to count vectors in Milvus: {e}")
            sys.exit(1)

    # 返回的res包含ids和distances
    def search(self, collection_name, vectors, top_k):
        try:
            self.set_collection(collection_name)
            search_params = {"metric_type": METRIC_TYPE, "params": {"nprobe": 16}}
            # vectors必须是 list[list[Float]]
            res = self.collection.search(vectors, anns_field="embedding", param=search_params, limit=top_k)
            LOGGER.debug(f"Successfully search in collection: {res}")
            return res
        except Exception as e:
            LOGGER.error(f"Failed to search in Milvus: {e}")
            sys.exit(1)

    def upsert(self, collection_name, mId, vectors):
        try:
            self.set_collection(collection_name)
            data = [mId, vectors]
            res = self.collection.upsert(data)
            LOGGER.debug(f"Successfully search in collection: {res}")
            return res
        except Exception as e:
            LOGGER.error(f"Failed to upsert in Milvus: {e}")
            sys.exit(1)
