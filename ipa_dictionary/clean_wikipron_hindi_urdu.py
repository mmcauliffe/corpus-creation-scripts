# coding=utf8
import itertools
import os
import re
from collections import Counter

dictionary_dir = r'C:\Users\michael\Documents\Dev\mfa-models\dictionary\training'
source_dir = r'D:\Data\speech\dictionaries\wikipron\raw'
output_dir = r'D:\Data\speech\dictionaries\wikipron\cleaned'
os.makedirs(output_dir, exist_ok=True)


bad_graphemes = {}

langs = [
    'hindi',
    #'urdu'
]

lang_mapping = {
    'äː': 'aː',
    'ä': 'aː',
    'æ': 'æː',
    'æ̃': 'æ̃ː',
    'äːʱ': 'aːʱ',
    'ä̃ː': 'ãː',
    'ɑ̃ː': 'ãː',
    'ä̃ːʱ': 'ãːʱ',
    'ɑː': 'aː',
    'ō': 'oː',
    'o': 'oː',
    'i': 'ɪ',
    'ɪː': 'iː',
    'kːʰ': 'kʰː',
    'd̪ːʰ': 'd̪ʱː',
    'd̪ːʱ': 'd̪ʱː',
    'tʃːʰ': 'tʃʰː',
    't̪ːʰ': 't̪ʰː',
    'ʈːʰ': 'ʈʰː',
    'l': 'l̪',
    'lᵊ': 'l̪ᵊ',
    'ɭ': 'l̪',
    'lː': 'l̪ː',
    'n': 'n̪',
    'ɴ': 'ŋ',
    'nʱ': 'n̪ʱ',
    'nː': 'n̪ː',
    'nᵊ': 'n̪ᵊ',
    's': 's̪',
    'z': 'z̪',
    'v': 'ʋ',
    #'w': 'ʋ',
    #'wᵊ': 'ʋᵊ',
    'h': 'ɦ',
    'u': 'ʊ',
    't': 't̪',
    'd': 'd̪',
    'dz': 'dʒ',
    'ãː': 'ãː',
    'ĩː': 'ĩː',
    'ĩːʱ': 'ĩːʱ',
    'ũː': 'ũː',
    'ũːʱ': 'ũːʱ',
    'õː': 'õː',
    'ẽː': 'ẽː',
    'ə': 'ɐ',
    'ə̃': 'ɐ̃',
    'rː': 'r',
}
bad_phones = {'ɐː'}

vowels = { }

vowel_pattern = None

standardization_mapping = {
    'aɪ': 'aj',
    'aʊ': 'aw',
}

def load_existing_words(lang):
    dict_path = os.path.join(dictionary_dir, f"{lang}_mfa.dict")
    existing_words = set()
    return existing_words
    with open(dict_path, encoding='utf8') as f:
        for line in f:
            word = line.split(maxsplit=1)[0]
            existing_words.add(word)
    return existing_words


grapheme_phoneme_mappings =[
    ('क़', 'q'),
    ('झ़', 'ʒ'),
    ('ज़', 'z'),
    ('ग़', 'ɣ'),
    ('फ़', 'f'),
    ('ख़', 'x'),
]

