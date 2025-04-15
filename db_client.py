import os
from datetime import datetime, timezone

import psycopg2
from dotenv import load_dotenv

from logger import Logger
from psycopg2.extras import execute_values


class DBClient:
    def __init__(self, name='DBClient'):
        load_dotenv()
        self.logger = Logger(name).get_logger()
        self.connection = psycopg2.connect(
            user=os.getenv('PG_USER'), password=os.getenv('PG_PASSWORD'),
            host=os.getenv('PG_HOST'), port=os.getenv('PG_PORT'), dbname=os.getenv('PG_DBNAME')
        )
        self.cursor = self.connection.cursor()
        self.table = f'attempts_per_{datetime.now(timezone.utc).strftime("%d_%m_%Y")}'
        self.constraint = f'con_{datetime.now(timezone.utc).strftime("%d_%m_%Y")}'

    def create_table(self):
        query = f'''
        CREATE TABLE IF NOT EXISTS {self.table} (
        user_id TEXT, oauth_consumer_key TEXT, lis_result_sourcedid TEXT, 
        lis_outcome_service_url TEXT, is_correct SMALLINT, attempt_type TEXT, 
        created_at TIMESTAMP, CONSTRAINT {self.constraint} UNIQUE (user_id, created_at, attempt_type))'''
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info(f'Таблица {self.table} создана или уже существует')

    def __get_table_size(self):
        self.cursor.execute(f'SELECT COUNT(*) FROM {self.table}')
        return self.cursor.fetchone()[0]

    def insert_data(self, data):
        if not data:
            self.logger.warning('Данных для вставки не найдено')
            return

        values = [(row['user_id'], row['oauth_consumer_key'], row['lis_result_sourcedid'],
                   row['lis_outcome_service_url'], row['is_correct'], row['attempt_type'],
                   row['created_at']) for row in data]
        query = f'''
        INSERT INTO {self.table} (user_id, oauth_consumer_key, lis_result_sourcedid, 
        lis_outcome_service_url, is_correct, attempt_type, created_at) VALUES %s 
        ON CONFLICT ON CONSTRAINT {self.constraint} DO NOTHING'''

        try:
            start_table_size = self.__get_table_size()

            psycopg2.extras.execute_values(self.cursor, query, values)
            self.connection.commit()

            now_table_size = self.__get_table_size()
            new_rows_count = now_table_size - start_table_size

            self.logger.info(f'В таблицу {self.table} добавлено {new_rows_count} новых строк')
        except Exception as ex:
            self.connection.rollback()
            self.logger.error(f'Ошибка при добавлении данных: {ex}')

    def close_connection(self):
        self.cursor.close()
        self.connection.close()
        self.logger.info('Соединение с базой данных закрыто')
