import sqlite3
import logging
import json

from info import *


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


# для выполнения любого запроса для изменения данных
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


# для выполнения любого запроса, чтобы получить данные
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


# создает таблицу
def create_table(table_name: str = TABLE_NAME):
    sql_query = (
        f'CREATE TABLE IF NOT EXISTS {table_name} '
        f"(id INTEGER PRIMARY KEY, "
        f"user_id INTEGER,"
        f"messages TEXT,"
        f"author TEXT,"
        f"genre TEXT,"
        f"tokens INTEGER);"
    )
    execute_query(sql_query)
    logging.info('Таблица создана.')


# проверяет есть ли пользователь в таблице
def is_user_in_db(user_id: int, table_name: str = TABLE_NAME) -> bool:
    sql_query = f'SELECT user_id FROM {table_name} WHERE user_id=?;'
    result = execute_selection_query(sql_query, (user_id,))
    return bool(result)


# добавляет в таблицу нового юзера
def add_new_user(user_id: int, table_name: str = TABLE_NAME):
    if not is_user_in_db(user_id):
        sql_query = (
            f'INSERT INTO {table_name} (user_id, messages, author, genre, tokens) '
            f'VALUES (?, 0, 0, 0, ?);'
        )
        json_values = json.dumps([{'role': 'system', 'text': SYSTEM_PROMPT_1}])
        execute_query(sql_query, (user_id, json_values))
        logging.info(f'Юзер {user_id} добавлен в таблицу')
    else:
        logging.info(f'Пользователь {user_id} уже добавлен в таблицу')


# изменяет данные в колонках
def update_row(user_id: int, column_name: str, new_value: int | str, table_name: str = TABLE_NAME):
    sql_query = f'UPDATE {table_name} SET {column_name} = ? WHERE user_id = ?;'
    execute_query(sql_query, (new_value, user_id))
    logging.info(f'{column_name} поменялось на {new_value} у пользователя {user_id}')


# возвращает инфу про юзера
def get_user_data(user_id: int, table_name: str = TABLE_NAME) -> dict:
    sql_query = f'SELECT * FROM {table_name} WHERE user_id = ?;'
    row = execute_selection_query(sql_query, (user_id,))[0]
    result = {'messages': json.loads(row[2]),
              'author': row[3],
              'genre': row[4],
              'tokens': row[5]}
    return result


# функция, которая нужна если захотим установить лимит пользователей
def get_all_from_table() -> list:
    sql_query = f'SELECT * FROM {TABLE_NAME};'
    res = execute_selection_query(sql_query)
    return res
