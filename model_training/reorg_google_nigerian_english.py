import os

corpus_root = r'D:\Data\speech\english_corpora\google_nigeria'

speaker_data = {

}

for g in ['male', 'female']:
    gender_dir = os.path.join(corpus_root, f'en_ng_{g}')
    if not os.path.exists(gender_dir):
        continue
    transcription_file = os.path.join(gender_dir, 'line_index.tsv')
    with open(transcription_file, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()

            utt, text = line.split(maxsplit=1)
            speaker = utt.rsplit('_', maxsplit=1)[0]
            speaker_dir = os.path.join(corpus_root, speaker)
            os.makedirs(speaker_dir, exist_ok=True)
            speaker_data[speaker] = g
            with open(os.path.join(speaker_dir, utt +'.lab'), 'w', encoding='utf8') as f:
                f.write(text)
            if os.path.exists(os.path.join(gender_dir, utt +'.wav')):
                os.rename(os.path.join(gender_dir, utt +'.wav'), os.path.join(speaker_dir, utt+'.wav'))

with open(os.path.join(corpus_root, 'speaker_info.tsv'), 'w', encoding='utf8') as f:
    for k, v in speaker_data.items():
        f.write(f"{k}\t{v}\n")