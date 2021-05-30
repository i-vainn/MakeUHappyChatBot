import requests

## @namespace web
# Содержит функции для взаимодействия с веб-сервисами

## @var api_url
# Ссылка на Telegram API
api_url = 'https://api.telegram.org/'


## Получает новые сообщения с сервера.
# Если сообщений нет, то возвращает пустой массив.
# @see https://core.telegram.org/bots/api#getupdates
# @param token Токен для чат-бота
# @param offset Параметр offset в Telegram API
# @returns Массив с последними сообщениями
def get_updates(token, offset):
    get_updates_url = f'{api_url}{token}/getUpdates?offset={offset}'
    return requests.get(get_updates_url).json()


## Отправляет сообщение в чат.
# @see https://core.telegram.org/bots/api#sendmessage
# @param token Токен для чат-бота
# @param chat_id id чата
# @param text Отправляемое сообщение
def send_message(token, chat_id, text):
    send_message_url = f'{api_url}{token}/sendMessage?chat_id={chat_id}&text={text}'
    requests.get(send_message_url)


## Отправляет фотографию в чат.
# @param token Токен для чат-бота
# @param chat_id id чата
# @param url Ссылка на фотографию
def send_photo(token, chat_id, url):
    send_photo_url = f'{api_url}{token}/sendPhoto?chat_id={chat_id}&photo={photo}'
    requests.get(send_photo_url)


## Вовзращает ссылку на случайную картинку с котиком
# @returns Ссылка на картинку с котиком
def get_cat():
    return 'https://i.redd.it/yzwguryrul421.jpg'


## Достаёт случайный совет
# @see https://fucking-great-advice.ru/api
# @returns Случайный совет в виде строки
def get_advice():
    magic_word = 'блять'
    while True:
        possible_advice = requests.get('http://fucking-great-advice.ru/api/random').json()
        advice = possible_advice['text']
        if magic_word in advice:
            advice = ''.join(advice.split(magic_word))
            advice = ' '.join(filter(bool, advice.split()))
            return advice

