import collections

import fugashi
import sys

import os

import re
import itertools
from pathlib import Path
import jsonlines
import subprocess
from bs4 import BeautifulSoup as bs

root_dir = Path(__file__).resolve().parent

japanese_path = root_dir.joinpath('rich_lexicons', 'english.jsonl')

new_forms = []

new_pronunciations = []

tagger = fugashi.Tagger("-Owakati")

def generate_morphological_string(word, pos, inflection=None):
    pos_tag =  None
    if 'Verb' in pos:
        pos_tag = '動詞'
        if 'Auxiliary' in pos:
            pos_tag = '助動詞'
    elif "Noun" in pos:
        pos_tag = '名詞'
    elif "Adverb" in pos:
        pos_tag = '副詞'
    elif "Adjective" in pos:
        if '-i' in pos:
            pos_tag = '形容詞'
        elif '-na' in pos:
            pos_tag = '形容動詞'
    elif "Proper noun" in pos:
        pos_tag = '固有名詞'
    elif "Interjection" in pos:
        pos_tag = '感嘆詞'
    elif "Pronoun" in pos:
        pos_tag = '代名詞'
    elif "Particle" in pos:
        pos_tag = '助詞'
    elif "Adnominal" in pos:
        pos_tag = '連体詞'
    elif "Counter" in pos:
        pos_tag = '助数詞'
    elif "Conjunction" in pos:
        pos_tag = '接続詞'
    elif "Numeral" in pos:
        pos_tag = '数詞'
    elif "Suffix" in pos:
        pos_tag = '接尾辞'
    elif "Prefix" in pos:
        pos_tag = '接頭辞'
    morphology_tag = f"{word}_{pos_tag}"

    if inflection is None:
        return morphology_tag
    return f"{morphology_tag} {inflection_to_morphemes[inflection]}"

ichidan_forms = {
    'る': "終止形",
    'て': 'て形',
    'れ': '仮定形',
    'られ': '可能形',
    'れば': '仮定形 ば_接尾辞',
    'た': '過去形',
    'ず': "ず_接尾辞",
    'よ': '命令形',
    'よう': '意志形',
    'ろ': '命令形',
    'りゃあ': '仮定形 ば_接尾辞',
}

proclitics = [
    ("御", ("Prefix",)),
    ("不", ("Prefix",)),
    ("元", ("Prefix",)),
]
enclitics = [
    ("は", ("Particle",)),
    ("も", ("Particle",)),
    ("が", ("Particle",)),
    ("に", ("Particle",)),
    ("に", ("Particle",)),
]

contractions = {
    'そりゃあ': 'それ_代名詞 は_助詞',
    'こりゃあ': 'これ_代名詞 は_助詞',
    'ありゃあ': 'あれ_代名詞 は_助詞',
    'っちゅう': f'{generate_morphological_string("って", "Particle")} {generate_morphological_string("言う", "Verb")} 終止形',
    'っつう': f'{generate_morphological_string("って", "Particle")} {generate_morphological_string("言う", "Verb")} 終止形',
}

