import os


corpus_root = '/mnt/d/Data/speech/vietnamese_corpora/vivos'


for folder in ['test', 'train']:
    folder_path = os.path.join(corpus_root, folder)
    if not os.path.exists(folder_path):
        continue
    texts = {}
    transcript_path = os.path.join(folder_path, 'prompts.txt')
    with open(transcript_path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            utterance, text = line.split(maxsplit=1)
            texts[utterance] = text
    wav_folder = os.path.join(folder_path, 'waves')
    for speaker in os.listdir(wav_folder):
        speaker_dir = os.path.join(wav_folder, speaker)
        out_dir = os.path.join(corpus_root, speaker)
        os.makedirs(out_dir, exist_ok=True)
        for file in os.listdir(speaker_dir):
            utterance = os.path.splitext(os.path.basename(file))[0]
            text = texts[utterance]
            with open(os.path.join(out_dir, f'{utterance}.lab'), 'w', encoding='utf8') as outf:
                outf.write(text)
            os.rename(os.path.join(speaker_dir, file), os.path.join(out_dir, file))