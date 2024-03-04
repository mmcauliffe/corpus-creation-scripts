import os.path
import re
import subprocess

#from montreal_forced_aligner.command_line.train_acoustic_model import run_train_acoustic_model


root_dir = '/data/mmcauliffe/transcription_benchmarking'
mfa10_dir = '/data/mmcauliffe/mfa_output/1.0_archived'
mfa20_archive_dir = '/data/mmcauliffe/mfa_output/2.0_archived'
mfa20_current_dir = '/data/mmcauliffe/mfa_output/models'
mfa205_dir = '/data/mmcauliffe/mfa_output/2.0.5_models'

root_corpus_dir = '/media/share/corpora/GP_for_MFA/{}/files'
dictionary_template = '/data/mmcauliffe/mfa_output/models/{}_speaker_dictionaries.yaml'
language_model_template = '/data/mmcauliffe/mfa_output/language_models/{}_lm.zip'
model_directory = '/data/mmcauliffe/mfa_output/models'
out_directory = '/data/mmcauliffe/mfa_output/transcriptions'
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

temp_dir = r'/data/mmcauliffe/mfa_temp/transcription'

class DefaultArgs:
    def __init__(self, corpus_directory, dictionary_path, temporary_directory, output_model_path, output_textgrid_directory):
        self.corpus_directory = corpus_directory
        self.dictionary_path = dictionary_path
        self.output_model_path = output_model_path
        self.output_paths = [output_textgrid_directory]
        self.temporary_directory = temporary_directory
        self.config_path = None
        self.num_jobs = 5
        self.speaker_characters = 5
        self.use_mp = True
        self.debug = False
        self.clean = False
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
    conditions = {
        #'gp_1.0': (os.path.join(mfa10_dir, f'{lang}_dictionary.txt'), os.path.join(mfa10_dir, f'{full_names[lang].lower()}.zip')),
        #'mfa_2.0': (os.path.join(mfa20_archive_dir, f'{full_names[lang]}_speaker_dictionaries.yaml'), os.path.join(mfa20_archive_dir, f'{full_names[lang].lower()}_mfa.zip')),
        'mfa_2.0.5': (os.path.join(mfa205_dir, f'{full_names[lang]}_speaker_dictionaries.yaml'),
                      os.path.join(mfa205_dir, f'{full_names[lang].lower()}_mfa.zip')),
        #'mfa_2.0a': (os.path.join(mfa20_current_dir, f'{full_names[lang]}_speaker_dictionaries.yaml'), os.path.join(mfa20_current_dir, f'{full_names[lang].lower()}_mfa.zip')),
    }
    for c, (dictionary_path, model_path) in conditions.items():
        print(lang, c)
        #if lang == 'TH':
        #    continue
        language_model_path = language_model_template.format(full_names[lang].lower())
        out_path = os.path.join(out_directory, c, f'{full_names[lang].lower()}')
        if not os.path.exists(model_path):
            continue
        if os.path.exists(out_path):
            continue
        corpus_path = root_corpus_dir.format(lang)
        if c == 'gp_1.0' and lang == 'CH':
            corpus_path = '/media/share/corpora/GP_for_MFA/CH/files_rmn'
            language_model_path = '/data/mmcauliffe/mfa_output/language_models/mandarin_gp_lm.zip'
        command = ['mfa', 'transcribe', corpus_path, dictionary_path,
                         model_path, language_model_path, out_path, '-t', os.path.join(temp_dir, c, lang),
                   '-j', '20', '-s', '5', '--evaluate', '--language_model_weight', '16', '--word_insertion_penalty', '1.0']
        config_path = config_template.format(lang)
        if os.path.exists(config_path):
            command += ['--config_path', config_path]
        #args = DefaultArgs(root_corpus_dir.format(lang),
        #                   root_dictionary.format(full_names[lang]), os.path.join(temp_dir, lang), model_path, tg_path)
        subprocess.call(command)
        #run_train_acoustic_model(args)