inflection_to_morphemes = {
    'Imperfective': '未然形',
    'Continuative': '連用形',
    'Terminal': '終止形',
    'Hypothetical': '仮定形',
    'Imperative': '命令形',
    'Passive': '未然形 受身形 終止形',
    'Causative': '未然形 使役形 終止形',
    'Potential': '可能形',
    'Volitional': '意志形',
    'Negative': '未然形 ない_形容詞',
    'Negative continuative': '未然形 ず_接尾辞',
    'Formal': '連用形 ます_助動詞',
    'Perfective': '過去形',
    'Conjunctive': 'て形',
    'Hypothetical conditional': '仮定形 ば_接尾辞',
    'Adverbial': '副詞',
    'Degree': 'さ_接尾辞',
}
chau_forms = {
    "ちゃい": "しまう_助動詞 連用形",
    "ちゃう": "しまう_助動詞 終止形",
    "ちゃ": "は_助詞",
    "ちゃわ": "しまう_助動詞 未然形",
    "ちゃおう": "しまう_助動詞 意志形",
    "ちゃえ": "しまう_助動詞 命令形",
    "ちゃった": "しまう_助動詞 過去形",
    "ちゃって": "しまう_助動詞 て形"
}
chimau_forms = {  # Already has て形
    "ちまい": "しまう_助動詞 連用形",
    "ちまう": "しまう_助動詞 終止形",
    "ちまわ": "しまう_助動詞 未然形",
    "ちまおう": "しまう_助動詞 意志形",
    "ちまえ": "しまう_助動詞 命令形",
    "ちまって": " しまう_助動詞 て形",
    "ちまった": "しまう_助動詞 過去形",
}
jau_forms = {
    "じゃい": "しまう_助動詞 連用形",
    "じゃう": "しまう_助動詞 終止形",
    "じゃ": "は_助詞",
    "じゃおう": "しまう_助動詞 意志形",
    "じゃえ": "しまう_助動詞 命令形",
    "じゃえる": "しまう_助動詞 可能形",
    "じゃって": "しまう_助動詞 て形",
    "じゃった": "しまう_助動詞 過去形",
}
toku_forms = {
    "とき": "おく_助動詞 連用形",
    "とく": "おく_助動詞 終止形",
    "とこう": "おく_助動詞 意志形",
    "とけ": "おく_助動詞 命令形",
    "とける": "おく_助動詞 仮定形 終止形",
    "とけば": "おく_助動詞 仮定形 ば_接尾辞",
    "といて": "おく_助動詞 て形",
    "といた": "おく_助動詞 過去形",
}
doku_forms = {
    "どき": "おく_助動詞 連用形",
    "どく": "おく_助動詞 終止形",
    "どこう": "おく_助動詞 意志形",
    "どけ": "おく_助動詞 命令形",
    "どいて": "おく_助動詞 て形",
    "どいた": "おく_助動詞 過去形",
}
toru_forms = {
    "とり": "おる_助動詞 連用形",
    "とる": "おる_助動詞 終止形",
    "とろう": "おる_助動詞 意志形",
    "とれ": "おる_助動詞 命令形",
    "とった": "おる_助動詞 て形",
    "とって": "おる_助動詞 過去形",
}
doru_forms = {
    "どり": "おる_助動詞 連用形",
    "どる": "おる_助動詞 終止形",
    "どろう": "おる_助動詞 意志形",
    "どれ": "おる_助動詞 命令形",
    "どった": "おる_助動詞 て形",
    "どって": "おる_助動詞 過去形",
}
taru_forms = {
    "たり": "やる_助動詞 連用形",
    "たる": "やる_助動詞 終止形",
    "たろう": "やる_助動詞 意志形",
    "たれ": "やる_助動詞 命令形",
    "たった": "やる_助動詞 て形",
    "たって": "やる_助動詞 過去形",
}
daru_forms = {
    "だり": "やる_助動詞 連用形",
    "だる": "やる_助動詞 終止形",
    "だろう": "やる_助動詞 意志形",
    "だれ": "やる_助動詞 命令形",
    "だった": "やる_助動詞 て形",
    "だって": "やる_助動詞 過去形",
}

ba_contractions = {
    'けば': 'きゃあ',
    'れば': 'りゃあ',
}
name_morph_string ={
    '工業工場': '工業_名詞 工場_名詞',
    'ゴルフクラブゴルフ場': 'ゴルフ_名詞 クラブ_名詞 ゴルフ_名詞 場_接尾辞',
    'ゴルフ場': 'ゴルフ_名詞 場_接尾辞',
    '生命保険': '生命_名詞 保険_名詞',
}

def generate_chau_forms(form, morph_string):
    if not form.endswith('て') and not form.endswith('で'):
        return []
    base_form = form[:-1]
    forms = []
    if form.endswith('て'):
        extra_forms = itertools.chain(chau_forms.items(), chimau_forms.items())
    else:
        extra_forms = jau_forms.items()
    for t, ms in extra_forms:
        current_form = base_form+t
        current_morph_string = f"{morph_string} {ms}"
        forms.append((current_form, current_morph_string))
        if current_form.endswith('い'):
            forms.extend(generate_continuative_forms(current_form, current_morph_string))
            forms.extend(generate_tai_forms(current_form, current_morph_string))
        elif current_form.endswith('え'):
            current_morph_string = current_morph_string.replace("命令形", "可能形")
            forms.extend(generate_continuative_forms(current_form, current_morph_string))
            forms.extend(generate_tai_forms(current_form, current_morph_string))
            for t2, ms2 in ichidan_forms.items():
                if t2 == 'られ':
                    continue
                forms.append((t+t2, f"{current_morph_string} {ms2}"))
        elif current_form.endswith('わ'):
            forms.extend(generate_nai_forms(current_form, morph_string))
    return forms

