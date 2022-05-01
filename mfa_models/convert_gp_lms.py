import dataclasses
import typing
import os
import re
import subprocess
import math

root_dir = '/mnt/d/Data/models/language_models'

langs = ['BG', 'CZ', 'FR', 'GE', 'HAU', 'HR', 'JP', 'KO', 'MAN', 'PL', 'PT', 'RU', 'SP', 'SWE', 'TA', 'TH', 'TU', 'VN']

seed = 1917

specials_set = {'<unk>', "<s>", "</s>"}
unknown_pattern = re.compile(r'\b([<＜]\S+[＞>])\b')

@dataclasses.dataclass
class Ngram:
    key: str
    log_probability: float
    backoff_weight: typing.Optional[float]

full_names = {
                'AR': 'Arabic',
                'BG': 'Bulgarian',
                'CH': 'Mandarin',
                'MAN': 'Mandarin',
                'WU': 'Cantonese',
                'CR': 'Croatian',
                'HR': 'Croatian',
                'CZ': 'Czech',
                'FR': 'French',
                'GE': 'German',
                'HA': 'Hausa',
                'HAU': 'Hausa',
                'JA': 'Japanese',
                'JP': 'Japanese',
                'KO': 'Korean',
                'RU': 'Russian',
                'PO': 'Portuguese',
                'PT': 'Portuguese',
                'PL': 'Polish',
                'SP': 'Spanish',
                'SA': 'Swahili',
                'SW': 'Swedish',
                'SWE': 'Swedish',
                'TA': 'Tamil',
                'TH': 'Thai',
                'TU': 'Turkish',
                'VN': 'Vietnamese',
                'UA': 'Ukrainian'
                }

