from translate_emoji import de_emojify


"""
Извлекает текст из сообщения
@param message Получаемое сообщение из Telegram API
@returns Текст из сообщения
"""
def extract_text(message):
    if 'text' in message:
        return message['text']
    elif 'caption' in message:
        return message['caption']
    elif 'sticker' in message:
        return message['sticker']['emoji']
    else:
        return ''

    
"""
Получает и обрабатывает текст из сообщения
@param message Получаемое сообщение из Telegram API
@returns Обработанный текст
"""
def get_text(message):
    return de_emojify(extract_text(message))


"""
Обрабатывает команду
@param text Текст, в котором может содержаться команда
@param chat_id id чата
@param chat_bot Чат-бот

@returns Пару (итоговый текст, отправлять ли этот текст на обработку ботом)
"""
def process_command(text, chat_id, chat_bot):
    start = '/start'
    restart = '/restart'
    ref = '/make_u_happy_bot'
    
    if text.startswith(start):
        return 'Привет! Хочешь о чём-нибудь поговорить?', False
    elif text.startswith(restart):
        chat_bot.restart(chat_id)
        return 'История диалога очищена', False
    elif text.startswith(ref):
        return text[len(ref):], True
    else:
        return text, True