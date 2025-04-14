import os.path

from api_client import ApiClient
from data_parsing import DataParsing
from db_client import DBClient
from logger import Logger


class App:
    def __init__(self):
        self.project_name = os.path.basename(os.getcwd())
        self.logger = Logger('App').get_logger()
        self.api_client = ApiClient()
        self.parser = DataParsing()
        self.db_client = DBClient()

    def run(self):
        self.logger.info(f'Запуск работы «{self.project_name}»')
        try:
            data = self.api_client.get_data()
            if not data:
                self.logger.warning('Нет данных для обработки. Завершение работы')
                return

            data_parsed = self.parser.process(data)
            self.db_client.create_table()
            self.db_client.insert_data(data_parsed)
        except Exception as ex:
            self.logger.exception(f'Возникла ошибка: {str(ex)}. Завершение работы')
        finally:
            self.db_client.close_connection()
            self.logger.info(f'Завершение работы «{self.project_name}»')
            self.logger.info('\n' + '=' * 60 + '\n')
