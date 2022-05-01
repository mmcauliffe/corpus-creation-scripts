import dataclasses
import typing
import os
import re
import subprocess
import math

corpus_template = '/media/share/corpora/GP_for_MFA/{}/files'
model_root_dir = '/data/mmcauliffe/mfa_output/language_models'
config_template = '/data/mmcauliffe/GP_for_MFA/{}.yaml'
dictionary_template = '/data/mmcauliffe/GP_for_MFA/{}_speaker_dictionaries.yaml'

temp_dir = r'/data/mmcauliffe/mfa_temp/lm_training'

langs = ['BG', 'CZ', 'FR', 'GE', 'HAU', 'HR', 'JP', 'KO', 'MAN', 'PL', 'PT', 'RU', 'SP', 'SWE', 'TA', 'TH', 'TU', 'VN']

seed = 1917


full_names = {
                #'AR': 'Arabic',
                'BG': 'Bulgarian',
                'CH': 'Mandarin',
                #'WU': 'Cantonese',
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
                #'TA': 'Tamil',
                'TH': 'Thai',
                'TU': 'Turkish',
                'VN': 'Vietnamese',
                'UA': 'Ukrainian'
                }

if __name__ == '__main__':
    for lang, full_name in full_names.items():
        print(lang)
        mfa_lm_path = os.path.join(model_root_dir, f'{full_name.lower()}_lm.zip')
        if os.path.exists(mfa_lm_path):
            continue
        command = ['mfa', 'train_lm', corpus_template.format(lang), mfa_lm_path,
                               '-t', os.path.join(temp_dir, lang)]
        config_path = config_template.format(lang)
        if os.path.exists(config_path):
            command += ['--config_path', config_path]
        dictionary_path = dictionary_template.format(full_name)
        if os.path.exists(dictionary_path):
            command += ['--dictionary_path', dictionary_path]
        print(command)
        subprocess.check_call(command)


