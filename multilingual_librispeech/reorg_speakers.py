import os

mls_root = 'D:/Data/speech/multilingual_librispeech'

for language in os.listdir(mls_root):
    language_dir = os.path.join(mls_root, language)
    if not os.path.isdir(language_dir):
        continue
    print(language)
    for speaker in os.listdir(language_dir):
        if '_' in speaker:
            continue
        if speaker in ['dev', 'test', 'train']:
            continue
        original_speaker_dir = os.path.join(language_dir, speaker)
        if not os.path.isdir(original_speaker_dir):
            continue
        print(speaker)
        for file in os.listdir(original_speaker_dir):
            t = file.split('_')
            speaker, book = t[0], t[1]
            new_speaker = speaker +"_" + book
            new_speaker_dir = os.path.join(language_dir, new_speaker)
            os.makedirs(new_speaker_dir, exist_ok=True)
            os.rename(os.path.join(original_speaker_dir, file), os.path.join(new_speaker_dir, file))
