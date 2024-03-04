import json
from pathlib import Path
import os
import re
import jsonlines
import pykakasi

kks = pykakasi.kakasi()

root_dir = os.path.dirname(os.path.abspath(__file__))
lexicon_dir = os.path.join(root_dir, 'rich_lexicons')
output_dir = r'C:\Users\michael\Documents\Dev\mfa-models\dictionary\training'
training_path = Path(r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\japanese_mfa.dict")

json_file = os.path.join(lexicon_dir, 'japanese.jsonl')

prons = {}
with open(training_path, encoding='utf8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        word, pron = line.split('\t')
        prons[word] = pron

languages = set()
mandarin_dialects = set()

hira_start = int("3041", 16)
hira_end = int("3096", 16)
kata_start = int("30a1", 16)

hira_to_kata = dict()
kata_to_hira = dict()
for i in range(hira_start, hira_end+1):
    hira_to_kata[chr(i)] = chr(i-hira_start+kata_start)
    kata_to_hira[chr(i-hira_start+kata_start)] = chr(i)

def convert_hira_to_kata(text):
    new_text = []
    for c in text:
        if c not in hira_to_kata:
            raise Exception(f"Character {c} not in hira_to_kata")
        new_text.append(hira_to_kata[c])
    return ''.join(new_text)

def convert_kata_to_hira(text):
    new_text = []
    for c in text:
        if c not in kata_to_hira:
            raise Exception(f"Character {c} not in kata_to_hira")
        new_text.append(kata_to_hira[c])
    return ''.join(new_text)

def is_hiragana(s: str) -> bool:
    return all((c in hira_to_kata for c in s))

def is_katakana(s: str) -> bool:
    return all((c in kata_to_hira for c in s))

def is_romaji(s: str) -> bool:
    return re.match(r'^[a-zA-Z]+$', s) is not None

mfa_phones = set()

mfa_dict_data = {}

if __name__ == '__main__':
    with open(json_file, encoding='utf8') as f:
        reader = jsonlines.Reader(f)
        for line in reader:
            key, pos = line['key']
            if key not in mfa_dict_data:

                written_forms = line['written_forms']
                orthography_data = {}
                kanji = None
                romaji = None
                katakana = None
                hiragana = None
                primary_orthography = None
                if is_katakana(key):
                    primary_orthography = 'katakana'
                elif is_hiragana(key):
                    primary_orthography = 'hiragana'
                elif is_romaji(key):
                    primary_orthography = 'romaji'
                else:
                    primary_orthography = 'kanji'
                    kanji = key
                for wf in written_forms:
                    if is_katakana(wf):
                        katakana = wf
                    elif is_hiragana(wf):
                        hiragana = wf
                    elif is_romaji(wf):
                        romaji = wf
                    else:
                        hiragana = ''
                        katakana = ''
                        romaji = ''
                        for item in kks.convert(wf):
                            hiragana += item['hira']
                            katakana += item['kana']
                            romaji += item['hepburn']
                pronunciation = None
                if katakana in prons:
                    pronunciation = prons[katakana]
                elif hiragana in prons:
                    pronunciation = prons[hiragana]
                if kanji is not None:
                    orthography_data['kanji'] = kanji
                if hiragana is not None:
                    orthography_data['hiragana'] = hiragana
                if katakana is not None:
                    orthography_data['katakana'] = katakana
                if romaji is not None:
                    orthography_data['romaji'] = romaji

                if pronunciation is not None:
                    mfa_phones.update(pronunciation.split())
                    mfa_dict_data[key] = {
                        'primary_orthography': primary_orthography,
                        'orthographic_forms': orthography_data,
                        'pronunciations': [pronunciation]
                    }

    mfa_dict = {
        'transparent_orthography': 'katakana',
        'phones': {},
        'words': list(mfa_dict_data.values())
    }
    mfa_dict['phones']['<eps>'] = 0
    mfa_dict['phones']['sil'] = 1
    mfa_dict['phones']['spn'] = 2
    for i, p in enumerate(sorted(mfa_phones)):
        mfa_dict['phones'][p] = i + 3
    with open(os.path.join(lexicon_dir, 'japanese_mfa.dict'), 'w', encoding='utf8') as f:
        json.dump(mfa_dict, f, indent=2, ensure_ascii=False)