import os
import csv

corpus_root = '/mnt/d/Data/speech/chinese_corpora/aidatatang_200zh/corpus'


for folder in ['test', 'dev', 'train']:
    folder_path = os.path.join(corpus_root, folder)
    if not os.path.exists(folder_path):
        continue
    speaker_info = {}
    for speaker in os.listdir(folder_path):
        speaker_dir = os.path.join(folder_path, speaker)
        out_dir = os.path.join(corpus_root, speaker)
        os.makedirs(out_dir, exist_ok=True)
        for file in os.listdir(speaker_dir):
            if file.endswith('.wav'):
                os.rename(os.path.join(speaker_dir, file), os.path.join(out_dir, file))
            elif file.endswith('.trn'):
                os.rename(os.path.join(speaker_dir, file), os.path.join(out_dir, file.replace('.trn', '.lab')))
            elif file.endswith('.metadata'):
                if speaker not in speaker_info:
                    speaker_info[speaker] = {}
                    with open(os.path.join(speaker_dir, file), 'r', encoding='utf8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                key, value = line.split('\t')
                            except ValueError:
                                continue
                            if key == 'SEX':
                                speaker_info[speaker]['gender'] = value
                            elif key == 'AGE':
                                speaker_info[speaker]['age'] = value
                            elif key == 'BIR':
                                speaker_info[speaker]['birth_place'] = value
                            elif key == 'ACC':
                                speaker_info[speaker]['accent'] = value
    with open(os.path.join(corpus_root, 'speaker_info.tsv'), 'w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['speaker', 'gender', 'age', 'birth_place', 'accent'], delimiter='\t')
        for speaker, info in speaker_info.items():
            info['speaker'] = speaker
            writer.writerow(info)
