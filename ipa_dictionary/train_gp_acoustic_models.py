import os.path
import re
import subprocess

#from montreal_forced_aligner.command_line.train_acoustic_model import run_train_acoustic_model

root_corpus_dir = '/media/share/corpora/GP_for_MFA/{}/files'
root_dictionary = '/data/mmcauliffe/GP_for_MFA/{}_speaker_dictionaries.yaml'
model_directory = '/data/mmcauliffe/mfa_output/models'
config_template = '/data/mmcauliffe/GP_for_MFA/{}.yaml'

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

temp_dir = r'/data/mmcauliffe/mfa_temp/'

class DefaultArgs:
    def __init__(self, corpus_directory, dictionary_path, temporary_directory, output_model_path, output_textgrid_directory):
        self.corpus_directory = corpus_directory
        self.dictionary_path = dictionary_path
        self.output_model_path = output_model_path
        self.output_paths = [output_textgrid_directory]
        self.temporary_directory = temporary_directory
        self.config_path = None
        self.num_jobs = 24
        self.speaker_characters = 5
        self.use_mp = True
        self.debug = False
        self.clean = True
        self.verbose = True
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

for lang in lang_codes:
    print(lang)
    model_path = os.path.join(model_directory, f'{full_names[lang].lower()}_ipa.zip')
    if os.path.exists(model_path):
        continue
    command = ['mfa', 'train', root_corpus_dir.format(lang), root_dictionary.format(full_names[lang]),
                     model_path, '-t', os.path.join(temp_dir, lang), '-j', '24', '-s', '5', '--phone_set', 'IPA']
    config_path = config_template.format(lang)
    if os.path.exists(config_path):
        command += ['--config_path', config_path]
    #args = DefaultArgs(root_corpus_dir.format(lang),
    #                   root_dictionary.format(full_names[lang]), os.path.join(temp_dir, lang), model_path, tg_path)
    subprocess.check_call(command)
    #run_train_acoustic_model(args)