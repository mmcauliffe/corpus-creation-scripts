import json

import os
import re
import jsonlines
import hanziconv
from dragonmapper.hanzi import to_pinyin, to_zhuyin
from dragonmapper.transcriptions import is_zhuyin, is_pinyin


root_dir = os.path.dirname(os.path.abspath(__file__))
lexicon_dir = os.path.join(root_dir, 'rich_lexicons')
output_dir = r'C:\Users\michael\Documents\Dev\mfa-models\dictionary\training'

json_file = os.path.join(lexicon_dir, 'chinese.jsonl')

languages = set()
mandarin_dialects = set()


bad_phones = {'ai', 'a', 'ei', 'o', 'ə'}

vowels = {'a', 'e', 'o', 'i', 'u', 'y', 'ə', 'ɚ', 'ɤ̃', 'ʊ̃'}
vowel_pattern = re.compile(r'^[ayeiouəɚʊɤ̃]+[²³⁰¹⁴⁵]*$')
phone_mapping = {
        'b̥': 'p',
        'd̥': 't',
        'g̊': 'k',
        'ɡ̊': 'k',
        'ɖʐ̥': 'ʈʂ',
        'dz̥': 'ts',
        'dʑ̥': 'tɕ',
        'ä': 'a',
        'ä': 'a',
        'æ̃': 'a',
        'ɤ': 'o',
        'ɤ̃': 'o',
        'ʊ̃': 'o',
        'ɪ': 'i',
        'ɻʷ': 'ɻ',
        'ʊ': 'u',
        'ɛ': 'e',
        'ɑ': 'a',
        'ɑ̃': 'a',
        'ɔ': 'o',
        'ɔː': 'o',
        '⁵⁵': '˥',
        '⁵¹': '˥˩',
        '³⁵': '˧˥',
        '²¹⁴': '˨˩˦',
    }
tone_mapping = {
    '²¹⁴': '˨˩˦',
    '²¹¹': '˨˩˦',
    '⁵⁵': '˥',
    '³⁵': '˧˥',
    '⁵¹': '˥˩',
    '⁵³': '˥˩',
    '⁰': '',
    '¹': '˩',
    '²': '˩',
    '³': '˧',
    '⁴': '˥',
    '⁵': '˥',
}

pinyin_vowels = re.compile(r'[aǎáàāeěéèēiǐíìīoǒóòōuǔúùū]')

def create_pinyin(input_text):
    pinyin = to_pinyin(input_text).lower()
    new_pron = []
    for p in pinyin:
        if new_pron and p == 'h' and  new_pron[-1] in {'s', 'c', 'z'}:
            new_pron[-1] += p
            continue
        elif new_pron and p == 'g' and  new_pron[-1] in {'n'}:
            new_pron[-1] += p
            continue
        elif new_pron and pinyin_vowels.search(p) and pinyin_vowels.search(new_pron[-1]):
            new_pron[-1] += p
            continue
        new_pron.append(p)
    return " ".join(new_pron)

def process_ipa(input_text):
    if '² ¹ ⁴ ⁻ ² ¹ ⁽ ⁴ ⁾' in input_text:
        input_text = input_text.replace('² ¹ ⁴ ⁻ ² ¹ ⁽ ⁴ ⁾', '² ¹ ⁴')
    if '² ¹ ⁴ ⁻ ² ¹ ¹' in line:
        input_text = input_text.replace('² ¹ ⁴ ⁻ ² ¹ ¹', '² ¹ ⁴')
    if '² ¹ ⁴ ⁻ ³ ⁵' in input_text:
        input_text = input_text.replace('² ¹ ⁴ ⁻ ³ ⁵', '² ¹ ⁴')
    if '⁵ ¹ ⁻ ⁵ ³' in input_text:
        input_text = input_text.replace('⁵ ¹ ⁻ ⁵ ³', '⁵ ¹')
    if '⁵ ⁵ ⁻ ⁵ ¹' in input_text:
        input_text = input_text.replace('⁵ ⁵ ⁻ ⁵ ¹', '⁵ ⁵')
    pronunciations = []
    if '⁻' in input_text:
        pronunciations.append(re.sub(r' ⁻ [ ⁰¹²³⁴⁵]+', ' ', input_text).split())
        pronunciations.append(re.sub(r'[ ⁰¹²³⁴⁵]+ ⁻ ', ' ', input_text).split())
    else:
        pronunciations.append(input_text.split())
    for pron_index, pronunciation in enumerate(pronunciations):
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
        new_pron = []
        for i, p in enumerate(pronunciation):
            for k, v in phone_mapping.items():
                if p == k:
                    p = v
                    break
            if p in {'²', '³', '¹', '⁰', '⁴', '⁵', '⁻', '⁽', '⁾'} and len(new_pron):
                index = -1
                for j in range(len(new_pron) - 1, -1, -1):
                    if vowel_pattern.match(new_pron[j]) or '̩' in new_pron[j]:
                        index = j
                        break
                if new_pron[index].endswith('²¹⁴'):
                    continue
                new_pron[index] += p
                continue
            elif p.startswith('ˀ'):
                new_pron.append('ʔ')
                if p[1] in phone_mapping:
                    new_pron.append(phone_mapping[p[1]])
                else:
                    new_pron.append(p[1])
                continue
            elif any(p.startswith(x) for x in vowels) and len(new_pron) and new_pron[-1] == 'i':
                new_pron[-1] = 'j'
            elif any(p.startswith(x) for x in vowels) and len(new_pron) and new_pron[-1] == 'y':
                new_pron[-1] = 'ɥ'
            elif any(p.startswith(x) for x in vowels) and len(new_pron) and new_pron[-1] == 'u':
                new_pron[-1] = 'w'
            elif any(p.startswith(x) for x in vowels) and len(new_pron) and re.match(r'^[ayeiouəɚʊɤ̃]+$',
                                                                                           new_pron[-1]):
                new_pron[-1] += p
                continue
            new_pron.append(p)
        tone_symbols = {'²', '³', '¹', '⁴', '⁵', '⁰'}
        for i, p in enumerate(new_pron):
            if 'au' in p:
                new_pron[i] = p.replace('au', 'aw')
            elif 'ai' in p:
                new_pron[i] = p.replace('ai', 'aj')
            elif 'ei' in p:
                new_pron[i] = p.replace('ei', 'ej')
            elif 'ou' in p:
                new_pron[i] = p.replace('ou', 'ow')
            if any(x in p for x in tone_symbols):
                for k, v in tone_mapping.items():
                    if k in new_pron[i]:
                        new_pron[i] = re.sub(r'([^²³¹⁴⁵⁰˨˩˦˥˧]+)'+k, r'\1'+v,new_pron[i])
        new_pron = extra_processing(new_pron)
        pronunciations[pron_index] = new_pron

    return pronunciations