def read_arpa(path, output_path):
    ngrams = {1:{}, 2:{}, 3:{}}
    current = 0
    header = []
    with open(path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line == r'\1-grams:':
                current = 1
                continue
            elif line == r'\2-grams:':
                current = 2
                continue
            elif line == r'\3-grams:':
                current = 3
                continue
            elif r'\data' in line or r'\end' in line:
                continue
            if current == 0:
                header.append(line)
                continue
            line = line.split('\t')
            probability = float(line[0])
            ngram = line[1]
            backoff = None
            if len(line) > 2:
                backoff = float(line[2])
            ngrams[current][ngram] = Ngram(ngram, probability, backoff)

    new_ngrams = {1:{}, 2:{}, 3:{}}
    print(header)
    for k, n in ngrams.items():
        print(k, len(n))
        for ng in n.values():
            ng.key = ng.key.lower()
            if '<' in ng.key and '<s>' not in ng.key and '</s>' not in ng.key:
                print(unknown_pattern, ng.key, unknown_pattern.findall(ng.key))
            for m in unknown_pattern.finditer(ng.key):
                print(ng.key, m, m.groups()[0])
                if m.groups()[0] not in specials_set:
                    ng.key = ng.key.replace(m.groups()[0], '<unk>')
            if ng.key not in new_ngrams[k]:
                new_ngrams[k][ng.key] = ng
                continue
            old_log_prob = new_ngrams[k][ng.key].log_probability
            old_log_backoff = new_ngrams[k][ng.key].backoff_weight
            old_prob = math.pow(10,old_log_prob)
            old_backoff = 0
            if old_log_backoff is not None:
                old_backoff = math.pow(10, old_log_backoff)

            new_log_prob = ng.log_probability
            new_prob = math.pow(10,new_log_prob)
            new_log_backoff = ng.backoff_weight
            new_backoff = 0
            if new_log_backoff is not None:
                new_backoff = math.pow(10, new_log_backoff)
            new_ngrams[k][ng.key].log_probability = math.log10(old_prob+new_prob)
            if new_backoff:
                #print(ng)
                #print(new_ngrams[k][ng.key])
                new_ngrams[k][ng.key].backoff_weight = math.log10(old_backoff+ new_backoff)

    with open(output_path, 'w', encoding='utf8') as f:
        f.write("\n")
        f.write("\\data\\")
        f.write("\n")
        for k, n in new_ngrams.items(): # Header
            print(k, len(n))
            f.write(f"ngram {k}={len(n)}\n")
        f.write("\n")

        for order, ngs in new_ngrams.items():
            f.write(f"\\{order}-grams:")
            f.write("\n")
            for ng in sorted(ngs.values(), key=lambda x: x.key):
                if ng.backoff_weight:
                    f.write(f"{ng.log_probability}\t{ng.key}\t{ng.backoff_weight}\n")
                else:
                    f.write(f"{ng.log_probability}\t{ng.key}\n")
            f.write("\n")
        f.write("\\end\\")


for lang in langs:
    if lang != 'JP':
        continue
    if lang in {'HR', 'SWE'}:
        continue
    temp_dir = os.path.join(root_dir, lang)
    os.makedirs(temp_dir, exist_ok=True)
    lm_path = os.path.join(root_dir, f'{lang}.3gram.lm')
    arpa_path = os.path.join(root_dir, f'{lang}.3gram.arpa')
    if not os.path.exists(arpa_path):
        os.rename(lm_path, arpa_path)
    mfa_lm_path = os.path.join(root_dir, f'{full_names[lang].lower()}_converted_lm.zip')
    subprocess.check_call(['mfa', 'train_lm', arpa_path, mfa_lm_path, '--keep_case', 'true'])
    continue







    lower_lm_path = os.path.join(temp_dir, f'{lang}.3gram.arpa')
    read_arpa(lm_path, lower_lm_path)
    mod_path = os.path.join(temp_dir, lang+'.mod')
    junk_path = os.path.join(temp_dir, lang+'.junk')
    symbols_path = os.path.join(temp_dir, lang+'.symbols')
    lower_symbols_path = os.path.join(temp_dir, lang+'lower.symbols')
    lower_mod_path = os.path.join(temp_dir, lang+'lower.mod')

    subprocess.call(['ngramread', '--ARPA', '--OOV_symbol=<UNK>', lm_path, mod_path])

    subprocess.call(['ngraminfo',  mod_path])

    print("LOWER INFO")

    subprocess.call(['ngramread', '--ARPA', '--OOV_symbol=<unk>', lower_lm_path, lower_mod_path])

    subprocess.call(['ngraminfo',  lower_mod_path])
    #subprocess.call(['ngramread', '--ARPA', '--OOV_symbol=<unk>', lower_lm_path, mod_path])
    eeror
    far_path = os.path.join(temp_dir, lang+'.far')
    lower_far_path = os.path.join(temp_dir, lang+'lower.far')
    lower_cnts_path = os.path.join(temp_dir, lang+'lower.cnts')
    string_path = os.path.join(temp_dir, lang+'.txt')
    lower_string_path = os.path.join(temp_dir, lang+'lower.txt')
    subprocess.call(['ngramread', '--ARPA', '--OOV_symbol=<UNK>', lm_path, mod_path])
    max_sents = 100000
    print('read arpa')
    string_count = 0
    while string_count < max_sents:
        subprocess.call(['ngramrandgen', '--remove_epsilon', f'--max_sents={max_sents}', '--max_length=30', f'--seed={seed}', mod_path, far_path])
        print('generated random far')
        if string_count == 0:
            mode = 'w'
        else:
            mode = 'a'
        with open(string_path, mode, encoding='utf8') as f:
            subprocess.call(['farprintstrings', '--print_weight', far_path], stdout=f)
        with open(string_path, 'r', encoding='utf8') as in_f, open(lower_string_path, 'w', encoding='utf8') as out_f:
            for line in in_f:
                string_count += 1
        print('created strings')
    err
    subprocess.call(['ngramperplexity', '--OOV_symbol=<UNK>', mod_path, far_path])
    with open(string_path, 'r', encoding='utf8') as in_f, open(lower_string_path, 'w', encoding='utf8') as out_f:
        for line in in_f:
            out_f.write(line.lower())
    print('created lower strings')
    oov_word = '<unk>'
    subprocess.call(
        ["ngramsymbols", f'--OOV_symbol={oov_word}', lower_string_path, lower_symbols_path]
    )
    print('generated symbols')
    method = "kneser_ney"
    order = 3
    subprocess.call(['farcompilestrings',
                "--fst_type=compact",
                f'--unknown_symbol={oov_word}',
                f"--symbols={lower_symbols_path}",
                "--keep_symbols",
                     string_path, lower_far_path])
    print('compiled far')

    subprocess.call(["ngramcount", f"--order={order}", lower_far_path, lower_cnts_path])
    print('counted ngrams')
    subprocess.call(["ngrammake", f"--method={method}", lower_cnts_path, lower_mod_path])
    print('counted made lower mod')
    subprocess.call(['ngramperplexity', f'--OOV_symbol={oov_word}', lower_mod_path, lower_far_path])

    error