import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.telegram.web import *
from utils.telegram.text import get_joke
from utils.JokeClassifier import JokeClassifier

## @package dialogpt
# Содержит класс чат-бота DialoGPT

## @class DialoGPT
# Класс, содержащий в себе интерфейс работы с DialoGPT
class DialoGPT:
    ## @var tokenizer
    # Токенайзер модели DialoGPT
    tokenizer = AutoTokenizer.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2")
    ## @var model
    # Сама модель DialoGPT
    model = AutoModelForCausalLM.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2")
    ## @var joke_classifier
    # Модель JokeClassifier
    joke_classifier = None
    
    
    ## Создаёт объект класса DialoGPT для отдельного чата
    # @param token Токен чат-бота
    # @param chat_id id чата
    # @param window_size Число диалогов, которых запоминает бот
    def __init__(self, token, chat_id, window_size=10):
        ## @var token
        # Токен, по которому бот может связаться с Telegram API
        self.token = token

        ## @var chat_id
        # Id чата, в котором общается бот
        self.chat_id = chat_id
        
        self.joke_classifier = JokeClassifier(bert_path='models/joke_classifier')
        
        ## @var chat_history
        # Содержимое текущего диалога
        self.chat_history = []
        
        ## @var user_input_size
        # Размеры каждой фразы диалога
        self.user_input_size = []
        
        ## @var window_size
        # Число запоминаемых фраз в диалоге
        self.window_size = window_size

    def get_length_param(self, text: str) -> str:
        tokens_count = len(self.tokenizer.encode(text))
        if tokens_count <= 15:
            len_param = '1'
        elif tokens_count <= 50:
            len_param = '2'
        elif tokens_count <= 256:
            len_param = '3'
        else:
            len_param = '-'
        return len_param
    
    ## Передаёт агрументы в функцию self.model.generate и вызывает её
    # @param bot_input_ids Токены, подаваемые self.model.generate на вход
    # @returns Токены, сгенерированные моделью
    def generate(self, bot_input_ids,
                num_return_sequences=1,
                max_length=512,
                no_repeat_ngram_size=3,
                do_sample=True,
                top_k=50,
                top_p=0.9,
                temperature = 0.6,
                mask_token_id=tokenizer.mask_token_id,
                eos_token_id=tokenizer.eos_token_id,
                unk_token_id=tokenizer.unk_token_id,
                pad_token_id=tokenizer.pad_token_id,
                device='cuda'):
        return self.model.generate(
                bot_input_ids,
                num_return_sequences=num_return_sequences,
                max_length=max_length,
                no_repeat_ngram_size=no_repeat_ngram_size,
                do_sample=do_sample,
                top_k=top_k,
                top_p=top_p,
                temperature = temperature,
                mask_token_id=mask_token_id,
                eos_token_id=eos_token_id,
                unk_token_id=unk_token_id,
                pad_token_id=pad_token_id,
                device=device,
            )
    
    ## Обрабатывает текст без команды
    # @param input_user Текст без команды
    # @param cnt_JokeClassifier Число итераций для поиска ответа, 0 - не использовать классификатор
    # @returns Ответ на текст
    def process_text(self, input_user, cnt_JokeClassifier=0):
        input_user = input_user[:256]
        tokenizer = self.tokenizer
        
        # encode the new user input, add parameters and return a tensor in Pytorch
        new_user_input = f"|0|{self.get_length_param(input_user)}|" + input_user + tokenizer.eos_token +  "|1|1|"
        new_user_input_ids = tokenizer.encode(new_user_input, return_tensors="pt")
        
        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([self.chat_history, new_user_input_ids], dim=-1) if len(self.chat_history) else new_user_input_ids
        
        # generated a response
        if (cnt_JokeClassifier > 0):
            results = []
            for iter in range(cnt_JokeClassifier):
                cur_chat_history = self.generate(bot_input_ids)
                cur_result = tokenizer.decode(cur_chat_history[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
                cur_score = self.joke_classifier(cur_result)
                results.append([cur_chat_history, cur_result, cur_score])
            results.sort(key=lambda x:x[2])
            
            self.chat_history = results[-1][0]
            result = results[-1][1]
            worst_score = results[0][2]
            best_score = results[-1][2]
            for elem in results:
                print('Possible answer:', elem[1], elem[2] * 100)
            print('Best score:', best_score * 100, 'Worst score:', worst_score * 100)
        else:
            self.chat_history = self.generate(bot_input_ids)
            result = tokenizer.decode(self.chat_history[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        
        self.user_input_size.append(new_user_input_ids.shape[-1])
        if len(self.user_input_size) > self.window_size:
            self.chat_history = self.chat_history[:, self.user_input_size[0]:]
            self.user_input_size = self.user_input_size[-self.window_size:]
 
        print('Length of current chat history:', self.chat_history.shape[-1])
        return result
    
    ## Обрабатывает текст с возможной командой
    # @param text Текст, в котором может содержаться команда
    # @returns Итоговый текст
    def get_response(self, text):
        start = '/start'
        restart = '/restart'
        advice = '/advice'
        joke = '/joke'
        cat = '/cat'
        ref = '/make_u_happy_bot'
        help_cmd = '/help'

        if text.startswith(start):
            return 'Привет! Хочешь о чём-нибудь поговорить?'
        elif text.startswith(restart):
            self.restart()
            return 'Предыдущие сообщения забыты'
        elif text.startswith(advice):
            return get_advice()
        elif text.startswith(cat):
            send_cat(self.token, self.chat_id)
            return ''
        elif text.startswith(joke):
            return get_joke()
        elif text.startswith(help_cmd):
            return '''
Привет!
Я чат-бот, который улучшает людям настроение)
Со мной легко работать: ты пишешь сообщение, а я на него отвечаю.

Список полезных команд:
/advice - Дать совет
/cat - Выдать фотографию котика
/joke - Рассказать возможно нецензурный анекдот
/help - Вывести это сообщение
/restart - Забыть предыдущие сообщения
'''
        
        if text.startswith(ref):
            text = text[len(ref):]
        return self.process_text(text, cnt_JokeClassifier=5)
    
    ## Забывает все предыдущие фразы в диалоге
    def restart(self):
        self.chat_history = []
        self.user_input_size = []
