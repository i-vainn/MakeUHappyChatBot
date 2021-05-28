import emoji
import unicodedata
from google_trans_new import google_translator

translator = google_translator()  
def eng_to_rus(text):
    return translator.translate(text,lang_tgt='ru')

def emoji_to_text(emoji):
    return eng_to_rus(unicodedata.name(emoji).lower())

def de_emojify(text):
    result = ''
    for sym in text:
        if emoji.emoji_count(sym):
            result += " " + emoji_to_text(sym) + " "
        else:
            result += sym
    return ' '.join(filter(bool, result.split(' ')))