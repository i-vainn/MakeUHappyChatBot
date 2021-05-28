import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
class DialoGPT:
    tokenizer = AutoTokenizer.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2")
    model = AutoModelForCausalLM.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2")
    
    """
    @param window_size Размер окна диалогов
    """
    def __init__(self, window_size=10):
        self.chat_history = []
        self.user_input_size = []
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
                device='cuda',
            )
    
    """
    Обрабатывает текст без команды
    @param input_user Текст без команды
    @returns Ответ на текст
    """
    def process_text(self, input_user):
        input_user = input_user[:256]
        tokenizer = self.tokenizer
        
        # encode the new user input, add parameters and return a tensor in Pytorch
        new_user_input = f"|0|{self.get_length_param(input_user)}|" + input_user + tokenizer.eos_token +  "|1|1|"
        new_user_input_ids = tokenizer.encode(new_user_input, return_tensors="pt")
        
        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([self.chat_history, new_user_input_ids], dim=-1) if len(self.chat_history) else new_user_input_ids
        
        # generated a response
        self.chat_history = self.generate(bot_input_ids)
        
        result = tokenizer.decode(self.chat_history[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        
        self.user_input_size.append(new_user_input_ids.shape[-1])
        if len(self.user_input_size) > self.window_size:
            self.chat_history = self.chat_history[:, self.user_input_size[0]:]
            self.user_input_size = self.user_input_size[-self.window_size:]
 
        print('Length of current chat history:', self.chat_history.shape[-1])
        return result
    
    """
    Обрабатывает текст с возможной командой
    @param text Текст, в котором может содержаться команда

    @returns Итоговый текст
    """
    def get_response(self, text):
        start = '/start'
        restart = '/restart'
        meme = '/meme'
        ref = '/make_u_happy_bot'
        help_cmd = '/help'

        if text.startswith(start):
            return 'Привет! Хочешь о чём-нибудь поговорить?'
        elif text.startswith(restart):
            self.restart()
            return 'Предыдущие сообщения забыты'
        elif text.startswith(meme):
            return 'Учёные доказали, что сначала появились чёрные, а потом люди\n- Lorem Ipsum'
        elif text.startswith(ref):
            return self.process_text(text[len(ref):])
        elif text.startswith(help_cmd):
            return '''
Привет!
Я чат-бот, который улучшает людям настроение)
Со мной легко работать: ты пишешь сообщение, а я на него отвечаю.

Список полезных команд:
/restart - Забыть предыдущие сообщения
/meme - Скинуть случайный мем на английском
/help - Вывести это сообщение
'''
        else:
            return self.process_text(text)
    
    def restart(self):
        self.chat_history = []
        self.user_input_size = []