GREETING = (
    'Приветствую, любезный пользователь! Я бот-книжный помощник для любителей почитать.\n'
    ' Тыкай /help , если что-то непонятно.'
)

TEXT_HELP = ('Я - бот, который отлично разбирается в книгах! \nЧтобы задать вопрос, '
             'введи /ask и следуй подсказкам на экране!')

# короче это костяк системного промта в файле ya_gpt будет составляться системный промт и там же вставляться в запрос
SYSTEM_PROMPT = ('Ты консультант по подбору книг. Отвечай на вопросы пользователя, указывая необходимую информацию о '
                 'книгах.')

DATABASE_NAME = 'messages.db'

TABLE_NAME = 'users'

NAME_FILE_LOGS = 'logs.txt'

GOOD_STATUS_CODE = 200
