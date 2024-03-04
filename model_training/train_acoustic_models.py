import os.path
import re
import sys
from montreal_forced_aligner.command_line.mfa import mfa_cli

if sys.platform == 'win32':
    training_root = 'D:/Data/speech/model_training_corpora'
    dictionary_dir = 'C:/Users/michael/Documents/Dev/mfa-models/dictionary/training'
    groups_dir = 'C:/Users/michael/Documents/Dev/mfa-models/config/acoustic/phone_groups'
    rules_dir = 'C:/Users/michael/Documents/Dev/mfa-models/config/acoustic/rules'
    config_dir = 'C:/Users/michael/Documents/Dev/mfa-models/config/acoustic'
    model_output_directory = 'D:/Data/models/final_training'
    temp_dir = r'D:/temp/model_training_temp2/'
else:
    training_root = '/mnt/d/Data/speech/model_training_corpora'
    dictionary_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/dictionary/training'
    groups_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/config/acoustic/phone_groups'
    rules_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/config/acoustic/rules'
    config_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/config/acoustic'
    model_output_directory = '/mnt/d/Data/models/final_training'
    temp_dir = r'/mnt/d/temp/model_training_temp2/'

languages = [

    'english',
    'korean',
    'bulgarian',
    'vietnamese',
             'croatian',
    'hausa',
    'ukrainian',
'thai',
'swahili',
     'turkish',
    'spanish',
             'swedish',
             'portuguese', 'polish',
             'french',
             'czech', #'japanese',
             'russian',
    'german',
     'mandarin', #'tamil',
             ]
languages = [
    'english'
#'japanese', #'hausa', 'bulgarian'
             ]


if __name__ == '__main__':
    for lang in languages:
        print(lang)
        model_path = os.path.join(model_output_directory, f'{lang}_mfa.zip')
        if os.path.exists(model_path):
            continue
        lang_corpus_dir = os.path.join(training_root, lang)
        dictionary_path = os.path.join(lang_corpus_dir, lang+'_speaker_dictionaries.yaml')
        command = ['train', lang_corpus_dir.format(lang), dictionary_path,
                         model_path, '-t', os.path.join(temp_dir, lang), '-j',
                   '10', '--phone_set', 'IPA', '--oov_count_threshold', "1",
                   '--use_cutoff_model', '--no_clean', '--no_debug']
        groups_path = os.path.join(groups_dir, f'{lang}_mfa.yaml')
        if os.path.exists(groups_path):
            command += ['--groups_path', groups_path]

        rules_path = os.path.join(rules_dir, f'{lang}_mfa.yaml')
        if os.path.exists(rules_path):
            command += ['--rules_path', rules_path]
        config_path = os.path.join(config_dir, lang +".yaml")
        if os.path.exists(config_path):
            command += ['--config_path', config_path]
        print(command)
        mfa_cli(command, standalone_mode=False)
        #subprocess.check_call(command, env=os.environ)
        #train_acoustic_model(args)