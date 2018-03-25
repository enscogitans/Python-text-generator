import re
from fractions import Fraction
from collections import defaultdict

# Наш алфавит
alphabet = re.compile(u'[ёЁа-яА-Я0-9]+[-]?[ёЁа-яА-Я0-9]+|[.,?!;:]+')
# Наша кодировка
encodeType = 'utf-8'


# Возвращает пользовательские аргументы
def get_args():
    line = input().split()

    input_path = str()
    model_dir = str()
    is_lc = False
    is_help = False

    i = 0
    while i < len(line):
        if line[i] == '--input-dir':
            input_path = line[i + 1]
            i += 1
        elif line[i] == '--model-dir':
            model_dir = line[i + 1]
            i += 1
        elif line[i] == '--lc':
            is_lc = True
        elif line[i] == '--help':
            is_help = True
        i += 1

    return input_path, model_dir, is_lc, is_help


# Построчно генерирует строки из данного файла (stdin)
def line_generator(filename, file_path):
    if file_path != '':
        file = open(filename, 'r', encoding=encodeType)
        for line in file:
            yield str(bytes(line, encodeType).decode(encodeType))
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

    pair_freq[(last_symbol, '&')] += 1

    return word_freq, pair_freq


# Ввод аргументов
print('--help, для описания команд')
filePath, modelDirectory, isLC, isHelp = get_args()
while (isHelp):
    if isHelp:
        print('''Введите:
        (Опционально) --input-dir <Путь до файла, на которо проходит обучение>,
          иначе ввод осуществляется через консоль. Если ввод из консосли, окан-
          чивайте свой текст: ////
         --model-dir <Папка для сохранения модели>
        (Опционально) --lc, если требуется привести слова к нижнему регистру
        (Опционально) --help, для описания команд''')

    filePath, modelDirectory, isLC, isHelp = get_args()


# Инициализация генератора биграмм
lines = line_generator(filePath, filePath)
tokens = token_generator(lines, isLC)
bigrams = bigram_generator(tokens)


# Подсчёт количества слов и пар слов соответственно
wordFreq, pairFreq = count_words_and_pairs(bigrams)


# Инициализация нашей модели. По ключу хранится лист слов,
# которые могут идти после него с указаним вероятности (в виде рац. дроби)
model = dict()
for (t0, t1), freq in pairFreq.items():
    if t0 in model:
        model[t0].append((t1, Fraction(freq, wordFreq[t0])))
    else:
        model[t0] = [(t1, Fraction(freq, wordFreq[t0]))]


# Сохранение нашей модели в файл model.txt в указанной пользователем папке
modelFile = open('{}\\model.txt'.format(modelDirectory), 'w',
                 encoding=encodeType)

for key, lst in model.items():
    modelFile.write(key)
    for (word, freq) in lst:
        modelFile.write(' {} {}'.format(word, freq))
    modelFile.write('\n')

modelFile.close()
