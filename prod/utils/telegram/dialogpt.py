import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
class DialoGPT:
    tokenizer = AutoTokenizer.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2")
    model = AutoModelForCausalLM.from_pretrained("Grossmend/rudialogpt3_medium_based_on_gpt2")
    chat_history = {}

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

    """
    Возвращает ответ на текст, введённый пользователем
    @param input_user Текст, введённый пользователе
    @param chat_id id чата, куда был введен ответ или -1, если чата нет
    @returns Ответ на текст, введённый пользователем
    """
    def get_response(self, input_user, chat_id):
        input_user = input_user[:256]
        tokenizer = self.tokenizer
        
        # encode the new user input, add parameters and return a tensor in Pytorch
        new_user_input = f"|0|{self.get_length_param(input_user)}|" + input_user + tokenizer.eos_token +  "|1|1|"
        new_user_input_ids = tokenizer.encode(new_user_input, return_tensors="pt")

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([self.chat_history[chat_id], new_user_input_ids], dim=-1) if chat_id in self.chat_history else new_user_input_ids

        # generated a response
        self.chat_history[chat_id] = self.model.generate(
            bot_input_ids,
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
            device='cuda',
        )
        print(len(self.chat_history[chat_id]))
        
        result = tokenizer.decode(self.chat_history[chat_id][:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        if chat_id == -1:
            self.restart(-1)
        
        return result
    
    def restart(self, chat_id):
        if chat_id in self.chat_history:
            del self.chat_history[chat_id]