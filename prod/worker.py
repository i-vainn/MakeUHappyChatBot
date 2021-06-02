from utils.dialogpt import DialoGPT
from utils.joke_classifier import JokeClassifier
from utils.bad_language import SwearMerger
from utils.web import *
from utils.text import *

from pathlib import Path
import gdown
from transformers import AutoModelForCausalLM, AutoTokenizer


## @package prod.worker
# Содержит класс Worker

## @class Worker
# Класс для работы с Telegram API
class Worker:
    
    ## Создаёт объект класса Worker и достаёт необходимые для работы файлы
    # @param token Токен для работы с Telegram API
    def __init__(self, token):
        ## @var chat_bots
        # Словарь из id чата в чат-бот по работе с этим чатом
        self.chat_bots = {}
        
        ## @var offset
        # Текущее отклонение от сообщений
        # Необходимо, чтобы старые сообщения не обрабатывались
        self.offset = 0
        
        ## @var token
        # Токен для работы с Telegram API
        self.token = token

        ## Загрузка модели с гугл-диска
        Path('models/joke_classifier').mkdir(parents=True, exist_ok=True)
        url = 'https://drive.google.com/uc?id=1-3IxKzOlWu32uZ-mk2OI7mF6S4101b8n'
        gdown.download(url, 'models/joke_classifier/config.json', quiet=False)
        url = 'https://drive.google.com/uc?id=1-6AN-3KbLHNH6w0Kmy3Hbp2WEWdCfhdA'
        gdown.download(url, 'models/joke_classifier/pytorch_model.bin', quiet=False)

        ## Определение статических атрибутов класса DialoGPT
        DialoGPT.joke_classifier = JokeClassifier(bert_path='models/joke_classifier')
        DialoGPT.has_swear = SwearMerger()
        DialoGPT.tokenizer = AutoTokenizer.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2")
        DialoGPT.model = AutoModelForCausalLM.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2").cuda()
        

    ## Получает текущее состояние чат-бота и обрабатывает одно сообщение
    def work_once(self):
        result = get_updates(self.token, self.offset)
        if len(result['result']) == 0:
            return

        result = result['result'][0]
        if 'message' in result:
            message = result['message']
            chat_id = message['chat']['id']
            
            if chat_id not in self.chat_bots:
                self.chat_bots[chat_id] = DialoGPT(self.token, chat_id)
            chat_bot = self.chat_bots[chat_id]

            text = get_text(message)
            from_user = message['from']
            print('Received message from:', from_user['first_name'] if 'first_name' in from_user else '', from_user['last_name'] if 'last_name' in from_user else '')
            print('Working with chat:', chat_id)
            print('Received message:', text)
            
            to_send = chat_bot.get_response(text)
            if len(to_send) > 0:
                send_message(self.token, chat_id, to_send)
                print('Sent message:', to_send)
            print()
        self.offset = int(result['update_id']) + 1

    ## Основной цикл работы программы
    def work(self):
        try:
            print('Chat-bot started')
            while True:
                self.work_once()
        except KeyboardInterrupt:
            print('Chat-bot stopped')