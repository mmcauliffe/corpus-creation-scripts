import collections
import os.path
import re
import itertools
from montreal_forced_aligner.command_line.mfa import mfa_cli

training_root = 'D:/Data/speech/model_training_corpora'
temp_root = 'D:/temp/validation'
g2p_model_dir = r'C:/Users/michael/Documents/Dev/mfa-models/g2p/staging'

languages = [
    'japanese', 'bulgarian', 'french', 'german', 'portuguese',
             'croatian', 'swedish', 'korean', 'thai',
             'mandarin',
             'hausa', 'russian', 'spanish', 'english', 'vietnamese',
             'turkish', 'swahili', 'polish','czech','ukrainian'
             ]
languages = ['hindi-urdu', 'tamil']


models = {
    'spanish': ['spanish_spain_mfa.zip','spanish_latin_america_mfa.zip',],
    'portuguese': ['portuguese_brazil_mfa.zip','portuguese_portugal_mfa.zip',],
    'english': ['english_us_mfa.zip','english_uk_mfa.zip',],
    'hindi-urdu': ['hindi_mfa.zip', 'urdu_mfa.zip',],
    'serbian': ['croatian_mfa.zip',],
    'mandarin': ['mandarin_china_mfa.zip','mandarin_erhua_mfa.zip','mandarin_taiwan_mfa.zip',],
    'vietnamese': ['vietnamese_ho_chi_minh_city_mfa.zip','vietnamese_hanoi_mfa.zip',
                   'vietnamese_hue_mfa.zip'],
}

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
        for word, count in sorted(counter.items(), key=lambda x: -x[1]):
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
        if lang in models:
            m = [os.path.join(g2p_model_dir,x) for x in models[lang]]
        else:
            m = [os.path.join(g2p_model_dir, lang+'_mfa.zip')]
        for model_path in m:
            print(model_path, os.path.exists(model_path))
            if not os.path.exists(model_path):
                continue
            dictionary_name = os.path.splitext(os.path.basename(model_path))[0]
            validation_temporary_directory = os.path.join(temp_root, f'validation_temp_{lang}')
            print(validation_temporary_directory, os.path.exists(validation_temporary_directory))
            if not os.path.exists(validation_temporary_directory):
                continue
            g2p_temporary_directory = os.path.join(temp_root, 'g2p_temp')
            to_g2p_file = os.path.join(validation_temporary_directory,
                                       f'{dictionary_name}.to_g2p')
            g2pped_file = os.path.join(temp_root, f'{dictionary_name}.g2pped')
            print(g2pped_file, os.path.exists(g2pped_file))
            if os.path.exists(g2pped_file):
                continue
            oov_counter = collections.Counter()
            for corpus in os.listdir(language_root):
                output_mapping = {}
                oov_file = os.path.join(validation_temporary_directory, corpus, corpus, f'oov_counts_{dictionary_name}.txt')
                print(oov_file, os.path.exists(oov_file))
                if not os.path.exists(oov_file):
                    continue
                oov_counter.update(load_oov_counts(oov_file))
            if not oov_counter:
                continue
            save_oov_file(oov_counter, to_g2p_file, 1)
            #process_oov_counts(oov_file, to_g2p_file)
            if not os.path.exists(to_g2p_file):
                continue
            elif lang == 'korean':
                if 'jamo' not in model_path:
                    model_path = model_path.replace('_mfa.zip', '_jamo_mfa.zip')

            command = ['g2p', to_g2p_file, model_path, g2pped_file, '--num_pronunciations', '1',
                       '-t', g2p_temporary_directory, '-j', '2', '--clean']
            print(command)
            mfa_cli(command, standalone_mode=False)
