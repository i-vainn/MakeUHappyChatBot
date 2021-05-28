import requests

api_url = 'https://api.telegram.org/bot1853926901:AAHs-iYO-hp559x52L67egfEZ8FzLo26WAk/'

"""
Получает новые сообщения с сервера.
Если сообщений нет, то возвращает пустой массив.
@see https://core.telegram.org/bots/api#getupdates

@param offset Параметр offset в Telegram API
@returns Массив с последними сообщениями
"""
def get_updates(offset):
    get_updates_url = f'{api_url}getUpdates?offset={offset}'
    return requests.get(get_updates_url).json()

"""
Отправляет сообщение в чат.
@see https://core.telegram.org/bots/api#sendmessage

@param chat_id id чата
@param text Отправляемое сообщение
"""
def send_message(chat_id, text):
    send_message_url = f'{api_url}sendMessage?chat_id={chat_id}&text={text}'
    requests.get(send_message_url)