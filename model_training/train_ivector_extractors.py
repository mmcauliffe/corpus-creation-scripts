import os.path
import re
import sys
import subprocess
from montreal_forced_aligner.command_line.mfa import mfa_cli

if sys.platform == 'win32':
    training_root = 'D:/Data/speech/model_training_corpora'
    dictionary_dir = 'C:/Users/michael/Documents/Dev/mfa-models/dictionary/training'
    config_dir = 'C:/Users/michael/Documents/Dev/mfa-models/config'
    model_output_directory = 'D:/Data/models/final_training'
    temp_dir = r'D:/temp/model_training_temp/'
else:
    training_root = '/mnt/d/Data/speech/model_training_corpora'
    dictionary_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/dictionary/training'
    config_dir = '/mnt/c/Users/michael/Documents/Dev/mfa-models/config'
    model_output_directory = '/mnt/d/Data/models/final_training'
    temp_dir = r'/mnt/d/temp/model_training_temp/'

if __name__ == '__main__':
    model_path = os.path.join(model_output_directory, f'ivector_mfa.ivector')
    corpus_dir = os.path.join(training_root, 'ivector_corpora')
    config_path = os.path.join(config_dir, "ivector.yaml")
    command = ['train_ivector', corpus_dir,
                     model_path, '-t', os.path.join(temp_dir, 'ivector'), '-j',
               '10', '--no_clean']

    if os.path.exists(config_path):
        command += ['--config_path', config_path]
    mfa_cli(command, standalone_mode=False)