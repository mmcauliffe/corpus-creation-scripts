import collections
import os
import shutil


root = r'D:\Data\speech\model_training_corpora\korean\archive'

audio_dir = os.path.join(root, 'kss')

utt_file = os.path.join(root, 'transcript.v.1.4.txt')

with open(utt_file, 'r', encoding='utf8') as f:
    for line in f:
        line = line.strip()
        line = line.split('|')
        print(line)
        file = line[0]
        text_file = file.replace('.wav', '.lab')
        transcript = line[2]
        with open(os.path.join(audio_dir, text_file), 'w', encoding='utf8') as outf:
            outf.write(transcript)



