import os
import subprocess

mls_root = r'D:\Data\speech\model_training_corpora\german\mls_german'


for root, _, files in os.walk(mls_root, followlinks=True):
    for f in files:
        if not f.endswith('.opus'):
            continue
        path = os.path.join(root, f)
        flac_path = path.replace('.opus', '.flac')
        if os.path.exists(flac_path):
            os.remove(flac_path)
        command = ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-nostats', '-i', path,
                   '-c:a', 'flac', flac_path]
        subprocess.check_call(command)
        os.remove(path)

error

for folder in ['dev', 'test', 'train']:
    folder_path = os.path.join(polish_directory, folder)
    if not os.path.exists(folder_path):
        continue
    transcripts = {}
    transcript_path = os.path.join(folder_path, 'transcripts.txt')
    with open(transcript_path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            utterance, text = line.split(maxsplit=1)
            transcripts[utterance] = text
    audio_dir = os.path.join(folder_path, 'audio')
    for speaker in os.listdir(audio_dir):
        speaker_dir = os.path.join(audio_dir, speaker)
        output_speaker_dir = os.path.join(polish_directory, speaker)
        os.makedirs(output_speaker_dir, exist_ok=True)
        for sub_dir in os.listdir(speaker_dir):
            for file in os.listdir(os.path.join(speaker_dir, sub_dir)):
                os.rename(os.path.join(speaker_dir, sub_dir, file), os.path.join(output_speaker_dir, file))
                utterance = os.path.splitext(file)[0]
                lab_path = os.path.join(output_speaker_dir, utterance + '.lab')
                with open(lab_path, 'w', encoding='utf8') as f:
                    f.write(transcripts[utterance])