# coding=utf8
import itertools
import os
import re
from collections import Counter

source_dir = r'D:\Data\speech\dictionaries\wikipron\raw'
output_dir = r'D:\Data\speech\dictionaries\wikipron\cleaned'
os.makedirs(output_dir, exist_ok=True)


bad_graphemes = {'ࢳ', 'ࢳ', 'ࢴ', 'ࢴ'}

lang='tamil'

lang_mapping = {
        'ə': 'ɐ',
        'aː': 'ɑː',
        'ɨː': 'iː',
        'ɨ': 'ɪ',
        'a': 'ɐ',
        'ʌ': 'ɐ',
        'ʊ': 'u',
        'ʷo': 'o',
        'i': 'ɪ',
        'ʉ': 'u',
        'l̪': 'l',
        'ɣ': 'ɡ',
        'l̪ː': 'lː',
        'r̥': 'r',
        'ɾ̪': 'ɾ',
        'tʃ': 'tɕ',
        'dʒ': 'dʑ',
        'ɕ': 'tɕ',
        'tʃː': 'tɕː',
        'sː': 'tɕː',
        'e': 'ɛ',
        't': 't̪',
        'd': 'd̪',
        'ʔ': '',

}
bad_phones = {}

vowels = { }

vowel_pattern = None

standardization_mapping = {
    'ɐɪ': 'aj',
    'ɐʊ': 'aw',
}


def read_source():
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
            if lang in bad_graphemes:
                if any(x in bad_graphemes for x in word):
                    print(word)
                    continue
            graphemes.update(word)
            phones.update(pronunciation)
            dictionary.append((word, pronunciation))
    return dictionary, graphemes, phones


def save_dictionary(dictionary):
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
        if p in {'ʊ', 'ɪ'} and len(new_pron) and new_pron[-1] in {'a', 'ɑ', 'ɐ'}:
            new_pron[-1] += p
            continue
        elif len(new_pron) and new_pron[-1] == p:
            new_pron[-1] += 'ː'
            continue
        elif len(new_pron) == 0 and p == 's':
            p = 'tɕ'
        elif p not in {'d̪'} and len(new_pron) and new_pron[-1] in {'n̪'}:
            new_pron[-1] = 'n'
        elif p not in {'d̪'} and len(new_pron) and new_pron[-1] in {'n̪ː'}:
            new_pron[-1] = 'nː'
        elif p in {'r'} and len(new_pron) and new_pron[-1] in {'n'}:
            new_pron.append('d')

        for k, v in lang_mapping.items():
            if p == k:
                p = v
                break
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


def process_tamil():
    print('Processing Tamil')
    dictionary, input_graphemes, input_phones = read_source()

    print('Input graphemes', sorted(input_graphemes))
    print('Input phones', sorted(input_phones))
    filtered = fix_pronunciations(dictionary)
    save_dictionary(filtered)


if __name__ == '__main__':
    process_tamil()
