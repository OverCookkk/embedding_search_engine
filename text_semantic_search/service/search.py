import sys

sys.path.append('../')
from config import DEFAULT_TABLE, TOP_K
from logs import LOGGER


def do_search(collection_name, query_sentence, milvus_client, mysql_client, encode_model):
    if not collection_name:
        collection_name = DEFAULT_TABLE
    try:
        # 转embeddings
        sentence_embeddings = encode_model.sentence_encode([query_sentence])
        result = milvus_client.search(collection_name, sentence_embeddings, TOP_K)
        mIds = [str(x.id) for x in result[0]]  # 通过milvus中返回的id去数据库中查询id对应的文本信息
        ids, titles, texts = mysql_client.search_by_milvus_ids(collection_name, mIds)
        distances = [x.distance for x in result[0]]  # 相似性
        return ids, titles, texts, distances
    except Exception as e:
        LOGGER.error(f" Error with search : {e}")
        sys.exit(1)
