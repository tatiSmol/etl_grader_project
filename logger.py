import logging
import os
from datetime import datetime, timezone


class Logger:
    def __init__(self, name):
        self.logger = None
        self.days_of_interest = 3
        self.directory = 'logs_history'
        self.name = name

        self._logger_configure()

    def _logger_configure(self):
        os.makedirs(self.directory, exist_ok=True)
        file_name = datetime.now(timezone.utc).strftime('%Y-%m-%d.txt')
        path = os.path.join(self.directory, file_name)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.FileHandler(path, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self._remove_extra_logs()

    def _remove_extra_logs(self):
        now = datetime.now(timezone.utc)
        for file in os.listdir(self.directory):
            try:
                date_str = file[:-4]
                log_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                if (now - log_date).days >= self.days_of_interest:
                    os.remove(os.path.join(self.directory, file))
            except ValueError:
                continue

    def get_logger(self):
        return self.logger
