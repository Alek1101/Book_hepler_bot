import telebot
import os
from telebot.types import Message, ReplyKeyboardMarkup
from dotenv import load_dotenv
from config import *
from info import *
from database import *
from yandex_gpt import *

logging.basicConfig(
    filename=LOGS,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)

# load_dotenv()
bot = telebot.TeleBot(TOKEN)


# create_db() пока просто столбцы точно не знаем лучше не создавать загляни еще в database
# create_table()


def create_keyboard(data: list):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in data:
        markup.add(i)
    return markup


@bot.message_handler(commands=['start'])
def say_start(message: Message):
    # здесь короче тоже надо будет сначала со столбцами разобраться, а потом думать, но пока так
    # Не, давай его добавим в бд, когда непосредственно обратится к gpt
    bot.send_message(message.from_user.id, GREETING)


@bot.message_handler(commands=['help'])
def say_help(message: Message):
    bot.send_message(message.from_user.id, TEXT_HELP, reply_markup=create_keyboard(['/ask']))


@bot.message_handler(commands=['debug'])
def logs(message: Message):
    try:
        with open(LOGS, "rb") as f:
            bot.send_document(message.chat.id, f)

    except Exception as e:
        bot.send_message(message.chat.id, f'Не удалось отправить файл {e}')


@bot.message_handler(commands=['menu'])
def menu(m):
    bot.send_message(m.chat.id, 'Выберите одну из команд:\n'
                                '/book - узнать информацию о конкретной книге\n'
                                '/look_for - найти похожие книги',
                     reply_markup=create_keyboard(['/book', '/look_for']))


@bot.message_handler(commands=['ask'])
def ask(m):
    # TODO: здесь надо добавить функцию count_tokens и привязать её к значению токена пользователя в базе данных
    bot.send_message(m.chat.id, 'Хотите ли вы узнать о какой-то конкретной книге?\n '
                                'Или, может быть, вам хочется найти книги, соответствующие определённым'
                                ' критериям?')
    bot.send_message(m.chat.id, 'Вы наверняка общаетесь со мной первый раз. Поделюсь лайфхаком:'
                                '\n-чтобы узнать краткое содержание определённой книги, нажмите /book\n'
                                '-чтобы подобрать книги по фильтру, нажмите /look_for',
                     reply_markup=create_keyboard(['/book', '/look_for']))


@bot.message_handler(commands=['book', 'continue'])
def book(m):
    text = m.text
    bot.send_message(m.chat.id, 'Введите название книги и имя автора')
    bot.register_next_step_handler(m, book_circle)


def book_circle(m):
    text = m.text
    messages = [{'role': 'system', 'text': SYSTEM_PROMPT_1}, {'role': 'user', 'text': text}]
    bot.send_message(m.chat.id, ask_ya_gpt(messages))
    bot.send_message(m.chat.id, 'Хотите продолжить поиск?', reply_markup=create_keyboard(['/continue', '/menu']))



