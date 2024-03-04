# coding=utf8
import itertools
import os
import re
from collections import Counter

source_dir = r'D:\Data\speech\dictionaries\wikipron\raw'
output_dir = r'D:\Data\speech\dictionaries\wikipron\cleaned'
os.makedirs(output_dir, exist_ok=True)


bad_graphemes = {}

langs=['hindi', 'urdu']

lang_mapping = {
    'äː': 'aː',
    'ä̃ː': 'ãː',
    'ɑː': 'aː',
    'ō': 'oː',
    'i': 'ɪ',
    'ɪː': 'iː',
    'kːʰ': 'kʰː',
    'd̪ːʰ': 'd̪ʱː',
    'l': 'l̪',
    'ɭ': 'l̪',
    'lː': 'l̪ː',
    'n': 'n̪',
    'nʱ': 'n̪ʱ',
    'nː': 'n̪ː',
    's': 's̪',
    'z': 'z̪',
    'v': 'ʋ',
    'h': 'ɦ',
    'u': 'ʊ',
    't': 't̪',
    'd': 'd̪',
    'dz': 'dʒ',
    'ãː': 'ãː',
    'ĩː': 'ĩː',
    'ũː': 'ũː',
    'õː': 'õː',
    'ẽː': 'ẽː',
}
bad_phones = {}

vowels = { }

vowel_pattern = None

standardization_mapping = {
    'aɪ': 'aj',
    'aʊ': 'aw',
}


def read_source(lang):
    path = os.path.join(source_dir, '{}.tsv'.format(lang))
    graphemes = set()
    phones = set()
    dictionary = []
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
            graphemes.update(word)
            phones.update(pronunciation)
            dictionary.append((word, pronunciation))
    return dictionary, graphemes, phones


def save_dictionary(dictionary, lang):
    deduplication = set()
    final_phones = Counter()
    path = os.path.join(output_dir, '{}.txt'.format(lang))
    with open(path, 'w', encoding='utf8') as f:
        for w, p in sorted(dictionary):
            final_phones.update(p)
            p = ' '.join(p)
            if (w, p) in deduplication:
                continue
            f.write('{}\t{}\n'.format(w, p))
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


        if p in {'dʒ', 'd̪', 'd̪ʱ', 'k', 'kʰ', 'b', 'bʱ', 't̪', 'ɖ', 'ɖʱ', 'ɡ', 'ɡʱ', 't̪ʰ', 'pʰ', 'p', 'tʃʰ', 'tʃ', 'ʈʰ', 'ʈ'} and len(new_pron) and new_pron[-1].endswith('̚'):
            new_pron[-1] = p + 'ː'
            continue
        elif len(new_pron) and new_pron[-1].endswith('̚'):
            new_pron[-1] = new_pron[-1][:-1]
        elif len(new_pron) and new_pron[-1] == p:
            new_pron[-1] += 'ː'
            if new_pron[-1] == 'ɾː':
                new_pron[-1] = 'rː'
            continue
        elif p.endswith('ᵊ'):
            new_pron.append(p[:-1])
            p = 'ə'
        elif p in {'eʱ'}:
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
