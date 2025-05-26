import os.path
import re

from montreal_forced_aligner.command_line.mfa import mfa_cli
from montreal_forced_aligner.config import TEMPORARY_DIRECTORY

dictionary_dir = r'D:/Data/speech/dictionaries/wikipron/cleaned'
output_dir = r'D:/Data/speech/dictionaries/wikipron/g2p_models'
to_g2p_dir = r'D:/Data/speech/dictionaries/wikipron/missing'
temp_dir = TEMPORARY_DIRECTORY
os.makedirs(output_dir, exist_ok=True)


lang_codes = ['czech', 'russian',
              'french', 'german',
              'portuguese_brazil', 'portuguese_portugal',
              'spanish_spain', 'spanish_latin_america',
              'swedish',
              'thai',
              'turkish',
              'english_us', 'english_us_arpa', 'english_uk', 'english_nigeria',
              'korean_jamo', 'korean',
              'hausa', 'swahili',
              'vietnamese_hanoi', 'vietnamese_hue', 'vietnamese_ho_chi_minh_city',
              'ukrainian', 'polish', 'croatian', 'bulgarian',
              'japanese',
              'japanese_katakana',
                #'mandarin_china', 'mandarin_erhua', 'mandarin_taiwan'
              'tamil',
              'hindi',
              'urdu',
'serbo-croatian_croatian', 'serbo-croatian_serbian',
              ]

lang_codes = [
#'czech',
'serbo-croatian_croatian', 'serbo-croatian_serbian',
              #'spanish_spain', 'spanish_latin_america',
              #'hindi',
    #'urdu',
    #'russian',
              #'vietnamese_hanoi', 'vietnamese_hue', 'vietnamese_ho_chi_minh_city',
              ]

dialect_to_lang = {
    'serbo-croatian_croatian': 'serbo-croatian',
    'serbo-croatian_serbian': 'serbo-croatian',
    'spanish_spain': 'spanish',
    'spanish_latin_america': 'spanish',
}

def get_error_rates(lang):
    train_temp_dir = os.path.join(temp_dir, f'{lang}_mfa')
    log_file = os.path.join(train_temp_dir, f'{lang}_mfa.log')
    print("Parsing:", log_file)
    if not os.path.exists(log_file):
        return 1, 1
    wer_pattern = re.compile(r'WER:\s+([\d.]+)$')
    ler_pattern = re.compile(r'LER:\s+([\d.]+)$')
    wer, ler = None, None
    with open(log_file, 'r', encoding='utf8') as f:
        for line in f:
            m = wer_pattern.search(line)
            if m:
                wer = m.group(0)
            m = ler_pattern.search(line)
            if m:
                ler = m.group(0)
    print(f"{lang}: {wer}% WER, {ler}% LER")
    return wer, ler


