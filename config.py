HOME_DIR = '' # TODO: здесь указать свою директорию с файлом

LOGS = f'{HOME_DIR}/logs.txt'
DB_FILE = f'{HOME_DIR}/messages.db'

TABLE_NAME = 'users'

# TODO: надо разобраться с folder_id и iam_token
# TODO: кстати, импорт Telegram-токена с os до меня не дошёл
# TODO: есть предложение лучше: я выкидываю config с удалённого репозитория и пишу его в .gitigore
# TODO: и мы добавляем все константы в свои config'и и пользуемся ими до финальной готовности

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'

MAX_GPT_TOKENS = 120