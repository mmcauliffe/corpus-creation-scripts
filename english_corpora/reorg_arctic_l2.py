import os
import shutil
from pathlib import Path
root_dir = Path(r'D:\Data\speech\model_training_corpora\english\l2arctic_release_v5.0')

speakers = []
for speaker_dir in root_dir.iterdir():
    if not speaker_dir.is_dir():
        continue
    if speaker_dir.name == 'suitcase_corpus':
        wav_dir = speaker_dir.joinpath('wav')
        trans_dir = speaker_dir.joinpath('transcript')
        for wf in wav_dir.iterdir():
            actual_speaker_dir = root_dir.joinpath(wf.stem.upper())
            wf.rename(actual_speaker_dir.joinpath(f"{wf.stem.upper()}_suitcase.wav"))
        for tf in trans_dir.iterdir():
            actual_speaker_dir = root_dir.joinpath(tf.stem.upper())
            tf.rename(actual_speaker_dir.joinpath(f"{tf.stem.upper()}_suitcase.lab"))
    else:
        wav_dir = speaker_dir.joinpath('wav')
        trans_dir = speaker_dir.joinpath('transcript')
        for wf in wav_dir.iterdir():
            wf.rename(speaker_dir.joinpath(wf.name))
        for tf in trans_dir.iterdir():
            tf.rename(speaker_dir.joinpath(tf.name).with_suffix('.lab'))