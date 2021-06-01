import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.web import *
from utils.text import *
from utils.joke_classifier import JokeClassifier
from utils.read_config import ConfigReader
from utils.bad_language import SwearMerger

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
    model = AutoModelForCausalLM.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2").cuda()
    
    @classmethod
    def load_models(cls, joke_model='models/joke_classifier'):
        ## @var joke_classifier
        # Модель предсказания удачности высказывания
        cls.joke_classifier = JokeClassifier(bert_path='models/joke_classifier')
        ## @var has_swear
        # Классификатор наличия ненормативной лексики
        cls.has_swear = SwearMerger()
            
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
        
        ## @var chat_history
        # Содержимое текущего диалога
        self.chat_history = []
        
        ## @var user_input_size
        # Размеры каждой фразы диалога
        self.user_input_size = []
        
        ## @var window_size
        # Число запоминаемых фраз в диалоге
        self.window_size = window_size

        ## @var config_reader
        # Объект, читающий конфигурацию для обработки команд
        self.config_reader = ConfigReader()

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
                max_length=2048,
                no_repeat_ngram_size=3,
                do_sample=True,
                top_k=50,
                top_p=0.9,
                temperature = 0.6,
                mask_token_id=tokenizer.mask_token_id,
                eos_token_id=tokenizer.eos_token_id,
                unk_token_id=tokenizer.unk_token_id,
                pad_token_id=tokenizer.pad_token_id,
                device='cuda'
    ):
        generated = self.model.generate(
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
                    ) # генерируем k возможных ответов
        
        ok_seq = [] # осуществляем отбор по признаку наличия мата
        for cur_chat_history in generated:
            decoded = tokenizer.decode(cur_chat_history[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
            if not has_swear(decoded):
                ok_seq.append([cur_chat_history, decoded])
            else:
                print("We found swear here:", decoded)

        results = [] # ранжируем оставшиеся предложения
        for cur_chat_history, cur_result in ok_seq:
            cur_score = self.joke_classifier(cur_result)
            results.append([cur_chat_history, cur_result, cur_score])
        results.sort(key=lambda x:x[2])

        if len(results) == 0:
            result = 'Хммм'
            token = tokenizer.encode(result, return_tensors="pt").cuda()
            results.append([token, result])
        
        self.chat_history = results[-1][0]

        return results[:2]
    
    ## Обрабатывает текст без команды
    # @param input_user Текст без команды
    # @param cnt_JokeClassifier Число итераций для поиска ответа, 0 - не использовать классификатор
    # @returns Ответ на текст
    def process_text(self, input_user, cnt_JokeClassifier=0):
        input_user = input_user[:256]
        tokenizer = self.tokenizer
        
        # encode the new user input, add parameters and return a tensor in Pytorch
        new_user_input = f"|0|{self.get_length_param(input_user)}|" + input_user + tokenizer.eos_token +  "|1|1|"
        new_user_input_ids = tokenizer.encode(new_user_input, return_tensors="pt").cuda()
        
        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([self.chat_history, new_user_input_ids], dim=-1) if len(self.chat_history) else new_user_input_ids
        
        # generated a response
        result = generate(bot_input_ids, num_return_sequences=cnt_JokeClassifier)
        
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
        command = self.config_reader(text)
        print('Executing command:', command)
        if command != None:
            return eval(command)

        ref = '/make_u_happy_bot'
        if text.startswith(ref):
            text = text[len(ref):]
        return self.process_text(text, cnt_JokeClassifier=5)
    
    ## Забывает все предыдущие фразы в диалоге
    # @returns Сообщение о рестарте
    def restart(self):
        self.chat_history = []
        self.user_input_size = []
        return 'Хорошо, начнём сначала'
