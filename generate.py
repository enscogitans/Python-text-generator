import re
import argparse
import numpy as np
import random
from collections import defaultdict
from fractions import Fraction

encode_type = 'utf-8'  # Наша кодировка


# Позволяет использовать те же основные методы, что и
# открытый через open файл, но только с выводом в консоль
class ConsoleOutAsFile:
    def write(self, line):
        print(line, sep='', end='')

    def close(self):
        return


# Создание парсера
def create_parser():
    parser = argparse.ArgumentParser(
        description='''Это программа для генерации псевдотекста на основе
        модели некоторого текста. Эта модель создаётся программой train.py'''
    )
    parser.add_argument('-m', '--model', required=True,
                        help='Путь к файлу, из которого загружается модель'
                        )
    parser.add_argument('-s', '--seed',
                        help='''Начальное слово. Если не указано, оно будет
                        выбрано случайно'''
                        )
    parser.add_argument('-l', '--length', type=int, default=200,
                        help='Длина генерируемого тектса. По умолчанию - 200'
                        )
    parser.add_argument('-o', '--output',
                        help='''Файл, в который будет записан результат.
                        Если не указан, результат выведется в консоль.'''
                        )
    return parser


# Считывание данных из нашей модели. Возвращает отдельно слова и вероятности
def read_model_from_file(model_path):
    model_file = open('{}\\model.txt'.format(model_path),
                      'r', encoding=encode_type)
    model_words = defaultdict(list)
    model_probabilities = defaultdict(list)
    for line in model_file:
        new_line = list(line.split())
        key = new_line[0]
        for i in range(1, len(new_line), 2):
            model_words[key].append(new_line[i])
            model_probabilities[key].append(Fraction(new_line[i + 1]))

    return model_words, model_probabilities


# Генерация текста и запись его в файл (в stdout)
def generate_and_print_text(model_words, model_probabilities, seed,
                            length, output):
    # Открытие файла
    result_file = 0
    if output is None:
        result_file = ConsoleOutAsFile
    else:
        result_file = open(output, 'w', encoding=encode_type)

    # Выбор первого слова, и его вывод
    prev_word = seed
    if seed is None:
        prev_word = np.random.choice(model_words['&'])
    result_file.write(prev_word)

    # Проверка этого слова на наличие в нашей модели
    # Если нет, переобозначим его как конец предложения
    if seed is not None and prev_word not in model_words.keys():
        prev_word = '&'

    # Генерация и вывод дальнейших слов
    for i in range(1, length):
        next_word = np.random.choice(model_words[prev_word],
                                     p=model_probabilities[prev_word])

        # Ставить ли пробел перед очередным словом?
        # "Сдвиг" текущего слова в предыдущее
        is_space = False
        if re.fullmatch(r'[?!.]+', next_word):
            # Если точка и тп, пробел не нужен
            prev_word = '&'
            is_space = False
        else:
            # Если не запятая и тп, пробел нужен
            if not re.fullmatch(r'[,;:]+', next_word):
                is_space = True
            prev_word = next_word

        # Вывод слова
        if is_space:
            result_file.write(' ')
        result_file.write(next_word)

    result_file.close()


# Считывание аргументов
parser = create_parser()
args = parser.parse_args()

# Извлечение из модели слов и вероятностей
model_words, model_probabilities = read_model_from_file(args.model)

# Создание текста и его вывод
generate_and_print_text(model_words, model_probabilities,
                        args.seed, args.length, args.output)
