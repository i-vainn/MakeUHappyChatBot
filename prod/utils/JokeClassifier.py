from transformers import BertTokenizer
from transformers import BertForSequenceClassification

## @class JokeClassifier
# Класс для определения является ли сообщение шуткой
class JokeClassifier:
    ## Создаёт объект класса JokeClassifier
    # @param tokenizer_path Путь к токенайзеру
    # @param bert_path Путь к модели BERT
    def __init__(self, 
                 bert_path,
                 tokenizer_path = 'DeepPavlov/rubert-base-cased',
                 ):
        ## @var tokenizer
        # Токенайзер
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
        ## @var model
        # Модель классификатора 
        self.model = BertForSequenceClassification.from_pretrained(bert_path)

    ## Выдаёт вероятность наличия шутки во входном сообщении
    # @param sentence Входное предложение
    # @returns Вероятность наличия шутки
    def __call__(self,
                 sentence):
        tokenized = self.tokenizer(sentence, return_tensors="pt")
        outputs = self.model(**tokenized)
        prob = torch.softmax(outputs['logits'], dim=1);
        return prob[0][1].item()