def generate_tai_forms(form, morph_string):
    forms = []
    for t, ms in tai_forms.items():
        forms.append((form + t, f"{morph_string} {ms}"))
    return forms

def generate_nai_forms(form, morph_string):
    forms = []
    for t, ms in nai_forms.items():
        forms.append((form + t, f"{morph_string} {ms}"))
    return forms

def generate_continuative_forms(form, morph_string):
    forms = []
    for t, ms in continuative_forms.items():
        forms.append((form + t, f"{morph_string} {ms}"))
    return forms

def generate_ra_ri_forms(form, morph_string):
    return [
        (form+'ら', f"{morph_string} ら_接尾辞"),
        (form+'り', f"{morph_string} り_接尾辞")
    ]

def generate_ichidan_conjucations(form, morph_string):
    forms = []
    for t, ms in ichidan_forms.items():
        new_form = form+t
        new_morph_string = f"{morph_string} {ms}"
        forms.append((new_form, new_morph_string))
        if t == 'て':
            forms.extend(generate_chau_forms(new_form, new_morph_string))
        elif t == 'た':
            forms.extend(generate_ra_ri_forms(new_form, new_morph_string))
        elif t == 'られ':
            for t2, ms2 in ichidan_forms.items():
                if t2 == t:
                    continue
                forms.append((t+t2, f"{new_morph_string} {ms2}"))
    return forms

def generate_ichidan_causative(form, morpheme_string):
    base_form = form + 'させ'
    base_ms  = f"{morpheme_string} 使役形"
    forms = [(base_form, base_ms)]
    forms.extend(generate_continuative_forms(base_form, base_ms))
    forms.extend(generate_tai_forms(base_form, base_ms))
    forms.extend(generate_nai_forms(base_form, base_ms))
    forms.extend(generate_ichidan_conjucations(base_form, base_ms))
    forms.extend(generate_ichidan_passive(base_form, base_ms))
    return forms

def generate_ichidan_passive(form, morpheme_string):
    base_form = form + 'られ'
    base_ms  = f"{morpheme_string} 受身形"
    forms = [(base_form, base_ms)]
    forms.extend(generate_continuative_forms(base_form, base_ms))
    forms.extend(generate_tai_forms(base_form, base_ms))
    forms.extend(generate_nai_forms(base_form, base_ms))
    forms.extend(generate_ichidan_conjucations(base_form, base_ms))
    return forms

def generate_nai_mapping(morphemes):
    nai_mapping = {}
    form = morphemes["ない"][("-i", "Suffix")][0]

    for inflection, w in form['inflections'].items():
        if inflection not in inflection_to_morphemes:
            continue
        if 'Negative' in inflection:
            continue
        for wf in w['written_forms']:
            if 'ō' in wf or wf.startswith('-'):
                continue
            nai_mapping[wf] = f"ない_接尾辞 {inflection_to_morphemes[inflection]}"
    nai_mapping['なきゃ'] = 'ない_接尾辞 副詞 て形 は_助詞'
    return nai_mapping

def generate_tai_mapping(morphemes):
    tai_mapping = {}
    form = morphemes["たい"][("-i", "Suffix")][0]

    for inflection, w in form['inflections'].items():
        if inflection not in inflection_to_morphemes:
            continue
        if 'Negative' in inflection:
            continue
        for wf in w['written_forms']:
            if 'ō' in wf or wf.startswith('-'):
                continue
            tai_mapping[wf] = f"たい_接尾辞 {inflection_to_morphemes[inflection]}"
    return tai_mapping

