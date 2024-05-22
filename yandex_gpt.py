import requests

from config import *
from info import *
import logging
# from creds import get_creds

# IAM_TOKEN, FOLDER_ID = get_creds()


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


def ask_ya_gpt(user_collection: list):
    headers = {'Authorization': f'Bearer {IAM_TOKEN}',
               'Content-Type': 'application/json'}
    data = {'modelUri': f'gpt://{FOLDER_ID}/yandexgpt-lite',
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": MAX_GPT_TOKENS
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
