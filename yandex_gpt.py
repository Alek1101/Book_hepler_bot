import logging

import requests

from config import LOGS
from creds import get_creds
from info import GOOD_STATUS_CODE, SYSTEM_PROMPT

IAM_TOKEN, FOLDER_ID = get_creds()
logging.basicConfig(filename=LOGS, level=logging.INFO, format='%(asctime)s FILE: %(filename)s IN: %(funcName)s '
                                                              'MESSAGE: %(message)s', filemode='w')


def create_system_prompt(user_data: dict) -> list:
    res = [{'role': 'system', 'text': SYSTEM_PROMPT + f"автора {user_data['author']} в жанре {user_data['genre']}. "}]
    return res


def count_gpt_tokens(messages: list) -> int:
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f'gpt://{FOLDER_ID}/yandexgpt-lite',
        'messages': messages
    }
    try:
        return len(requests.post(url=url, json=data, headers=headers).json()['tokens'])
    except Exception as e:
        logging.error(e)
        return 0


def ask_ya_gpt(user_collection: list, max_token: int):
    headers = {'Authorization': f'Bearer {IAM_TOKEN}',
               'Content-Type': 'application/json'}
    data = {'modelUri': f'gpt://{FOLDER_ID}/yandexgpt-lite',
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": max_token
            },
            'messages': user_collection
            }

    try:
        response = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
                                 headers=headers,
                                 json=data)

        if response.status_code != GOOD_STATUS_CODE:
            result = f'Ошибка при получении ответа от нейросети! Статус кода: {response.status_code}'
            logging.debug(f'Ошибка при получении ответа от GPT {response.status_code}')
            return False, result

        result = response.json()["result"]["alternatives"][0]["message"]["text"]
        return True, result
    except Exception as e:
        result = f'Произошла ошибка: {e}'
        logging.error(f'Ошибка при получении ответа от GPT {e}')
    return False, result