def read_source(lang):
    existing = load_existing_words(lang)
    narrow_path = os.path.join(source_dir, f'{lang}_narrow.tsv')
    graphemes = set()
    phones = set()
    dictionary = []
    if not os.path.exists(narrow_path):
        path = os.path.join(source_dir, f'{lang}.tsv')
        with open(path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if "\t" in line:
                    line = line.split("\t")
                    word = line[0]
                    pronunciation = line[1].split()
                else:
                    line = line.split()
                    word = line[0]
                    pronunciation = line[1:]
                if any(x in bad_graphemes for x in word):
                    print(word)
                    continue
                if 'क़' in word and 'q' not in ' '.join(pronunciation):
                    continue
                if word in existing:
                    continue
                graphemes.update(word)
                phones.update(pronunciation)
                dictionary.append((word, pronunciation))
    else:
        broad_path = os.path.join(source_dir, f'{lang}_broad.tsv')
        with open(narrow_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if "\t" in line:
                    line = line.split("\t")
                    word = line[0]
                    pronunciation = line[1].split()
                else:
                    line = line.split()
                    word = line[0]
                    pronunciation = line[1:]
                if any(x in bad_graphemes for x in word):
                    print(word)
                    continue
                if any(x[0] in word and not re.search(rf'\b{x[1]}',  ' '.join(pronunciation)) for x in grapheme_phoneme_mappings):
                    continue
                #if word in existing:
                #    continue
                graphemes.update(word)
                phones.update(pronunciation)
                dictionary.append((word, pronunciation))
        existing.update(x[0] for x in dictionary)
        with open(broad_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if "\t" in line:
                    line = line.split("\t")
                    word = line[0]
                    pronunciation = line[1].split()
                else:
                    line = line.split()
                    word = line[0]
                    pronunciation = line[1:]
                if any(x in bad_graphemes for x in word):
                    print(word)
                    continue
                if 'क़' in word and not re.search(r'\bq',  ' '.join(pronunciation)):
                    continue
                if 'झ़' in word and not re.search(r'\bʒ',  ' '.join(pronunciation)):
                    continue
                if 'ज़' in word and not re.search(r'\bz',  ' '.join(pronunciation)):
                    continue
                if 'ग़' in word and not re.search(r'\bɣ',  ' '.join(pronunciation)):
                    continue
                if 'फ़' in word and not re.search(r'\bf',  ' '.join(pronunciation)):
                    continue
                if 'ख़' in word and not re.search(r'\bx',  ' '.join(pronunciation)):
                    continue
                if word in existing:
                    continue
                graphemes.update(word)
                phones.update(pronunciation)
                dictionary.append((word, pronunciation))
    return dictionary, graphemes, phones


def save_dictionary(dictionary, lang):
    existing = load_existing_words(lang)
    deduplication = set()
    final_phones = Counter()
    path = os.path.join(output_dir, f'{lang}.txt')
    with open(path, 'w', encoding='utf8') as f:
        for w, p in sorted(dictionary):
            final_phones.update(p)
            p = ' '.join(p)
            if (w, p) in deduplication:
                continue
            if w in existing:
                continue
            f.write(f'{w}\t{p}\n')
            deduplication.add((w, p))
    print("Final phones:", sorted(final_phones))
    print("Final phone counts:", sorted(final_phones.items(), key=lambda x: -x[1]))


def convert_language_specific(word, phones):
    new_pron = []
    for i, p in enumerate(phones):

        for k, v in lang_mapping.items():
            if p == k:
                p = v
                break

        if p in {'ʔ'}:
            continue

        if p in {'dʒ', 'd̪', 'd̪ʱ', 'k', 'kʰ', 'b', 'bʱ', 't̪', 'ɖ', 'ɖʱ', 'ɡ', 'ɡʱ', 't̪ʰ', 'pʰ', 'p', 'tʃʰ', 'tʃ', 'ʈʰ', 'ʈ'} and len(new_pron) and new_pron[-1].endswith('̚'):
            new_pron[-1] = p + 'ː'
            continue
        elif len(new_pron) and new_pron[-1].endswith('̚'):
            new_pron[-1] = new_pron[-1][:-1]
        if len(new_pron) and new_pron[-1] == p and not new_pron[-1].endswith('ː'):
            new_pron[-1] += 'ː'
            if new_pron[-1] in {'ɾː', 'rː'}:
                new_pron[-1] = 'r'
            continue
        elif p.endswith('ᵊ'):
            new_pron.append(p[:-1])
            p = 'ɐ'
        elif p in {'eʱ', 'ɔʱ', 'ɔːʱ', 'ɐʱ', 'ɛːʱ', 'ɔ̃ːʱ', 'ʊ̃ʱ', 'oːʱ', 'iːʱ', 'eːʱ', 'uːʱ', 'aːʱ', 'ũːʱ', 'ɛʱ', 'ɪʱ', 'ĩːʱ', 'ãːʱ', 'ũːʱ'}:
            new_pron.append(p[:-1])
            p = 'ɦ'
        elif p in {'ɦ'} and len(new_pron) and new_pron[-1] in {'m', 'l̪', 'r', 'n̪'}:
            new_pron[-1] += 'ʱ'
            continue
        elif p in {'dʒ', 'dʒː', 'tʃʰ', 'tʃ', 'tʃʰː'} and len(new_pron) and new_pron[-1] in {'n', 'n̪'}:
            new_pron[-1] = 'ɲ'
        elif p in {'ʈʰ', 'ʈ', 'ʈʰː', 'ʈː', 'ɖ', 'ɖʱ', 'ɖː', 'ɖʱː'} and len(new_pron) and new_pron[-1] in {'n', 'n̪'}:
            new_pron[-1] = 'ɳ'

        if not p:
            continue
        new_pron.append(p)

    return new_pron

def check_language_specific(word, phones):
    odd_set = set()
    if odd_set & set(phones):
        print(word)
        print(phones)

def standardize_pronunciation(word, phones):
    new_pron = []
    for i, p in enumerate(phones):

        for k, v in standardization_mapping.items():
            if p == k:
                p = v
                break
        if not p:
            continue
        new_pron.append(p)

    return new_pron


def fix_pronunciations(dictionary):
    filtered_dictionary = []
    for word, pronunciation in dictionary:
        for i, p in enumerate(pronunciation):
            if '̯' in p:
                pronunciation[i] = p.replace('̯', '')
            elif '͡' in p:
                pronunciation[i] = p.replace('͡', '')
            elif '‿' in p:
                pronunciation[i] = p.replace('‿', '')
            elif '͜' in p:
                pronunciation[i] = p.replace('͜', '')
            elif 'g' in p:
                pronunciation[i] = p.replace('g', 'ɡ')
        # Language specific conversions
        new_pron = convert_language_specific(word, pronunciation)
        if new_pron is None:
            continue
        new_pron = standardize_pronunciation(word, new_pron)
        check_language_specific(word, new_pron)
        if (word, new_pron) not in filtered_dictionary:
            filtered_dictionary.append((word, new_pron))
    return filtered_dictionary


def process():
    for lang in langs:
        print(f'Processing {lang}')
        dictionary, input_graphemes, input_phones = read_source(lang)

        print('Input graphemes', sorted(input_graphemes))
        print('Input phones', sorted(input_phones))
        filtered = fix_pronunciations(dictionary)
        save_dictionary(filtered, lang)


if __name__ == '__main__':
    process()
