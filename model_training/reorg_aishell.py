import os


corpus_root = '/mnt/d/Data/speech/chinese_corpora/data_aishell'
transcript_path = os.path.join(corpus_root, 'transcript', 'aishell_transcript_v0.8.txt')

texts = {}
with open(transcript_path, 'r', encoding='utf8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        utterance, text = line.split(maxsplit=1)
        texts[utterance] = text


for folder in ['test', 'test', 'train']:
    folder_path = os.path.join(corpus_root, 'wav', folder)
    if not os.path.exists(folder_path):
        continue
    for speaker in os.listdir(folder_path):
        speaker_dir = os.path.join(folder_path, speaker)
        out_dir = os.path.join(corpus_root, speaker)
        os.makedirs(out_dir, exist_ok=True)
        for file in os.listdir(speaker_dir):
            utt = file.replace('.wav', '')
            try:
                text = texts[utt]
            except KeyError:
                continue
            with open(os.path.join(out_dir, utt + '.lab'), 'w', encoding='utf8') as f:
                f.write(text)
            os.rename(os.path.join(speaker_dir, file), os.path.join(out_dir, file))