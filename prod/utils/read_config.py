import yaml

from utils.text import clear_text

## @package read_config
# Содержит класс CongigReader
 
## @class ConfigReader
# Позволяет считывать информацию из конфига для rule-based ответов
class ConfigReader:
    ## Создает объект класса CongigReader
    # @param config_path Путь до конфига
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)

    ## Обрабатывает словарь и говорит что из него надо вернуть
    # @param desc словарь из self.config
    # @returns Итоговый текст
    def get_response(self, desc):
        return desc['execute']

    ## Обрабатывает текст с возможной командой
    # @param text Текст, в котором может содержаться команда
    # @returns Команду, которую нужно исполнить,
    # либо None, если в тексте нет команды
    def parse_command(self, text):
        text = clear_text(text)
        
        for option, desc in self.config['options'].items():
            if text.startswith('/' + option):
                return self.get_response(desc)
            if 'special_alias' in desc:
                for alias in desc['special_alias']:
                    if alias.lower() in text:
                        print(alias.lower(), text)
                        return self.get_response(desc)
            if 'common_alias' in desc:
                for verb in self.config['verbs']:
                    if verb in text:
                        for alias in desc['common_alias']:
                            if alias in text:
                                return self.get_response(desc)
        return None

    ## Обрабатывает текст с возможной командой,
    # полный аналог self.parse_command, используется для
    # унификации интерфейса
    # @param text Текст, в котором может содержаться команда
    # @returns Итоговый текст
    def __call__(self, text):
        return self.parse_command(text)

    ## Возвращает названия и описания всех опций из self.config['Options']
    # @param context Текст, в который надо вставить описания опций
    # @param to_replace токен, который необходимо заменить на описания опций
    # @returns Итоговый текст
    def get_options(self, context='', to_replace='get_options'):
        text = ''
        for option, desc in self.config['options'].items():
            text += '/{} - {}\n'.format(option, desc['description'])
        if to_replace in context:
            return context.replace(to_replace, text)
        else:
            return context + text