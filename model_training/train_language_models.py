import os.path
import re
import sys
import subprocess

from montreal_forced_aligner.command_line.mfa import mfa_cli

if sys.platform == 'win32':
    training_root = 'D:/Data/speech/model_training_corpora'
    dictionary_dir = 'C:/Users/michael/Documents/Dev/mfa-models/dictionary/staging'
    config_dir = 'C:/Users/michael/Documents/Dev/mfa-models/config/acoustic'
    model_output_directory = 'D:/Data/models/language_models'
    temp_dir = r'D:/temp/lm_training_temp/'
else:
    training_root = '/mnt/d/Data/speech/model_training_corpora'
    dictionary_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/dictionary/staging'
    config_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/config/acoustic'
    model_output_directory = '/mnt/d/Data/models/language_models/final_training'
    temp_dir = r'/mnt/d/temp/lm_training_temp/'

languages = [

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
    'english',
             ]
languages = [
    'japanese',
             ]

if __name__ == '__main__':
    for lang in languages:
        print(lang)
        model_path = os.path.join(model_output_directory, f'{lang}_mfa_lm.zip')
        if os.path.exists(model_path):
            continue
        lang_corpus_dir = os.path.join(training_root, lang)
        dictionary_path = os.path.join(dictionary_dir, lang+'_mfa.dict')
        config_path = os.path.join(config_dir, lang +".yaml")
        command = ['train_lm', lang_corpus_dir.format(lang),
                         model_path, '--dictionary_path', dictionary_path, '-t', os.path.join(temp_dir, lang), '-j',
                   '4', '--clean', '--overwrite', '--oov_count_threshold', '3']
        if os.path.exists(config_path):
            command += ['--config_path', config_path]
        print(command)
        mfa_cli(command, standalone_mode=False)