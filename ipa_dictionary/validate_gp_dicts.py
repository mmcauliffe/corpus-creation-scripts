import os.path
import re

from montreal_forced_aligner.command_line.validate import run_validate_corpus

root_corpus_dir = '/media/share/corpora/GP_for_MFA/{}/files'
root_dictionary = '/data/mmcauliffe/GP_for_MFA/{}_speaker_dictionaries.yaml'
config_template = '/data/mmcauliffe/GP_for_MFA/{}.yaml'

temp_dir = r'/data/mmcauliffe/mfa_temp/validation'

lang_codes = {
                #'AR': 'iso-8859-1',
                'BG': 'utf8',
                'CH': 'gb2312',
                #'WU': 'gb2312',
                'CR': 'iso-8859-2',
                'CZ': 'iso-8859-2',
                'FR': 'iso-8859-1',
                'GE': 'iso-8859-1',
                'HA': 'utf8',
                'JA': 'eucjp',
                'KO': 'korean',
                'RU': 'koi8-r',
                'PO': 'iso-8859-1',
                'PL': 'utf8',
                'SP': 'iso-8859-1',
                'SW': 'iso-8859-1',
                'SA': 'utf8',
                #'TA': '',
                'TH': 'utf8',
                'TU': 'iso-8859-9',
                'VN': 'utf8',
                'UA': 'utf8',
                }

class DefaultArgs:
    def __init__(self, corpus_directory, dictionary_path, temporary_directory, config_path):
        self.corpus_directory = corpus_directory
        self.dictionary_path = dictionary_path
        self.temporary_directory = temporary_directory
        self.config_path = config_path
        self.num_jobs = 10
        self.speaker_characters = 5
        self.debug = True
        self.clean = True
        self.verbose = True
        self.ignore_acoustics = True
        self.position_dependent_phones = False
        self.test_transcriptions = False
        self.acoustic_model_path = None
        self.audio_directory = None
        self.phone_set_type = 'IPA'


full_names = {
                'AR': 'Arabic',
                'BG': 'Bulgarian',
                'CH': 'Mandarin',
                'WU': 'Cantonese',
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
                'TA': 'Tamil',
                'TH': 'Thai',
                'TU': 'Turkish',
                'VN': 'Vietnamese',
                'UA': 'Ukrainian'
                }

if __name__ == '__main__':
    for lang in lang_codes:
        if lang not in ['JA']:
            continue
        print(lang)
        out_dir = os.path.join(temp_dir, lang)
        if os.path.exists(out_dir):
            continue
        config_path = config_template.format(lang)
        if not os.path.exists(config_path):
            config_path = None
        print(config_path)
        args = DefaultArgs(root_corpus_dir.format(lang),
                           root_dictionary.format(full_names[lang]), out_dir, config_path)
        run_validate_corpus(args)