def generate_continuative_mapping(morphemes):
    continuative_forms = {
        "ます": 'ます_助動詞',
        "ました": 'ます_助動詞 過去形',
        "まして": 'ます_助動詞 て形',
        "ましょう": 'ます_助動詞 意志形',
        "ませ": 'ます_助動詞 命令形',
        "ません": 'ます_助動詞 ない_形容詞',
        "まへん": 'ます_助動詞 ない_形容詞',
        "ながら": 'ながら_助詞',
        "そう": 'そう_助詞'
    }
    inflected_continuative_suffixes = ["たい", "辛い", "易い", '難い']
    for suffix in inflected_continuative_suffixes:
        for form in morphemes[suffix][("-i", "Suffix")]:
            for inflection, w in form['inflections'].items():
                if inflection not in inflection_to_morphemes:
                    continue
                if 'Negative' in inflection:
                    continue
                if 'Formal' in inflection:
                    continue
                for wf in w['written_forms']:
                    if 'ō' in wf or wf.startswith('-'):
                        continue
                    continuative_forms[wf] = f"{suffix}_接尾辞 {inflection_to_morphemes[inflection]}"
                    if inflection == 'Adverbial':
                        new_wf = wf[:-1] + 'う'
                        continuative_forms[new_wf] = f"{suffix}_接尾辞 {inflection_to_morphemes[inflection]}"
                        new_wf = wf[:-1] + 'きゃ'
                        continuative_forms[new_wf] = f"{suffix}_接尾辞 {inflection_to_morphemes[inflection]} て形 は_助詞"
    return continuative_forms


def generate_name_morphological_string(word, pos, names):
    if 'Station Name' in pos:
        if word.endswith('駅'):
            base_name = word[:-1]
            if base_name in names:
                pos = list(names[base_name].keys())
                if len(pos) > 1:
                    pos = [x for x in pos if x != 'Proper Noun']
                base_morph_string = generate_name_morphological_string(base_name, pos[0], names)
                return f"{base_morph_string} 駅_接尾辞"
    elif 'Group Name' in pos:
        for noun  in ['放送', '会社', '社', '生命保険']:
            base_name = word[:-len(noun)]
            if word.endswith(noun) and word[:-len(noun)] in names:
                pos = list(names[base_name].keys())
                if len(pos) > 1:
                    pos = [x for x in pos if x != 'Proper Noun']
                base_morph_string = generate_name_morphological_string(base_name, pos[0], names)
                if noun in name_morph_string:
                    return f"{base_morph_string} {name_morph_string[noun]}"
                return f"{base_morph_string} {noun}_名詞"
    elif 'Product Name' in pos:
        for noun  in ['新聞']:
            base_name = word[:-len(noun)]
            if word.endswith(noun) and word[:-len(noun)] in names:
                pos = list(names[base_name].keys())
                if len(pos) > 1:
                    pos = [x for x in pos if x != 'Proper Noun']
                base_morph_string = generate_name_morphological_string(base_name, pos[0], names)
                if noun in name_morph_string:
                    return f"{base_morph_string} {name_morph_string[noun]}"
                return f"{base_morph_string} {noun}_名詞"
    elif 'Place Name' in pos:
        for place_suffix in ['山', '湖', '城', '川', '州', '県', '町', '市', '区', '村']:
            if word.endswith(place_suffix):
                base_name = word[:-1]
                if word[:-1] in names and 'Place Name' in names[word[:-1]]:
                    pos = list(names[base_name].keys())
                    if len(pos) > 1:
                        pos = [x for x in pos if x != 'Proper Noun']
                    base_morph_string = generate_name_morphological_string(base_name, pos[0], names)
                    return f"{base_morph_string} {place_suffix}_接尾辞"
        for noun  in ['公園', '役所', 'トンネル', '神社', 'ヒュッテ', '発電所',
                      'ゴルフクラブゴルフ場', 'ゴルフ場', '工業工場', 'ダム', '大学校',
                      '半島', '人民軍', '学園', '学校', '大学']:
            base_name = word[:-len(noun)]
            if word.endswith(noun) and word[:-len(noun)] in names:
                pos = list(names[base_name].keys())
                if len(pos) > 1:
                    pos = [x for x in pos if x != 'Proper Noun']
                base_morph_string = generate_name_morphological_string(base_name, pos[0], names)
                if noun in name_morph_string:
                    return f"{base_morph_string} {name_morph_string[noun]}"
                return f"{base_morph_string} {noun}_名詞"
        return f"{word}_地名"
    elif 'Individual Name' in pos:
        return f"{word}_人名"
    return f"{word}_固有名詞"


def fix_forms(forms):
    new_forms = []
    for form in forms:
        kanji_definitions = {}
        for d  in form['definitions']:
            m = re.match(r"(?P<kanji>[一-龯]+): (?P<definition>.*)",d)
            if m:
                kanji_definitions[d] = (m.group('kanji'), m.group('definition'))
        form['definitions'] = [x for x in form['definitions'] if x not in kanji_definitions]
        if form['definitions']:
            new_forms.append(form)
        for k, definition in kanji_definitions.values():
            new_form = {'written_forms':[k], 'definitions': [definition]}
            new_form['written_forms'].extend(form['written_forms'])
            new_forms.append(new_form)
    return new_forms