def extra_processing(pronunciation):
    new_pron = []
    for i, p in enumerate(pronunciation):
        if p == 'j' and new_pron and new_pron[-1] in {'tɕʰ', 'tɕ', 'ɕ'}:
            continue
        elif p == 'ɥ' and new_pron and new_pron[-1] in {'tɕ', 'ɕ', 'ʂ', 'ʈʂ'}:
            new_pron[-1] += 'ʷ'
            continue
        elif p == 'ɥ' and new_pron and new_pron[-1] in {'tɕʰ', 'ʈʂʰ'}:
            new_pron[-1] = new_pron[-1][:-1] + 'ʷ'
            continue
        elif p == 'w' and new_pron and new_pron[-1] in {'x'}:
            new_pron[-1] = 'xʷ'
            continue
        elif p.startswith('i') and new_pron and new_pron[-1] in {'pʰ', 'p'}:
            new_pron[-1] = 'pʲ'
        elif p[0] in {'i','y'} and new_pron and new_pron[-1] in {'l'}:
            new_pron[-1] = 'ʎ'
        elif p[0] in {'i','y'} and new_pron and new_pron[-1] in {'n'}:
            new_pron[-1] = 'ɲ'
        elif p[0] in {'i','y'} and new_pron and new_pron[-1] in {'m'}:
            new_pron[-1] = 'mʲ'
        elif p.startswith('u') and new_pron and new_pron[-1] in {'pʰ', 'p'}:
            new_pron[-1] = 'pʷ'
        elif p.startswith('u') and new_pron and new_pron[-1] in {'x'}:
            new_pron[-1] = 'xʷ'
        elif p.startswith('u') and new_pron and new_pron[-1] in {'kʰ', 'k'}:
            new_pron[-1] = 'kʷ'
        elif p.startswith('i') and new_pron and new_pron[-1] in {'tʰ', 't'}:
            new_pron[-1] = 'tʲ'
        elif p.startswith('u') and new_pron and new_pron[-1] in {'tʰ', 't'}:
            new_pron[-1] = 'tʷ'
        new_pron.append(p)
    return new_pron

def generate_orthographic_key(text):
    try:
        return (hanziconv.HanziConv.toTraditional(text), hanziconv.HanziConv.toSimplified(text), to_pinyin(text), to_zhuyin(text))
    except ValueError:
        return None

mfa_phones = set()

mfa_dict_data = {}

