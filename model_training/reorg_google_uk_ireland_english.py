import os

corpus_root = r'D:\Data\speech\english_corpora\google_uk_ireland'

speaker_data = {

}

dialects = ['irish', 'midlands', 'northern', 'scottish', 'southern', 'welsh']

for d in dialects:
    for g in ['male', 'female']:
        gender_dir = os.path.join(corpus_root, f'{d}_english_{g}')
        if not os.path.exists(gender_dir):
            continue
        transcription_file = os.path.join(gender_dir, 'line_index.csv')
        with open(transcription_file, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()

                _, utt, text = line.split(', ')
                speaker = '_'.join(utt.split("_")[:2])
                speaker_dir = os.path.join(corpus_root, d, speaker)
                os.makedirs(speaker_dir, exist_ok=True)
                speaker_data[speaker] = {'gender':g, 'dialect': d}
                with open(os.path.join(speaker_dir, utt +'.lab'), 'w', encoding='utf8') as f:
                    f.write(text.strip())
                if os.path.exists(os.path.join(gender_dir, utt +'.wav')):
                    os.rename(os.path.join(gender_dir, utt +'.wav'), os.path.join(speaker_dir, utt+'.wav'))

with open(os.path.join(corpus_root, 'speaker_info.tsv'), 'w', encoding='utf8') as f:
    for k, v in speaker_data.items():
        f.write(f"{k}\t\t{v['gender']}\t{v['dialect']}\n")