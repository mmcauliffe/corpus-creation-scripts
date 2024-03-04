import json

import os


root_dir = r'D:\Data\speech\model_training_corpora\thai\thai_elderly'


for setting in os.listdir(root_dir):
    setting_directory = os.path.join(root_dir, setting)
    if not os.path.isdir(setting_directory):
        continue
    if not os.path.exists(os.path.join(setting_directory, 'transcription.json')):
        continue
    with open(os.path.join(setting_directory, 'transcription.json'), encoding='utf8') as f:
        data = json.load(f)
    for d in data:
        speaker = d["speaker_id"]
        file_name = d["filename"]
        text = d["transcript"]
        speaker_directory = os.path.join(root_dir, speaker)
        os.makedirs(speaker_directory, exist_ok=True)
        with open(os.path.join(speaker_directory, file_name + '.lab'), 'w', encoding='utf8') as f:
            f.write(text)
        wav_file_path = os.path.join(setting_directory, 'Record', file_name +'.wav')
        if os.path.exists(wav_file_path):
            os.rename(wav_file_path, os.path.join(speaker_directory, file_name + '.wav'))

