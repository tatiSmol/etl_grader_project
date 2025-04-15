from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class GoogleSheetsClient:
    def __init__(self, credentials_path, spreadsheet_name):
        self.credentials_path = credentials_path
        self.spreadsheet_name = spreadsheet_name

        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = Credentials.from_service_account_file(self.credentials_path, scopes=self.scopes)
        self.client = gspread.authorize(self.credentials)
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def upload_daily_summary(self, summary_data: dict):
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        sheet = self.client.open(self.spreadsheet_name)

        try:
            worksheet = sheet.worksheet(date_str)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=date_str, rows='2', cols='4')

        headers = list(summary_data.keys())
        values = list(summary_data.values())
        worksheet.append_row(headers)
        worksheet.append_row(values)
        self.__auto_resize_columns(sheet.id, worksheet._properties['sheetId'], len(summary_data))

    def __auto_resize_columns(self, spreadsheet_id, sheet_id, col_count):
        req_body = {'requests': [
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': col_count
                    }
                }
            }
        ]}
        self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=req_body).execute()
