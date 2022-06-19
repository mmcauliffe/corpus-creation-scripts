import os.path
import re
import sys
import subprocess

from montreal_forced_aligner.command_line.train_lm import run_train_lm

if sys.platform == 'win32':
    training_root = 'D:/Data/speech/model_training_corpora'
    dictionary_dir = 'C:/Users/michael/Documents/Dev/mfa-models/dictionary/training'
    model_output_directory = 'D:/Data/models/language_models'
    temp_dir = r'D:/temp/lm_training_temp/'
else:
    training_root = '/mnt/d/Data/speech/model_training_corpora'
    dictionary_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/dictionary/training'
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

class DefaultArgs:
    def __init__(self, corpus_directory, dictionary_path, temporary_directory, output_model_path):
        self.source_path = corpus_directory
        self.dictionary_path = dictionary_path
        self.output_model_path = output_model_path
        self.temporary_directory = temporary_directory
        self.config_path = None
        self.model_path = None
        self.num_jobs = 15
        self.output_paths = []
        self.speaker_characters = 0
        self.use_mp = True
        self.debug = False
        self.clean = False
        self.verbose = False
        self.audio_directory = None
        self.phone_set_type = 'IPA'

if __name__ == '__main__':
    for lang in languages:
        print(lang)
        model_path = os.path.join(model_output_directory, f'{lang}_mfa_lm.zip')
        if os.path.exists(model_path):
            continue
        lang_corpus_dir = os.path.join(training_root, lang)
        dictionary_path = os.path.join(lang_corpus_dir, lang+'_speaker_dictionaries.yaml')
        config_path = os.path.join(lang_corpus_dir, lang +".yaml")
        command = ['mfa', 'train_lm', lang_corpus_dir.format(lang), dictionary_path,
                         model_path, '-t', os.path.join(temp_dir, lang), '-j',
                   '20']
        args = DefaultArgs(lang_corpus_dir.format(lang),
                           dictionary_path, os.path.join(temp_dir, lang), model_path)
        if os.path.exists(config_path):
            command += ['--config_path', config_path]
            args.config_path = config_path
        #subprocess.check_call(command, env=os.environ)
        run_train_lm(args)