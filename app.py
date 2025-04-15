import os.path
from datetime import datetime, timezone

from api_client import ApiClient
from data_parsing import DataParsing
from db_client import DBClient
from email_client import EmailClient
from google_sheets_client import GoogleSheetsClient
from logger import Logger


class App:
    def __init__(self, daily_summary_needed=False, email_report_needed=False):
        self.project_name = os.path.basename(os.getcwd())
        self.logger = Logger('App').get_logger()
        self.api_client = ApiClient()
        self.parser = DataParsing()
        self.db_client = DBClient()
        self.daily_summary_needed = daily_summary_needed
        self.email_report_needed = email_report_needed

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

            if self.daily_summary_needed:
                summary = {
                    'Дата и время (UTC+0) ': datetime.now(timezone.utc).strftime("%Y-%m-%d, %H:%M"),
                    'Всего попыток': len(data_parsed),
                    'Успешных попыток': sum(1 for value in data_parsed if value['is_correct'] == 1),
                    'Уникальных пользователей': len(set(value['user_id'] for value in data_parsed)),
                }
                sheets = GoogleSheetsClient('credentials.json', 'Daily Summary')
                sheets.upload_daily_summary(summary)

            if self.email_report_needed:
                subject = 'Данные обновлены'
                message = ('Данные успешно загружены в БД и выгружены в Google Sheets. Скрипт отработал без ошибок.\n'
                           f'Обновление выполнено: {datetime.now().strftime("%d.%m.%Y %H:%M")}')
                e_client = EmailClient()
                e_client.send_email(subject, message)

        except Exception as ex:
            self.logger.error(f'Возникла ошибка: {ex}. Завершение работы')
        finally:
            self.db_client.close_connection()
            self.logger.info(f'Завершение работы «{self.project_name}»')
            self.logger.info('\n' + '=' * 60 + '\n')
