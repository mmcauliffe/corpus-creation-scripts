import collections
import os.path
import re

import hanziconv
import hangul_jamo
import itertools
from montreal_forced_aligner.command_line.g2p import run_g2p

root_dir = r'/mnt/d/Data/speech/dictionaries/wikipron/gp_validation'
g2p_model_dir = r'/mnt/c/Users/michael/Documents/Dev/mfa-models/g2p/staging'
temp_dir = r'/mnt/d/temp/g2p_temp'


full_names = {
                'AR': 'Arabic',
                'BG': 'Bulgarian',
                'CH': 'Mandarin',
                'WU': 'Cantonese',
                'CR': 'Croatian',
                'CZ': 'Czech',
                'FR': 'French',
                'GE': 'German',
                'HA': 'Hausa',
                'JA': 'Japanese',
                'KO': 'Korean',
                'RU': 'Russian',
                'PO': 'Portuguese',
                'PL': 'Polish',
                'SP': 'Spanish',
                'SA': 'Swahili',
                'SW': 'Swedish',
                'TA': 'Tamil',
                'TH': 'Thai',
                'TU': 'Turkish',
                'VN': 'Vietnamese',
                'UA': 'Ukrainian'
                }
chinese_ipa_mapping_files = {
    'mandarin_standard': r"/mnt/d/Data/speech/dictionaries/wikipron/cleaned/mandarin_hani_standard.txt",
    'mandarin_erhua': r"/mnt/d/Data/speech/dictionaries/wikipron/cleaned/mandarin_hani_beijing.txt",
}
dialects = {
                'AR': [],
                'BG': ['bulgarian'],
                'CH': ['mandarin_standard', 'mandarin_erhua'],
                'WU': [],
                'CR': ['croatian'],
                'CZ': ['czech'],
                'FR': ['french'],
                'GE': ['german'],
                'HA': ['hausa'],
                'JA': ['japanese'],
                'KO': ['korean_jamo'],
                'RU': ['russian'],
                'PO': ['portuguese_brazil', 'portuguese_portugal'],
                'PL': ['polish'],
                'SP': ['spanish_castilian', 'spanish_latin_america'],
                'SA': ['swahili'],
                'SW': ['swedish'],
                'TA': ['tamil'],
                'TH': ['thai'],
                'TU': ['turkish'],
                'VN': ['vietnamese_hanoi',
              'vietnamese_hue', 'vietnamese_hochiminhcity'],
                'UA': ['ukrainian']
                }

lang_codes = ['bulgarian', 'croatian', 'czech', 'french', 'german', 'polish', 'portuguese_brazil',
              'portuguese_portugal', 'spanish_castilian', 'spanish_latin_america', 'swedish',
              'tamil', 'thai', 'turkish', 'ukrainian', 'swahili',
              'korean_jamo', 'korean_hangul', 'hausa', 'japanese', 'vietnamese_hanoi',
              'vietnamese_hue', 'vietnamese_hochiminhcity', 'russian', 'mandarin_hani']
#lang_codes = ['japanese']

# words that G2P models can't really do
ignore_words = {}

class DefaultArgs:
    def __init__(self, input_path, g2p_model_path, output_path, temporary_directory):
        self.input_path = input_path
        self.g2p_model_path = g2p_model_path
        self.output_path = output_path
        self.temporary_directory = temporary_directory
        self.config_path = None
        self.num_jobs = 10
        self.num_pronunciations = 1
        self.strict_graphemes = True
        self.debug = True
        self.verbose = True
        self.clean = True