def generate_morphological_training_data(lexicon: dict[dict[list[dict]]], morphemes,names):
    with open(morphology_training_path, 'w', encoding='utf8') as f:
        for word, pos_data in morphemes.items():
            for pos, forms in pos_data.items():
                for form in forms:
                    for wf in form['written_forms']:
                        if 'ō' in wf or wf.startswith('-'):
                            continue
                        morph_string = generate_morphological_string(word,  pos)
                        f.write(f"{wf}\t{morph_string}\n")
        for word, pos_data in names.items():
            for pos, forms in pos_data.items():
                morph_string = generate_name_morphological_string(word,  pos, names)
                f.write(f"{word}\t{morph_string}\n")
        for word, pos_data in lexicon.items():
            for pos, forms in pos_data.items():
                for form in forms:
                    for wf in form['written_forms']:
                        if 'ō' in wf or wf.startswith('-'):
                            continue
                        morph_string = generate_morphological_string(word,  pos)
                        f.write(f"{wf}\t{morph_string}\n")
                    if 'Verb' in pos and 'suru' in pos:
                        continue
                    if 'inflections' in form:
                        for inflection, w in form['inflections'].items():
                            if inflection not in inflection_to_morphemes:
                                continue
                            if 'Adjective' in pos:
                                if 'Negative' in inflection:
                                    continue
                                if '-na' in pos:
                                    if 'Degree' not in inflection:
                                        continue
                            for wf in w['written_forms']:
                                if 'ō' in wf or wf.startswith('-'):
                                    continue
                                morph_string = generate_morphological_string(word,  pos, inflection)
                                f.write(f"{wf}\t{morph_string}\n")
                                if 'Continuative' in inflection:
                                    for c, ms in generate_continuative_forms(wf, morph_string):
                                        f.write(f"{c}\t{ms}\n")
                                elif 'Potential' in inflection:
                                    for c, ms in generate_continuative_forms(wf, morph_string):
                                        f.write(f"{c}\t{ms}\n")
                                    for c, ms in generate_nai_forms(wf, morph_string):
                                        f.write(f"{c}\t{ms}\n")
                                    for c, ms in generate_tai_forms(wf, morph_string):
                                        f.write(f"{c}\t{ms}\n")
                                elif 'Perfective' in inflection:
                                    for c, ms in generate_ra_ri_forms(wf, morph_string):
                                        f.write(f"{c}\t{ms}\n")
                                elif "Hypothetical conditional" in inflection:
                                    mod_c, s = wf[:-2], wf[-2:]
                                    if s in ba_contractions:
                                        f.write(f"{mod_c}{ba_contractions[s]}\t{ms}\n")
                                elif "Passive" in inflection:
                                    base_morph_string = morph_string.rsplit(maxsplit=1)[0]
                                    for c, ms in generate_ichidan_conjucations(wf[:-1], base_morph_string):
                                        f.write(f"{c}\t{ms}\n")
                                elif "Causative" in inflection:
                                    base_morph_string = morph_string.rsplit(maxsplit=1)[0]
                                    if wf[-1] == 'る':
                                        for c, ms in generate_ichidan_passive(wf[:-1], base_morph_string):
                                            f.write(f"{c}\t{ms}\n")
                                        for c, ms in generate_ichidan_conjucations(wf[:-1], base_morph_string):
                                            f.write(f"{c}\t{ms}\n")
                                    elif wf[-1] == 'す':
                                        for c, ms in generate_ichidan_passive(wf[:-1] + 'され', base_morph_string):
                                            f.write(f"{c}\t{ms}\n")
                                        for c, ms in generate_ichidan_conjucations(wf[:-1] + 'され', base_morph_string):
                                            f.write(f"{c}\t{ms}\n")
                                        for c, ms in generate_tai_forms(wf[:-1] + 'され', base_morph_string):
                                            f.write(f"{c}\t{ms}\n")
                                        for c, ms in generate_nai_forms(wf[:-1] + 'され', base_morph_string):
                                            f.write(f"{c}\t{ms}\n")
                                        for c, ms in generate_continuative_forms(wf[:-1] + 'し', base_morph_string):
                                            f.write(f"{c}\t{ms}\n")
    return


