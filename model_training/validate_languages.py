import os
import subprocess

training_root = '/mnt/d/Data/speech/model_training_corpora'
dictionary_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/dictionary/staging'

languages = ['english', 'korean', 'bulgarian', 'french', 'german', 'portuguese', 'polish', 'turkish',
             'croatian', 'swedish', 'thai', 'mandarin', 'tamil',
             'czech', 'japanese', 'vietnamese', 'ukrainian', 'swahili', 'spanish',
             'swedish',
             'russian', 'hausa', ]


class DefaultArgs:
    def __init__(self, corpus_directory, temp_dir):
        self.corpus_directory = corpus_directory
        self.dictionary_path = dictionary_path
        self.temporary_directory = temp_dir
        self.config_path = None
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

skip_corpora = {'librispeech_en'}

skip_languages = {'french', 'german', 'czech', 'korean', 'english'}

if __name__ == '__main__':
    for lang in languages:
        if lang in skip_languages:
            continue
        language_root = os.path.join(training_root, lang)
        dictionary_path = os.path.join(language_root, f"{lang}_speaker_dictionaries.yaml")

        temporary_directory = os.path.join(language_root, 'validation_temp')
        for corpus in os.listdir(language_root):
            print(corpus)
            if 'common' in corpus:
                continue
            if 'globalphone' in corpus:
                continue
            if corpus.endswith('_temp'):
                continue
            if not os.path.isdir(os.path.join(language_root, corpus)):
                continue
            print(corpus)
            corpus_dir = os.path.join(language_root, corpus)
            out_dir = os.path.join(temporary_directory, corpus)
            if os.path.exists(out_dir):
                continue
            args = DefaultArgs(corpus_dir, out_dir)
            config_path = os.path.join(language_root, lang + '.yaml')
            command = ['mfa', 'validate', corpus_dir, dictionary_path,
                                   '-t', out_dir, '-j', '10', '--clean',
                                   '--ignore_acoustics', '--phone_set_type', 'IPA']
            if os.path.exists(config_path):
                command.extend(['--config_path', config_path])
            print(command)
            subprocess.call(command)
        #break