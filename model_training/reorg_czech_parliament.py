import collections
import os
import re
corpus_root = r"D:\Data\speech\czech_corpora\snemovna"


if False:
    for partition in ['train', 'test']:
        asr_data = os.path.join(corpus_root, "ASR_DATA", partition)
        for session in os.listdir(asr_data):
            output_dir = os.path.join(corpus_root, session)
            os.makedirs(output_dir, exist_ok=True)
            session_dir = os.path.join(asr_data, session)
            for file in os.listdir(session_dir):
                if not file.endswith('.wav'):
                    continue
                wav_path = os.path.join(session_dir, file)
                trn_path =wav_path +'.trn'
                lab_path = os.path.join(output_dir, file.replace('.wav', '.lab'))
                os.rename(wav_path, os.path.join(output_dir, file))
                os.rename(trn_path, lab_path)

for session in os.listdir(corpus_root):
    session_dir = os.path.join(corpus_root, session)
    if not os.path.isdir(session_dir):
        continue
    for file in os.listdir(session_dir):
        new_file_name = file.replace('.wav-', '-').replace('.lab-', '-')
        os.rename(os.path.join(session_dir, file), os.path.join(session_dir, new_file_name))