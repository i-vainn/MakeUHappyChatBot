import json

from prod.utils.telegram.text import clear_text

## @package read_config
# Содержит класс CongigReader
 
## @class CongigReader
# Позволяет 
# считывать информацию из конфига для rule-based ответов
class CongigReader:
    ## Создает объект класса CongigReader
    # @param config_path Путь до конфига
    def __init__(self, config_path='config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)


    ## Обрабатывает словарь и говорит что из него надо вернуть
    # @param desc словарь из self.config
    # @returns Итоговый текст
    def get_response(self, desc):
        if 'execute' in desc:
            return self.execute(desc)
        elif 'output_text' in desc:
            return desc['output_text']
        else:
            return ""

    ## Обрабатывает текст с возможной командой
    # @param text Текст, в котором может содержаться команда
    # @returns Итоговый текст
    def parse_command(self, text):
        text = clear_text(text)
        
        for option, desc in self.config['Options'].items():
            if text.index('/' + option) == 0:
                return self.get_response(desc)
            elif 'special_alias' in desc:
                for alias in desc['special_alias']:
                    if text.count(alias.lower()):
                        return self.get_response(desc)
            elif 'common_alias' in desc:
                for verb in self.config['Verbs']:
                    for alias in desc['common_alias']:
                        new_alias = verb + ' ' + alias
                        if text.count(new_alias.lower()):
                            return self.get_response(desc)

    ## Обрабатывает текст с возможной командой,
    # полный аналог self.parse_command, используется для
    # унификации интерфейса
    # @param text Текст, в котором может содержаться команда
    # @returns Итоговый текст
    def __call__(self, text):
        self.parse_command(text)

    ## Печатает названия и описания всех опций из self.config['Options']
    # @param context Текст, в который надо вставить описания опций
    # @param to_replace токен, который необходимо заменить на описания опций
    # @returns Итоговый текст
    def print_options(self, context='', to_replace='print_options'):
        text = ''
        for option, desc in self.config['Options'].items():
            text += '/{} - {}\n'.format(option, desc['description'])
        if to_replace in context:
            return context.replace(to_replace, text)
        else:
            return context + text

    ## Обрабатывает словарь и говорит, какую команду выполнить/выполняет команду
    # @param desc словарь из self.config
    # @returns итоговый текст если для исполнения команды не требуется
    # обращение к API и {API NAME}_API иначе
    def execute(self, desc):
        if desc['execute'] == 'print_options':
            return self.print_options(
                desc['output_text'] if 'output_text' in desc else ''
            )
        elif desc['execute'] == 'print_help':
            return self.execute(self.config['Options']['help'])
        elif 'api' in desc['execute']:
            return desc['execute'].upper()


                    