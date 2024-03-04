import os.path
import re
import sys
from montreal_forced_aligner.command_line.mfa import mfa_cli

if sys.platform == 'win32':
    gp_root = 'D:/Data/speech/GlobalPhone'
    root_output_dir = 'D:/Data/experiments/transcription_benchmarking'
    dictionary_dir = 'C:/Users/michael/Documents/Dev/mfa-models/dictionary/staging'
    model_dir = 'C:/Users/michael/Documents/Dev/mfa-models/acoustic/staging'
    lm_dir = 'C:/Users/michael/Documents/Dev/mfa-models/language_model/staging'
    groups_dir = 'C:/Users/michael/Documents/Dev/mfa-models/config/acoustic/phone_groups'
    rules_dir = 'C:/Users/michael/Documents/Dev/mfa-models/config/acoustic/rules'
    config_dir = 'C:/Users/michael/Documents/Dev/mfa-models/config/acoustic'
    temp_dir = r'D:/temp/model_transcription/'
else:
    gp_root = '/mnt/d/Data/speech/GlobalPhone'
    root_output_dir = '/mnt/d/Data/experiments/transcription_benchmarking'
    dictionary_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/dictionary/staging'
    model_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/acoustic/staging'
    lm_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/language_model/staging'
    groups_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/config/acoustic/phone_groups'
    rules_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/config/acoustic/rules'
    config_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/config/acoustic'
    model_output_directory = '/mnt/d/Data/models/final_training'
    temp_dir = r'/mnt/d/temp/model_transcription/'

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
'japanese', #'hausa', 'bulgarian'
             ]


if __name__ == '__main__':
    for lang in languages:
        print(lang)
        model_path = os.path.join(model_dir, f'{lang}_mfa.zip')
        if not os.path.exists(model_path):
            continue
        language_model_path = os.path.join(lm_dir, f'{lang}_mfa_lm.zip')
        lang_corpus_dir = os.path.join(gp_root, lang, f'gp_{lang}')
        dictionary_path = os.path.join(dictionary_dir, f"{lang}_mfa.dict")
        print(language_model_path, os.path.exists(language_model_path))
        command = ['transcribe', lang_corpus_dir, dictionary_path,
                         model_path, language_model_path, os.path.join(root_output_dir, lang), '-t', os.path.join(temp_dir, lang), '-j',
                   '10',
                   '--no_clean', '--evaluate', '--language_model_weight', '16', '--word_insertion_penalty', '1.0']
        config_path = os.path.join(config_dir, lang +".yaml")
        if os.path.exists(config_path):
            command += ['--config_path', config_path]
        print(command)
        mfa_cli(command, standalone_mode=False)
        #subprocess.check_call(command, env=os.environ)
        #train_acoustic_model(args)