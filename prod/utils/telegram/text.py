from .translate_emoji import de_emojify

## @package text
# Cодержит функции для обработки текстов, полученных по Telegram API.

## Извлекает текст из сообщения
# @param message Получаемое сообщение из Telegram API
# @returns Текст из сообщения
def extract_text(message):
    if 'text' in message:
        return message['text']
    elif 'caption' in message:
        return message['caption']
    elif 'sticker' in message:
        return message['sticker']['emoji']
    else:
        return ''


## Получает и обрабатывает текст из сообщения
# @param message Получаемое сообщение из Telegram API
# @returns Обработанный текст
def get_text(message):
    return de_emojify(extract_text(message))