for code, lang in full_names.items():

    output_mapping = {}
    print(lang)
    oov_file = os.path.join(root_dir, code, 'files_validate_training', 'oov_counts.txt')
    print(oov_file, os.path.exists(oov_file))
    if not os.path.exists(oov_file):
        continue
    to_g2p_file = os.path.join(root_dir, code, 'files_validate_training', 'to_g2p.txt')
    with open(oov_file, 'r', encoding='utf8') as f, open(to_g2p_file, 'w', encoding='utf8') as outf:
        oovs = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                word, count = line.split()
            except ValueError:
                continue
            #if int(count) == 2 and code != 'CZ':
            #    break
            if word in ignore_words:
                continue
            oovs.append(word)
            if code == 'KO':
                word = hangul_jamo.decompose(word)
            elif code == 'GE':
                if 'ß' in word:
                    new_word = word.replace('ß', 'ss')
                    output_mapping[new_word] = word
                    word = new_word
            outf.write(word + '\n')
    for dialect in dialects[code]:
        g2pped_file = os.path.join(root_dir, dialect+'_ipa.dict')
        if code == 'CH':
            character_lookups = {
                '峡': '崃',
                '〇': '零',
                '杠': '零',
                '恒': '恆',
                '斌': '彬',
                '著': '着',
            }
            mapping = {}
            vowel_pattern = re.compile(r'[˨˩˦˥˥˩˩˧˥]')
            vowel_end_pattern = re.compile(r'[˨˩˦˥˥˩˩˧˥]$')
            chinese_ipa_mapping_file = chinese_ipa_mapping_files[dialect]
            with open(chinese_ipa_mapping_file, 'r', encoding='utf8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    word, pronunciation = line.split('\t')
                    if len(word) == 1:
                        characters = [word]
                        pronunciations = [pronunciation]
                    else:
                        characters = []
                        pronunciations = []
                        phones = pronunciation.split()
                        if phones[-1] == 'ɻ' and word.endswith('儿'):
                            phones = phones[:-1]
                            word = word[:-1]
                            if '儿' not in mapping:
                                mapping['儿'] = collections.Counter()
                            else:
                                mapping['儿'].update(['ɻ'])
                        for c in word:
                            cur_pron = []
                            while True:
                                #print(c, cur_pron, phones)
                                if not phones:
                                    break
                                if not cur_pron and phones:
                                    cur_pron.append(phones.pop(0))
                                elif vowel_pattern.search(phones[0]):
                                    if cur_pron and vowel_pattern.search(cur_pron[-1]):
                                        break
                                    cur_pron.append(phones.pop(0))
                                elif phones[0] == 'ŋ':
                                    cur_pron.append(phones.pop(0))
                                    break
                                elif phones[0] in ['n', 'ɻ']:
                                    if len(phones) == 1:
                                        cur_pron.append(phones.pop(0))
                                        break
                                    elif vowel_pattern.search(phones[1]):
                                        break
                                    else:
                                        cur_pron.append(phones.pop(0))
                                        break
                                elif any(vowel_pattern.search(x) for x in cur_pron):
                                    break
                                else:
                                    cur_pron.append(phones.pop(0))
                            if cur_pron:
                                characters.append(c)

                                pronunciations.append(' '.join(cur_pron))
                            cur_pron = []
                    for x, y in itertools.combinations(
                            range(len(characters) + 1), r=2):
                        c = ''.join(characters[x:y])
                        p = ' '.join(pronunciations[x:y])
                        if not c:
                            continue
                        if c not in mapping:
                            mapping[c] = collections.Counter()
                        mapping[c].update([p])
            for k,v in mapping.items():
                max_values = max(v.values())
                v = {k2:v2 for k2,v2 in v.items() if v2 > max_values - 10}
                mapping[k] = sorted(v, key=lambda x: v[x])[:2]
            new_words = {}
            missing_characters = set()
            for w in oovs:
                prons = []
                possibles = {}
                look_up = w
                for m, replacement in character_lookups.items():
                    if m in w:
                        look_up= w.replace(m, replacement)
                print(look_up, (look_up,) in mapping, (hanziconv.HanziConv.toSimplified(look_up),) in mapping)
                look_up= hanziconv.HanziConv.toSimplified(look_up)
                for x, y in itertools.combinations(
                        range(len(look_up) + 1), r=2):
                    c = "".join(look_up[x:y])
                    if not c:
                        continue
                    if c in mapping:
                        possibles[''.join(c)] = mapping[c]
                    elif len(c) == 1:
                        missing_characters.update(c)
                        print(c)
                        continue
                if len(possibles) < len(w):
                    continue
                print("POSSIBLES", possibles)
                if len(possibles)> 1:
                    combinations = list(itertools.combinations(range(len(w) + 1), r=2))
                    print(combinations)
                    combinations = sorted(combinations, key=lambda x:(x[0], -(x[1]-x[0])))
                    last_ind = 0
                    prons = []
                    for x, y in combinations:
                        if x != last_ind:
                            continue

                        print(x, y, w[x:y], w[x:y] in possibles)
                        if look_up[x:y] in possibles:
                            print(x, y, look_up[x:y], possibles[look_up[x:y]])
                            prons.append(possibles[look_up[x:y]])
                            last_ind = y
                        if last_ind == len(w):
                            break
                else:
                    prons = possibles[''.join(c)]
                if False and len(prons) < len(w):
                    print(w)
                    print(prons)
                    error
                    continue
                new_prons = list(itertools.product(*prons))
                if len(w) == 1:
                    new_words[w] = [x for x in prons]
                else:
                    new_words[w] = sorted(set(' '.join(x) for x in new_prons))
                print("NEW WORDS", w, new_words[w])
                if False and w == '著名':
                    for k, v in possibles.items():
                        print(k, v)
                        print(mapping[k])
                    error
            print(missing_characters)
            with open(g2pped_file, 'w', encoding='utf8') as f:
                for word, prons in new_words.items():
                    for pron in prons:
                        if not pron:
                            continue
                            print(word)
                            error
                        f.write(f'{word}\t{pron}\n')
        else:
            model_path = os.path.join(g2p_model_dir, dialect+'_ipa.zip')
            if not os.path.exists(model_path):
                continue
            args = DefaultArgs(to_g2p_file, model_path, g2pped_file, os.path.join(temp_dir,code + '_g2p'))
            if os.path.exists(args.output_path):
                continue
            run_g2p(args)
        if code == 'KO':
            with open(args.output_path, 'r', encoding='utf8') as f, \
                open(args.output_path.replace('jamo', 'hangul'), 'w', encoding='utf8') as outf:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    word, pron = line.split(maxsplit=1)
                    word = hangul_jamo.compose(word)
                    outf.write(f"{word}\t{pron}\n")
        elif code == 'GE':
            with open(args.output_path, 'r', encoding='utf8') as f:
                words = []
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    word, pron = line.split(maxsplit=1)
                    if word in output_mapping:
                        words.append((output_mapping[word], pron))
                    words.append((word, pron))
            with open(args.output_path, 'w', encoding='utf8') as f:
                for word, pron in words:
                    f.write(f'{word}\t{pron}\n')


