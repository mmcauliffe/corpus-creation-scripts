import os
import jsonlines

russian_directory = r'D:\Data\speech\model_training_corpora\russian\russian_librispeech'

for speaker in os.listdir(russian_directory):
    if speaker != '8086':
        continue
    speaker_dir = os.path.join(russian_directory, speaker)
    for filename in os.listdir(speaker_dir):
        new_speaker = '_'.join(filename.split('_')[:2])
        new_speaker_dir = os.path.join(russian_directory, new_speaker)
        os.makedirs(new_speaker_dir, exist_ok=True)
        file_path = os.path.join(speaker_dir, filename)
        new_file_path = os.path.join(new_speaker_dir, filename)
        os.rename(file_path, new_file_path)

if False:
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
