import telebot
from telebot.types import Message

import os
from dotenv import load_dotenv
import logging

from config import NAME_FILE_LOGS
from info import GREETING, TEXT_HELP
from database import create_db, create_table, add_new_user, is_user_in_db


logging.basicConfig(
    filename=NAME_FILE_LOGS,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

# create_db() пока просто столбцы точно не знаем лучше не создавать загляни еще в database
# create_table()


@bot.message_handler(commands=['start'])
def say_start(message: Message):
    # здесь короче тоже надо будет сначала со столбцами разобраться, а потом думать, но пока так
    user_id = message.from_user.id
    bot.send_message(user_id, GREETING)


@bot.message_handler(commands=['help'])
def say_help(message: Message):
    bot.send_message(message.from_user.id, TEXT_HELP)


@bot.message_handler(commands=['debug'])
def send_logs(message: Message):
    try:
        with open(NAME_FILE_LOGS, "rb") as f:
            bot.send_document(message.chat.id, f)

    except Exception as e:
        bot.send_message(message.chat.id, f'Не удалось отправить файл {e}')
