from dialogpt import DialoGPT
from utils.telegram.web import *
from utils.telegram.text import *


class Worker:
    def __init__(self):
        self.chat_bot = DialoGPT()
        self.offset_file = open('offset.txt', 'r+')
        self.offset = int(offset_file.read())

    
    def work_once(self):
        result = get_updates(self.offset)
        if len(result['result']) == 0:
            return

        result = result['result'][0]
        if 'message' in result:
            message = result['message']
            chat_id = message['chat']['id']

            text = get_text(message)
            print(text)
            text, should_send = process_command(text, chat_id)
            
            if should_send:
                text = chat_bot.get_response(text, chat_id)

            if len(text) > 0:
                send_message(chat_id, text)
        offset = int(result['update_id']) + 1
        offset_file.truncate()
        offset_file.write(str(offset))


    def work(self):
        print('Started')
        try:
            while True:
                self.work_once()
        except KeyboardInterrupt:
            print('Stopped')