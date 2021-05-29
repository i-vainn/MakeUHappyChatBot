from .translate_emoji import de_emojify
import random

## @namespace text
# Содержит функции для работы с текстами и с Telegram

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


## Выводит случайный анекдот из набора случайных анекдотов
# @returns Случайный анекдот
def get_joke():
    jokes = open('../data/jokes_good.txt').readlines()
    return random.choice(jokes).strip()