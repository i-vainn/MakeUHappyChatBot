from transformers import BertForSequenceClassification, BertTokenizer

class ToxicClassifier:
    def __init__(self, model_path='sismetanin/rubert-toxic-pikabu-2ch'):
        self.toxic_tokenizer = BertTokenizer.from_pretrained(model_path)
        self.toxic_bert = BertForSequenceClassification.from_pretrained(model_path)
    
    def is_toxic(self, message):
        return self.how_toxic(message).argmax()

    def how_toxic(self, message):
        token = self.toxic_tokenizer.encode(message, return_tensors="pt")
        res = self.toxic_bert(token)
        return torch.softmax(res['logits'].detach(), 1)
