from transformers import BertForSequenceClassification, BertTokenizer
from pymystem3 import Mystem

import re
import string

class ToxicClassifier:
    def __init__(self, model_path='sismetanin/rubert-toxic-pikabu-2ch'):
        self.toxic_tokenizer = BertTokenizer.from_pretrained(model_path)
        self.toxic_bert = BertForSequenceClassification.from_pretrained(model_path)

    def __call__(self, message):
        return self.is_toxic(message)
    
    def is_toxic(self, message):
        return self.how_toxic(message).argmax()

    def how_toxic(self, message):
        token = self.toxic_tokenizer.encode(message, return_tensors="pt")
        res = self.toxic_bert(token)
        return torch.softmax(res['logits'].detach(), 1)

class SwearDetector:
    def __init__(self, path_or_list='../data/swear.txt', use_stemming=True):
        self.lemmatizer = None
        if use_stemming:
            self.lemmatizer = Mystem()
        
        self.blocklist = None
        if type(path_or_list) == str:
            with open(path_or_list, 'r') as f:
                self.blocklist = [x[:-1] for x in f.readlines()]
        else:
            assert type(path_or_list) == list, "Wrong path_or_list type: expected str or list, found {}".format(type(path_or_list))
            self.blocklist = path_or_list

    def __call__(self, sentence):
        return self.has_swear(sentence)

    def clear(self, sentence):
        return re.sub(f'[{string.punctuation}]', '', sentence)
        
    def has_swear(self, sentence):
        clean = self.clear(sentence)
        for word in clean.lower().split():
            if self.lemmatizer:
                word = self.lemmatizer.lemmatize(word)[0]
            if word in self.blocklist:
                return True
        return False

    def find_swear(self, sentence):
        clean = self.clear(sentence)
        swear = []
        for idx, word in enumerate(clean.lower().split()):
            lemmatized = word
            if self.lemmatizer:
                lemmatized = self.lemmatizer.lemmatize(word)[0]
            if lemmatized in self.blocklist:
                swear.append(word)
        return swear

class SwearMerger:
    def __init__(self, classifiers=[ToxicClassifier(), SwearDetector()], is_soft=False):
        self.classifiers = classifiers
        self.is_soft = is_soft

    def __call__(self, sentence):
        decision = not self.is_soft
        for clf in self.classifiers:
            if self.is_soft:
                decision |= clf(sentence)
            else:
                decision &= clf(sentence)
        return decision