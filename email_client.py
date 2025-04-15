import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

from logger import Logger


class EmailClient:
    def __init__(self, name='EmailClient'):
        load_dotenv()
        self.logger = Logger(name).get_logger()
        self.server = os.getenv('EMAIL_SERVER')
        self.port = int(os.getenv('EMAIL_PORT'))
        self.sender = os.getenv('EMAIL_SENDER')
        self.receiver = os.getenv('EMAIL_RECEIVER')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.context = ssl.create_default_context()

    def send_email(self, subject, message):
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = subject
        msg['From'], msg['To'] = self.sender, self.receiver
        try:
            with smtplib.SMTP_SSL(self.server, self.port, context=self.context) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
                self.logger.info('Информация отправлена на почту')
        except Exception as ex:
            self.logger.error(f'Ошибка при отправке информации на почту: {ex}')
