import os
import csv

root_dir = r"D:\Data\speech\voxpopuli\transcribed_data\pl"

transcripts = {}
utt2spk = {}

speaker_info = {}

for s in ['dev', 'train', 'test']:
    path = os.path.join(root_dir, f'asr_{s}.tsv')
    with open(path, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for line in reader:
            speaker = 'vp_pl_' + line['speaker_id']
            utt = line['id'].replace(':', '_')

            if speaker not in speaker_info:
                speaker_info[speaker] = {'Speaker': speaker, 'Gender': line['gender'], 'Accent': line['accent']}
            transcripts[utt] = line['normalized_text']
            utt2spk[utt] = speaker

for year in os.listdir(root_dir):
    year_dir = os.path.join(root_dir, year)
    if not os.path.isdir(year_dir):
        continue
    for file in os.listdir(year_dir):
        new_name = file.replace('', '_')
        print(new_name)
        utterance = new_name.split('.')[0]
        print(transcripts[utterance])
        speaker = utt2spk[utterance]
        speaker_dir = os.path.join(root_dir, speaker)
        os.makedirs(speaker_dir, exist_ok=True)
        with open(os.path.join(speaker_dir, f'{utterance}.lab'), 'w', encoding='utf8') as f:
            f.write(transcripts[utterance])
        os.rename(os.path.join(year_dir, file), os.path.join(speaker_dir, new_name))

with open(os.path.join(root_dir, 'speaker_info.tsv'), 'w', encoding='utf8') as f:
    writer = csv.DictWriter(f,fieldnames=['Speaker', 'Gender', 'Accent'])
    writer.writeheader()
    for speaker, info in speaker_info.items():
        writer.writerow(info)