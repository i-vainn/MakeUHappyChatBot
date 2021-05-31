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


## @var verbs
# Глаголы для активации команд
verbs = [
    'дай',
    'скинь',
    'расскажи',
    'покажи',
    'скажи',
    'го',
    'давай',
    'хочу',
    'напиши',
    'еще',
    'желаю'
]


## @var cmd_to_text
# Словарь из пар (команда, способы скрыть команду в тексте)
cmd_to_text = {
    '/restart' : [
        'забудь все что я сказал',
        'забудь все, что я сказал'
    ],

    '/advice' : [
        'совет',
        'случайный совет'
    ],

    '/joke' : [
        'шутку',
        'анекдот',
        'случайную шутку',
        'случайный анекдот',
        'шутейку',
        'смешнявку',
        'прикол',
        'смешное',
        'смеяться'
    ],

    '/cat' : [
        'котиков',
        'котика',
        'картинки котиков',
        'картинку котика',
        'кошек',
        'кошку',
        'картинки кошек',
        'картинку кошки',
    ]
}

## Определяет, скрыта ли команда в тексте.
# Если да, то заменяет текст на эту команду.
# @param Текст пользователя
# @returns Текст пользователя или команда пользователя
def parse_command(text):
    text_parse = text.strip()
    text_parse = text_parse.replace('ё', 'е').lower()
    for key in cmd_to_text.keys():
        if text.startswith(key):
            return key
        for substr in cmd_to_text[key]:
            if key == '/restart' and substr in text:
                return key
            for verb in verbs:
                if verb in text and substr in text:
                    return key
    return text