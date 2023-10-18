import sys

import pymysql

sys.path.append('../')
# from config import MILVUS_HOST, MILVUS_PORT, VECTOR_DIMENSION, METRIC_TYPE
from logs import LOGGER


class MySQLHandler():
    def __init__(self, host, port, username, password, database):
        try:
            self.conn = pymysql.connect(host=host, port=port, user=username, password=password, database=database,
                                        local_infile=True)
            self.cursor = self.conn.cursor()
            self.conn.ping()
        except Exception as e:
            LOGGER.error(f"MYSQL ERROR: {e} with mysql host:{host}, port:{port}")
            sys.exit(1)

    def create_mysql_table(self, table_name):
        # Create mysql table if not exists
        sql = "create table if not exists " + table_name + "(id BIGINT AUTO_INCREMENT PRIMARY KEY, image_path TEXT ,label TEXT);"
        try:
            self.cursor.execute(sql)
            LOGGER.debug(f"MYSQL create table: {table_name} with sql: {sql}")
        except Exception as e:
            LOGGER.error(f"MYSQL ERROR: {e} with sql: {sql}")
            sys.exit(1)

    def query_data_to_mysql(self, table_name, path):
        sql = "select id from " + table_name + " where image_path = %s"
        try:
            self.cursor.execute(sql, (path,))
            self.conn.commit()
            result = self.cursor.fetchone()  # 获取单行结果
            if result is not None:  # 存在
                id = result[0]
                print("ID found:", id)
                return id
            else:  # 不存在
                return 0
        except Exception as e:
            LOGGER.error(f"MYSQL ERROR: {e} with sql: {sql}")
            # sys.exit(1)

    def insert_data_to_mysql(self, table_name, path, label):
        LOGGER.debug(f"insert_data_to_mysql")
        # LOGGER.debug(f"data: {data}")
        sql = "insert into " + table_name + " (image_path,label) values (%s,%s);"
        try:
            self.cursor.execute(sql, (path, label))
            self.conn.commit()
            LOGGER.debug(
                f"MYSQL insert data to table: {table_name} successfully, self.cursor.lastrowid :{self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except Exception as e:
            LOGGER.error(f"MYSQL ERROR: {e} with sql: {sql}")
            # sys.exit(1)

    def update_data_to_mysql(self, table_name, id, path, label):
        LOGGER.debug(f"update_data_to_mysql, id:{id}")
        sql = "update " + table_name + " set  image_path = %s, label = %s where id = %s"
        self.cursor.execute(sql, (path, label, id))
        self.conn.commit()
        LOGGER.debug(f"MYSQL update data to table: {table_name} successfully, id :{id}")

    def search_by_milvus_ids(self, table_name, ids):
        # Get the img_path according to the milvus ids
        str_ids = str(ids).replace('[', '').replace(']', '')
        sql = "select * from " + table_name + " where id in (" + str_ids + ") order by field (id," + str_ids + ");"
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            results_ids = [res[0] for res in results]
            results_image_paths = [res[1] for res in results]
            results_labels = [res[2] for res in results]
            LOGGER.debug("MYSQL search by milvus id.")
            return results_ids, results_image_paths, results_labels
        except Exception as e:
            LOGGER.error(f"MYSQL ERROR: {e} with sql: {sql}")
            sys.exit(1)
