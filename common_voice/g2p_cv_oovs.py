import collections
import os.path
import re

import hanziconv
import hangul_jamo
import itertools
from montreal_forced_aligner.command_line.g2p import run_g2p

root_dir = r'/mnt/d/Data/speech/CommonVoice'
validation_temp_dir = os.path.join(root_dir, 'validation_temp')
g2p_model_dir = r'/mnt/c/Users/michael/Documents/Dev/mfa-models/g2p/staging'
temp_dir = r'/mnt/d/Data/speech/CommonVoice/g2p_temp'


languages = ['bulgarian', 'czech', 'french', 'german',
             'japanese',
             'english',
             #'mandarin_china', 'mandarin_taiwan',
             'polish',
             'portuguese', 'serbian', 'swedish',
             #'tamil',
             'thai', 'turkish'
]

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

for lang in languages:

    output_mapping = {}
    print(lang)
    to_g2p_file = os.path.join(validation_temp_dir, lang, f'common_voice_{lang}_validate_training', 'oovs_found.txt')
    print(to_g2p_file, os.path.exists(to_g2p_file))
    if not os.path.exists(to_g2p_file):
        continue
    g2pped_file = os.path.join(root_dir, lang+'.g2pped')
    model_path = os.path.join(g2p_model_dir, lang+'_ipa.zip')
    if lang == 'serbian':
        model_path = os.path.join(g2p_model_dir, f'croatian_ipa.zip')
    elif lang == 'portuguese':
        model_path = os.path.join(g2p_model_dir, f'{lang}_brazil_ipa.zip')
    elif lang == 'english':
        model_path = os.path.join(g2p_model_dir, f'{lang}_us_ipa.zip')
    if not os.path.exists(model_path):
        continue
    args = DefaultArgs(to_g2p_file, model_path, g2pped_file, os.path.join(temp_dir,lang + '_g2p'))
    if os.path.exists(args.output_path):
        continue
    run_g2p(args)


