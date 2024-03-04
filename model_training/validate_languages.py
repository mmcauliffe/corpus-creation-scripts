import os
from montreal_forced_aligner.command_line.mfa import mfa_cli

training_root = 'D:/Data/speech/model_training_corpora'
temp_root = 'D:/temp/validation'
dictionary_dir = 'C:/Users/michael/Documents/Dev/mfa-models/dictionary/training'

languages = ['english', 'korean', 'bulgarian', 'french', 'german', 'portuguese', 'polish', 'turkish',
             'croatian', 'swedish', 'thai', 'mandarin', 'tamil',
             'czech', 'japanese', 'vietnamese', 'ukrainian', 'swahili', 'spanish',
             'swedish',
             'russian', 'hausa', ]
languages = [
     #'hindi-urdu', 'tamil'
    'english',
]

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

skip_corpora = {'librispeech_english', 'common_voice_english','coraal','google_uk_ireland',
                'google_nigeria','aru_english','nchlt_english'}

skip_languages = {
    #'french', 'german', 'korean', 'english'
}

if __name__ == '__main__':
    for lang in languages:
        #if lang != 'mandarin':
        #    continue
        if lang in skip_languages:
            continue
        language_root = os.path.join(training_root, lang)
        dictionary_path = os.path.join(language_root, f"{lang}_speaker_dictionaries.yaml")

        temporary_directory = os.path.join(temp_root, f'validation_temp_{lang}')
        for corpus in os.listdir(language_root):
            print(corpus)
            if corpus in skip_corpora:
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
            config_path = os.path.join(language_root, lang + '.yaml')
            command = ['validate', corpus_dir, dictionary_path,
                                   '-t', out_dir, '-j', '2', '--clean',
                                   '--ignore_acoustics', '--phone_set_type', 'IPA']
            if os.path.exists(config_path):
                command.extend(['--config_path', config_path])
            print(command)
            mfa_cli(command, standalone_mode=False)
        #break