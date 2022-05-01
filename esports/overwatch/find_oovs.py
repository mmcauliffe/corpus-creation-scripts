import os

from montreal_forced_aligner.command_line import mfa

command = ['validate', '/mnt/d/Data/speech/esports/combined_esports',
           '/mnt/d/Data/speech/esports/esports_dict.txt', '--ignore_acoustics', '-t', '/mnt/d/Data/speech/esports/oov_temp',
           '-j', '13', '--clean']

args, unknown = mfa.parser.parse_known_args(command)

mfa.run_validate_corpus(args, unknown)