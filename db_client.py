import datetime
import os

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
        self.table = f'attempts_per_{datetime.date.today().strftime("%d_%m_%Y")}'

    def create_table(self):
        query = f'''
        CREATE TABLE IF NOT EXISTS {self.table} (
        user_id TEXT, oauth_consumer_key TEXT, lis_result_sourcedid TEXT, 
        lis_outcome_service_url TEXT, is_correct SMALLINT, attempt_type TEXT, 
        created_at TIMESTAMP)'''
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info(f'Таблица {self.table} создана или уже существует')

    def insert_data(self, data):
        if not data:
            self.logger.warning('Данных для вставки не найдено')
            return

        values = [(row['user_id'], row['oauth_consumer_key'], row['lis_result_sourcedid'],
                   row['lis_outcome_service_url'], row['is_correct'], row['attempt_type'],
                   row['created_at']) for row in data]
        query = f'''
        INSERT INTO {self.table} (user_id, oauth_consumer_key, lis_result_sourcedid, 
        lis_outcome_service_url, is_correct, attempt_type, created_at) VALUES %s'''

        try:
            # self.cursor.execute(query, values)
            psycopg2.extras.execute_values(self.cursor, query, values)
            self.connection.commit()
            self.logger.info(f'В таблицу {self.table} добавлено {len(data)} строк')
        except Exception as ex:
            self.connection.rollback()
            self.logger.error(f'Ошибка при добавлении данных: {str(ex)}')

    def close_connection(self):
        self.cursor.close()
        self.connection.close()
        self.logger.info('Соединение с базой данных закрыто')
