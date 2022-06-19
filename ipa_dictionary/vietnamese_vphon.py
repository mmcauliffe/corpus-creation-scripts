import functools
import subprocess
import os
import re
import multiprocessing as mp
dictionary_dir = r'C:\Users\michael\Documents\Dev\mfa-models\dictionary\training'
vphon_dir = r'C:\Users\michael\Documents\Dev\vPhon'
vphon_script = os.path.join(vphon_dir, 'vPhon.py')
dialects = {
    'ho_chi_minh_city':'s',
    'hue': 'c',
    'hanoi': 'n',
}
vowels = {'a', 'aː', 'e', 'i', 'o', 'u', 'ɔ', 'ə', 'əː', 'ɛ', 'ɨ', 'ʊ', 'ɪ'} |{'a', 'aː', 'e', 'i', 'o', 'u', 'ɔ', 'ə', 'əː', 'ɛ', 'ɨ', 'ʊ', 'ɪ'} |{'a', 'aː', 'e', 'i', 'o', 'u', 'ɔ', 'ə', 'əː', 'ɛ', 'ɨ', 'ʊ', 'ɪ'}

space_regex = re.compile(r'[ .]+')

def run_pron(word, d):
    proc = subprocess.Popen(['python', vphon_script,
                             '-d', d,
                             '-m', '.', '-c'], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            encoding='utf8')
    pron, _ = proc.communicate(word)
    pron = space_regex.sub(' ', pron)
    pron = pron.strip()
    if pron.startswith('['):
        return word, pron
    mapping = {
        '¹': '˩',
        '²': '˨',
        '³': '˨',
        '⁴': '˦',
        '⁵': '˥',
        '͡': '',
        'ʷ': 'w',
        'ʲk': 'c',
        'ʲŋ': 'ɲ',
    }
    for c, i in mapping.items():
        pron = pron.replace(c, i)
    phones = pron.split(' ')
    vowel_pattern = re.compile(rf'^[{"".join(vowels)}]+ː?')
    new_pron = []
    tone_pattern = re.compile(r'^[˩˨˧˦˥ˀ]+$')
    for i, p in enumerate(phones):
        if tone_pattern.match(p):
            for j in range(len(new_pron) - 1, 0, -1):
                if vowel_pattern.match(new_pron[j]):
                    new_pron[j] += p
                    break
        else:
            new_pron.append(p)
    if new_pron[-1] in {'p', 't', 'k'}:
        new_pron[-1] += '̚'
    return word, ' '.join(new_pron)


if __name__ == '__main__':

    word_set = set()
    for dialect in dialects:
        dict_path = os.path.join(dictionary_dir, f'vietnamese_{dialect}_mfa.dict')
        with open(dict_path, 'r', encoding='utf8') as f:
            for line in f:
                word_set.add(line.split('\t')[0])
    print(len(word_set))
    for dialect in dialects:
        print(dialect)
        func = functools.partial(run_pron, d=dialects[dialect])
        new_dict_path = os.path.join(vphon_dir, f'vietnamese_{dialect}_mfa.dict')
        with open(new_dict_path, 'w', encoding='utf8') as f:
            with mp.Pool(5) as pool:
                results = pool.map(func, sorted(word_set))
                for w, p in results:
                    if p.startswith('['):
                        continue
                    f.write(f"{w}\t{p}\n")