def load_morphemes():
    morphemes =  collections.defaultdict(dict)
    with open(morpheme_path, encoding='utf8') as f:
        reader = jsonlines.Reader(f)
        for line in reader:
            word, pos = line['key'][0], tuple(line['key'][1])
            line = {k: v for k,v in line.items() if k not in ['word', 'pos_tags', 'key']}
            if word in morphemes and pos in morphemes[word]:
                for other_morph in morphemes[word][pos]:
                    if set(other_morph['written_forms']) == set(line['written_forms']):
                        for d in line['definitions']:
                            if d not in other_morph['definitions']:
                                other_morph['definitions'].append(d)
                        break
                else:
                    morphemes[word][pos].append(line)
            else:
                morphemes[word][pos] = [line]
    return morphemes


def load_lexicon():
    lexicon = collections.defaultdict(dict)
    with open(japanese_path, encoding='utf8') as f:
        reader = jsonlines.Reader(f)
        for line in reader:
            word, pos = line['key'][0], tuple(line['key'][1])
            line = {k: v for k,v in line.items() if k not in ['word', 'pos_tags', 'key']}
            if word in lexicon and pos in lexicon[word]:
                for other_morph in lexicon[word][pos]:
                    if set(other_morph['written_forms']) == set(line['written_forms']):
                        for d in line['definitions']:
                            if d not in other_morph['definitions']:
                                other_morph['definitions'].append(d)
                        break
                else:
                    lexicon[word][pos].append(line)
            else:
                lexicon[word][pos] = [line]
    return lexicon

def load_name_dict():
    names = collections.defaultdict(dict)
    if not os.path.exists(japanese_names_path):
        with open("D:/Data/speech/dictionaries/japanese/JMnedict.xml", 'r', encoding='utf8') as f, \
                open(japanese_names_path, 'w', encoding='utf8') as outf:
            content = bs(f.read(), features='xml')
            words = content.findAll('entry')
            writer = jsonlines.Writer(outf)
            for w in words:
                kanji = w.find('keb')
                readings = [x.text for x in w.findAll('reb')]
                if not readings:
                    continue
                name_type = w.find("name_type")
                if name_type is None:
                    continue
                if kanji is not None:
                    kanji = kanji.text
                    word = kanji
                    forms = [kanji]
                else:
                    word = readings[0]
                    forms = []
                definitions = [x.text for x in w.findAll('trans_det')]
                forms.extend(readings)
                pos = ['Proper Noun']
                if any (x in name_type for x in ['surname', 'fem',
                                                 'person', 'masc',
                                                 'given', 'char', 'dei']):
                    pos.append('Individual Name')
                elif 'place' in name_type:
                    pos.append('Place Name')
                elif 'station' in name_type:
                    pos.append('Station Name')
                elif 'serv' in name_type:
                    pos.append('Service Name')
                elif 'ev' in name_type:
                    continue
                elif any(x in name_type for x in ['work', 'obj', 'doc']):
                    pos.append('Media Name')
                elif any(x in name_type for x in ['creat', 'leg', 'myth']):
                    pos.append('Creature Name')
                elif any(x in name_type for x in ['company', 'organization', 'group']):
                    pos.append('Group Name')
                elif 'product' in name_type:
                    pos.append('Product Name')
                elif 'relig' in name_type:
                    continue
                elif any(x in name_type for x in ['unclass', 'obj', 'oth']):
                    pass
                else:
                    continue
                pos = tuple(pos)
                line = {'written_forms': forms, 'pos_tags': pos, "definitions": definitions}
                if word in names and pos in names[word]:
                    names[word][pos].append(line)
                else:
                    names[word][pos] = [line]
                names[word][pos].append(line)
                out_line = {'key': [word, pos], 'written_forms': forms, 'pos_tags': pos, "definitions": definitions}
                writer.write(out_line)
    else:
        with open(japanese_names_path, encoding='utf8') as f:
            reader = jsonlines.Reader(f)
            for line in reader:
                word, pos = line['key'][0], tuple(line['key'][1])
                line = {k: v for k,v in line.items() if k not in ['word', 'pos_tags', 'key']}
                if word in lexicon and pos in lexicon[word]:
                    names[word][pos].append(line)
                else:
                    names[word][pos] = [line]
    return names

