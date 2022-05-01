import collections
import os
import re
import shutil

import hangul_jamo


pansori_root = '/mnt/d/Data/speech/korean_corpora/pansori_tedxkr'

for top_folder in os.listdir(pansori_root):
    top_dir = os.path.join(pansori_root, top_folder)
    if not os.path.isdir(top_dir):
        continue
    for sub_folder in os.listdir(top_dir):

        speaker_directory = os.path.join(pansori_root, top_folder, sub_folder)
        transcription_path = os.path.join(speaker_directory, f"{top_folder}-{sub_folder}.trans.txt")
        with open(transcription_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                print(line)
                utterance, transcript = line.split(maxsplit=1)
                with open(os.path.join(speaker_directory, f'{utterance}.lab'), 'w', encoding='utf8') as labf:
                    labf.write(transcript)

