from utils.translate_emoji import de_emojify
import random
import re
import string

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

## Выводит случайный комплимент из набора случайных комплиментов
# @returns Случайный комплимент
def get_compliment():
    compliments = open('../data/compliments.txt').readlines()
    return random.choice(compliments).strip()

## Выводит номер психологической помощи
# @returns номер психологической помощи
def get_sos():
    return "Вот телефон психологической поддержки, +7 (499) 173-09-09, ты не один"


## Выводит случайный анекдот из набора случайных анекдотов
# @returns Случайный анекдот
def get_joke():
    jokes = open('../data/jokes_good.txt').readlines()
    return random.choice(jokes).strip()


## Возвращает сообщение о помощи
# @param config_reader ConfigReader, в котором содержится информация о командах
# @returns Сообщение о помощи
def get_help_message(config_reader):
    start_message = '''
Привет!
Я чат-бот, который улучшает людям настроение)
Со мной легко работать: ты пишешь сообщение, а я на него отвечаю.
Список полезных команд:
get_options
'''
    return config_reader.get_options(context=start_message)


## Возвращает сообщение о старте
# @returns Сообщение о старте
def get_start_message():
    return 'Привет! Хочешь о чём-нибудь поговорить?'


## Очищает текст от заданных символов.
# Например, может использоваться для удаления пунктуации
# с параметром symbols по умолчанию.
# @param text - Текст, который хотим почистить
# @param symbols - строка, содержащая все символы, которые хотим удалить
# @param dont_kill_slash - если True, то символ `/` из строки не удаляем
# @returns Очищенный текст
def clear_text(text, symbols=None, dont_kill_slash=True):
    if symbols is None:
        symbols = string.punctuation
    if dont_kill_slash:
        symbols = symbols.replace('/', '')
    return re.sub(f'[{symbols}]', '', text).replace('ё', 'е').lower()
