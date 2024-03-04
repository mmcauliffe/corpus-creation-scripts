import os

tamil_root = r'D:\Data\speech\tamil_corpora\mile_tamil_asr_corpus'


for folder in ['train', 'test']:
    if folder == 'train':
        split = 'mile_tamil_train'
    else:
        split = 'mile_tamil_test'
    folder_path = os.path.join(tamil_root, folder)
    audio_dir = os.path.join(folder_path, 'audio_files')
    transcription_dir = os.path.join(folder_path, 'trans_files')
    if not os.path.exists(audio_dir):
        continue

    for file_name in os.listdir(audio_dir):
        if not file_name.endswith('.wav'):
            continue
        utterance_id = file_name.split('.')[0]
        speaker = utterance_id.rsplit('_', maxsplit=1)[0]
        speaker_dir = os.path.join(tamil_root, split, speaker)
        os.makedirs(speaker_dir, exist_ok=True)
        os.rename(os.path.join(audio_dir, file_name), os.path.join(speaker_dir, file_name))

    for file_name in os.listdir(transcription_dir):
        if not file_name.endswith('.txt'):
            continue
        utterance_id = file_name.split('.')[0]
        speaker = utterance_id.rsplit('_', maxsplit=1)[0]
        speaker_dir = os.path.join(tamil_root, split, speaker)
        os.makedirs(speaker_dir, exist_ok=True)
        os.rename(os.path.join(transcription_dir, file_name), os.path.join(speaker_dir, file_name.replace('.txt', '.lab')))
