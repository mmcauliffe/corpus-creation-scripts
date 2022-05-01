import collections
import os.path
import re

import hanziconv
import hangul_jamo
import itertools
from montreal_forced_aligner.command_line.g2p import run_g2p

training_root = '/mnt/d/Data/speech/model_training_corpora'
g2p_model_dir = r'/mnt/c/Users/michael/Documents/Dev/mfa-models/g2p/staging'


languages = ['japanese', 'bulgarian', 'french', 'german', 'portuguese',
             'croatian', 'swedish', 'korean', 'thai', 'mandarin',
             'hausa', 'russian', 'spanish', 'english', 'vietnamese',
             'turkish', 'swahili', 'polish','czech','ukrainian']

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

models = {
    'spanish': ['spanish_spain_mfa.zip','spanish_latin_america_mfa.zip',],
    'portuguese': ['portuguese_brazil_mfa.zip','portuguese_portugal_mfa.zip',],
    'english': ['english_us_mfa.zip','english_uk_mfa.zip',],
    'serbian': ['croatian_mfa.zip',],
    'madarin': ['mandarin_china_mfa.zip','mandarin_erhua_mfa.zip','mandarin_taiwan_mfa.zip',],
    'vietnamese': ['vietnamese_ho_chi_minh_city_mfa.zip','vietnamese_hanoi_mfa.zip',
                   'vietnamese_hue_mfa.zip'],
}
chinese_ipa_mapping_files = {
    'mandarin_china': r"/mnt/d/Data/speech/dictionaries/wikipron/cleaned/mandarin_hani_standard.txt",
    'mandarin_erhua': r"/mnt/d/Data/speech/dictionaries/wikipron/cleaned/mandarin_hani_beijing.txt",
    'mandarin_taiwan': r"/mnt/d/Data/speech/dictionaries/wikipron/cleaned/mandarin_hani_taiwan.txt",
}

chinese_ipa_mapping = {}
for language, file in chinese_ipa_mapping_files.items():
    character_lookups = {
                    '峡': '崃',
                    '〇': '零',
                    '杠': '零',
                    '恒': '恆',
                    '斌': '彬',
                    '著': '着',
                }
    chinese_ipa_mapping[language] = {}
    vowel_pattern = re.compile(r'[˨˩˦˥˥˩˩˧˥]')
    vowel_end_pattern = re.compile(r'[˨˩˦˥˥˩˩˧˥]$')
    with open(file, 'r', encoding='utf8') as f:
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
                    if '儿' not in chinese_ipa_mapping[language]:
                        chinese_ipa_mapping[language]['儿'] = collections.Counter()
                    else:
                        chinese_ipa_mapping[language]['儿'].update(['ɻ'])
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
                if c not in chinese_ipa_mapping[language]:
                    chinese_ipa_mapping[language][c] = collections.Counter()
                chinese_ipa_mapping[language][c].update([p])
    for k,v in chinese_ipa_mapping[language].items():
        max_values = max(v.values())
        v = {k2:v2 for k2,v2 in v.items() if v2 > max_values - 10}
        chinese_ipa_mapping[language][k] = sorted(v, key=lambda x: v[x])[:2]

