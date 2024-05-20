import sqlite3
import logging
import json

from config import DATABASE_NAME, TABLE_NAME, NAME_FILE_LOGS
from info import SYSTEM_PROMPT


logging.basicConfig(
    filename=NAME_FILE_LOGS,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)


# подключение/создание базы данных
def create_db(database_name: str = DATABASE_NAME):
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()


def execute_query(sql_query: str, data: tuple = None, database_name: str = DATABASE_NAME):
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            if data:
                cursor.execute(sql_query, data)
            else:
                cursor.execute(sql_query)
            connection.commit()

    except Exception as e:
        logging.debug(f'Ошибка при изменении данных в бд: {e}')


def execute_selection_query(sql_query: str, data: tuple = None, database_name: str = DATABASE_NAME) -> list:
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            if data:
                cursor.execute(sql_query, data)
            else:
                cursor.execute(sql_query)
            row = cursor.fetchall()

            return row
    except Exception as e:
        logging.debug(f'Данные не были получены из бд. Ошибка: {e}')


def create_table(table_name: str = TABLE_NAME):
    # TODO: дописать столбики в таблице какие нужны ну и типы данных
    sql_query = (
        f'CREATE TABLE IF NOT EXISTS {table_name} '
        f"(id INTEGER PRIMARY KEY, "
        f"user_id INTEGER,"
        f"messages TEXT);"
    )
    logging.info('таблица создана.')
    execute_query(sql_query)


def is_user_in_db(user_id: int, table_name: str = TABLE_NAME) -> bool:
    sql_query = f'SELECT user_id FROM {table_name} WHERE user_id=?;'
    result = execute_selection_query(sql_query, (user_id,))
    return bool(result)


def add_new_user(user_id: int, table_name: str = TABLE_NAME):
    # TODO: опять таки столбики + что под ними класть
    if not is_user_in_db(user_id):
        sql_query = (
            f'INSERT INTO {table_name} (user_id, messages) '
            f'VALUES (?, ?);'
        )
        json_values = json.dumps([{'role': 'system', 'text': SYSTEM_PROMPT}])
        execute_query(sql_query, (user_id, json_values))
        logging.info(f'Юзер {user_id} добавлен в таблицу')
    else:
        logging.info(f'Пользователь {user_id} уже добавлен в таблицу')
