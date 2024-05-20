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
        logging.error(f'Ошибка при изменении данных в бд: {e}')


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
        logging.error(f'Данные не были получены из бд. Ошибка: {e}')


def create_table(table_name: str = TABLE_NAME):
    sql_query = (
        f'CREATE TABLE IF NOT EXISTS {table_name} '
        f"(id INTEGER PRIMARY KEY, "
        f"user_id INTEGER,"
        f"message TEXT,"
        f"role TEXT"
        f"tokens INTEGER);"  # TODO: books - заготовка для последующих добавлений в избранное
    )
    execute_query(sql_query)
    logging.info('Таблица создана.')
#
# def is_user_in_db(user_id: int, table_name: str = TABLE_NAME) -> bool:
#     sql_query = f'SELECT user_id FROM {table_name} WHERE user_id=?;'
#     result = execute_selection_query(sql_query, (user_id,))
#     return bool(result)
#
#
# def add_new_user(user_id: int, table_name: str = TABLE_NAME):
#     if not is_user_in_db(user_id):
#         sql_query = (
#             f'INSERT INTO {table_name} (user_id, messages, role, ) '
#             f'VALUES (?, ?);'
#         )
#         json_values = json.dumps([{'role': 'system', 'text': SYSTEM_PROMPT}])
#         execute_query(sql_query, (user_id, json_values))
#         logging.info(f'Юзер {user_id} добавлен в таблицу')
#     else:
#         logging.info(f'Пользователь {user_id} уже добавлен в таблицу')


def add_message(user_id, full_message, table_name = TABLE_NAME):
    message, role, tokens = full_message
    sql_query = f'INSERT INTO {table_name} (user_id, message, role, tokens) VALUES (?,?,?,?)'
    execute_query(sql_query, (user_id, message, role, tokens))
    logging.info(f'Добавлен пользователь с user_id={user_id}')