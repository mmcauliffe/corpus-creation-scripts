import sys

import os
import collections
import itertools
import re

from pathlib import Path
import jsonlines
import subprocess

root_dir = Path(__file__).resolve().parent

japanese_path = root_dir.joinpath('rich_lexicons', 'japanese.jsonl')
morpheme_path = root_dir.joinpath('rich_lexicons', 'japanese_morphs.jsonl')
to_g2p_path = root_dir.joinpath('rich_lexicons', 'to_g2p.txt')
g2pped_path = root_dir.joinpath('rich_lexicons', 'g2pped.txt')
kana_g2pped_path = root_dir.joinpath('rich_lexicons', 'kana_g2pped.txt')

training_path = Path(r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\japanese_mfa.dict")
g2p_path = Path(r"C:\Users\michael\Documents\Dev\mfa-models\g2p\staging\japanese_mfa.zip")
prons = {}
new_forms = []

new_pronunciations = []

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

def generate_chau_forms(form):
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
        forms.append(current_form)
        if current_form.endswith('い'):
            forms.extend(generate_continuative_forms(current_form))
            forms.extend(generate_tai_forms(current_form))
        elif current_form.endswith('え'):
            forms.extend(generate_continuative_forms(current_form))
            forms.extend(generate_tai_forms(current_form))
            for t2, ms2 in ichidan_forms.items():
                if t2 == 'られ':
                    continue
                forms.append(t+t2)
        elif current_form.endswith('わ'):
            forms.extend(generate_nai_forms(current_form))
    return forms

def generate_tai_forms(form):
    forms = []
    for t in tai_forms:
        forms.append(form + t)
    return forms

def generate_nai_forms(form):
    forms = []
    for t in nai_forms:
        forms.append(form + t)
    return forms

def generate_continuative_forms(form):
    forms = []
    for t in continuative_forms:
        forms.append(form + t)
    return forms

def generate_ra_ri_forms(form):
    forms = [form+'ら', form+'り']
    return forms


def generate_ichidan_conjucations(form):
    forms = []
    for t, ms in ichidan_forms.items():
        new_form = form+t
        forms.append(new_form)
        if t == 'て':
            forms.extend(generate_chau_forms(new_form))
        elif t == 'た':
            forms.extend(generate_ra_ri_forms(new_form))
        elif t == 'られ':
            for t2, ms2 in ichidan_forms.items():
                if t2 == t:
                    continue
                forms.append(t+t2)
    return forms

def generate_ichidan_causative(form):
    base_form = form + 'させ'
    forms = [base_form]
    forms.extend(generate_continuative_forms(base_form))
    forms.extend(generate_tai_forms(base_form))
    forms.extend(generate_nai_forms(base_form))
    forms.extend(generate_ichidan_conjucations(base_form))
    forms.extend(generate_ichidan_passive(base_form))
    return forms

def generate_ichidan_passive(form):
    base_form = form + 'られ'
    forms = [base_form]
    forms.extend(generate_continuative_forms(base_form))
    forms.extend(generate_tai_forms(base_form))
    forms.extend(generate_nai_forms(base_form))
    forms.extend(generate_ichidan_conjucations(base_form))
    return forms

ba_contractions = {
    'けば': 'きゃあ',
    'れば': 'りゃあ',
}

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
        "なさい": 'なさい_助動詞',
        "なっせ": 'なさい_助動詞',
        "な": 'なさい_助動詞',
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
    continuative_forms = generate_continuative_mapping(morphemes)
    nai_forms = generate_nai_mapping(morphemes)
    tai_forms = generate_tai_mapping(morphemes)
    g2p_proc = subprocess.Popen([
        'mfa',
        'g2p',
        '-',
        g2p_path,
        '-',
        '-t', r'D:\g2p_temp',
        '--num_pronunciations', '1'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8', env=os.environ)
    with open(kana_g2pped_path, 'w', encoding='utf8') as outf:
        for word, pos_data in lexicon.items():
            for pos, forms in pos_data.items():
                for form in forms:
                    for wf in form['written_forms']:
                        if 'ō' in wf or wf.startswith('-'):
                            continue
                    if 'Verb' in pos and 'suru' in pos:
                        continue
                    if 'inflections' in form:
                        for inflection, w in form['inflections'].items():
                            if inflection not in inflection_to_morphemes:
                                continue
                            if 'Formal' in inflection:
                                continue
                            if 'Adjective' in pos:
                                if 'Negative' in inflection:
                                    continue
                                if '-na' in pos:
                                    if 'Degree' not in inflection:
                                        continue
                            p = []
                            non_kana_forms = []
                            kana_forms = []
                            for wf in w['written_forms']:
                                if re.search(r'[^ぁ-んァ-ン]', wf):
                                    non_kana_forms.append(wf)
                                    if 'Continuative' in inflection:
                                        non_kana_forms.extend(generate_continuative_forms(wf))
                                    elif 'Potential' in inflection:
                                        non_kana_forms.extend(generate_continuative_forms(wf))
                                        non_kana_forms.extend(generate_nai_forms(wf))
                                        non_kana_forms.extend(generate_tai_forms(wf))
                                    elif 'Imperfective' in inflection:
                                        non_kana_forms.extend(generate_nai_forms(wf))
                                    elif 'Perfective' in inflection:
                                        non_kana_forms.extend(generate_ra_ri_forms(wf))
                                    elif "Passive" in inflection:
                                        non_kana_forms.extend(generate_ichidan_conjucations(wf[:-1]))
                                    elif "Hypothetical conditional" in inflection:
                                        mod_c, s = wf[:-2], wf[-2:]
                                        if s in ba_contractions:
                                            non_kana_forms.append(f"{mod_c}{ba_contractions[s]}")
                                    elif "Causative" in inflection:
                                        if wf[-1] == 'る':
                                            non_kana_forms.extend(generate_ichidan_passive(wf[:-1]))
                                            non_kana_forms.extend(generate_ichidan_conjucations(wf[:-1]))
                                        elif wf[-1] == 'す':
                                            non_kana_forms.extend(generate_ichidan_conjucations(wf[:-1] + 'され'))
                                            non_kana_forms.extend(generate_tai_forms(wf[:-1] + 'され'))
                                            non_kana_forms.extend(generate_nai_forms(wf[:-1] + 'され'))
                                            non_kana_forms.extend(generate_continuative_forms(wf[:-1] + 'し'))
                                else:
                                    kana_forms.append(wf)
                                    if 'Continuative' in inflection:
                                        kana_forms.extend(generate_continuative_forms(wf))
                                    elif 'Hypothetical' in inflection:
                                        kana_forms.extend(generate_continuative_forms(wf))
                                        kana_forms.extend(generate_nai_forms(wf))
                                        kana_forms.extend(generate_tai_forms(wf))
                                    elif 'Imperfective' in inflection:
                                        kana_forms.extend(generate_nai_forms(wf))
                                    elif "Passive" in inflection:
                                        kana_forms.extend(generate_ichidan_conjucations(wf[:-1]))
                                    elif "Hypothetical conditional" in inflection:
                                        mod_c, s = wf[:-2], wf[-2:]
                                        if s in ba_contractions:
                                            kana_forms.append(f"{mod_c}{ba_contractions[s]}")
                                    elif "Causative" in inflection:
                                        if wf[-1] == 'る':
                                            kana_forms.extend(generate_ichidan_passive(wf[:-1]))
                                            kana_forms.extend(generate_ichidan_conjucations(wf[:-1]))
                                        elif wf[-1] == 'す':
                                            kana_forms.extend(generate_ichidan_conjucations(wf[:-1] + 'され'))
                                            kana_forms.extend(generate_tai_forms(wf[:-1] + 'され'))
                                            kana_forms.extend(generate_nai_forms(wf[:-1] + 'され'))
                                            kana_forms.extend(generate_continuative_forms(wf[:-1] + 'し'))

                            print(non_kana_forms, kana_forms)

                            kana_pronunciations = set()
                            for x in kana_forms:
                                if x not in prons:
                                    g2p_proc.stdin.write(f"{x}\n")
                                    g2p_proc.stdin.flush()
                                    # stdout, stderr = g2p_proc.communicate(f)
                                    stdout = g2p_proc.stdout.readline()
                                    kana_pronunciation = stdout.strip().split('\t')[1]
                                    outf.write(f"{x}\t{kana_pronunciation}\n")
                                    outf.flush()
                                    new_pronunciations.append((x, kana_pronunciation))
                                    prons[x] = kana_pronunciation
                                else:
                                    kana_pronunciation = prons[x]
                                kana_pronunciations.add(kana_pronunciation)
                            print(kana_pronunciations)
                            if len(kana_pronunciations) == 1 and non_kana_forms:
                                if non_kana_forms[0] in prons:
                                    continue
                                if kana_forms[0] not in prons:
                                    g2p_proc.stdin.write(f"{kana_forms[0]}\n")
                                    g2p_proc.stdin.flush()
                                    # stdout, stderr = g2p_proc.communicate(f)
                                    stdout = g2p_proc.stdout.readline()
                                    non_kana_pronunciation = stdout.strip().split('\t')[1]
                                    outf.write(f"{kana_forms[0]}\t{non_kana_pronunciation}\n")
                                    outf.flush()
                                    new_pronunciations.append((kana_forms[0], non_kana_pronunciation))
                                else:
                                    non_kana_pronunciation = prons[kana_forms[0]]
                                outf.write(f"{non_kana_forms[0]}\t{non_kana_pronunciation}\n")
                                outf.flush()
                                new_pronunciations.append((non_kana_forms[0], non_kana_pronunciation))
                            elif len(non_kana_forms) == 1 and non_kana_forms:
                                for wf in kana_forms:
                                    if wf not in prons:
                                        g2p_proc.stdin.write(f"{wf}\n")
                                        g2p_proc.stdin.flush()
                                        # stdout, stderr = g2p_proc.communicate(f)
                                        stdout = g2p_proc.stdout.readline()
                                        kana_pronunciation = stdout.strip().split('\t')[1]
                                        outf.write(f"{wf}\t{kana_pronunciation}\n")
                                        outf.flush()
                                        new_pronunciations.append((wf, kana_pronunciation))
                                        prons[wf] = kana_pronunciation
                                    else:
                                        kana_pronunciation = prons[wf]
                                    outf.write(f"{non_kana_forms[0]}\t{kana_pronunciation}\n")
                                    outf.flush()
                                    new_pronunciations.append((non_kana_forms[0], kana_pronunciation))
                            else:
                                for wf in non_kana_forms:
                                    if wf in prons:
                                        continue
                                    g2p_proc.stdin.write(f"{wf}\n")
                                    g2p_proc.stdin.flush()
                                    # stdout, stderr = g2p_proc.communicate(f)
                                    stdout = g2p_proc.stdout.readline().strip()
                                    print(stdout)
                                    try:
                                        non_kana_pronunciation = stdout.strip().split('\t')[1]
                                    except:
                                        continue
                                    if non_kana_pronunciation in kana_pronunciations:
                                        outf.write(f"{wf}\t{non_kana_pronunciation}\n")
                                        outf.flush()
                                        new_pronunciations.append((wf, non_kana_pronunciation))
                            continue
                    non_kana_forms = []
                    kana_forms = []
                    for wf in form['written_forms']:
                        if re.search(r'[-a-zō]', wf):
                            continue
                        elif re.search(r'[^ぁ-んァ-ン]', wf):
                            non_kana_forms.append(wf)
                        else:
                            kana_forms.append(wf)
                    print(line)
                    print(non_kana_forms, kana_forms)
                    if not non_kana_forms:
                        continue
                    kana_pronunciations = set()
                    for x in kana_forms:
                        if x not in prons:
                            g2p_proc.stdin.write(f"{x}\n")
                            g2p_proc.stdin.flush()
                            #stdout, stderr = g2p_proc.communicate(f)
                            stdout = g2p_proc.stdout.readline()
                            kana_pronunciation = stdout.strip().split('\t')[1]
                            outf.write(f"{x}\t{kana_pronunciation}\n")
                            outf.flush()
                            new_pronunciations.append((x, kana_pronunciation))
                            prons[x] = kana_pronunciation
                        else:
                            kana_pronunciation = prons[x]
                        kana_pronunciations.add(kana_pronunciation)
                    print(kana_pronunciations)
                    if len(kana_pronunciations) == 1:
                        if non_kana_forms[0] in prons:
                            continue
                        if kana_forms[0] not in prons:
                            g2p_proc.stdin.write(f"{kana_forms[0]}\n")
                            g2p_proc.stdin.flush()
                            #stdout, stderr = g2p_proc.communicate(f)
                            stdout = g2p_proc.stdout.readline()
                            non_kana_pronunciation = stdout.strip().split('\t')[1]
                            outf.write(f"{kana_forms[0]}\t{non_kana_pronunciation}\n")
                            outf.flush()
                            new_pronunciations.append((kana_forms[0], non_kana_pronunciation))
                        else:
                            non_kana_pronunciation = prons[kana_forms[0]]
                        outf.write(f"{non_kana_forms[0]}\t{non_kana_pronunciation}\n")
                        outf.flush()
                        new_pronunciations.append((non_kana_forms[0], non_kana_pronunciation))
                    elif len(non_kana_forms) == 1:
                        for wf in kana_forms:
                            if wf not in prons:
                                g2p_proc.stdin.write(f"{wf}\n")
                                g2p_proc.stdin.flush()
                                #stdout, stderr = g2p_proc.communicate(f)
                                stdout = g2p_proc.stdout.readline()
                                kana_pronunciation = stdout.strip().split('\t')[1]
                                outf.write(f"{wf}\t{kana_pronunciation}\n")
                                outf.flush()
                                new_pronunciations.append((wf, kana_pronunciation))
                                prons[wf] = kana_pronunciation
                            else:
                                kana_pronunciation = prons[wf]
                            outf.write(f"{non_kana_forms[0]}\t{kana_pronunciation}\n")
                            outf.flush()
                            new_pronunciations.append((non_kana_forms[0], kana_pronunciation))
                    else:
                        for wf in non_kana_forms:
                            if wf in prons:
                                continue
                            g2p_proc.stdin.write(f"{wf}\n")
                            g2p_proc.stdin.flush()
                            #stdout, stderr = g2p_proc.communicate(f)
                            stdout = g2p_proc.stdout.readline().strip()
                            print(stdout)
                            try:
                                non_kana_pronunciation = stdout.strip().split('\t')[1]
                            except:
                                continue
                            if non_kana_pronunciation in kana_pronunciations:
                                outf.write(f"{wf}\t{non_kana_pronunciation}\n")
                                outf.flush()
                                new_pronunciations.append((wf, non_kana_pronunciation))

    g2p_proc.stdin.close()

print(len(new_pronunciations))