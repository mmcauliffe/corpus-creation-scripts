import collections
import os
import re
import shutil

import hangul_jamo


zeroth_root = '/mnt/d/Data/speech/korean_corpora/zeroth_korean'

for speaker in os.listdir(zeroth_root):
    speaker_directory = os.path.join(zeroth_root, speaker)
    transcription_path = os.path.join(speaker_directory, f"{speaker}_003.trans.txt")
    with open(transcription_path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            print(line)
            utterance, transcript = line.split(maxsplit=1)
            with open(os.path.join(speaker_directory, f'{utterance}.lab'), 'w', encoding='utf8') as labf:
                labf.write(transcript)

