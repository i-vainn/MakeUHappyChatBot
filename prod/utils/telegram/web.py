import requests

## @namespace web
# Содержит функции для взаимодействия с веб-сервисами

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