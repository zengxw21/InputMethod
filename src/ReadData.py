import json
from pypinyin import lazy_pinyin
# 使用时在linux环境，否则无法生成文件

SENTENCES = '../dataset/sentences-%02d.json'
MONTHS = [2, 4, 5, 6, 7, 8, 9, 10, 11]
NEWS_PATH = '../sina_news_gbk/2016-%02d.txt'
FREQUENCY = '../dataset/frequency-%d.json'
WORD_MAP = '../dataset/word_map.json'
PINYIN_MAP = '../dataset/pinyin_map.json'
SMP_PATH = '../语料库/SMP2020/block1.txt'
FORWARD = '../dataset/forward.json'


def read_file(path: str):
    try:
        with open(path, 'r', encoding='gbk') as f:
            ret = f.readlines()
        return ret
    except Exception as e:
        print(e)
        return []


# word_map为每个拼音对应的汉字
# pinyin_map为每个汉字对应的拼音


def word_pinyin(path: str):
    lines = read_file(path)
    word_map = {}
    pinyin_map = {}
    for line in lines:
        words = line.split()
        word_map[words[0]] = words[1:]
        for word in words[1:]:
            if word in pinyin_map:
                pinyin_map[word].append(words[0])
            else:
                pinyin_map[word] = [words[0]]
    return word_map, pinyin_map


def extract_news(path: str):
    try:
        lines = read_file(path)
        ret = []
        for line in lines:
            news = json.loads(line)
            ret.append(news['html'])
            ret.append(news['title'])
        return ret
    except Exception as e:
        print(e)
        return []


def extract_SMP(path: str):
    try:
        lines = read_file(path)
        ret = []
        for line in lines:
            item = json.loads(line)
            ret.append(item['content'])
        return ret
    except Exception as e:
        print(e)
        return []


def save_word_pinyin():
    word_map, pinyin_map = word_pinyin('../拼音汉字表.txt')
    with open('../dataset/word_map.json', 'w', encoding='utf8') as f:
        json.dump(word_map, f, ensure_ascii=False)
    with open('../dataset/pinyin_map.json', 'w', encoding='utf8') as f:
        json.dump(pinyin_map, f, ensure_ascii=False)


def output_sentences():
    for month in MONTHS:
        with open(SENTENCES % month, 'w', encoding='utf8') as f:
            pass
        print('start process month ' + str(month))
        sina_news = extract_news(NEWS_PATH % month)

        sentence = []
        percent = 1
        for new in sina_news:
            pinyin_sentence = lazy_pinyin(
                new, errors=lambda item: ['*' for i in range(len(item))])
            sentence.append((new, pinyin_sentence))
            while len(sentence) / len(sina_news) >= percent / 100:
                print(str(percent) + '%')
                percent += 1
        with open(SENTENCES % month, 'w', encoding='utf8') as f:
            json.dump(sentence, f, ensure_ascii=False)
        print('finish process month ' + str(month))


def output_sentences_SMP():
    with open(SENTENCES % 13, 'w', encoding='utf8') as f:
        pass
    print('start process SMP')
    SMP_sentences = extract_SMP(SMP_PATH)
    sentence = []
    percent = 1
    for single in SMP_sentences:
        pinyin_sentence = lazy_pinyin(
            single, errors=lambda item: ['*' for i in range(len(item))])
        sentence.append((single, pinyin_sentence))
        while len(sentence) / len(SMP_sentences) >= percent / 100:
            print(str(percent) + '%')
            percent += 1
    with open(SENTENCES % 13, 'w', encoding='utf8') as f:
        json.dump(sentence, f, ensure_ascii=False)
    print('finish process')


def count():
    with open('../dataset/pinyin_map.json', 'r', encoding='utf8') as f:
        pinyin_map = json.load(f)
    pinyin_map = pinyin_map.keys()
    count = {}
    binary_count = {}
    for month in MONTHS:
        print('start counting month ' + str(month))
        percent = 1
        cnt = 0
        with open(SENTENCES % month, 'r', encoding='utf8') as f:
            sentences = json.load(f)
        for sentence in sentences:
            for i in range(len(sentence[0])):
                if sentence[0][i] not in pinyin_map:
                    continue
                now = sentence[0][i] + sentence[1][i]
                if now not in count:
                    count[now] = 1
                else:
                    count[now] += 1
                if i == 0:
                    continue
                if sentence[0][i - 1] in pinyin_map:
                    last = sentence[0][i - 1] + sentence[1][i - 1]
                    if last not in binary_count:
                        binary_count[last] = {}
                    if now not in binary_count[last]:
                        binary_count[last][now] = 0
                    binary_count[last][now] += 1
            cnt += 1
            while cnt / len(sentences) >= percent / 100:
                print(str(percent) + '%')
                percent += 1
        print('finish counting month ' + str(month))
    with open(FREQUENCY % 1, 'w', encoding='utf8') as f:
        json.dump(count, f, ensure_ascii=False)
    with open(FREQUENCY % 2, 'w', encoding='utf8') as f:
        json.dump(binary_count, f, ensure_ascii=False)


# 3007341
def count_forward():
    with open(FREQUENCY % 1, 'r', encoding='utf8') as f1:
        with open(FREQUENCY % 2, 'r', encoding='utf8') as f2:
            with open(FORWARD, 'w', encoding='utf8') as f:
                unigram_frequency = json.load(f1)
                binary_frequency = json.load(f2)
                total = 0
                count = 0
                percent = 0
                forward_frequency = {}
                for item in unigram_frequency.keys():
                    forward_frequency[item] = 0
                    total += len(binary_frequency[item]
                                 ) if item in binary_frequency else 0
                    for key in binary_frequency.keys():
                        # total += len(binary_frequency[key])
                        if item in binary_frequency[key]:
                            forward_frequency[item] += 1
                    count += 1
                    while count / len(unigram_frequency) >= percent / 100:
                        print(str(percent) + '%')
                        percent += 1
                json.dump(forward_frequency, f, ensure_ascii=False)
    print(total)


def count_ternery():
    with open(PINYIN_MAP, 'r', encoding='utf8') as f:
        pinyin_map = json.load(f)
    pinyin_map = pinyin_map.keys()
    ternery_count = {}
    for month in MONTHS:
        print('start counting month ' + str(month))
        percent = 1
        cnt = 0
        with open(SENTENCES % month, 'r', encoding='utf8') as f:
            sentences = json.load(f)
        for sentence in sentences:
            for i in range(2, len(sentence[0])):
                if sentence[0][i] not in pinyin_map:
                    continue
                if sentence[0][i - 1] not in pinyin_map:
                    continue
                if sentence[0][i - 2] in pinyin_map:
                    second_last = sentence[0][i - 2] + sentence[1][i - 2]
                    last = sentence[0][i - 1] + sentence[1][i - 1]
                    now = sentence[0][i] + sentence[1][i]
                    if second_last not in ternery_count:
                        ternery_count[second_last] = {}
                    if last not in ternery_count[second_last]:
                        ternery_count[second_last][last] = {}
                    if now not in ternery_count[second_last][last]:
                        ternery_count[second_last][last][now] = 0
                    ternery_count[second_last][last][now] += 1
            cnt += 1
            while cnt / len(sentences) >= percent / 100:
                print(str(percent) + '%')
                percent += 1
        print('finish process month ', str(month))
    with open(FREQUENCY % 3, 'w', encoding='utf8') as f:
        json.dump(ternery_count, f, ensure_ascii=False)
