import os
import shutil

import tqdm

root_dir = r"D:\Data\speech\japanese_corpora\LaboroTVSpeech"

bad_file_path = r"D:\Data\speech\japanese_corpora\bad_files.txt"

bad_files = set()
with open(bad_file_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        bad_files.add(line)

for speaker in tqdm.tqdm(os.listdir(root_dir)):
    if speaker.startswith('.'):
        continue
    speaker_dir = os.path.join(root_dir, speaker)
    if len(os.listdir(speaker_dir)) == 0:
        os.removedirs(speaker_dir)
        continue
    for f in os.listdir(speaker_dir):
        if f.split('.')[0] in bad_files:
            os.remove(os.path.join(speaker_dir, f))