def get_oovs(lang):

    oov_dir = fr"C:\Users\micha\Documents\Dev\mfa-models\scripts\corpus_prep\temp\{dialect_to_lang.get(lang, lang)}"

    oov_paths = [os.path.join(oov_dir, rf"oovs_found_{lang}_mfa.txt"),]
    wordform_path = rf"C:\Users\micha\Documents\Dev\corpus-creation-scripts\ipa_dictionary\rich_lexicons\{dialect_to_lang.get(lang, lang)}_forms.txt"
    suffixes_path = rf"C:\Users\micha\Documents\Dev\corpus-creation-scripts\ipa_dictionary\rich_lexicons\{dialect_to_lang.get(lang, lang)}_suffixes.txt"
    suffix_set = set()
    if os.path.exists(suffixes_path):
        with open(suffixes_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip().replace('-', '')
                suffix_set.add(line)
    prefixes_path = rf"C:\Users\micha\Documents\Dev\corpus-creation-scripts\ipa_dictionary\rich_lexicons\{dialect_to_lang.get(lang, lang)}_prefixes.txt"
    prefix_set = set()
    if os.path.exists(prefixes_path):
        with open(prefixes_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip().replace('-', '')
                prefix_set.add(line)
    print(prefix_set)
    oovs = set()
    wordforms = set()
    with open(wordform_path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if line.istitle():
                line = line.lower()
            if line.count('(') > 1:
                continue
            if '(' in line:
                stem, suffixes = line.replace(')', '').split('(')
                suffixes = suffixes.split('/')
                if stem:
                    wordforms.add(stem)
                    wordforms.update([stem+x for x in suffixes if x not in {'?'}])
                else:
                    wordforms.add(suffixes[0])
            else:
                wordforms.add(line)
                if lang == 'czech':
                    for x in prefix_set:
                        if line.startswith(x):
                            continue
                        wordforms.add(x + line)
    for oov_path in oov_paths:
        with open(oov_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                oovs.add(line)
                if lang.startswith('spanish'):
                    if any(x in line for x in ['á','é','í','ú','ó', 'ñ']):
                        wordforms.add(line)
                    if any(line.endswith(x) for x in ['mente', 'ador', 'idad', 'iento', 'arme', 'iales', 'inante', 'rones']):
                        wordforms.add(line)
                    if any(line.endswith(x) for x in ['ronme', 'ronle', 'ronles', ]):
                        wordforms.add(line)
                elif lang == 'czech' and False:
                    if any(x in line for x in ['ý','ě','ř','š','ť', 'ů', 'ď', 'č', 'á', 'ž', 'é', 'ň', 'ú', 'í']):
                        wordforms.add(line)
                    if any(line.endswith(x) for x in [
                            'vou', 'kou', 'val','ych', 'vám', 'hlo','chom','jeme','jte','ismu', 'ímu','ů','ími', 'ány','ám','át','eno','že','ých','ej','pěji',
                        'ána', 'eji', 'uj', 'u', 'hl',
                            'uje', 'ije', 'ího', 'ého', 'nost', 'nosti', 'ují', 'desát', 'vat', 'ý', 'ím', 'í', 'ým', 'icky', 'ity', 'em', 'ili', 'ii', 'ace', 'á', 'ě', 'ích', 'ž', 'š'
                    ]):
                        wordforms.add(line)
                    if any(line.endswith(x) for x in suffix_set):
                        wordforms.add(line)
                #if any(line.replace(x, y) in wordforms for x,y in [('e', 'é'),('o', 'ó'),('a', 'á'),('i', 'í'),('u', 'ú')]):
                #    wordforms.add(line)
                #if any(x in line for x in 'aieuoy') and any(x in line for x in ['ž','š','č','ř','ň', 'ť', 'ď']):
                #    wordforms.add(line)
    print(len(oovs), len(wordforms))
    return oovs.intersection(wordforms)


def save_oovs(oovs, oov_path):
    with open(oov_path, 'w', encoding='utf8') as f:
        for w in sorted(oovs):
            f.write(f"{w}\n")


if __name__ == '__main__':

    for lang in lang_codes:
        print(lang)
        if lang.endswith('arpa'):
            dictionary_path = os.path.join(dictionary_dir, lang + '.dict')
            model_path = os.path.join(output_dir, lang + '.zip')
        else:
            dictionary_path = os.path.join(dictionary_dir, lang + '_mfa.dict')
            model_path = os.path.join(output_dir, lang + '_mfa.zip')
        print(model_path)
        if not os.path.exists(model_path):
            if not os.path.exists(dictionary_path):
                continue

            command = ['train_g2p',
                       dictionary_path,
                       model_path,
                       '--clean',
                       '-j', '10',
                       '--use_mp',
                       '--evaluate',
                       '--num_pronunciations', '2',
                       '--phonetisaurus',
                       ]
            print(command)
            mfa_cli(command, standalone_mode=False)

            get_error_rates(lang)

        oovs = get_oovs(lang)
        print(len(oovs))
        to_g2p_path = os.path.join(to_g2p_dir, f"{lang}.txt")
        if oovs:
            save_oovs(oovs, to_g2p_path)
        else:
            continue
        g2pped_path = os.path.join(to_g2p_dir, f"{lang}_mfa.dict")
        command = ['g2p',
                   to_g2p_path,
                   model_path,
                   g2pped_path,
                   '--clean',
                   '-j', '10',
                   '--use_mp',
                   '--num_pronunciations', '1',
                   '--strict_graphemes',
                   ]
        print(command)
        mfa_cli(command, standalone_mode=False)