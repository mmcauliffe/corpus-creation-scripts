import os

corpus_root = r'D:\Data\speech\hindi_corpora\musc2021_hindi'


for split in ['test', 'train']:
    folder_path = os.path.join(corpus_root, split)
    audio_dir = os.path.join(folder_path, 'audio')
    if not os.path.exists(audio_dir):
        continue
    transcription_path = os.path.join(folder_path, 'transcription.txt')
    if os.path.exists(transcription_path):
        with open(transcription_path, encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                utterance_id, text = line.split(maxsplit=1)
                speaker = utterance_id.split('_')[1]
                speaker_dir = os.path.join(corpus_root, split, f'musc21_hindi_{speaker}')
                os.makedirs(speaker_dir, exist_ok=True)
                with open(os.path.join(speaker_dir, f"{utterance_id}.lab"), 'w', encoding='utf8') as lab_f:
                    lab_f.write(text)
    for file_name in os.listdir(audio_dir):
        if not file_name.endswith('.wav'):
            continue
        utterance_id = file_name.split('.')[0]
        speaker = utterance_id.split('_')[1]
        speaker_dir = os.path.join(corpus_root, split, f'musc21_hindi_{speaker}')
        os.makedirs(speaker_dir, exist_ok=True)
        os.rename(os.path.join(audio_dir, file_name), os.path.join(speaker_dir, file_name))
