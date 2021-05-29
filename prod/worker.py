from utils.telegram.dialogpt import DialoGPT
from utils.telegram.web import *
from utils.telegram.text import *


class Worker:
    def __init__(self, token):
        self.chat_bots = {}
        self.offset = 0
        self.token = token

    def work_once(self):
        result = get_updates(self.token, self.offset)
        if len(result['result']) == 0:
            return

        result = result['result'][0]
        if 'message' in result:
            message = result['message']
            chat_id = message['chat']['id']
            
            if chat_id not in self.chat_bots:
                self.chat_bots[chat_id] = DialoGPT()
            chat_bot = self.chat_bots[chat_id]

            text = get_text(message)
            print('Working with chat:', chat_id)
            print('Received message:', text)
            
            to_send = chat_bot.get_response(text)
            if len(to_send) > 0:
                send_message(self.token, chat_id, to_send)
                print('Sent message:', to_send)
            print()
        self.offset = int(result['update_id']) + 1

    def work(self):
        try:
            print('Chat-bot started')
            while True:
                self.work_once()
        except KeyboardInterrupt:
            print('Chat-bot stopped')