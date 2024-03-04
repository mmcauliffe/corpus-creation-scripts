
import os
import jsonlines

corpus_root = r"D:\Data\speech\croatian_corpora\ParlaSpeech"

json_path = os.path.join(corpus_root, 'ParlaSpeech-HR.v1.0.jsonl')
flac_directory = os.path.join(corpus_root, 'ParlaSpeech-HR.flac')

speaker_data = {}

for speaker in os.listdir(corpus_root):
    speaker_dir = os.path.join(corpus_root, speaker)
    if not  os.path.isdir(speaker_dir):
        continue
    for file in os.listdir(speaker_dir):
        if not file.endswith('.wav'):
            continue
        os.rename(os.path.join(speaker_dir, file), os.path.join(speaker_dir,file.replace('.wav', '.lab')))

error

with open(json_path, 'r', encoding='utf8') as f:
    reader =jsonlines.Reader(f)
    for line in reader.iter():
        speaker = 'unknown'
        if line['speaker_info'] is not None:
            speaker = line['speaker_info']['Speaker_name']
            if speaker not in speaker_data:
                speaker_data[speaker] = {
                    'gender': line['speaker_info']['Speaker_gender'],
                'birth': line['speaker_info']['Speaker_birth']
                }
        wav_path = os.path.join(corpus_root, line['path'])
        if not os.path.exists(wav_path):
            continue
        text = ' '.join(line['norm_words'])
        speaker_dir = os.path.join(corpus_root, speaker)
        os.makedirs(speaker_dir, exist_ok=True)
        os.rename(wav_path, os.path.join(speaker_dir, line['path']))
        with open(os.path.join(speaker_dir, line['path'].replace('.flac', '.lab')), 'w', encoding='utf8') as outf:
            outf.write(text)

with open(os.path.join(corpus_root, 'speaker_info.tsv'), 'w', encoding='utf8') as f:
    for speaker, info in speaker_data.items():
        f.write(f'{speaker}\t{info["birth"]}\t{info["gender"]}\n')