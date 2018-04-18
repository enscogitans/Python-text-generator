# testing git
import re
import argparse
from fractions import Fraction
from collections import defaultdict

# Наш алфавит и используемая кодировка
alphabet = re.compile(u'[ёЁа-яА-Я0-9]+[-]?[ёЁа-яА-Я0-9]+|[.,?!;:]+')
encode_type = 'utf-8'


# Создание парсера
def create_parser():
    parser = argparse.ArgumentParser(
        description='''Это программа для создания модели введённого текста.
        Созданная модель в дальнейшем используется для генерации псевдотекста
        программой generate.py'''
    )
    parser.add_argument('-id', '--input-dir',
                        help='''Директория, в которой лежит коллекция документов.
                        Если не указано, ввод текта осуществляется из консоли.
                        В данном случае необходимо закончить ввод данных вводом
                        строки: '////' '''
                        )
    parser.add_argument('-m', '--model', required=True,
                        help='Путь к файлу, в который сохраняется модель')
    parser.add_argument('-lc', '--lowercase', type=bool, default=False,
                        help='Приводить тексты к lowercase')
    return parser


# Построчно генерирует строки из данного файла (stdin)
def line_generator(file_path):
    if file_path is not None:
        with open(file_path, 'r', encoding=encode_type) as file:
            for line in file:
                yield str(bytes(line, encode_type).decode(encode_type))
    else:
        while True:
            line = input()
            if line == '////':
                return
            yield line


# Обрабатывает строки, возвращая отдельные слова, согласованные
# с алфавитом, и, при необходимости, в нижнем регистре
def token_generator(lines, is_lower):
    for line in lines:
        for token in alphabet.findall(line):
            yield token.lower() if is_lower else token


# По словам (токенам) возвращает биграммы
def bigram_generator(tokens):
    t0 = '&'
    for t1 in tokens:
        yield t0, t1
        if re.fullmatch(r'[?!.]+', t1):
            t0 = '&'
        else:
            t0 = t1


# Подсчёт количества слов и пар слов из биграмм соответственно
def count_words_and_pairs(bigrams):
    word_freq = defaultdict(lambda: 0)
    pair_freq = defaultdict(lambda: 0)

    last_symbol = '&'
    word_freq['&'] = 1
    for (t0, t1) in bigrams:
        if re.fullmatch(r'[?!.]+', t1):
            word_freq['&'] += 1
        word_freq[t1] += 1
        pair_freq[(t0, t1)] += 1
        last_symbol = t1

    if re.fullmatch(r'[?!.]+', last_symbol):
        pair_freq[('&', '&')] += 1
    else:
        pair_freq[(last_symbol, '&')] += 1
    return word_freq, pair_freq


# Инициализация нашей модели. По ключу хранится лист слов,
# которые могут идти после него с указаним вероятности (в виде рац. дроби)
def initialise_model(word_freq, pair_freq):
    model = dict()
    for (t0, t1), freq in pair_freq.items():
        if t0 in model:
            model[t0].append((t1, Fraction(freq, word_freq[t0])))
        else:
            model[t0] = [(t1, Fraction(freq, word_freq[t0]))]
    return model


# Сохранение модели в файл model.txt в указанной папке
def save_model(model, model_path):
    with open('{}\\model.txt'.format(model_path), 'w',
              encoding=encode_type) as model_file:
        for key, lst in model.items():
            model_file.write(key)
            for (word, freq) in lst:
                model_file.write(' {} {}'.format(word, freq))
            model_file.write('\n')


# Считывание аргументов
parser = create_parser()
args = parser.parse_args()

# Инициализация генератора биграмм
lines = line_generator(args.input_dir)
tokens = token_generator(lines, args.lowercase)
bigrams = bigram_generator(tokens)

# Подсчёт количества слов и пар слов соответственно
word_freq, pair_freq = count_words_and_pairs(bigrams)

# Инициализация и сохранение нашей модели
model = initialise_model(word_freq, pair_freq)
save_model(model, args.model)
