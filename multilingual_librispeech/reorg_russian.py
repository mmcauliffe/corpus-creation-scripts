import os
import jsonlines

russian_directory = r'D:\Data\speech\russian_corpora\russian_librispeech'

for folder in ['dev', 'test', 'train']:
    folder_path = os.path.join(russian_directory, folder)
    if not os.path.exists(folder_path):
        continue
    transcripts = {}
    transcript_path = os.path.join(folder_path, 'manifest.json')
    with jsonlines.open(transcript_path, 'r') as f:
        for d in f:
            print(d)
            file_path = d['audio_filepath']
            sp = file_path.split('/')
            speaker = sp[1]
            utterance = f"{speaker}_{os.path.splitext(sp[-1])[0]}"
            out_dir = os.path.join(russian_directory, speaker)
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, utterance +'.lab'), 'w', encoding='utf8') as outf:
                outf.write(d['text'])
            os.rename(os.path.join(folder_path, file_path), os.path.join(out_dir, utterance +'.wav'))
