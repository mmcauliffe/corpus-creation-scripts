import os.path
import sys

from montreal_forced_aligner.command_line.mfa import mfa_cli

if sys.platform == 'win32':
    root_dir = r"D:\Data\speech\model_training_corpora\spanish\mtedx_es"
    output_dir = r"D:\Data\speech\model_training_corpora\spanish\mtedx_es_transcribed"
else:
    root_dir = r"/mnt/d/Data/speech/model_training_corpora/spanish/mtedx_es"
    output_dir = r"/mnt/d/Data/speech/model_training_corpora/spanish/mtedx_es_transcribed"

if __name__ == '__main__':
    command = ["transcribe_whisper",
            root_dir,
            output_dir,
            "--language",
            "spanish",
            "--clean",
            "--use_postgres",
            "-j",
            "20",
            "--architecture",
            "large-v3",
            "--cuda",
            "--incremental",
            "--vad",
            "--no_verbose",
            "--no_debug",
            "--no_overwrite"]
    mfa_cli(command, standalone_mode=False)