if __name__ == '__main__':
    with open(json_file, encoding='utf8') as f, \
          open(os.path.join(output_dir, 'mandarin_china_mfa.dict'), 'w', encoding='utf8') as china_f, \
            open(os.path.join(output_dir, 'mandarin_taiwan_mfa.dict'), 'w', encoding='utf8') as taiwan_f, \
          open(os.path.join(output_dir, 'mandarin_china_pinyin.dict'), 'w', encoding='utf8') as china_pinyin_f, \
            open(os.path.join(output_dir, 'mandarin_taiwan_pinyin.dict'), 'w', encoding='utf8') as taiwan_pinyin_f, \
          open(os.path.join(output_dir, 'mandarin_china_pinyin_mfa.dict'), 'w', encoding='utf8') as china_pinyin_mfa_f, \
            open(os.path.join(output_dir, 'mandarin_taiwan_pinyin_mfa.dict'), 'w', encoding='utf8') as taiwan_pinyin_mfa_f:
        reader = jsonlines.Reader(f)
        for line in reader:
            word = line['word']
            if re.search('[\Wβπασγλδτφのμ]', word):
                continue
            for language, dialects in line['languages'].items():
                if language != 'Mandarin':
                    continue
                for dialect, pronunciations in dialects.items():
                    if 'obsolete' in dialect:
                        continue
                    if 'Standard Chinese' not in dialect:
                        continue
                    china = True
                    taiwan = True
                    erhuaed = False
                    if 'erhua-ed) (' in dialect:
                        taiwan = False
                        erhuaed = True
                    if dialect.endswith('erhua-ed'):
                        taiwan = False
                        if not word.endswith('儿'):
                            erhuaed = True
                    if dialect.startswith('Beijing dialect'):
                        taiwan = False
                    if 'Mandarin' in line['languages']:
                        mandarin_dialects.add(dialect)
                    for p in pronunciations:
                        if '/ → /' in p:
                            p = p.split('/ → /')[0]
                        new_pronunciations = process_ipa(p)
                        for new_p in new_pronunciations:
                            new_p = " ".join(new_p)
                            if '˨˩˩' in new_p:
                                continue
                            mfa_phones.update(new_p.split(" "))
                            if china:
                                output_word = word
                                if erhuaed:
                                    output_word += '儿'
                                key = generate_orthographic_key(output_word)
                                w = to_pinyin(output_word).lower()
                                if key is not None:
                                    if key not in mfa_dict_data:
                                        orthography_data = {
                                            'traditional': key[0],
                                            'simplified': key[1],
                                            'pinyin': key[2],
                                            'zhujin': key[3],
                                        }
                                        mfa_dict_data[key] = {
                                            'orthographic_forms': orthography_data,
                                            'pronunciations': {
                                            }
                                        }
                                        if 'china' not in mfa_dict_data[key]['pronunciations']:
                                            mfa_dict_data[key]['pronunciations']['china'] = []
                                        mfa_dict_data[key]['pronunciations']['china'].append(new_p)
                                        #if is_pinyin(w):
                                        #    if 'pinyin' not in mfa_dict_data[key]['pronunciations']['china']:
                                        #        mfa_dict_data[key]['pronunciations']['china']['pinyin'] = []
                                        #    mfa_dict_data[key]['pronunciations']['china']['pinyin'].append(create_pinyin(output_word))
                                china_f.write(f"{hanziconv.HanziConv.toSimplified(output_word)}\t{new_p}\n")
                                if is_pinyin(w):
                                    china_pinyin_mfa_f.write(f"{w}\t{new_p}\n")
                            if taiwan:
                                taiwan_f.write(f"{hanziconv.HanziConv.toTraditional(word)}\t{new_p}\n")
                                key = generate_orthographic_key(output_word)
                                w = to_pinyin(output_word).lower()
                                if key is not None:
                                    if key not in mfa_dict_data:
                                        orthography_data = {
                                            'traditional': key[0],
                                            'simplified': key[1],
                                            'pinyin': key[2],
                                            'zhujin': key[3],
                                        }
                                        mfa_dict_data[key] = {
                                            'orthographic_forms': orthography_data,
                                            'pronunciations': {
                                            }
                                        }
                                    if 'taiwan' not in mfa_dict_data[key]['pronunciations']:
                                        mfa_dict_data[key]['pronunciations']['taiwan'] = []
                                    mfa_dict_data[key]['pronunciations']['taiwan'].append(new_p)
                                    #if is_pinyin(w):
                                    #    if 'pinyin' not in mfa_dict_data[key]['pronunciations']['taiwan']:
                                    #        mfa_dict_data[key]['pronunciations']['taiwan']['pinyin'] = []
                                    #    mfa_dict_data[key]['pronunciations']['taiwan']['pinyin'].append(create_pinyin(output_word))
                                if is_pinyin(w):
                                    taiwan_pinyin_mfa_f.write(f"{w}\t{new_p}\n")
                    if re.search(r'[a-zA-Z]', word):
                        continue
                    pinyin = create_pinyin(word)
                    if not is_pinyin(pinyin):
                        continue
                    if china:
                        china_pinyin_f.write(f"{pinyin.replace(' ', '')}\t{pinyin}\n")
                    if taiwan:
                        taiwan_pinyin_f.write(f"{pinyin.replace(' ', '')}\t{pinyin}\n")

    mfa_dict = {
        'transparent_orthography': 'pinyin',
        'phones': {},
        'words': list(mfa_dict_data.values())
    }
    mfa_dict['phones']['<eps>'] = 0
    mfa_dict['phones']['sil'] = 1
    mfa_dict['phones']['spn'] = 2
    for i, p in enumerate(sorted(mfa_phones)):
        mfa_dict['phones'][p] = i + 3
    with open(os.path.join(output_dir, 'mandarin_mfa.dict'), 'w', encoding='utf8') as f:
        json.dump(mfa_dict, f, indent=2, ensure_ascii=False)