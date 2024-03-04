import os

tamil_root = r'D:/Data/speech/Microsoft/tamil'
tamil_training = r'D:/Data/speech/model_training_corpora/tamil'


for folder in ['ta-in-Measurement', 'ta-in-Train', 'ta-in-Test']:
    if folder == 'ta-in-Train':
        split = 'ms_tamil_train'
    elif folder == 'ta-in-Test':
        split = 'ms_tamil_test'
    else:
        split = 'ms_tamil_other'
    folder_path = os.path.join(tamil_root, folder)
    audio_dir = os.path.join(folder_path, 'Audios')
    if not os.path.exists(audio_dir):
        continue
    transcription_path = os.path.join(folder_path, 'transcription.txt')
    if os.path.exists(transcription_path):
        with open(transcription_path, encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                utterance_id, text = line.split('\t')
                if utterance_id.startswith('TA'):
                    parts = utterance_id.split('_')[0].split('-')
                    if '-A' in utterance_id:
                        speaker=parts[0]
                    else:
                        speaker= parts[1]
                else:
                    speaker = utterance_id[:5]
                speaker_dir = os.path.join(tamil_root, split, speaker)
                os.makedirs(speaker_dir, exist_ok=True)
                with open(os.path.join(speaker_dir, f"{utterance_id}.lab"), 'w', encoding='utf8') as lab_f:
                    lab_f.write(text)
    for file_name in os.listdir(audio_dir):
        if not file_name.endswith('.wav'):
            continue
        utterance_id = file_name.split('.')[0]
        if utterance_id.startswith('TA'):
            parts = utterance_id.split('_')[0].split('-')
            if '-A' in utterance_id:
                speaker=parts[0]
            else:
                speaker= parts[1]
        else:
            speaker = utterance_id[:5]
        speaker_dir = os.path.join(tamil_root, split, speaker)
        os.makedirs(speaker_dir, exist_ok=True)
        os.rename(os.path.join(audio_dir, file_name), os.path.join(speaker_dir, file_name))

if not os.path.exists(os.path.join(tamil_training, 'ms_tamil_train')):
    os.symlink(os.path.join(tamil_root, 'ms_tamil_train'), os.path.join(tamil_training, 'ms_tamil_train'))