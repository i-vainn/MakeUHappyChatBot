import torch
from transformers import BertTokenizer
from transformers import BertForSequenceClassification

## @package joke_classifier
# Содержит класс для определения шуток JokeClassifier

## @class JokeClassifier
# Класс для определения, является ли сообщение шуткой
class JokeClassifier:
    ## @var tokenizer
    # Токенайзер
    tokenizer = None
    
    
    ## @var model
    # Модель классификатора 
    model = None

    ## Создаёт объект класса JokeClassifier
    # @param tokenizer_path Путь к токенайзеру
    # @param bert_path Путь к модели BERT
    def __init__(self, 
                 bert_path,
                 tokenizer_path = 'DeepPavlov/rubert-base-cased',
                 ):
        
        if self.tokenizer != None:
            self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
        
        if self.model != None:
            self.model = BertForSequenceClassification.from_pretrained(bert_path).cuda()

    ## Выдаёт вероятность наличия шутки во входном сообщении
    # @param sentence Входное предложение
    # @returns Вероятность наличия шутки
    def __call__(self,
                 sentence):
        tokenized = self.tokenizer(sentence, return_tensors="pt").to(device='cuda')
        outputs = self.model(**tokenized)
        prob = torch.softmax(outputs['logits'], dim=1);
        return prob[0][1].item()