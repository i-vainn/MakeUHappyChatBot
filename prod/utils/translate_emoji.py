import emoji
import unicodedata
from google_trans_new import google_translator

## @package translate_emoji
# Содержит материалы для обработки эмоджи

## @var translator
# Переводчик
translator = google_translator()

## Переводит текст с английского на русский
# @param text Текст на английском
# @returns Текст на русском
def eng_to_rus(text):
    return translator.translate(text, lang_tgt='ru')

## Переводит эмоджи в текст на русском
# @see https://unicode.org/emoji/charts/full-emoji-list.html
# @param emoji Эмоджи
# @returns Значение эмоджи на русском
def emoji_to_text(emoji):
    try:
        return eng_to_rus(unicodedata.name(emoji).lower())
    except:
        return ''


## Переводит эмоджи в тексте на русский язык
# @see https://unicode.org/emoji/charts/full-emoji-list.html
# @param text Текст на русском
# @returns Текст на русском без эмоджи
def de_emojify(text):
    result = ''
    for sym in text:
        if emoji.emoji_count(sym):
            result += " " + emoji_to_text(sym) + " "
        else:
            result += sym
    return ' '.join(filter(bool, result.split(' ')))