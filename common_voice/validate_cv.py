import os
import re

import os.path
import re

from montreal_forced_aligner.command_line.validate import run_validate_corpus

root_corpus_dir = '/mnt/d/Data/speech/CommonVoice'
dictionary_root_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/dictionary/staging'
config_template = '/data/mmcauliffe/GP_for_MFA/{}.yaml'

temp_dir = r'/mnt/d/Data/speech/CommonVoice/validation_temp'


class DefaultArgs:
    def __init__(self, corpus_directory, dictionary_path, temporary_directory, config_path):
        self.corpus_directory = corpus_directory
        self.dictionary_path = dictionary_path
        self.temporary_directory = temporary_directory
        self.config_path = config_path
        self.num_jobs = 10
        self.speaker_characters = 0
        self.debug = True
        self.clean = True
        self.verbose = False
        self.ignore_acoustics = True
        self.position_dependent_phones = False
        self.test_transcriptions = False
        self.acoustic_model_path = None
        self.audio_directory = None
        self.phone_set_type = 'IPA'


languages = ['bulgarian', 'czech', 'french', 'german',
             #'japanese',
             #'mandarin_china', 'mandarin_taiwan',
             'polish',
             'english',
             'portuguese', 'serbian', 'swedish', 'tamil', 'thai', 'turkish']

if __name__ == '__main__':
    for lang in languages:
        #if lang not in ['SW']:
        #    continue
        print(lang)
        corpus_dir = os.path.join(root_corpus_dir, f'common_voice_{lang}')
        dictionary_path = os.path.join(dictionary_root_dir, f'{lang}_ipa.dict')
        if lang == 'mandarin_china':
            dictionary_path = os.path.join(dictionary_root_dir, f'{lang}_ipa.dict')
        elif lang == 'serbian':
            dictionary_path = os.path.join(dictionary_root_dir, f'croatian_ipa.dict')
        elif lang == 'portuguese':
            dictionary_path = os.path.join(dictionary_root_dir, f'{lang}_brazil_ipa.dict')
        elif lang == 'english':
            dictionary_path = os.path.join(dictionary_root_dir, f'{lang}_us_ipa.dict')
        out_dir = os.path.join(temp_dir, lang)
        if os.path.exists(out_dir):
            continue
        config_path = os.path.join(corpus_dir, lang + '.yaml')
        if not os.path.exists(config_path):
            config_path = None
        print(config_path)
        args = DefaultArgs(corpus_dir,
                           dictionary_path, out_dir, config_path)
        run_validate_corpus(args)