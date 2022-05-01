import os
import json

import librosa
import soundfile
import subprocess
root = r'D:/Data/speech/swedish_corpora'

transcription_data_dir = os.path.join(root, 'ADB_SWE_0467')
audio_dir = os.path.join(root, 'se')

replacements = ['(', ')', '...']

speaker_data = {}
for speaker_file in os.listdir(transcription_data_dir):
    speaker_id = os.path.splitext(speaker_file)[0].split('_')[0]
    speaker_dir = os.path.join(audio_dir, speaker_id)
    print(speaker_dir)
    if not os.path.exists(speaker_dir):
        continue
    with open(os.path.join(transcription_data_dir, speaker_file), 'r', encoding='utf8') as f:
        data = json.load(f)
    if 'val_recordings' not in data:
        continue
    speaker_info = data.pop('info')
    print(speaker_info)
    speaker_data[speaker_id] = {'gender': speaker_info['Sex'],
                                'age': speaker_info['Age'],
                                'dialect': speaker_info['Region_of_Youth']}
    print(data.keys())
    for recording_data in data['val_recordings']:
        file = recording_data['file']
        print(file)
        text = recording_data['text']
        for r in replacements:
            text = text.replace(r, '')
        text = text.strip()
        words = text.split()
        new_words = []
        for w in words:
            if '\\' in w:
               w = w.split('\\')[-1]
            new_words.append(w)
        text = ' '.join(new_words)
        wav_path = os.path.join(speaker_dir, f'{speaker_id}_{file}').replace('\\','/')
        print(wav_path)
        if not os.path.exists(wav_path):
            continue
        text_path = wav_path.replace('.wav', '.lab')
        print(text_path)
        continue
        with open(text_path, 'w', encoding='utf8') as f:
            f.write(text)
        info =soundfile.info(wav_path)
        if info.channels > 1:
            y, sr = librosa.load(wav_path,sr=None,mono=False)
            left = y[0, ...]
            soundfile.write(wav_path, left, sr, format='WAV')

with open(os.path.join(audio_dir, 'speaker_info.tsv'), 'w', encoding='utf8') as f:
    for speaker, info in speaker_data.items():
        f.write(f'{speaker}\t{info["age"]}\t{info["gender"]}\t{info["dialect"]}\n')
