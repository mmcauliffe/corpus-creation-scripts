import html
import re
import fugashi
import os
from pathlib import Path
import jsonlines
from bs4 import BeautifulSoup as bs
import subprocess
working_directory = r"D:/Data/speech/dictionaries/japanese"

name_path = os.path.join(working_directory, "JMnedict.xml")
kana_g2pped_path = os.path.join(working_directory, "kana_g2pped.txt")
g2p_path = Path(r"C:\Users\michael\Documents\Dev\mfa-models\g2p\staging\japanese_mfa.zip")
morphological_parser_path = r"D:\Data\models\large_train\japanse_lexicon_mfa.zip"
output_path = os.path.join(working_directory, "japanese.jsonl")
training_path = Path(r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\japanese_mfa.dict")
prons = {}

new_pronunciations = []

pos_mapping = {
    '&n-pr;': '固有名詞',
    '&int;': '感嘆詞',
    '&pn;': '代名詞',
    '&ctr;': '助数詞',
    '&conj;': '接続詞',
    '&aux-v;': '助動詞',
    '&num;': '数詞',
    '&prt;': '助詞',
    '&pref;': '接頭辞',
    '&suf;': '接尾辞',
    '&adj-i;': '形容詞',
    '&adj-pn;': '連体詞',
    '&adj-no;': '名詞',
    '&adj-na;': '形容動詞',
    '&adv;': '副詞',
    '&adv-to;': '副詞',
    '&n;': '名詞',
    '&vs;': '動名詞',
    '&v1;': '動名詞',
    '&v5k;': '動詞',
    '&v5u;': '動詞',
    '&v5b;': '動詞',
    '&v5m;': '動詞',
    '&v5n;': '動詞',
    '&v5r;': '動詞',
    '&v5s;': '動詞',
    '&v5t;': '動詞',
    '&v5uru;': '動詞',
    '&v5u-s;': '動詞',
    '&v5r-i;': '動詞',
    '&v5k-s;': '動詞',

}
xrefs = {}

verb_prefixes = {
    "差し",
    "追い",
    "生い",
}

noun_suffixes = {
    "差し",
    "立て",
}

def generate_pronunciation(word, g2p_proc):
    g2p_proc.stdin.write(f"{word}\n")
    g2p_proc.stdin.flush()
    o = g2p_proc.stdout.readline()
    print(o)
    try:
        pronunciation = o.strip().split('\t')[1]
    except IndexError:
        return None
    return pronunciation

if __name__ == '__main__':
    with open(training_path, encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            word, pron = line.split('\t')
            prons[word] = pron
    g2p_proc = subprocess.Popen([
        'mfa',
        'g2p',
        '-',
        g2p_path,
        '-',
        '-t', r'D:\g2p_temp',
        '--num_pronunciations', '1'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8', env=os.environ)
    tagger = fugashi.Tagger("-Owakati")
    dictionary = {}
    with open(name_path, 'r', encoding='utf8') as f:
        content = bs(f.read(), features='lxml')
    words = content.findAll('entry')
    word_mapping = {}
    with open(output_path, 'w', encoding='utf8') as f, \
        open(kana_g2pped_path, 'w', encoding='utf8') as outf:
        writer = jsonlines.Writer(f)
        for w in words:
            kanji = w.find('keb')
            if kanji is not None:
                kanji = kanji.text
            index = w.find('ent_seq').text
            readings = []
            for r_e in w.findAll('r_ele'):
                reb = r_e.find('reb')
                if reb is None:
                    continue
                reading = reb.text
                if reading not in prons:
                    pron = generate_pronunciation(reading, g2p_proc)
                    if pron is not None:
                        prons[reading] = pron
                        outf.write(f"{reading}\t{prons[reading]}\n")
                        outf.flush()
                if reading not in prons:
                    continue
                if kanji:
                    re_restr = r_e.findAll('re_restr')
                    if not re_restr:
                        outf.write(f"{kanji}\t{prons[reading]}\n")
                        outf.flush()
                    else:
                        for restr in re_restr:
                            if restr.text not in prons:
                                outf.write(f"{restr.text}\t{prons[reading]}\n")
                                outf.flush()
            continue
            if not readings:
                continue
            if kanji is not None:
                kanji = kanji.text
                word = kanji
                readings.append(word)
            else:
                word = readings[0]
                kanji = ''
            senses = w.findAll('sense')
            pos_tags = set()
            misc_tags = set()
            glosses = set()
            for s in senses:

                pos_tags.update(html.unescape(x.text) for x in s.findAll('pos'))
                misc_tags.update(html.unescape(x.text) for x in s.findAll('misc'))
                glosses.update(x.text for x in s.findAll('gloss'))
                if "&abbr;" in misc_tags:
                    try:
                        xrefs[index] = s.find("xref").text
                    except AttributeError:
                        pass
            data = {'word': word}
            if glosses:
                data['definitions'] = tuple(sorted(glosses))
            if readings:
                data['written_forms'] = tuple(sorted(readings))
            if pos_tags:
                data['pos'] = tuple(sorted([x if x not in pos_mapping else pos_mapping[x] for x in pos_tags if x not in {'&vt;'}]))
            if misc_tags:
                data['misc'] = tuple(sorted(misc_tags))

            non_kana_forms = []
            kana_forms = []
            for wf in data['written_forms']:
                if re.search(r'[-a-zō]', wf):
                    continue
                if re.search(r'[^ぁ-んァ-ン]', wf):
                    non_kana_forms.append(wf)
                else:
                    kana_forms.append(wf)
            morpheme_list = []
            for x in tagger(word):
                morpheme = str(x)
                tag = x.pos.split(',')[0]
                morpheme_list.append(f"{morpheme}_{tag}")
            data['morphological_string'] = ' '.join(morpheme_list)
            if '&id;' in misc_tags:
                continue
            word_mapping[index] = data
            writer.write(data)
            print(data)
            print(non_kana_forms, kana_forms)
            if not non_kana_forms:
                continue
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
            if len(kana_pronunciations) == 1:
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
            elif len(non_kana_forms) == 1:
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

    g2p_proc.stdin.close()
