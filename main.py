import telebot
from telebot.types import Message, ReplyKeyboardMarkup

import os
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

create_db()
create_table()


def create_keyboard(data: list):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in data:
        markup.add(i)
    return markup


@bot.message_handler(commands=['start'])
def say_start(message: Message):
    bot.send_message(message.chat.id, 'Предупреждение от создателей бота:\n'
                                      '<i>К боту подключена нейросеть Yandex GPT, которая может ошибаться'
                                      ' в своих ответах. Просим относиться к этому с пониманием.</i>'
                                      '\nПриятного общения!', parse_mode='html')
    user_id = message.from_user.id
    # TODO: короче лимиты есть, там что по тексту что куда тыкать я хз
    # если пользователя нет в таблице и превышен лимит пользователей присылаем извинения и выходим из функции
    if not is_user_in_db(user_id) and len(get_all_from_table()) > MAX_USERS:
        bot.send_message(user_id, TEXT_APOLOGIES)
        return

    # а если юзера нет в таблице и не превышен лимит пользователей, то добавляем его в таблицу
    elif not is_user_in_db(message.from_user.id) and len(get_all_from_table()) < MAX_USERS:
        add_new_user(message.from_user.id)

    # обновляем messages и отправляем приветствие
    update_row(user_id, 'messages', json.dumps([{'role': 'system', 'text': SYSTEM_PROMPT}]))
    bot.send_message(message.from_user.id, 'Приветствую тебя, пользователь!\n'
                                           'Ты, скорее всего, обращаешься ко мне в первый раз\n'
                                           'Я умею работать с книгами и могу помочь узнать о книге или найти её.'
                                           '\nЖду тебя в меню!', reply_markup=create_keyboard(['/menu']))


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


@bot.message_handler(commands=['book', 'continue'])
def book(m):
    bot.send_message(m.chat.id, 'Введите название книги и имя автора')
    bot.register_next_step_handler(m, book_circle)


def book_circle(m):
    text = m.text
    messages = [{'role': 'system', 'text': SYSTEM_PROMPT_1}, {'role': 'user', 'text': text}]

    if count_gpt_tokens(messages) >= MAX_USER_GPT_TOKENS:
        bot.send_message(m.chat.id, TEXT_APOLOGIES)
        return
    status, res = ask_ya_gpt(messages)
    if status:
        bot.send_message(m.chat.id, res)
        messages.append({'role': 'assistant', 'text': res})
        update_row(m.chat.id, 'messages', messages)
    else:
        bot.send_message(m.from_user.id, res)
    bot.send_message(m.chat.id, 'Хотите продолжить поиск?', reply_markup=create_keyboard(['/book', '/menu']))


@bot.message_handler(commands=['look_for'])
def choose_genre(message: Message):
    # отправляем сообщение, чтобы юзер выбрал понравившейся жанр и передаем ответ в следющую функцию
    bot.send_message(message.from_user.id, 'Выбери желаемый жанр.', reply_markup=create_keyboard(GENRE_LIST))
    bot.register_next_step_handler(message, choose_author)


def choose_author(message: Message):
    # если юзер отправил не то,что есть на кнопках,то просим его выбрать жанр, опять передаем значение в эту функцию
    if message.text not in GENRE_LIST:
        bot.send_message(message.from_user.id, 'Выбери желаемый жанр из предложенных ниже',
                         reply_markup=create_keyboard(GENRE_LIST))
        bot.register_next_step_handler(message, choose_author)
        return

    # записываем жанр в бд
    update_row(message.from_user.id, 'genre', message.text)
    # просим отправить автора
    bot.send_message(message.from_user.id, ('Отправьте желаемого автора, если вам все равно или не можете выбрать '
                                            'тыкайте кнопку. Убедительная просьба отправить фамилию существующего'
                                            ' писателя. Например: Джоан Роулинг, Александр Сергеевич Пушкин.'),
                     reply_markup=create_keyboard(['любой']))
    bot.register_next_step_handler(message, send_books)


def send_books(message: Message):
    user_id = message.from_user.id
    update_row(user_id, 'author', message.text)
    user_data = get_user_data(user_id)
    user_collection = create_system_prompt(user_data)

    if count_gpt_tokens(user_collection) >= MAX_USER_GPT_TOKENS:  # проверяем не вышел ли пользователь за лимит токенов
        bot.send_message(user_id, TEXT_APOLOGIES)
        return

    update_row(user_id, 'tokens', int(user_data['tokens']) + count_gpt_tokens(user_collection))
    status, res = ask_ya_gpt(user_collection)

    if status:
        bot.send_message(user_id, res)
        user_collection.append({'role': 'assistant', 'text': res})
        update_row(user_id, 'messages', user_collection)
    else:
        bot.send_message(user_id, res)
    bot.send_message(message.chat.id, 'Хотите продолжить поиск?', reply_markup=create_keyboard(['/look_for', '/menu']))


bot.polling(non_stop=True)
