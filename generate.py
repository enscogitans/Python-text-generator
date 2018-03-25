import re
import numpy as np
import random
from collections import defaultdict
from fractions import Fraction

# Наша кодировка
encodeType = 'utf-8'


# Возвращает пользовательские аргументы
def get_args():
    line = input().split()

    model_dir = str()
    seed = ''
    length = 200
    output_file = str()
    is_help = False

    i = 0
    while i < len(line):
        if line[i] == '--model':
            model_dir = line[i + 1]
            i += 1
        elif line[i] == '--seed':
            seed = line[i + 1]
            i += 1
        elif line[i] == '--length':
            length = int(line[i + 1])
            i += 1
        elif line[i] == '--output':
            output_file = line[i + 1]
            i += 1
        elif line[i] == '--help':
            is_help = True
        i += 1

    return model_dir, seed, length, output_file, is_help


# Ввод аргументов
print('--help, для описания команд')
modelDirectory, firstWord, length, outputFile, isHelp = get_args()
while isHelp:
    if isHelp:
        print('''Введите:
                 --model <Папка для загрузки модели>
                (Опционально) --output <Путь до файла, в который будет сохранён текст>, 
                    иначе вывод в консоль
                (Опционально) --seed <Слово>, задаёт первое слово текста
                (Опционально) --length <Число>, задаёт длину текста, иначе 200
                (Опционально) --help, для описания команд''')
    modelDirectory, firstWord, length, outputFile, isHelp = get_args()


# Считывание данных из нашей модели
modelFile = open('{}\\model.txt'.format(modelDirectory), 'r', encoding=encodeType)

modelWords = defaultdict(list)
modelProbabilities = defaultdict(list)
for line in modelFile:
    newLine = list(line.split())
    key = newLine[0]
    for i in range(1, len(newLine), 2):
        modelWords[key].append(newLine[i])
        modelProbabilities[key].append(Fraction(newLine[i+1]))


# Генерация текста и запись его в файл (в stdout)
result = 0
if outputFile != '':
    result = open(outputFile, 'w', encoding=encodeType)

prevWord = firstWord    # Выбор первого слова
if firstWord == '':
    prevWord = np.random.choice(modelWords['&'], p=modelProbabilities['&'])

if outputFile != '':    # Печать первого слова
    result.write(prevWord)
else:
    print(prevWord, sep='', end='')

if firstWord != '' and firstWord not in modelWords.keys():
    # Проверка на корректность первого слова
    prevWord = '&'


for i in range(length - 1):     # Генерация последующих слов
    nextWord = np.random.choice(modelWords[prevWord], p=modelProbabilities[prevWord])
    isSpace = False     # Ставить ли пробел перед очередным словом

    if re.fullmatch(r'[?!.]+', nextWord):
        # Если точка и тп, пробел не нужен
        prevWord = '&'
        isSpace = False
    else:
        # Если не запятая и тп, пробел нужен
        if not re.fullmatch(r'[,;:]+', nextWord):
            isSpace = True
        prevWord = nextWord

    if outputFile != '':    # Вывод в файл
        if isSpace:
            result.write(' ')
        result.write(nextWord)
    else:   # Вывод в консоль
        if isSpace:
            print(' ', sep='', end='')
        print(nextWord, sep='', end='')

if outputFile != '':
    result.close()