def load_oov_counts(input_path):
    counter = collections.Counter()
    with open(input_path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                word, count = line.split()
            except ValueError:
                continue
            if lang == 'korean':
                word = hangul_jamo.decompose(word)
            elif lang == 'german':
                if 'ß' in word:
                    new_word = word.replace('ß', 'ss')
                    output_mapping[new_word] = word
                    word = new_word
            counter[word] += int(count)
    return counter

def save_oov_file(counter, output_path, count_threshold=2):
    with open(output_path, 'w', encoding='utf8') as outf:
        for word, count in counter.items():
            if count_threshold and count < count_threshold:
                break
            outf.write(word + '\n')

def process_oov_counts(input_path, output_path, count_threshold=2):
    with open(input_path, 'r', encoding='utf8') as f, open(output_path, 'w', encoding='utf8') as outf:
        oovs = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                word, count = line.split()
            except ValueError:
                continue
            if count_threshold and int(count) == count_threshold:
                break
            if lang == 'korean':
                word = hangul_jamo.decompose(word)
            elif lang == 'german':
                if 'ß' in word:
                    new_word = word.replace('ß', 'ss')
                    output_mapping[new_word] = word
                    word = new_word
            elif lang == 'mandarin':
                oovs.append(word)
                continue
            outf.write(word + '\n')

if __name__ == '__main__':
    for lang in languages:
        print(lang)
        language_root = os.path.join(training_root, lang)
        validation_temporary_directory = os.path.join(language_root, 'validation_temp')
        if lang == 'mandarin':
            for corpus in os.listdir(language_root):
                for dialect, mapping in chinese_ipa_mapping.items():
                    g2pped_file = os.path.join(language_root, f'{corpus}_{dialect}.g2pped')
                    oov_file = os.path.join(validation_temporary_directory, corpus, f'{corpus}_validate_training', f'oov_counts_{dialect}_ipa.txt')
                    print(oov_file)
                    if not os.path.exists(oov_file):
                        continue
                    with open(oov_file, 'r', encoding='utf8') as f:
                        oovs = []
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                word, count = line.split()
                            except ValueError:
                                continue
                            oovs.append(word)
                    new_words = {}
                    missing_characters = set()
                    for w in oovs:
                        prons = []
                        possibles = {}
                        look_up = w
                        for m, replacement in character_lookups.items():
                            if m in w:
                                look_up = w.replace(m, replacement)
                        print(look_up, (look_up,) in mapping, (hanziconv.HanziConv.toSimplified(look_up),) in mapping)
                        look_up = hanziconv.HanziConv.toSimplified(look_up)
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
                        if len(possibles) > 1:
                            combinations = list(itertools.combinations(range(len(w) + 1), r=2))
                            print(combinations)
                            combinations = sorted(combinations, key=lambda x: (x[0], -(x[1] - x[0])))
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
            continue
        if lang in models:
            m = [os.path.join(g2p_model_dir,x) for x in models[lang]]
        else:
            m = [os.path.join(g2p_model_dir, lang+'_mfa.zip')]
        for model_path in m:
            if not os.path.exists(model_path) and lang != 'mandarin':
                continue
            dictionary_name = os.path.splitext(os.path.basename(model_path))[0]
            validation_temporary_directory = os.path.join(language_root, 'validation_temp')
            if not os.path.exists(validation_temporary_directory):
                continue
            g2p_temporary_directory = os.path.join(language_root, 'g2p_temp')
            to_g2p_file = os.path.join(validation_temporary_directory,
                                       f'{dictionary_name}.to_g2p')
            g2pped_file = os.path.join(language_root, f'{dictionary_name}.g2pped')
            oov_counter = collections.Counter()
            for corpus in os.listdir(language_root):
                output_mapping = {}
                oov_file = os.path.join(validation_temporary_directory, corpus, f'{corpus}_validate_training', f'oov_counts_{dictionary_name}.txt')
                print(oov_file, os.path.exists(oov_file))
                if not os.path.exists(oov_file):
                    continue
                oov_counter.update(load_oov_counts(oov_file))
            if not oov_counter:
                continue
            save_oov_file(oov_counter, to_g2p_file)
            #process_oov_counts(oov_file, to_g2p_file)
            if not os.path.exists(to_g2p_file):
                continue
            elif lang == 'korean':
                if 'jamo' not in model_path:
                    model_path = model_path.replace('_mfa.zip', '_jamo_mfa.zip')
            args = DefaultArgs(to_g2p_file, model_path, g2pped_file, os.path.join(g2p_temporary_directory,lang + '_g2p'))
            if False and os.path.exists(args.output_path):
                continue
            if lang != 'mandarin':
                run_g2p(args)
            if lang == 'korean':
                words = []
                with open(g2pped_file, 'r', encoding='utf8') as f:
                    for line in f:
                        words.append(hangul_jamo.compose(line))
                with open(g2pped_file.replace('.g2pped', '_hangul.g2pped'), 'w', encoding='utf8') as f:
                    for line in words:
                        f.write(line)
