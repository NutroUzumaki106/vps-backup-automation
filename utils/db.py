import mysql.connector
import os
from dotenv import load_dotenv
import logging

load_dotenv()


class Database:
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST")
        self.user = os.getenv("MYSQL_USERNAME")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("DATABASE")
        self.conn = None
        self.cursor = None
        self.logger = logging.getLogger(os.getenv("LOGGER_APP"))

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None, if_data=False):
        try:
            self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.conn.commit()
            if not if_data:
                return self.cursor.lastrowid
            else:
                return result
        except Exception as e:
            self.logger.error(str(e))

    def add_update_token(self, values):
        try:
            self.connect()
            if self.check_data_exists("broker_token", "id", values["row_id"]):
                query = "UPDATE broker_token SET auth_token = %s, feed_token = %s WHERE id = %s"
                self.cursor.execute(
                    query,
                    (values["auth_token"], values["feed_token"], values["row_id"]),
                )
            else:
                query = (
                    "INSERT INTO broker_token (auth_token, feed_token) VALUES (%s, %s)"
                )
                self.cursor.execute(
                    query,
                    (values["auth_token"], values["feed_token"]),
                )
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.error(str(e))
            return False

    def check_data_exists(self, table_name, column_name, value):
        try:
            self.connect()
            query = f"SELECT * FROM {table_name} WHERE {column_name} = %s"
            self.cursor.execute(query, (value,))
            result = self.cursor.fetchone()
            return result is not None
        except Exception as e:
            self.logger.error(str(e))

    def get_token(self, key):
        try:
            self.connect()
            query = "SELECT * FROM broker_token WHERE id = %s"
            self.cursor.execute(query, (1,))
            result = self.cursor.fetchone()
            if result:
                return result[key]
            else:
                self.logger.error("DB Error")
        except Exception as e:
            self.logger.error(str(e))

    def get_exchange_list(self):
        exg_list = {"1": "NSE", "2": "NFO", "3": "BSE", "4": "BFO", "5": "MCX"}
        self.connect()
        query = "SELECT * FROM exchange_list WHERE status = 1 order by exchange ASC"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        token_list = []
        if result:
            for data in result:
                token_list.append(
                    {
                        "exchange_type": exg_list[str(data["exchange"])],
                        "token": data["token"],
                    }
                )
            return token_list
        else:
            self.logger.error("DB Error")
