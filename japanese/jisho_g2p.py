import collections

import requests
import time
import os
import unicodedata
import tqdm
from montreal_forced_aligner.g2p.generator import PyniniValidator

root_dir = r"/mnt/d/Data/speech/dictionaries/japanese"
oov_file = os.path.join(root_dir, 'oovs.txt')
jisho_output_file = os.path.join(root_dir, 'jisho_oovs.txt')
other_output_file = os.path.join(root_dir, 'other_oovs.txt')
g2pped_file = os.path.join(root_dir, 'jisho_oovs.g2pped')
g2p_model_path = os.path.join(root_dir, 'experimental.zip')
temporary_directory = os.path.join(root_dir, 'g2p_temp')

def save_data(data, path):
    with open(path, 'w', encoding='utf8') as outf:
        for k, v in sorted(data.items(), key=lambda x: -x[1]):
            outf.write(f"{k}\n")

def get_current_word_set():
    path = "/mnt/c/Users/michael/Documents/Dev/mfa-models/dictionary/training/japanese_mfa.dict"
    word_set = set()
    with open(path, 'r', encoding='utf8') as inf:
        for line in inf:
            line = line.strip()
            word = line.split(maxsplit=1)[0]
            word_set.add(word)
    return word_set

def look_up_jisho(data):
    to_g2p = set()
    done = set()

    for word in tqdm.tqdm(data.keys()):
        if word in done:
            continue
        resp = requests.get(f'https://jisho.org/api/v1/search/words?keyword={word}')
        data = resp.json()['data']
        for result in data:
            skip_check = True
            if result['slug'] == word:
                skip_check = False
            pairs = set()
            for d in result['japanese']:
                reading = d.get('reading', None)
                if reading is None:
                    continue
                if 'word' in d and d['word'] == word:
                    skip_check = False
                elif d['reading'] == word:
                    skip_check = False
                pairs.add((d.get('word', reading), reading))
            if skip_check:
                done.add(word)
                continue
            to_g2p.update(pairs)
            done.update([x[0] for x in pairs])
        time.sleep(1)
    return to_g2p


if __name__ == '__main__':
    already_done = get_current_word_set()
    mixed = collections.Counter()
    romaji = collections.Counter()
    kana = collections.Counter()
    other = collections.Counter()
    kanji = collections.Counter()
    skip_count = 0
    done_count = 0
    with open(oov_file, 'r', encoding='utf8') as inf:
        for line in inf:
            word, count = line.split()
            if word in already_done:
                done_count += 1
                continue
            if any(x in word for x in ['<', '>', '[', ']']):
                continue
            if word.endswith('っ'):
                continue
            skip_check = False
            character_sets = set()
            for c in word:
                try:
                    name = unicodedata.name(c)
                    if 'CJK' in name:
                        character_sets.add('kanji')
                    elif 'HIRAGANA' in name or 'KATAKANA' in name:
                        character_sets.add('kana')
                    elif 'LATIN' in name:
                        character_sets.add('romaji')
                except ValueError:
                    print(word, repr(c), c.encode('utf8'))
                    skip_check = True
                    break
            if skip_check:
                skip_count += 1
                continue
            if character_sets == {'kanji'}:
                kanji[word] += int(count)
            elif character_sets == {'romaji'}:
                romaji[word] += int(count)
            elif character_sets == {'kanji', 'kana'}:
                mixed[word] += int(count)
            elif character_sets == {'kana'}:
                kana[word] += int(count)
            else:
                other[word] += int(count)
    print(f"Romaji: {len(romaji)}")
    print(f"kanji: {len(kanji)}")
    print(f"kana: {len(kana)}")
    print(f"mixed: {len(mixed)}")
    print(f"other: {len(other)}")
    print(f"Already done: {done_count}")
    print(f"Skipped: {skip_count}")
    save_data(romaji, os.path.join(root_dir, 'romaji_oovs.txt'))
    save_data(kanji, os.path.join(root_dir, 'kanji_oovs.txt'))
    save_data(kana, os.path.join(root_dir, 'kana_oovs.txt'))
    save_data(mixed, os.path.join(root_dir, 'mixed_oovs.txt'))
    save_data(other, os.path.join(root_dir, 'other_oovs.txt'))
    if not os.path.exists(jisho_output_file):
        jisho_results = look_up_jisho(mixed)
        with open(jisho_output_file, 'w', encoding='utf8') as f:
            for word, kana in jisho_results:
                f.write(f"{word}\t{kana}\n")
    error
    to_g2p = collections.defaultdict(set)
    kanas = set()
    with open(jisho_output_file, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            word, kana = line.split()
            to_g2p[word].add(kana)
            kanas.add(kana)
    gen = PyniniValidator(
        g2p_model_path=g2p_model_path,
        word_list=list(kanas),
        num_pronunciations = 1,
        temporary_directory=temporary_directory,
    )
    output = gen.generate_pronunciations()
    with open(g2pped_file, 'w', encoding='utf8') as f:
        for word, kana_set in to_g2p.items():
            for kana in sorted(kana_set):
                f.write(f"{word}\t{output[kana][0]}\n")
