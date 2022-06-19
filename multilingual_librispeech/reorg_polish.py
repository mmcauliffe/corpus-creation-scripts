import os


mls_root = 'D:/Data/speech/multilingual_librispeech'
polish_directory = os.path.join(mls_root, 'mls_polish_opus')
output_directory = os.path.join(mls_root, 'mls_polish')


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
            s = utterance.split('_')
            new_speaker = s[0] + "_" + s[1]
            new_speaker_dir = os.path.join(output_directory, new_speaker)
            lab_path = os.path.join(new_speaker_dir, utterance + '.lab')
            if not os.path.exists(lab_path):
                with open(lab_path, 'w', encoding='utf8') as f:
                    f.write(transcripts[utterance])

    break
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