import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from logger import Logger


class ApiClient:
    def __init__(self, name='ApiClient'):
        load_dotenv()

        self.api_url = os.getenv('API_URL')
        self.client = os.getenv('API_CLIENT')
        self.client_key = os.getenv('API_CLIENT_KEY')

        self.logger = Logger(name).get_logger()

    @staticmethod
    def __get_time_range():
        now = datetime.now(timezone.utc)
        start = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=timezone.utc)
        return start.strftime('%Y-%m-%d %H:%M:%S.%f'), now.strftime('%Y-%m-%d %H:%M:%S.%f')

    def get_data(self):
        start, end = self.__get_time_range()
        params = {
            'client': self.client,
            'client_key': self.client_key,
            'start': start,
            'end': end
        }

        self.logger.info('Начинается загрузка данных с API')

        try:
            response = requests.get(self.api_url, params=params)
            self.logger.info(f'Ответ от API: статус {response.status_code}')

            if response.status_code == 200:
                data = response.json()
                self.logger.info(f'Успешно получено {len(data)} записей')
                return data
            else:
                self.logger.warning(f'Ошибка при получении данных: {response.text}')
                return None
        except requests.exceptions.RequestException as ex:
            self.logger.error(f'Ошибка соединения с API: {ex}')
            return None