if __name__ == '__main__':
    with open(training_path, encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            word, pron = line.split('\t')
            prons[word] = pron

    to_g2p = set()
    morphemes = load_morphemes()
    lexicon = load_lexicon()
    names = load_name_dict()
    continuative_forms = generate_continuative_mapping(morphemes)
    nai_forms = generate_nai_mapping(morphemes)
    tai_forms = generate_tai_mapping(morphemes)
    generate_morphological_training_data(lexicon, morphemes, names)
    error
    POS_CATEGORIES = set()
    INFLECTION_CATEGORIES = collections.defaultdict(set)
    with open(japanese_path, encoding='utf8') as f, \
        open(kana_g2pped_path, 'w', encoding='utf8') as outf:
        reader = jsonlines.Reader(f)
        for line in reader:
            pos = tuple(line['key'][1])
            POS_CATEGORIES.add(pos)
            if 'inflections' in line:
                INFLECTION_CATEGORIES[pos].update(line['inflections'].keys())
            continue
            if 'inflections' in line and line['inflections']:
                if 'Verb' not in line['pos_tags']:
                    continue
                for inflection, forms in line['inflections'].items():
                    if 'Formal' in inflection:
                        continue
                    p = []
                    non_kana_forms = []
                    kana_forms = []
                    for form in forms['written_forms']:
                        if re.search(r'[^ぁ-んァ-ン]', form):
                            non_kana_forms.append(form)
                            if 'Continuative' in inflection:
                                non_kana_forms.extend(generate_continuative_forms(form))
                            elif 'Hypothetical' in inflection:
                                non_kana_forms.extend(generate_continuative_forms(form))
                                non_kana_forms.extend(generate_nai_forms(form))
                                non_kana_forms.extend(generate_tai_forms(form))
                            elif 'Imperfective' in inflection:
                                non_kana_forms.extend(generate_nai_forms(form))
                            elif 'Perfective' in inflection:
                                non_kana_forms.extend(generate_ra_ri_forms(form))
                            elif "Passive" in inflection:
                                non_kana_forms.extend(generate_ichidan_conjucations(form[:-1]))
                            elif "Causative" in inflection:
                                if form[-1] == 'る':
                                    non_kana_forms.extend(generate_ichidan_passive(form[:-1]))
                                    non_kana_forms.extend(generate_ichidan_conjucations(form[:-1]))
                                elif form[-1] == 'す':
                                    non_kana_forms.extend(generate_ichidan_conjucations(form[:-1] + 'され'))
                                    non_kana_forms.extend(generate_tai_forms(form[:-1] + 'され'))
                                    non_kana_forms.extend(generate_nai_forms(form[:-1] + 'され'))
                                    non_kana_forms.extend(generate_continuative_forms(form[:-1] + 'し'))
                                else:
                                    print(inflection)
                                    print(form)
                                    error
                        else:
                            kana_forms.append(form)
                            if 'Continuative' in inflection:
                                kana_forms.extend(generate_continuative_forms(form))
                            elif 'Hypothetical' in inflection:
                                kana_forms.extend(generate_continuative_forms(form))
                                kana_forms.extend(generate_nai_forms(form))
                                kana_forms.extend(generate_tai_forms(form))
                            elif 'Imperfective' in inflection:
                                kana_forms.extend(generate_nai_forms(form))
                            elif "Passive" in inflection:
                                kana_forms.extend(generate_ichidan_conjucations(form[:-1]))
                            elif "Causative" in inflection:
                                if form[-1] == 'る':
                                    kana_forms.extend(generate_ichidan_passive(form[:-1]))
                                    kana_forms.extend(generate_ichidan_conjucations(form[:-1]))
                                elif form[-1] == 'す':
                                    kana_forms.extend(generate_ichidan_conjucations(form[:-1] + 'され'))
                                    kana_forms.extend(generate_tai_forms(form[:-1] + 'され'))
                                    kana_forms.extend(generate_nai_forms(form[:-1] + 'され'))
                                    kana_forms.extend(generate_continuative_forms(form[:-1] + 'し'))
                                else:
                                    print(inflection)
                                    print(form)
                                    error

    for pos in POS_CATEGORIES:
        print(pos)
        if pos in INFLECTION_CATEGORIES:
            print('INFLECTIONS:', INFLECTION_CATEGORIES[pos])
    print(len(POS_CATEGORIES))