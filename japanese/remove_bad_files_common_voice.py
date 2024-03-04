import os
import shutil

import tqdm

root_dir = r"D:\Data\speech\model_training_corpora\english\common_voice_english"

bad_file_path = r"D:\Data\speech\japanese_corpora\bad_files.txt"

bad_speakers = [
]

bad_files = set()
with open(bad_file_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        bad_files.add(line)

validated_files = set()

#for f in ['dev.tsv', 'train.tsv', 'validated.tsv', 'test.tsv']:

#    with open(os.path.join(root_dir, f), encoding='utf8') as inf:
#        for line in inf:
#            validated_files.add(line.strip().split('\t')[1].replace('.mp3', ''))

for speaker in tqdm.tqdm(os.listdir(root_dir)):
    speaker_dir = os.path.join(root_dir, speaker)
    if speaker in bad_speakers:
        shutil.rmtree(speaker_dir)
        continue
    if not os.path.isdir(speaker_dir):
        continue
    if validated_files:
        for f in os.listdir(speaker_dir):
            if f.split('.')[0] not in validated_files:
                os.remove(os.path.join(speaker_dir, f))
    for f in os.listdir(speaker_dir):
        if f.split('.')[0] in bad_files:
            os.remove(os.path.join(speaker_dir, f))
    if len(os.listdir(speaker_dir)) == 0:
        os.removedirs(speaker_dir)
        continue
