# ETL-скрипт для загрузки и агрегации данных

## Описание
Скрипт реализует процесс ETL (Extract — Transform — Load) с последующей агрегацией и отправкой уведомлений.  
Он:

- Получает данные из API
- Выполняет парсинг вложенных структур и валидацию
- Загружает данные в PostgreSQL (Supabase)
- Ведёт логирование в файл (с сохранением логов за последние 3 дня)
- Делает ежедневную агрегацию (попытки, успешные попытки, уникальные пользователи)
- Выгружает результат в Google Sheets
- Отправляет email-оповещение о завершении работы

---

## Структура проекта

<pre>
etl_grader_project/
├── logs_history/            # Логи (по дням, за последние 3 дня)
├── .env                     # Переменные окружения (доступы Supabase, SMTP и т.п.) - скрыты
├── credentials.json         # Доступ к Google Sheets (service account) - скрыт
├── api_client.py            # Модуль для работы с API
├── data_parsing.py          # Парсинг и валидация данных
├── db_client.py             # Загрузка данных в PostgreSQL
├── logger.py                # Конфигурация логгирования
├── sheets_client.py         # Выгрузка агрегации в Google Sheets
├── email_client.py          # Отправка email-уведомлений
├── app.py                   # Класс App — основная логика
└── main.py                  # Точка запуска
</pre>

---

## Результаты

Просмотр базы данных с таблицами, к сожалению, возможен только по специальному приглашению.

Результаты ежедневной агрегации автоматически выгружаются в Google Sheets:    
[Смотреть таблицу с результатами](https://docs.google.com/spreadsheets/d/1Os-jnNXyFbIusW1Pzf6apRP0XTpWeSVNWICGa2BUyGs/edit?usp=sharing)

---

## Email-уведомления

После успешного завершения скрипта отправляется письмо на адрес, указанный в `EMAIL_RECEIVER`.

---

## Используемые технологии

- Python 3.11+
- Supabase (PostgreSQL)
- Google Sheets API (`gspread`)
- smtplib, ssl, email.message
- dotenv
- Стандартные библиотеки (`datetime`, `json`, `os`, `logging` и др.)