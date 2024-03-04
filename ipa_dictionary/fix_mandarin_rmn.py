# coding=utf8
import os
import re
import itertools
from collections import Counter

working_dir = r'/mnt/d/Data/speech/GlobalPhone/mandarin/rmn'
output_dir = r'/mnt/d/Data/speech/GlobalPhone/mandarin/files_rmn'

if __name__ == '__main__':
    bracket_pattern = re.compile(r'[<(（].*?[）)>]')
    for file in os.listdir(working_dir):
        speaker_id = os.path.splitext(file)[0]
        path = os.path.join(working_dir, file)
        texts = {}
        current_utterance = 0
        with open(path, 'r', encoding='utf8') as f:
            for line in f:
                if 'SprecherID' in line:
                    continue
                if line.startswith(';'):
                    current_utterance += 1
                    continue
                else:
                    line = line.strip()
                    if not line:
                        continue

                    if current_utterance not in texts:
                        texts[current_utterance] = line
                    else:
                        texts[current_utterance] += line
        speaker_output_dir = os.path.join(output_dir,speaker_id)
        os.makedirs(speaker_output_dir, exist_ok=True)
        for utt, text in texts.items():
            lab_path = os.path.join(speaker_output_dir,  f"{speaker_id}_{utt}.lab")
            with open(lab_path, 'w', encoding='utf8') as f:
                f.write(text)